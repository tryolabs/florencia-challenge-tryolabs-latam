from enum import Enum
import logging
from typing import List

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi.exceptions import RequestValidationError

from challenge.model import DelayModel

app = FastAPI()

delay_model = DelayModel()

class FlightType(str, Enum):
    NATIONAL = 'N'
    INTERNATIONAL = 'I'

class Airline(str, Enum):
    AMERICAN_AIRLINES = 'American Airlines'
    AIR_CANADA = 'Air Canada'
    AIR_FRANCE = 'Air France'
    AEROMEXICO = 'Aeromexico'
    AEROLINEAS_ARGENTINAS = 'Aerolineas Argentinas'
    AUSTRAL = 'Austral'
    AVIANCA = 'Avianca'
    ALITALIA = 'Alitalia'
    BRITISH_AIRWAYS = 'British Airways'
    COPA_AIR = 'Copa Air'
    DELTA_AIR = 'Delta Air'
    GOL_TRANS = 'Gol Trans'
    IBERIA = 'Iberia'
    KLM = 'K.L.M.'
    QANTAS_AIRWAYS = 'Qantas Airways'
    UNITED_AIRLINES = 'United Airlines'
    GRUPO_LATAM = 'Grupo LATAM'
    SKY_AIRLINE = 'Sky Airline'
    LATIN_AMERICAN_WINGS = 'Latin American Wings'
    PLUS_ULTRA_LINEAS_AEREAS = 'Plus Ultra Lineas Aereas'
    JETSMART_SPA = 'JetSmart SPA'
    OCEANAIR_LINHAS_AEREAS = 'Oceanair Linhas Aereas'
    LACSA = 'Lacsa'

class FlightData(BaseModel):
    """
    Model to represent the data for each flight.
    """
    OPERA: Airline
    TIPOVUELO: FlightType
    MES: int = Field(..., ge=1, le=12, description="Month value must be between 1 and 12")

class FlightsRequest(BaseModel):
    """
    Model to represent the request body containing multiple flights.
    """
    flights: List[FlightData]
    
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors by returning a 400 status code.
    """
    logging.error("Validation error: %s", exc)
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )

@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

@app.post("/predict", status_code=200)
async def predict_delays(request: FlightsRequest) -> dict: 
    """
    Predict delays for given flight data.
    
    Args:
        request (FlightsRequest): The flight data for which to predict delays.

    Returns:
        dict: A dictionary containing the predictions.
    """
    try:
        flight_data = pd.DataFrame([flight.dict() for flight in request.flights])
        preprocessed_data = delay_model.preprocess(flight_data)
        predictions = delay_model.predict(preprocessed_data)
        return {"predict": predictions}
    except Exception as e:
        logging.error("An error occurred: %s", e)
        raise HTTPException(status_code=500, detail="An internal error occurred")
