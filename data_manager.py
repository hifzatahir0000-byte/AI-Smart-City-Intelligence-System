"""Dataset loading, validation, and CSV upload helpers."""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_FILE = BASE_DIR / "data" / "sample_city_data.csv"
REQUIRED_COLUMNS = ["location", "day", "traffic", "aqi"]


def load_sample_data():
    return pd.read_csv(SAMPLE_FILE)


def validate_dataset(file_storage):
    """Read and validate an uploaded CSV without silently filling missing values."""
    if not file_storage or not file_storage.filename:
        raise ValueError("Please choose a CSV file.")
    if Path(file_storage.filename).suffix.lower() != ".csv":
        raise ValueError("Only CSV files are supported.")
    try:
        df = pd.read_csv(file_storage, dtype={"location": "string", "day": "string"})
    except Exception as exc:
        raise ValueError("The CSV could not be read. Please check its format.") from exc
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError("Missing required columns: " + ", ".join(missing_columns))
    if df.empty:
        raise ValueError("The uploaded CSV contains no data rows.")
    df = df[REQUIRED_COLUMNS].copy()
    if df[REQUIRED_COLUMNS].isna().any().any():
        missing = df[REQUIRED_COLUMNS].isna().sum()
        details = ", ".join(f"{col}: {int(count)}" for col, count in missing.items() if count)
        raise ValueError("Missing values found (" + details + "). Please correct them; values are not replaced with zero.")
    for column in ("traffic", "aqi"):
        df[column] = pd.to_numeric(df[column], errors="coerce")
        if df[column].isna().any():
            raise ValueError(f"Column '{column}' contains non-numeric values.")
        if (df[column] < 0).any():
            raise ValueError(f"Column '{column}' cannot contain negative values.")
    df["location"] = df["location"].astype(str).str.strip()
    df["day"] = df["day"].astype(str).str.strip()
    if (df["location"] == "").any() or (df["day"] == "").any():
        raise ValueError("Location and day fields cannot be blank.")
    if df.duplicated(["location", "day"]).any():
        raise ValueError("Duplicate location/day rows were found. Each pair must be unique.")
    return df


def to_matrix(df, metric):
    pivot = df.pivot(index="location", columns="day", values=metric)
    return pivot.sort_index(axis=1), pivot.index.tolist()
