

import random
import re

# --- Realism settings ---
AMBIGUOUS_RATE = 0.18
TYPO_RATE = 0.06
FILLER_RATE = 0.35
REMOVE_KEYWORD_RATE = 0.12

FILLERS = [
    "actually", "to be honest", "we are facing", "we are suffering", "it is becoming",
    "please consider", "kindly look into", "requesting you to", "this is affecting us"
]

PREFIXES = ["", "Please", "Kindly", "We request", "Urgently", "I want to report"]
SUFFIXES = ["", "in our area", "near our houses", "for the past few days", "and it needs action", "as soon as possible"]

SYNONYMS = {
    "garbage": ["waste", "trash", "solid waste"],
    "not collected": ["not picked", "not cleared", "not taken"],
    "overflowing": ["spilling", "overfilled", "overflowed"],
    "blocked": ["obstructed", "closed", "not passable"],
    "damaged": ["broken", "bad condition", "worn out"],
    "road": ["street", "route", "lane"],
    "mosquito": ["insects", "mosquitoes"],
    "disease": ["health issues", "infection risk"],
}

def expand_complaint_text(category: str, text: str) -> str:
    base_intro = f"This complaint is related to {category} infrastructure."
    expanded = (
        f"{base_intro} "
        f"The citizen reports the following issue: {text.strip()}. "
        "This issue affects daily public usage and requires attention from authorities. "
        "The complaint has been submitted with location details for further analysis. "
        "The system will evaluate severity, recurrence, and impact to support officer decision-making."
    )
    return expanded

def apply_synonyms(text: str) -> str:
    t = text
    for k, options in SYNONYMS.items():
        if k in t.lower() and random.random() < 0.35:
            t = re.sub(re.escape(k), random.choice(options), t, flags=re.IGNORECASE)
    return t

def add_filler(text: str) -> str:
    if random.random() < FILLER_RATE:
        filler = random.choice(FILLERS)
        parts = text.split()
        if len(parts) > 4:
            idx = random.randint(1, min(6, len(parts)-1))
            parts.insert(idx, filler)
            return " ".join(parts)
    return text

def add_prefix_suffix(text: str) -> str:
    pre = random.choice(PREFIXES).strip()
    suf = random.choice(SUFFIXES).strip()
    t = text.strip()
    if pre:
        t = f"{pre} {t}"
    if suf and suf.lower() not in t.lower():
        t = f"{t} {suf}"
    return t

def maybe_remove_obvious_keywords(text: str) -> str:
    if random.random() < REMOVE_KEYWORD_RATE:
        easy_words = ["urgent", "ambulance", "school", "hospital", "mosquito", "disease", "health"]
        t = text
        for w in easy_words:
            t = re.sub(rf"\b{w}\b", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\s+", " ", t).strip()
        return t if len(t) > 10 else text
    return text

def add_small_typo(text: str) -> str:
    if random.random() < TYPO_RATE and len(text) > 12:
        i = random.randint(2, len(text)-3)
        if text[i].isalpha() and text[i+1].isalpha():
            text = text[:i] + text[i+1] + text[i] + text[i+2:]
    return text

def make_variation(base_text: str) -> str:
    t = base_text.strip()
    t = apply_synonyms(t)
    t = add_filler(t)
    t = add_prefix_suffix(t)
    t = maybe_remove_obvious_keywords(t)
    t = add_small_typo(t)
    t = t.replace("..", ".").strip()
    if not t.endswith("."):
        t += "."
    return t

def make_ambiguous_text(main_category: str, base_text: str) -> str:
    t = base_text
    if random.random() < AMBIGUOUS_RATE:
        if main_category == "road":
            t += " Also, waste is seen along the street sometimes."
        else:
            t += " The street condition also makes cleaning difficult."
    return t
