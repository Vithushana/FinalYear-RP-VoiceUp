# VoiceUp – AI or Real Image Classification (Backend)

This repository contains the backend service for **VoiceUp**, a research project that checks whether a road accident image is **AI-generated or real** and helps validate user reports from the mobile app (Flutter frontend).

The backend is built with **Python** and **FastAPI** and is designed to:

- Receive an **image + description** from the Flutter app
- Run the image through an AI vs Real classifier (Kaggle-trained model – to be integrated)
- Optionally analyse the text description
- Return a final **decision**: `accept`, `flag`, or `reject`

---

## 🚀 Tech Stack

- **Language:** Python
- **Framework:** FastAPI
- **Server:** Uvicorn
- **ML Model:** Kaggle-trained image classifier (AI vs Real) – PyTorch / TensorFlow (TBD)
- **Other:** Pillow (image handling)

---

## 📁 Project Structure

```text
RP-VoiceUp/
  ├─ main.py            # FastAPI app (endpoints)
  ├─ venv/              # Python virtual environment (not pushed to Git)
  └─ models/            # (Planned) model weights e.g. model.pth
