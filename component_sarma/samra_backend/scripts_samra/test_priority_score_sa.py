from app.services_sarma.priority_scoring_service_sa import calculate_priority_score

result = calculate_priority_score(
    text_severity=35,
    gis_severity=20,
    recurring_severity=15
)

print(result)
