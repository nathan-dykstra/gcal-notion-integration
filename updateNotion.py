from datetime import datetime
from setup import *
from helperFunctions import *


##################################################################################
### PART 5: UPDATE NOTION CALENDAR EVENTS THAT WERE CHANGED IN GOOGLE CALENDAR ###
##################################################################################


print("Updating Notion events that were changed in Google Calendar...\n")

# Get all Notion calendar events that aren't cancelled

query = {
    'database_id': NOTION_DATABASE_ID,
    'filter': {
        "and": [
            {
                'property': NOTION_CANCELLED, 
                'checkbox':  {
                    'equals': False
                }
            },
            {
                'property': NOTION_SYNCED, 
                'checkbox':  {
                    'equals': True
                }
            },
            {
                'property': NOTION_NEEDS_GCAL_UPDATE, 
                'checkbox':  {
                    'equals': False
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

notionPages = notion.databases.query(
    **query
)
nextCursor = notionPages['next_cursor']

while notionPages['has_more']:
    query['start_cursor'] = nextCursor
    moreNotionPages = notion.databases.query(
        **query
    )
    nextCursor = moreNotionPages['next_cursor']
    notionPages['results'] += moreNotionPages['results']
    if nextCursor is None:
        break

notionPageLastSyncedDates = [parseDateTimeString(page['properties'][NOTION_LAST_SYNCED]['date']['start'][:-6], '%Y-%m-%dT%H:%M:%S.000') for page in notionPages['results']]
notionPageIds = [page['id'] for page in notionPages['results']]
gCalEventIds = [makeOneLinePlainText(page['properties'][NOTION_GCAL_EVENT_ID]['rich_text']) for page in notionPages['results']]
gCalCalendarIds = [makeOneLinePlainText(page['properties'][NOTION_GCAL_CALENDAR_ID]['rich_text']) for page in notionPages['results']]

# Get all event info from Google Calendar

gCalEvents = []

calDictionaryKeys = list(CALENDAR_DICTIONARY.keys())
calDictionaryValues = list(CALENDAR_DICTIONARY.values())

for i, gCalEventId in enumerate(gCalEventIds):
    gCalEvent = None

    for gCalCalendarId in CALENDAR_DICTIONARY.values():
        if gCalCalendarId != UNKNOWN_CALENDAR_ID:
            try:
                gCalEvent = service.events().get(calendarId=gCalCalendarId, eventId=gCalEventId).execute()
            except:
                gCalEvent = {'status': 'cancelled'}

            if gCalEvent['status'] == 'confirmed' or gCalEvent['status'] == 'tentative':
                gCalEvents.append(gCalEvent)
            else:
                continue
    
    if len(gCalEvents) < i + 1:
        print(f'\nCould not find the Google Calendar event with ID: {gCalEventId}\nThis event is from an unknown Google Calendar (likely shared with you by someone else)\n')
        gCalEvents.append('')

gCalEventNames = []
gCalStartDates = []
gCalEndDates = []
gCalDescriptions = []
gCalLocations = []
gCalCallLinks = []
gCalCreators = [gCalEvent['creator']['email'] for gCalEvent in gCalEvents]
gCalAttendees = []
gCalEventIds = [gCalEvent['id'] for gCalEvent in gCalEvents]
gCalCalendarIds = [gCalEvent['organizer']['email'] for gCalEvent in gCalEvents]
gCalLastUpdatedDates = [convertTimeZone(parseDateTimeString(gCalEvent['updated'][:-5], '%Y-%m-%dT%H:%M:%S')) for gCalEvent in gCalEvents]

# Note: If the event is from a shared/unknown calendar, then the calendar ID won't be in gCalIDs. Change the Notion calendar name to 'Unknown'
notionCalendarNames = [calDictionaryKeys[calDictionaryValues.index(gCalCalendarId)] if gCalCalendarId in calDictionaryValues else UNKNOWN_CALENDAR_NAME for gCalCalendarId in gCalCalendarIds]

for gCalEvent in gCalEvents:
    try:
        gCalEventNames.append(gCalEvent['summary'])
    except:
        gCalEventNames.append('No Title')

    try:
        gCalStartDates.append(parseDateTimeString(gCalEvent['start']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S'))
    except:
        start = parseDateString(gCalEvent['start']['date'], '%Y-%m-%d')
        startWithTime = datetime(start.year, start.month, start.day, 0, 0, 0)
        gCalStartDates.append(startWithTime)

    try:
        gCalEndDates.append(parseDateTimeString(gCalEvent['end']['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S'))
    except:
        end = parseDateString(gCalEvent['end']['date'], '%Y-%m-%d')
        endWithTime = datetime(end.year, end.month, end.day, 0, 0, 0)
        gCalEndDates.append(endWithTime)

    try:
        gCalDescriptions.append(gCalEvent['description'])
    except:
        gCalDescriptions.append('')

    try:
        gCalLocations.append(gCalEvent['location'])
    except:
        gCalLocations.append('')

    try:
        gCalCallLinks.append(gCalEvent['hangoutLink'])
    except:
        gCalCallLinks.append('')

    try:
        participants = [participant['email'] for participant in gCalEvent['attendees']]
        gCalAttendees.append(participants)
    except:
        gCalAttendees.append([])

# Compare the Google Calendar event last updated time to the 'Last Synced' time in Notion
# If the Google Calendar last updated time is greater than the 'Last Synced' time, then the event needs to be updated in Notion

updatedGCalEventIndicies = []

for i in range(len(gCalEvents)):
    if gCalLastUpdatedDates[i] > notionPageLastSyncedDates[i]:
        updatedGCalEventIndicies.append(i)

if len(updatedGCalEventIndicies) > 0:
    for index in updatedGCalEventIndicies:
        # Update the Notion calendar event
        updatedNotionCalEvent = updateNotionCalEvent(gCalEventNames[index], gCalStartDates[index], gCalEndDates[index], gCalDescriptions[index], gCalLocations[index], gCalCallLinks[index], gCalCreators[index], gCalAttendees[index], gCalCalendarIds[index], notionCalendarNames[index], notionPageIds[index])
    
    print("Finished updating Notion events that were changed in Google Calendar!\n")
else:
    print("No Notion events to update\n")
