from setup import *
from helperFunctions import *


#########################################################################
### PART 4: UPDATE GOOGLE CALENDAR EVENTS THAT WERE CHANGED IN NOTION ###
#########################################################################


print("Updating Google Calendar events that were changed in Notion...\n")

# Get all of your Notion calendar events that need to be updated in Google Calendar

query = {
    'database_id': NOTION_DATABASE_ID, 
    'filter': {
        "and": [
            {
                'property': NOTION_NEEDS_GCAL_UPDATE,
                'checkbox': {
                    'equals': True
                }
            },
            {
                'property': NOTION_DATE,
                'date': {
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
                    'equals': False
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

notionPagesResults = notionPages['results']

notionEventNames = []
notionStartDates = []
notionEndDates = []
notionDescriptions = []
notionLocations = []
notionCallLinks = []
notionAttendees = []
gCalEventIds = []
notionCalendars = []
gCalCalendars = []
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
                
        try:
            gCalEventIds.append(makeOneLinePlainText(page['properties'][NOTION_GCAL_EVENT_ID]['rich_text']))
        except:
            print(f'The Google Calendar event ID is missing for event: {notionEventNames[i]}!')
            print("Exiting this part of the script!")
            exit()

        try:
            notionCalendars.append(CALENDAR_DICTIONARY[page['properties'][NOTION_CALENDAR_NAME]['select']['name']])
        except:
            notionCalendars.append(DEFAULT_CALENDAR_ID)

        try:
            gCalCalendars.append(makeOneLinePlainText(page['properties'][NOTION_GCAL_CALENDAR_ID]['rich_text']))
        except:
            gCalCalendars.append(DEFAULT_CALENDAR_ID)
        
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
        
        # Update the Google Calendar event
        updatedGCalEvent = updateGCalEvent(notionEventNames[i], notionDescriptions[i], notionStartDates[i], notionEndDates[i], gCalEventIds[i], gCalCalendars[i], notionCalendars[i], notionLocations[i], notionCallLinks[i], notionAttendees[i])

        # Update the necessary fields in Notion with the updated Google Calendar event info
        notionEventUpdate = notion.pages.update(
            **{
                'page_id': page['id'],
                'properties': {
                    NOTION_LAST_SYNCED: {
                        'date': {
                            'start': addTimeZoneForNotion(nowToDateTimeString()),
                            'end': None
                        }
                    },
                    NOTION_CREATOR: {
                        'select': {
                            'name': updatedGCalEvent['creator']['email'],
                            'color': 'default'
                        }
                    }
                }
            }
        )

        # Handle situation where the Notion 'Calendar' field was changed from a valid calendar to 'Unknown' or empty
        if (notionCalendars[i] == UNKNOWN_CALENDAR_ID and gCalCalendars[i] in CALENDAR_DICTIONARY.values()) or (notionCalendars[i] == DEFAULT_CALENDAR_ID and gCalCalendars[i] != DEFAULT_CALENDAR_ID and gCalCalendars[i] in CALENDAR_DICTIONARY.values()):
            notionEventUpdate = notion.pages.update(
                **{
                    'page_id': page['id'],
                    'properties': {
                        NOTION_CALENDAR_NAME: {
                            'select': {
                                'name': list(CALENDAR_DICTIONARY.keys())[list(CALENDAR_DICTIONARY.values()).index(gCalCalendars[i])]
                            }
                        },
                    }
                }
            )

        # Handle situation where the Notion 'Calendar' field was change from 'Unknown' to a different calendar
        # This is not permitted, since it would be attempting to move a shared calendar event from the sharer's calendar to your calendar
        elif notionCalendars[i] != UNKNOWN_CALENDAR_ID and gCalCalendars[i] not in CALENDAR_DICTIONARY.values():
            notionEventUpdate = notion.pages.update(
                **{
                    'page_id': page['id'],
                    'properties': {
                        NOTION_CALENDAR_NAME: {
                            'select': {
                                'name': UNKNOWN_CALENDAR_NAME
                            }
                        }
                    }
                }
            )

        # Update the 'GCal Calendar ID' field in Notion if the calendar was changed
        elif notionCalendars[i] != gCalCalendars[i]:
            notionEventUpdate = notion.pages.update(
                **{
                    'page_id': page['id'],
                    'properties': {
                        NOTION_GCAL_CALENDAR_ID: {
                            'rich_text': [{
                                'text': {
                                    'content': CALENDAR_DICTIONARY[notionEventUpdate['properties'][NOTION_CALENDAR_NAME]['select']['name']]
                                }
                            }]
                        }
                    }
                }
            )
        
    print("Finished updating Google Calendar events that were changed in Notion!\n")
else:
    print("No Google Calendar events to update\n")
