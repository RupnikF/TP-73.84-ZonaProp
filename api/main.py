from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import joblib
from preprocess import process_single_row

# Rutas de los modelos (ajustar luego)
SCALER_PATH = "../models/standardscaler.joblib"
ENCODER_PATH = "../models/onehotencoder.joblib"
MODEL_PATH = "../models/lgbm_model.joblib"
REFERENCE_DATA_PATH = "../dataset_reference.csv"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL_PATH)
    app.state.scaler = joblib.load(SCALER_PATH)
    app.state.encoder = joblib.load(ENCODER_PATH)
    app.state.reference_data = pd.read_csv(REFERENCE_DATA_PATH)
    yield

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
    reference_data = request.app.state.reference_data
    row_dict = req.to_dict()
    processed = process_single_row(row_dict, scaler, encoder,reference_data)
    if processed is None:
        raise HTTPException(status_code=400, detail="Could not resolve the location or process the input data.")
    # Eliminar columna 'price' si existe, para predecir
    if 'price' in processed.columns:
        X = processed.drop(columns=['price'])
    else:
        X = processed
    pred = model.predict(X)[0]
    #Aplicar la inversa del log1p para obtener el valor original
    pred = np.expm1(pred)
    return {"predicted_value": float(pred)}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000)