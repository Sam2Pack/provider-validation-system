from fastapi import FastAPI
from pydantic import BaseModel
from Pipeline.agent import run_pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API is running"}


class ProviderInput(BaseModel):
    npi: str
    provider_first_name: str
    provider_last_name: str
    provider_address: str


@app.post("/predict")
def predict_provider(data: ProviderInput):
    result = run_pipeline([data.dict()])
    return result[0]