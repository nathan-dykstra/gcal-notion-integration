import os
from notion_client import Client
from googleapiclient.discovery import build
import pickle
from setup import *

# Set up the Google Calendar API connection

gCalCredentials = pickle.load(open(PROJECT_LOCATION + 'token.pkl', 'rb'))
service = build('calendar', 'v3', credentials=gCalCredentials)

# If the the Google Calendar API token expires, then gCalToken.py creates a new token for the program to use

print("Verifying the Google Calendar API token...\n")

try:
    calendar = service.calendars().get(calendarId=DEFAULT_CALENDAR_ID).execute()
    print("Google Calendar API token is valid!\n")
except:
    print("Attempting to refresh the Google Calendar API token...\n")
    
    os.system('python3 ' + PROJECT_LOCATION + 'gCalApiToken.py') # Refresh the token (uses the gCalApiToken script)

    gCalCredentials = pickle.load(open(PROJECT_LOCATION + 'token.pkl', 'rb'))
    service = build('calendar', 'v3', credentials=gCalCredentials)

    try:
        calendar = service.calendars().get(calendarId=DEFAULT_CALENDAR_ID).execute()
        print("Successfully refreshed the Google Calendar API token!\n")
    except:
        print("Could not refresh the Google Calendar API token!\n")
        exit()

# Set up the Notion API connection

os.environ['NOTION_TOKEN'] = NOTION_TOKEN
notion = Client(auth=os.environ['NOTION_TOKEN'])
