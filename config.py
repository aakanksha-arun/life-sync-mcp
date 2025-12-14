import os
from dotenv import load_dotenv

load_dotenv()
# Notion Config
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
WATER_DB_ID = os.getenv("NOTION_WATER_DB_ID")
TITLE_PROP = "Title"
DATE_PROP = "Date"
AMOUNT_PROP = "Amount"
DAILY_GOAL_OZ = 100

# Todoist Config
TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")