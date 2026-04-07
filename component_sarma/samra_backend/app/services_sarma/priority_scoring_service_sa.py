def calculate_priority_score(
    text_severity: int,
    gis_severity: int,
    recurring_severity: int
) -> dict:
    """
    Combines Text, GIS, and Recurring severity into a final priority score (0-100).
    Enhanced with Strategic Weighting for Research-Grade Decision Support.
    """

    # 1. Strategic Weighting
    # In smart governance, GIS (location impact) often carries more weight for 
    # resource allocation than just the text of the complaint.
    weighted_text = text_severity * 1.0
    weighted_gis = gis_severity * 1.2  # GIS has a 20% higher impact on the final score
    weighted_recurring = recurring_severity * 1.0

    # 2. Calculate Final Score
    raw_total = weighted_text + weighted_gis + weighted_recurring
    final_score = int(min(raw_total, 100))

    # 3. Decision Justification (Explainable AI)
    # This helps the officer understand the "Big Issue" drivers.
    primary_driver = "Balanced"
    if gis_severity >= text_severity and gis_severity >= recurring_severity:
        primary_driver = "Geospatial Impact (Landmarks/Isolation)"
    elif text_severity >= gis_severity and text_severity >= recurring_severity:
        primary_driver = "Urgency/Public Sentiment (Text Analysis)"
    elif recurring_severity > 0:
        primary_driver = "Chronic Service Failure (Recurring Issue)"

    return {
        "priority_score": final_score,
        "score_breakdown": {
            "text_severity": text_severity,
            "gis_severity": gis_severity,
            "recurring_severity": recurring_severity
        },
        "analysis_meta": {
            "primary_priority_driver": primary_driver,
            "is_high_impact": final_score >= 70,
            "calculation_method": "Weighted Hybrid Logic (v2.0)"
        }
    }