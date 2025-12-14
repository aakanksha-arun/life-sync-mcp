from fastapi import APIRouter, HTTPException
from datetime import date
import schemas
from services import water_logger_svc

router = APIRouter(
    prefix="/notion",
    tags=["Water Tracking"]
)

@router.post("/water")
def add_water_log(entry: schemas.WaterLogInput):
    response = water_logger_svc.log_water_entry(entry)
    return {
        "status": "success",
        "id": response["id"],
        "logged_amount": entry.amount_oz,
        "date": entry.log_date
    }
    

@router.get("/water", response_model=schemas.WaterLogSummary)
def get_water_log_for_today():
    return water_logger_svc.get_daily_total(date.today())