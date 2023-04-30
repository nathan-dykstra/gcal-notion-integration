from datetime import datetime
from setup import *
from helperFunctions import *


####################################################################
### PART 3: IMPORT NEW GOOGLE CALENDAR EVENTS TO NOTION CALENDAR ###
####################################################################


print("Adding new Google Calendar events to Notion Calendar...\n")

# Get all Notion Calendar events that aren't cancelled

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
            }
        ]
    }
}
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

gCalEventIdsInNotion = [makeOneLinePlainText(page['properties'][NOTION_GCAL_EVENT_ID]['rich_text']) for page in notionPages['results']]

# Get all event info from Google Calendar

gCalEvents = []

for calendar in CALENDAR_DICTIONARY.keys(): # Only get Google Calendar info for calendars of interest
    if calendar != UNKNOWN_CALENDAR_NAME:
        maxDate = addTimeZoneForNotion(dateTimeToString(datetime.now() + timedelta(weeks=FUTURE_WEEKS_TO_SYNC)))
        minDate = addTimeZoneForNotion(dateTimeToString(datetime.now() - timedelta(weeks=PAST_WEEKS_TO_SYNC)))

        if PAST_WEEKS_TO_SYNC >= 0 and FUTURE_WEEKS_TO_SYNC >= 0:
            gCalEventResults = service.events().list(calendarId=CALENDAR_DICTIONARY[calendar], singleEvents=True, orderBy='startTime', timeMax=maxDate, timeMin=minDate).execute()
        elif PAST_WEEKS_TO_SYNC >= 0:
            gCalEventResults = service.events().list(calendarId=CALENDAR_DICTIONARY[calendar], singleEvents=True, orderBy='startTime', timeMin=minDate).execute()
        elif FUTURE_WEEKS_TO_SYNC >= 0:
            gCalEventResults = service.events().list(calendarId=CALENDAR_DICTIONARY[calendar], singleEvents=True, orderBy='startTime', timeMax=maxDate).execute()
        else:
            gCalEventResults = service.events().list(calendarId=CALENDAR_DICTIONARY[calendar], singleEvents=True, orderBy='startTime').execute()
        
        gCalEvents.extend(gCalEventResults['items'])
    
# Get the keys and values from calendar dictionary
calDictionaryKeys = list(CALENDAR_DICTIONARY.keys())
calDictionaryValues = list(CALENDAR_DICTIONARY.values())

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

# Compare the event IDs from Google Calendar to the event IDs currently in Notion.
# If an event ID from Google Calendar does not exist in Notion, then that event should be added to the Notion Calendar

newGCalEventIndicies = []

for i in range(len(gCalEventIds)):
    if gCalEventIds[i] not in gCalEventIdsInNotion:
        newGCalEventIndicies.append(i)

if len(newGCalEventIndicies) > 0:
    for index in newGCalEventIndicies:
        # Create the Notion Calendar event
        newNotionCalEvent = makeNotionCalEvent(gCalEventNames[index], gCalStartDates[index], gCalEndDates[index], gCalDescriptions[index], gCalLocations[index], gCalCallLinks[index], gCalCreators[index], gCalAttendees[index], gCalEventIds[index], gCalCalendarIds[index], notionCalendarNames[index])
    
    print("Finished adding new Google Calendar events to Notion Calendar!\n")
else:
    print("There are no new Google Calendar events to add to Notion Calendar\n")
