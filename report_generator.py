"""Create a downloadable PDF report using ReportLab."""
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "generated_reports"
REPORT_DIR.mkdir(exist_ok=True)


def generate_pdf(metrics, ai_result, recommendations):
    filename = f"smart_city_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = REPORT_DIR / filename
    styles = getSampleStyleSheet()
    story = [Paragraph("Smart City Intelligence Weekly Report", styles["Title"]),
             Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]), Spacer(1, 12),
             Paragraph("Executive Summary", styles["Heading2"]),
             Paragraph(f"Highest average traffic: {metrics['highest_traffic_location']}. Highest average AQI: {metrics['highest_aqi_location']}. Total readings: {metrics['total_readings']}.", styles["BodyText"]),
             Paragraph(metrics["sample_note"], styles["Italic"]), Spacer(1, 8),
             Paragraph("Traffic Analysis", styles["Heading2"])]
    traffic_rows = [["Location", "Average vehicles", "Total vehicles", "First-to-last change"]]
    for loc in metrics["locations"]:
        i = metrics["locations"].index(loc)
        traffic_rows.append([loc, str(metrics["traffic"]["average_by_location"][loc]), str(round(metrics["traffic"]["total_by_location"][loc])), f"{metrics['traffic']['percent_change_by_location'][i]}%"])
    table = Table(traffic_rows, repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0), colors.HexColor("#174d38")), ("TEXTCOLOR", (0,0),(-1,0), colors.white), ("GRID",(0,0),(-1,-1),0.4,colors.grey), ("PADDING",(0,0),(-1,-1),6)]))
    story += [table, Spacer(1, 10), Paragraph("Air Quality Analysis", styles["Heading2"])]
    aqi_rows = [["Location", "Average AQI"]] + [[loc, str(metrics["aqi"]["average_by_location"][loc])] for loc in metrics["locations"]]
    aqi_table = Table(aqi_rows, repeatRows=1)
    aqi_table.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0), colors.HexColor("#174d38")), ("TEXTCOLOR", (0,0),(-1,0), colors.white), ("GRID",(0,0),(-1,-1),0.4,colors.grey), ("PADDING",(0,0),(-1,-1),6)]))
    story += [aqi_table, Spacer(1, 10), Paragraph("Detected Anomalies", styles["Heading2"])]
    if metrics["anomalies"]:
        for item in metrics["anomalies"][:30]:
            story.append(Paragraph(f"{item['location']} — {item['day']}: traffic {item['traffic']}, AQI {item['aqi']} ({item['reason']})", styles["BodyText"]))
    else:
        story.append(Paragraph("No readings crossed the configured anomaly rules.", styles["BodyText"]))
    story += [Spacer(1, 8), Paragraph("Trend Estimates", styles["Heading2"]), Paragraph(metrics["predictions"]["warning"], styles["Italic"])]
    for item in metrics["predictions"]["traffic"]:
        story.append(Paragraph(f"{item['location']}: next-day traffic estimate {item['estimate']} ({item['trend']})", styles["BodyText"]))
    story += [Spacer(1, 8), Paragraph("AI Analysis", styles["Heading2"]), Paragraph(ai_result["label"], styles["Italic"]), Paragraph(ai_result["text"].replace("&", "&amp;").replace("<", "&lt;"), styles["BodyText"]), Paragraph("AI Recommendations", styles["Heading2"])]
    for item in recommendations["items"]:
        story.append(Paragraph("• " + item.replace("&", "&amp;"), styles["BodyText"]))
    story += [Spacer(1, 10), Paragraph("Limitations and Data Quality Notes", styles["Heading2"]), Paragraph("This report reflects only the currently loaded dataset. Missing values are rejected during CSV upload rather than silently replaced. Threshold and z-score flags are indicators for review, not proof of an emergency. Linear estimates based on a short series are experimental and are not reliable production forecasts. Confirm measurement source, units, sensor calibration, and collection methods before making decisions.", styles["BodyText"])]
    SimpleDocTemplate(str(path), pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42).build(story)
    return path
