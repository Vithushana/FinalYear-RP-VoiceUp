from app.services_sarma.text_severity_service_sa import calculate_text_severity

sample_text = "Garbage causes bad smell and health risk near school every day."
result = calculate_text_severity(sample_text)

print("RESULT:", result)
