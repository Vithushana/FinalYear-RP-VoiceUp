from app.services_sarma.gis_severity_service_sa import calculate_gis_severity

result = calculate_gis_severity(
    near_public_place=True,
    is_remote_area=False
)

print(result)
