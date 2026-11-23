"""NumPy-powered analytics for the Smart City Intelligence System."""
import numpy as np
from data_manager import to_matrix


def _matrix(df, metric):
    pivot, locations = to_matrix(df, metric)
    return pivot.to_numpy(dtype=float), locations, [str(x) for x in pivot.columns]


def analyze_dataset(df, traffic_threshold=1500, aqi_threshold=150, z_threshold=2.0):
    traffic, locations, days = _matrix(df, "traffic")
    aqi, aqi_locations, _ = _matrix(df, "aqi")
    if locations != aqi_locations or traffic.shape != aqi.shape:
        raise ValueError("Traffic and AQI data must have matching locations and days.")
    if not np.isfinite(traffic).all() or not np.isfinite(aqi).all():
        raise ValueError("Dataset contains missing or non-finite numeric values.")

    traffic_means = np.mean(traffic, axis=1)
    aqi_means = np.mean(aqi, axis=1)
    traffic_std = np.std(traffic, axis=1)
    aqi_std = np.std(aqi, axis=1)
    traffic_rank = np.argsort(traffic_means)[::-1]
    aqi_rank = np.argsort(aqi_means)[::-1]

    # Vectorized boolean masks and z-scores identify readings for review.
    traffic_mask = traffic > float(traffic_threshold)
    aqi_mask = aqi > float(aqi_threshold)
    traffic_global_std = float(np.std(traffic))
    aqi_global_std = float(np.std(aqi))
    traffic_z = (traffic - np.mean(traffic)) / traffic_global_std if traffic_global_std else np.zeros_like(traffic)
    aqi_z = (aqi - np.mean(aqi)) / aqi_global_std if aqi_global_std else np.zeros_like(aqi)
    anomalies = []
    for i, j in np.argwhere(traffic_mask | aqi_mask | (np.abs(traffic_z) >= z_threshold) | (np.abs(aqi_z) >= z_threshold)):
        reasons = []
        if traffic_mask[i, j]: reasons.append(f"traffic above {traffic_threshold}")
        if aqi_mask[i, j]: reasons.append(f"AQI above {aqi_threshold}")
        if abs(traffic_z[i, j]) >= z_threshold: reasons.append(f"traffic z-score {traffic_z[i, j]:.2f}")
        if abs(aqi_z[i, j]) >= z_threshold: reasons.append(f"AQI z-score {aqi_z[i, j]:.2f}")
        anomalies.append({"location": locations[i], "day": days[j], "traffic": float(traffic[i, j]), "aqi": float(aqi[i, j]), "reason": "; ".join(reasons)})

    # A least-squares linear fit is used only as a simple educational trend estimate.
    x = np.arange(traffic.shape[1], dtype=float)
    traffic_predictions, aqi_predictions = [], []
    for i, location in enumerate(locations):
        t_slope, t_intercept = np.polyfit(x, traffic[i], 1)
        a_slope, a_intercept = np.polyfit(x, aqi[i], 1)
        next_x = float(len(x))
        traffic_next = max(0.0, float(t_slope * next_x + t_intercept))
        aqi_next = max(0.0, float(a_slope * next_x + a_intercept))
        traffic_predictions.append({"location": location, "estimate": round(traffic_next, 1), "trend": "Increasing" if t_slope > 0 else "Decreasing" if t_slope < 0 else "Stable"})
        aqi_predictions.append({"location": location, "estimate": round(aqi_next, 1), "trend": "Increasing" if a_slope > 0 else "Decreasing" if a_slope < 0 else "Stable"})

    total_readings = int(traffic.size)
    result = {
        "sample_note": "Fictional educational sample values; not real-time city measurements." if set(locations).issubset({"Saddar", "Commercial Market", "Murree Road", "Satellite Town"}) else "User-uploaded dataset; measurement source was not independently verified.",
        "locations": locations, "days": days,
        "traffic_matrix": traffic.tolist(), "aqi_matrix": aqi.tolist(),
        "traffic": {"mean": round(float(np.mean(traffic)), 2), "median": round(float(np.median(traffic)), 2), "min": float(np.min(traffic)), "max": float(np.max(traffic)), "std": round(float(np.std(traffic)), 2), "percentile_75": round(float(np.percentile(traffic, 75)), 2), "daily_average": np.mean(traffic, axis=0).round(2).tolist(), "total_by_location": {loc: float(np.sum(traffic[i])) for i, loc in enumerate(locations)}, "average_by_location": {loc: round(float(traffic_means[i]), 2) for i, loc in enumerate(locations)}, "ranked_locations": [locations[i] for i in traffic_rank], "high_readings": int(np.count_nonzero(traffic_mask)), "growth_10_percent": (traffic * 1.10).round(2).tolist(), "percent_change_by_location": [round(float((row[-1] - row[0]) / row[0] * 100), 2) if row[0] else None for row in traffic]},
        "aqi": {"mean": round(float(np.mean(aqi)), 2), "median": round(float(np.median(aqi)), 2), "min": float(np.min(aqi)), "max": float(np.max(aqi)), "std": round(float(np.std(aqi)), 2), "percentile_75": round(float(np.percentile(aqi, 75)), 2), "daily_average": np.mean(aqi, axis=0).round(2).tolist(), "average_by_location": {loc: round(float(aqi_means[i]), 2) for i, loc in enumerate(locations)}, "ranked_locations": [locations[i] for i in aqi_rank], "high_readings": int(np.count_nonzero(aqi_mask)), "locations_above_100": [locations[i] for i in np.where(aqi_means > 100)[0]]},
        "array_info": {"traffic_ndim": int(traffic.ndim), "traffic_shape": list(traffic.shape), "traffic_size": int(traffic.size), "aqi_ndim": int(aqi.ndim), "aqi_shape": list(aqi.shape), "aqi_size": int(aqi.size)},
        "anomalies": anomalies,
        "predictions": {"traffic": traffic_predictions, "aqi": aqi_predictions, "warning": "Experimental linear estimates based on the available readings only. A short dataset is not sufficient for reliable real-world forecasting."},
        "highest_traffic_location": locations[int(np.argmax(traffic_means))],
        "highest_aqi_location": locations[int(np.argmax(aqi_means))],
        "high_traffic_readings": int(np.count_nonzero(traffic_mask)),
        "high_aqi_readings": int(np.count_nonzero(aqi_mask)),
        "total_readings": total_readings,
    }
    return result
