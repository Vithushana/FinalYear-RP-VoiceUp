from fastapi import FastAPI
from app.database_sarma import Base, engine
from app.routers_sarma.complints_router_sa import router as complaints_router
from app.routers_sarma.officer_router_sa import router as officer_router
from fastapi.middleware.cors import CORSMiddleware



# Create database tables 
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application 
app = FastAPI(title="VoiceUp Decision Support API")

app.include_router(complaints_router)
app.include_router(officer_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "OK"}
