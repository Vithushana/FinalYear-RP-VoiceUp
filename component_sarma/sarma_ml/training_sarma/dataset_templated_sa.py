TEMPLATES = [
    # ROAD
    # format:
    # (main_category, sub_category, priority_level, severity_score, [base_texts])

    ("road", "infrastructure_gap", 2, 20, [
        "We need a proper road connection in our area",
        "There is no proper road facility in our locality",
        "Our area does not have a usable road for vehicles",
        "Please provide a new road connection for our street"
    ]),

    ("road", "access_mobility", 1, 36, [
        "The road is damaged and garbage is also dumped nearby",
        "Vehicles cannot pass and waste is piled up on the side",
        "Road condition is bad and cleaning vehicles avoid this street"
    ]),

    ("road", "infrastructure_gap", 2, 18, [
        "Please check the condition in our area",
        "People are facing difficulty because of road issues",
        "This problem has been there for some time",
        "The situation is becoming worse day by day"
    ]),

    ("road", "access_mobility", 1, 38, [
        "Vehicles cannot pass because the road is blocked",
        "Ambulance access is difficult due to road condition",
        "Children cannot safely walk to school using this road",
        "Access is affected and people cannot reach easily"
    ]),

    # GARBAGE
    ("garbage", "missed_collection", 3, 12, [
        "Please look into this issue",
        "We are facing inconvenience daily",
        "This has been going on for many days",
        "Requesting authorities to take action"
    ]),

    ("garbage", "recurring_garbage_point", 2, 24, [
        "Garbage is dumped near the road and causes traffic problems",
        "Waste is blocking part of the street and people are affected",
        "Garbage accumulation makes it hard to use the road"
    ]),

    ("garbage", "health_risk", 1, 35, [
        "Garbage causes bad smell and mosquito breeding",
        "Children are affected due to insects and waste here",
        "Waste is rotting and may spread diseases",
        "There are rats and mosquitoes due to waste accumulation"
    ]),

    ("garbage", "access_mobility", 1, 34, [
        "Garbage blocks the road and vehicles cannot pass",
        "Pedestrians cannot walk because waste is spread",
        "Waste is blocking access and movement is affected",
        "The street is partially blocked because of garbage"
    ]),
]