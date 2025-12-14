from fastapi import HTTPException
from notion_client import Client
import config, schemas

#init
try:
    client = Client(auth=config.NOTION_TOKEN)
except Exception as e:
    client = None
    print(f"Notion client failed: {e}")


def get_data_source_id(database_id: str) -> str:
    if not client:
        raise HTTPException(status_code=400, detail=f"Notion Client not initialized: {str(e)}")
    db_info = client.databases.retrieve(database_id=database_id)
    data_sources = db_info.get("data_sources", [])
    if not data_sources:
        raise HTTPException(status_code=404, detail="No Data Source found in this Database.")
    target_source_id = data_sources[0]["id"]
    return target_source_id


def log_water_entry(entry: schemas.WaterLogInput):
    if not client:
        raise HTTPException(status_code=400, detail=f"Notion Client not initialized: {str(e)}")
    page_title = f"Water Log - {entry.log_date}"
    properties_payload = {
        config.TITLE_PROP: {
            "title": [
                {"text": {"content": page_title}}
            ]
        },
        config.AMOUNT_PROP: {
            "number": entry.amount_oz
        },
        config.DATE_PROP: {
            "date": {
                "start": entry.log_date.isoformat()
            }
        }
    }
    try:
        response = client.pages.create(
            parent={"database_id": config.WATER_DB_ID},
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
    
def get_daily_total(target_date):
    if not client:
        raise HTTPException(status_code=500, detail="Notion API key not configured in .env file.")
    target_date_iso = target_date.isoformat()
    try:
        target_source_id = get_data_source_id(config.WATER_DB_ID)
        response = client.data_sources.query(
            data_source_id=target_source_id,
            filter={
                "property": config.DATE_PROP,
                "date": {
                    "equals": target_date_iso
                }
            }
        )

        #calculate sum
        daily_total = 0.0
        results = response.get("results", [])
        for page in results:
            props = page["properties"]

            amount = props.get(config.AMOUNT_PROP, {}).get("number") or 0.0
            daily_total+=amount

        progress_percentage = (daily_total/config.DAILY_GOAL_OZ *100) if config.DAILY_GOAL_OZ else 0

        return{
            "date": target_date_iso,
            "total_intake_oz": round(daily_total, 2),
            "goal_oz": config.DAILY_GOAL_OZ,
            "progress_percentage": round(progress_percentage, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching from Notion: {str(e)}")
