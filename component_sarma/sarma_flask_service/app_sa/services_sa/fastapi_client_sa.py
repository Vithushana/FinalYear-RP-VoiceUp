import requests

FASTAPI_BASE = "http://127.0.0.1:8000"

# 1. NEW: AI Expansion call to FastAPI
def forward_expand_text(payload: dict) -> dict:
    url = f"{FASTAPI_BASE}/complaints/expand" # FastAPI engine expansion endpoint
    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        # Raise a clearer exception for the Flask layer to return
        err = f"Error forwarding expand_text to FastAPI ({url}): {e}"
        print(err)
        raise RuntimeError(err)

# 2. Existing Submission logic
def forward_submit_complaint(payload: dict) -> dict:
    url = f"{FASTAPI_BASE}/complaints/submit"
    try:
        # Change 30 to 60 here. 
        # This gives your GIS engine enough time to find landmarks.
        r = requests.post(url, json=payload, timeout=60) 
        r.raise_for_status()
        return r.json()
    except Exception as e:
        err = f"Error forwarding submit to FastAPI ({url}): {e}"
        print(err)
        raise RuntimeError(err)

# 3. Existing List logic
def forward_list_all() -> list:
    url = f"{FASTAPI_BASE}/complaints/all"
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        err = f"Error forwarding list_all to FastAPI ({url}): {e}"
        print(err)
        raise RuntimeError(err) 

def forward_officer_complaint(complaint_id: int) -> dict:
    url = f"{FASTAPI_BASE}/officer/complaint/{complaint_id}"
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        err = f"Error forwarding officer complaint to FastAPI ({url}): {e}"
        print(err)
        raise RuntimeError(err)