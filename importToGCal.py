from setup import *
from helperFunctions import *


####################################################################
### PART 2: IMPORT NEW NOTION CALENDAR EVENTS TO GOOGLE CALENDAR ###
####################################################################


print("Adding new Notion Calendar events to Google Calendar...\n")

# Get all of your Notion Calendar events that have not been synced with Google Calendar

query = {
    'database_id': NOTION_DATABASE_ID, 
    'filter': {
        "and": [
            {
                'property': NOTION_DATE,
                'date': {
                    'is_not_empty': True
                }
            },
            {
                'property': NOTION_SYNCED,
                'checkbox': {
                    'equals': False
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

notionPagesResults = notionPages['results']

notionEventNames = []
notionStartDates = []
notionEndDates = []
notionDescriptions = []
notionLocations = []
notionCallLinks = []
notionAttendees = []
notionPageUrls = []
gCalEventIds = []
notionCalendars = []
notionCreateGoogleMeets = []

if len(notionPagesResults) > 0:
    for i, page in enumerate(notionPagesResults):
        try:
            notionEventNames.append(page['properties'][NOTION_EVENT_NAME]['title'][0]['plain_text'])
        except:
            notionEventNames.append('No Title')

        try:
            notionStartDates.append(parseDateTimeString(page['properties'][NOTION_DATE]['date']['start'][:-6], '%Y-%m-%dT%H:%M:%S.000'))
        except:
            notionStartDates.append(parseDateString(page['properties'][NOTION_DATE]['date']['start'], '%Y-%m-%d'))

        if page['properties'][NOTION_DATE]['date']['end'] != None:
            try:
                notionEndDates.append(parseDateTimeString(page['properties'][NOTION_DATE]['date']['end'][:-6], '%Y-%m-%dT%H:%M:%S.000'))
            except:
                notionEndDates.append(parseDateString(page['properties'][NOTION_DATE]['date']['end'], '%Y-%m-%d'))
        else:
            try:
                notionEndDates.append(parseDateTimeString(page['properties'][NOTION_DATE]['date']['start'][:-6], '%Y-%m-%dT%H:%M:%S.000'))
            except:
                notionEndDates.append(parseDateString(page['properties'][NOTION_DATE]['date']['start'], '%Y-%m-%d'))

        try: 
            notionDescriptions.append(makeDescription(page['properties'][NOTION_DESCRIPTION]['rich_text']))
        except:
            notionDescriptions.append('')
        
        notionPageUrls.append(makeNotionPageURL(page['id'], NOTION_PAGE_URL_ROOT))
        
        try:
            notionCalendarName = page['properties'][NOTION_CALENDAR_NAME]['select']['name']

            if notionCalendarName != UNKNOWN_CALENDAR_NAME:
                notionCalendars.append(CALENDAR_DICTIONARY[notionCalendarName])
            else: # The Notion event was created with the 'Calendar' field set to 'Unkown'. This will be switched to the default calendar.
                notionCalendars.append(DEFAULT_CALENDAR_ID)
        except:
            notionCalendars.append(DEFAULT_CALENDAR_ID)

        try:
            notionLocations.append(makeOneLinePlainText(page['properties'][NOTION_LOCATION]['rich_text']))
        except:
            notionLocations.append('')

        try:
            notionCallLinks.append(makeLink(page['properties'][NOTION_VIDEO_CALL_LINK]['rich_text']))
        except:
            notionCallLinks.append([])

        try:
            attendees = [x['name'] for x in page['properties'][NOTION_ATTENDEES]['multi_select']]
            notionAttendees.append(attendees)
        except:
            notionAttendees.append([])
        
        # Create the Google Calendar event
        newGCalEvent = makeGCalEvent(notionEventNames[i], notionDescriptions[i], notionStartDates[i], notionPageUrls[i], notionEndDates[i], notionCalendars[i], notionLocations[i], notionCallLinks[i], notionAttendees[i])

        # Save the new Google Calendar event ID
        gCalEventIds.append(newGCalEvent['id'])

        # Update the necessary fields in Notion Calendar with the new Google Calendar event info
        notionEventUpdate = notion.pages.update(
            **{
                'page_id': page['id'],
                'properties': {
                    NOTION_GCAL_EVENT_ID: {
                        'rich_text': [{
                            'text': {
                                'content': newGCalEvent['id']
                            }
                        }]
                    },
                    NOTION_GCAL_CALENDAR_ID: {
                        'rich_text': [{
                            'text': {
                                'content': notionCalendars[i]
                            }
                        }]
                    },
                    NOTION_SYNCED: {
                        'checkbox': True
                    },
                    NOTION_LAST_SYNCED: {
                        'date': {
                            'start': addTimeZoneForNotion(nowToDateTimeString()),
                            'end': None
                        }
                    },
                    NOTION_CREATOR: {
                        'type': 'select',
                        'select': {
                            'name': newGCalEvent['creator']['email'],
                            'color': 'default'
                        }
                    }
                }
            }
        )

        # Update the Notion 'Calendar' field with the default calendar if it was not assigned in Notion or was assigned to 'Unknown'
        if notionCalendars[i] == DEFAULT_CALENDAR_ID:
            notionEventUpdate = notion.pages.update(
                **{
                    'page_id': page['id'],
                    'properties': {
                        NOTION_CALENDAR_NAME: { 
                            'select': {
                                "name": DEFAULT_CALENDAR_NAME
                            }
                        }
                    }
                }
            )
        
    print("Finished adding new Notion Calendar events to Google Calendar!\n")
else:
    print("There are no new Notion Calendar events to add to Google Calendar\n")
