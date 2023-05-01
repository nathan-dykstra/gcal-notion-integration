from setup import *
from helperFunctions import *


#################################################
### PART 1: SYNC CANCELLED AND DELETED EVENTS ###
#################################################


print("Updating calendar events that were cancelled or deleted...\n")

# Delete Google Calendar events where the 'Cancelled' checkbox is checked in Notion

query = {
    'database_id': NOTION_DATABASE_ID,
    'filter': {
        'and':[
            {
                'property': NOTION_GCAL_EVENT_ID,
                'rich_text': {
                    'is_not_empty': True
                }
            },
            {
                'property': NOTION_SYNCED,
                'checkbox': {
                    'equals': True
                }
            },
            {
                'property': NOTION_CANCELLED,
                'checkbox': {
                    'equals': True
                }
            },
            {
                'property': NOTION_NEEDS_GCAL_UPDATE,
                'checkbox': {
                    'equals': True
                }
            }
        ]
    }
}

maxDate = addTimeZoneForNotion(dateTimeToString(datetime.now() + timedelta(weeks=FUTURE_WEEKS_TO_SYNC)))
minDate = addTimeZoneForNotion(dateTimeToString(datetime.now() - timedelta(weeks=PAST_WEEKS_TO_SYNC)))

if PAST_WEEKS_TO_SYNC >=0 and FUTURE_WEEKS_TO_SYNC >= 0:
    query['filter']['and'].append({'property': NOTION_DATE, 'date': {'on_or_after': minDate}})
    query['filter']['and'].append({'property': NOTION_DATE, 'date': {'on_or_before': maxDate}})
elif PAST_WEEKS_TO_SYNC >=0:
    query['filter']['and'].append({'property': NOTION_DATE, 'date': {'on_or_after': minDate}})
elif FUTURE_WEEKS_TO_SYNC >= 0:
    query['filter']['and'].append({'property': NOTION_DATE, 'date': {'on_or_before': maxDate}})

cancelledNotionPages = notion.databases.query(
    **query
)
nextCursor = cancelledNotionPages['next_cursor']

while cancelledNotionPages['has_more']:
    query['start_cursor'] = nextCursor
    moreCancelledNotionPages = notion.databases.query(
        **query
    )
    nextCursor = moreCancelledNotionPages['next_cursor']
    cancelledNotionPages['results'] += moreCancelledNotionPages['results']
    if nextCursor is None:
        break

for i, cancelledPage in enumerate(cancelledNotionPages['results']):
    gCalCalendarId = makeOneLinePlainText(cancelledPage['properties'][NOTION_GCAL_CALENDAR_ID]['rich_text'])
    gCalEventId = makeOneLinePlainText(cancelledPage['properties'][NOTION_GCAL_EVENT_ID]['rich_text'])
    cancelledPageName = cancelledPage['properties'][NOTION_EVENT_NAME]['title'][0]['plain_text']

    try:
        print(f'Deleting this event from Google Calendar: {cancelledPageName}\n')
        service.events().delete(calendarId=gCalCalendarId, eventId=gCalEventId).execute() 
    except:
        print(f'Could not delete this event from Google Calendar: {cancelledPageName}\n')

# Check off the 'Cancelled' checkbox for events that were deleted in Google Calendar

deletedGCalEvents = []

for calendar in CALENDAR_DICTIONARY.keys(): # Only get Google Calendar info for calendars of interest
    if calendar != UNKNOWN_CALENDAR_NAME:
        maxDate = addTimeZoneForNotion(dateTimeToString(datetime.now() + timedelta(weeks=FUTURE_WEEKS_TO_SYNC)))
        minDate = addTimeZoneForNotion(dateTimeToString(datetime.now() - timedelta(weeks=PAST_WEEKS_TO_SYNC)))

        if PAST_WEEKS_TO_SYNC >= 0 and FUTURE_WEEKS_TO_SYNC >= 0:
            gCalEventResults = service.events().list(calendarId=CALENDAR_DICTIONARY[calendar], singleEvents=True, orderBy='startTime', showDeleted=True, timeMax=maxDate, timeMin=minDate).execute()
        elif PAST_WEEKS_TO_SYNC >= 0:
            gCalEventResults = service.events().list(calendarId=CALENDAR_DICTIONARY[calendar], singleEvents=True, orderBy='startTime', showDeleted=True, timeMin=minDate).execute()
        elif FUTURE_WEEKS_TO_SYNC >= 0:
            gCalEventResults = service.events().list(calendarId=CALENDAR_DICTIONARY[calendar], singleEvents=True, orderBy='startTime', showDeleted=True, timeMax=maxDate).execute()
        else:
            gCalEventResults = service.events().list(calendarId=CALENDAR_DICTIONARY[calendar], singleEvents=True, showDeleted=True, orderBy='startTime').execute()

        for item in gCalEventResults['items']:
            if item['status'] == 'cancelled':
                deletedGCalEvents.append(item)

for deletedGCalEvent in deletedGCalEvents:
    deletedGCalEventId = deletedGCalEvent['id']
    
    notionPagesToDelete = notion.databases.query(
        **{
            'database_id': NOTION_DATABASE_ID,
            'filter': {
                'and': [
                    {
                        'property': NOTION_GCAL_EVENT_ID,
                        'rich_text': {
                            'equals': deletedGCalEventId
                        }
                    },
                    {
                        'property': NOTION_CANCELLED,
                        'checkbox': {
                            'equals': False
                        }
                    }
                ]
            }
        }
    )

    for notionPageToDelete in notionPagesToDelete['results']:
        print(f'Cancelling this event in Notion Calendar: {deletedGCalEventId}\n')

        notionPageUpdate = notion.pages.update(
            **{
                'page_id': notionPageToDelete['id'],
                'properties': {
                    NOTION_CANCELLED: {
                        'checkbox': True
                    },
                    NOTION_LAST_SYNCED: {
                        'date': {
                            'start': addTimeZoneForNotion(nowToDateTimeString()),
                            'end': None
                        }
                    }
                }
            }
        )

print("Finished updating calendar events that were cancelled or deleted!\n")
