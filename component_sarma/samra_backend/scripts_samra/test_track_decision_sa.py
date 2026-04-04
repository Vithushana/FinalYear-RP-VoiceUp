from app.services_sarma.track_decision_service_sa import determine_priority_track

print(determine_priority_track("road", "We need a new road in our area.", False))
print(determine_priority_track("garbage", "Garbage is not collected on schedule.", False))
print(determine_priority_track("road", "This issue happens again and again.", True))
