from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import Optional
import joblib
from .preprocess import process_single_row

# Rutas de los modelos (ajustar luego)
SCALER_PATH = "minmaxscaler.joblib"
ENCODER_PATH = "onehotencoder.joblib"
MODEL_PATH = "randomforest.joblib"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL_PATH)
    app.state.scaler = joblib.load(SCALER_PATH)
    app.state.label_encoder = joblib.load(ENCODER_PATH)

app = FastAPI(lifespan=lifespan)

@app.get("/")
def welcome():
    return {"message": "Welcome, to the Prophetario API!"}

# Modelo de entrada
class PredictionRequest(BaseModel):
    url: str
    title: str
    rent_price: str
    expenses_price: str
    location: str
    icon_stotal: Optional[str] = Field(None, alias="icon-stotal")
    icon_scubierta: Optional[str] = Field(None, alias="icon-scubierta")
    icon_ambiente: Optional[str] = Field(None, alias="icon-ambiente")
    icon_bano: Optional[str] = Field(None, alias="icon-bano")
    icon_cochera: Optional[str] = Field(None, alias="icon-cochera")
    icon_dormitorio: Optional[str] = Field(None, alias="icon-dormitorio")
    icon_antiguedad: Optional[str] = Field(None, alias="icon-antiguedad")
    icon_orientacion: Optional[str] = Field(None, alias="icon-orientacion")
    general_features: Optional[str] = None
    icon_toilete: Optional[str] = Field(None, alias="icon-toilete")
    features: Optional[str] = None
    icon_luminosidad: Optional[str] = Field(None, alias="icon-luminosidad")
    icon_disposicion: Optional[str] = Field(None, alias="icon-disposicion")
    icon_inmueble: Optional[str] = Field(None, alias="icon-inmueble")

    # Para compatibilidad con preprocess
    def to_dict(self):
        return self.model_dump(by_alias=True)

@app.post("/predict")
def predict(req: PredictionRequest, request: Request):
    scaler = request.app.state.scaler
    encoder = request.app.state.encoder
    model = request.app.state.model
    row_dict = req.to_dict()
    processed = process_single_row(row_dict, scaler, encoder)
    # Eliminar columna 'price' si existe, para predecir
    if 'price' in processed.columns:
        X = processed.drop(columns=['price'])
    else:
        X = processed
    pred = model.predict(X)[0]
    return {"predicted_value": float(pred)}