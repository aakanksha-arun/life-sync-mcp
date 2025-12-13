from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import os
from notion_client import Client
from datetime import date
from dotenv import load_dotenv

load_dotenv()
# Configuration
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
WATER_DB_ID = os.getenv("NOTION_WATER_DB_ID")

TITLE_PROP = "Title"
DATE_PROP = "Date"
AMOUNT_PROP = "Amount"

#init notion
try:
    NOTION_CLIENT = Client(auth=NOTION_TOKEN)
except Exception as e:
    NOTION_CLIENT = None
    print(f"Notion client failed to initialize: {e}")

router = APIRouter()

WATER_LOG = {}
DAILY_GOAL_OZ = 100

class WaterLogInput(BaseModel):
    """
    Defines the structure for logging water intake in fl oz.
    Defaults to today's date if not provided.
    """
    amount_oz: float
    log_date: date = Field(default_factory=date.today)

@router.post("/notion/water")
def add_water_log(entry: WaterLogInput):
    if not NOTION_CLIENT:
        raise HTTPException(status_code=500, detail="Notion API key not configured in .env file.")
    
    #Ready the data for sending to notion
    page_title = f"Water Log - {entry.log_date}"
    properties_payload = {
        TITLE_PROP: {
            "title": [
                {"text": {"content": page_title}}
            ]
        },
        AMOUNT_PROP: {
            "number": entry.amount_oz
        },
        DATE_PROP: {
            "date": {
                "start": entry.log_date.isoformat()
            }
        }
    }
    
    #Send to Notion
    try:
        response = NOTION_CLIENT.pages.create(
            parent={"database_id": WATER_DB_ID},
            properties = properties_payload
        )
        return {
            "status": "success",
            "id": response["id"],
            "url": response["url"],
            "logged_amount": entry.amount_oz,
            "date": entry.log_date
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error logging to Notion: {str(e)}")
@router.get("/notion/water")
def get_water_log_for_today():
    if not NOTION_CLIENT:
        raise HTTPException(status_code=500, detail="Notion API key not configured in .env file.")
    today_iso = date.today().isoformat()

    try:
        db_info = NOTION_CLIENT.databases.retrieve(database_id=WATER_DB_ID)
        data_sources = db_info.get("data_sources", [])
        if not data_sources:
            raise HTTPException(status_code=404, detail="No Data Source found in this Database.")
        

        target_source_id = data_sources[0]["id"]

        response = NOTION_CLIENT.data_sources.query(
            data_source_id=target_source_id,
            filter={
                "property": DATE_PROP,
                "date": {
                    "equals": today_iso
                }
            }
        )

        #calculate sum
        daily_total = 0.0
        results = response.get("results", [])
        print(response)
        for page in results:
            props = page["properties"]

            amount = props.get(AMOUNT_PROP, {}).get("number") or 0.0
            daily_total+=amount

        progress_percentage = (daily_total/DAILY_GOAL_OZ *100) if DAILY_GOAL_OZ else 0

        return{
            "date": today_iso,
            "total_intake_oz": round(daily_total, 2),
            "goal_oz": DAILY_GOAL_OZ,
            "progress_percentage": round(progress_percentage, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching from Notion: {str(e)}")
