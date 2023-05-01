from datetime import datetime, timedelta
from pytz import timezone, utc
from setup import *
from apiConnections import *


########################
### HELPER FUNCTIONS ###
########################


def nowToDateTimeString():
    """Returns the current date and time as a string"""

    # Note: Adding the timedelta of +1 minute prevents events in both Google Calendar and Notion Calendar from having 
    # last updated times that are greater than the last synced time.
    now = datetime.now() + timedelta(minutes=1)
    return now.strftime('%Y-%m-%dT%H:%M:%S')


def dateTimeToString(dateTime):
    """
    Returns dateTime as a string
    Required: dateTime is a datetime object
    """

    return dateTime.strftime('%Y-%m-%dT%H:%M:%S')


def dateToString(date):
    """
    Returns date as a string
    Required: date is a datetime object
    """

    return date.strftime('%Y-%m-%d')
    

def parseDateTimeString(dateTimeString, format):
    """
    Returns dateTimeString as a datetime object with date and time
    Required: dateTimeString follows the specified format
    """

    return datetime.strptime(dateTimeString, format)


def parseDateString(dateString, format):
    """
    Returns dateString as a datetime object with date only
    Required: dateString follows the specified format
    """

    return datetime.strptime(dateString, format)


def addTimeZoneForNotion(dateTimeString):
    """Adds timezone indicator to dateTimeString (for ET this will be -04:00 or -05:00)"""

    return dateTimeString + TIMEZONE_OFFSET_FROM_GMT


def convertTimeZone(dateTime, newTimeZone=TIMEZONE):
    """
    Convert dateTime from UTC to newTimeZone
    Requires: dateTime is a datetime object of the form '%Y-%m-%dT%H:%M:%S'
    """

    return utc.localize(dateTime).astimezone(timezone(newTimeZone)).replace(tzinfo=None)


def getGoogleMeetId(link):
    """Returns the Google Meet ID (everything after https://meet.google.com/)"""

    link.split('https://meet.google.com/', 1)[1]


def makeNotionPageURL(pageId, urlRoot):
    """Returns a URL to the Notion page"""

    urlId = pageId.replace('-', '')
    return urlRoot + urlId


def makeDescription(richText):
    """Returns a plain text description from Notion's rich text field"""

    description = ""
    for item in richText:
        description += item['text']['content']
    return description


def makeOneLinePlainText(richText):
    """Returns a single line of plain text from Notion's rich text field"""

    return richText[0]['plain_text']


def makeLink(richText):
    """Returns a Python List with the following format: [Display text, URL]"""

    return [richText[0]['text']['content'], richText[0]['text']['link']['url']]


def makeGCalEvent(eventName, eventDescription, eventStartTime, sourceUrl, eventEndTime, gCalId, eventLocation, eventCallLink, eventAttendees):
    """Creates a new Google Calendar event and returns the event"""

    event = {
        'summary': eventName,
        'description': eventDescription,
        'source': {
            'title': 'From Notion',
            'url': sourceUrl
        },
        'location': eventLocation,
        'attendees': [{'email': attendee} for attendee in eventAttendees]
    }
    
    # Three cases for the start/end dates:
    #   1. The Notion Calendar event has one date without time
    #   2. The Notion Calendar event has two dates without times (i.e. start date and end date are different)
    #   3. The Notion Calendar event has two dates with times, or a single date with time
    if eventStartTime.hour == 0 and eventStartTime.minute == 0 and eventEndTime == eventStartTime:
        eventStartTime = datetime.combine(eventStartTime, datetime.min.time())
        eventEndTime = eventEndTime + timedelta(days=1)

        event['start'] = {
            'date': eventStartTime.strftime('%Y-%m-%d'),
            'timeZone': TIMEZONE
        }
        event['end'] = {
            'date': eventEndTime.strftime('%Y-%m-%d'),
            'timeZone': TIMEZONE
        }
    elif eventStartTime.hour == 0 and eventStartTime.minute ==  0 and eventEndTime.hour == 0 and eventEndTime.minute == 0 and eventStartTime != eventEndTime:
        eventEndTime = eventEndTime + timedelta(days=1)

        event['start'] = {
            'date': eventStartTime.strftime('%Y-%m-%d'),
            'timeZone': TIMEZONE
        }
        event['end'] = {
            'date': eventEndTime.strftime('%Y-%m-%d'),
            'timeZone': TIMEZONE
        }
    else:
        event['start'] = {
            'date': eventStartTime.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': TIMEZONE
        }
        event['end'] = {
            'date': eventEndTime.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': TIMEZONE
        }

    # TODO: get Notion-to-Google conference link working
    #if len(eventCallLink) == 2:
    #    event['hangoutLink'] = eventCallLink[1]
    #    event['conferenceData'] = {
    #        'entryPoints': [
    #            {
    #                'entryPointType': 'video',
    #                'uri': eventCallLink[1],
    #                'label': eventCallLink[0]
    #            }
    #        ],
    #        'conferenceSolution': {
    #            'key': {
    #                'type': 'hangoutsMeet'
    #            },
    #            'name': 'Google Meet',
    #            'iconUri': 'https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png'
    #        },
    #        'conferenceId': getGoogleMeetId(eventCallLink[1])
    #    }
     
    print(f'Adding this event to Google Calendar: {eventName}\n')

    newEvent = service.events().insert(calendarId=gCalId, body=event).execute()
    return newEvent


def makeNotionCalEvent(eventName, eventStartTime, eventEndTime, eventDescription, eventLocation, eventCallLink, eventCreator, eventAttendees, gCalEventId, gCalCalendarId, notionCalendarName):
    """Creates a new Notion Calendar event and returns the event"""

    newNotionEvent = notion.pages.create(
        **{
            'parent': {
                'database_id': NOTION_DATABASE_ID
            },
            'properties': {
                NOTION_EVENT_NAME: {
                    'type': 'title',
                    'title': [
                        {
                            'type': 'text',
                            'text': {
                                'content': eventName
                            }
                        }
                    ]
                },
                NOTION_CALENDAR_NAME: {
                    'type': 'select',
                    'select': {
                        'name': notionCalendarName
                    }
                },
                NOTION_CREATOR: {
                    'type': 'select',
                    'select': {
                        'name': eventCreator,
                        'color': 'default'
                    }
                },
                NOTION_ATTENDEES: {
                    'type': 'multi_select',
                    'multi_select': [{'name': eventAttendees[i], 'color': 'default'} for i in range(len(eventAttendees))]
                },
                NOTION_LOCATION: {
                    'type': 'rich_text',
                    'rich_text': [{
                        'text': {
                            'content': eventLocation
                        }
                    }]
                },
                NOTION_DESCRIPTION: {
                    'type': 'rich_text',
                    'rich_text': [{
                        'text': {
                            'content': eventDescription
                        }
                    }]
                },
                NOTION_SYNCED: {
                    'type': 'checkbox',
                    'checkbox': True
                },
                NOTION_GCAL_EVENT_ID: {
                    'type': 'rich_text',
                    'rich_text': [{
                        'text': {
                            'content': gCalEventId
                        }
                    }]
                },
                NOTION_GCAL_CALENDAR_ID: {
                    'type': 'rich_text',
                    'rich_text': [{
                        'text': {
                            'content': gCalCalendarId
                        }
                    }]
                },
                NOTION_LAST_SYNCED: {
                    'type': 'date',
                    'date': {
                        'start': addTimeZoneForNotion(nowToDateTimeString()),
                        'end': None
                    }
                }   
            }
        }
    )

    if eventCallLink != '':
        notionEventUpdate = notion.pages.update(
            **{
                'page_id': newNotionEvent['id'],
                'properties': {
                    NOTION_VIDEO_CALL_LINK: {
                        'type': 'rich_text',
                        'rich_text': [{
                            'text': {
                                'content': eventCallLink,
                                'link': {
                                    'url': eventCallLink
                                }
                            }
                        }]
                    }
                }
            }
        )
    
    # Four cases for the start and end dates:
    #   1. The Google Calendar event is an all-day event, so Notion only needs start date
    #   2. The Google Calendar event is a multi-day event (with dates only, not times), so Notion needs start and end dates
    #   3. The Google Calendar event start date & time is the same as the end date & time, so Notion only needs start date & time
    #   4. The Google Calendar event has start date & time and end date & time, so Notion needs everything
    if eventStartTime.hour == 0 and eventStartTime.minute == 0 and eventEndTime.hour == 0 and eventEndTime.minute == 0 and (eventStartTime == eventEndTime or eventStartTime == eventEndTime - timedelta(days=1)):
        notionEventUpdate = notion.pages.update(
            **{
                'page_id': newNotionEvent['id'],
                'properties': {
                    NOTION_DATE: {
                        'type': 'date',
                        'date': {
                            'start': dateToString(eventStartTime),
                            'end': None
                        }
                    }
                }
            }
        )
    elif eventStartTime.hour == 0 and eventStartTime.minute == 0 and eventEndTime.hour == 0 and eventEndTime.minute == 0:
        eventEndTime = eventEndTime - timedelta(days=1) # The end date is 00:00 the next day so this must be adjusted

        notionEventUpdate = notion.pages.update(
            **{
                'page_id': newNotionEvent['id'],
                'properties': {
                    NOTION_DATE: {
                        'type': 'date',
                        'date': {
                            'start': dateToString(eventStartTime),
                            'end': dateToString(eventEndTime)
                        }
                    }
                }
            }
        )
    elif eventStartTime == eventEndTime:
        notionEventUpdate = notion.pages.update(
            **{
                'page_id': newNotionEvent['id'],
                'properties': {
                    NOTION_DATE: {
                        "type": 'date',
                        'date': {
                            'start': addTimeZoneForNotion(dateTimeToString(eventStartTime)),
                            'end': None
                        }
                    }
                }
            }
        )
    else:
        notionEventUpdate = notion.pages.update(
            **{
                'page_id': newNotionEvent['id'],
                'properties': {
                    NOTION_DATE: {
                        'type': 'date',
                        'date': {
                            'start': addTimeZoneForNotion(dateTimeToString(eventStartTime)),
                            'end': addTimeZoneForNotion(dateTimeToString(eventEndTime))
                        }
                    }
                }
            }
        )

    print(f'Adding this event to Notion Calendar: {eventName}\n')
    return newNotionEvent


def updateGCalEvent(eventName, eventDescription, eventStartTime, eventEndTime, gCalEventId, currentGCalId, newGCalId, eventLocation, eventCallLink, eventAttendees):
    """Updates the Google Calendar event and returns the event"""
    
    # Three cases for the start/end dates:
    #   1. The Notion Calendar event has one date without time
    #   2. The Notion Calendar event has two dates without times (i.e. start date and end date are different)
    #   3. The Notion Calendar event has two dates with times, or a single date with time
    if eventStartTime.hour == 0 and eventStartTime.minute == 0 and eventEndTime == eventStartTime:
        eventStartTime = datetime.combine(eventStartTime, datetime.min.time())
        eventEndTime = eventEndTime + timedelta(days=1)

        event = {
            'summary': eventName,
            'description': eventDescription,
            'start': {
                'date': eventStartTime.strftime("%Y-%m-%d"),
                'timeZone': TIMEZONE
            },
            'end': {
                'date': eventEndTime.strftime("%Y-%m-%d"),
                'timeZone': TIMEZONE
            }, 
            'location': eventLocation,
            'attendees': [{'email': attendee} for attendee in eventAttendees]
        }
    elif eventStartTime.hour == 0 and eventStartTime.minute ==  0 and eventEndTime.hour == 0 and eventEndTime.minute == 0 and eventStartTime != eventEndTime:
        eventEndTime = eventEndTime + timedelta(days=1)
        
        event = {
            'summary': eventName,
            'description': eventDescription,
            'start': {
                'date': eventStartTime.strftime("%Y-%m-%d"),
                'timeZone': TIMEZONE
            },
            'end': {
                'date': eventEndTime.strftime("%Y-%m-%d"),
                'timeZone': TIMEZONE
            }, 
            'location': eventLocation,
            'attendees': [{'email': attendee} for attendee in eventAttendees]
        }
    else:
        event = {
            'summary': eventName,
            'description': eventDescription,
            'start': {
                'dateTime': eventStartTime.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': TIMEZONE
            },
            'end': {
                'dateTime': eventEndTime.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': TIMEZONE
            }, 
            'location': eventLocation,
            'attendees': [{'email': attendee} for attendee in eventAttendees]
        }

    # TODO: get Notion-to-Google conference link working
    #if len(eventCallLink) == 2:
    #    event['hangoutLink'] = eventCallLink[1]
    #    event['conferenceData'] = {
    #        'entryPoints': [
    #            {
    #                'entryPointType': 'video',
    #                'uri': eventCallLink[1],
    #                'label': eventCallLink[0]
    #            }
    #        ],
    #        'conferenceSolution': {
    #            'key': {
    #                'type': 'hangoutsMeet'
    #            },
    #            'name': 'Google Meet',
    #            'iconUri': 'https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png'
    #        },
    #        'conferenceId': getGoogleMeetId(eventCallLink[1])
    #    }
    
    print(f'Updating this event in Google Calendar: {eventName}\n')

    # Notes:
    #   1. currentGCalId is the Google Calendar ID saved in the 'GCal Calendar ID' field in Notion
    #   2. newGCalId is the Google Calendar ID associated with the 'Calendar' field in Notion
    #   3. If the 'Calendar' field in Notion is changed, then its associated Google Calendar ID will not match the 'GCal Calendar ID' field
    if currentGCalId == newGCalId and currentGCalId != UNKNOWN_CALENDAR_ID:
        updatedEvent = service.events().update(calendarId=currentGCalId, eventId=gCalEventId, body=event).execute()
    else: # The 'Calendar' field has been changed in Notion
        
        # The 'Calendar' field was changed to or from 'Unknown', or was 'Unknown' in the first place. Do not change the calendar.
        if newGCalId == UNKNOWN_CALENDAR_ID or (newGCalId != UNKNOWN_CALENDAR_ID and currentGCalId not in CALENDAR_DICTIONARY.values()): 
            updatedEvent = service.events().update(calendarId=currentGCalId, eventId=gCalEventId, body=event).execute()
        
        # The 'Calendar' field was changed to a valid calendar. First move the Google Calendar event to the new calendar, then update the information.
        else: 
            updatedEvent = service.events().move(calendarId=currentGCalId , eventId=gCalEventId, destination=newGCalId).execute()
            updatedEvent = service.events().update(calendarId=newGCalId, eventId=gCalEventId, body=event).execute()

    return updatedEvent


def updateNotionCalEvent(eventName, eventStartTime, eventEndTime, eventDescription, eventLocation, eventCallLink, eventCreator, eventAttendees, gCalCalendarId, notionCalendarName, notionPageId):
    """Updates the Notion Calendar event and returns the event"""

    updatedNotionEvent = notion.pages.update(
        **{
            'page_id': notionPageId,
            'properties': {
                NOTION_EVENT_NAME: {
                    'type': 'title',
                    'title': [
                        {
                            'type': 'text',
                            'text': {
                                'content': eventName
                            }
                        }
                    ]
                },
                NOTION_CALENDAR_NAME: {
                    'type': 'select',
                    'select': {
                        'name': notionCalendarName
                    }
                },
                NOTION_CREATOR: {
                    'type': 'select',
                    'select': {
                        'name': eventCreator,
                        'color': 'default'
                    }
                },
                NOTION_ATTENDEES: {
                    'type': 'multi_select',
                    'multi_select': [{'name': eventAttendees[i], 'color': 'default'} for i in range(len(eventAttendees))]
                },
                NOTION_LOCATION: {
                    'type': 'rich_text',
                    'rich_text': [{
                        'text': {
                            'content': eventLocation
                        }
                    }]
                },
                NOTION_DESCRIPTION: {
                    'type': 'rich_text',
                    'rich_text': [{
                        'text': {
                            'content': eventDescription
                        }
                    }]
                },
                NOTION_SYNCED: {
                    'type': 'checkbox',
                    'checkbox': True
                },
                NOTION_GCAL_CALENDAR_ID: {
                    'type': 'rich_text',
                    'rich_text': [{
                        'text': {
                            'content': gCalCalendarId
                        }
                    }]
                },
                NOTION_LAST_SYNCED: {
                    'type': 'date',
                    'date': {
                        'start': addTimeZoneForNotion(nowToDateTimeString()),
                        'end': None
                    }
                }
            }
        }
    )

    if eventCallLink != '':
        notionEventUpdate = notion.pages.update(
            **{
                'page_id': notionPageId,
                'properties': {
                    NOTION_VIDEO_CALL_LINK: {
                        'type': 'rich_text',
                        'rich_text': [{
                            'text': {
                                'content': eventCallLink,
                                'link': {
                                    'url': eventCallLink
                                }
                            }
                        }]
                    }
                }
            }
        )
    
    # Four cases for the start and end dates:
    #   1. The Google Calendar event is an all-day event, so Notion only needs start date
    #   2. The Google Calendar event is a multi-day event (with dates only, not times), so Notion needs start and end dates
    #   3. The Google Calendar event start date & time is the same as the end date & time, so Notion only needs start date & time
    #   4. The Google Calendar event has start date & time and end date & time, so Notion needs everything
    if eventStartTime.hour == 0 and eventStartTime.minute == 0 and eventEndTime.hour == 0 and eventEndTime.minute == 0 and (eventStartTime == eventEndTime or eventStartTime == eventEndTime - timedelta(days=1)):
        updatedNotionEventUpdate = notion.pages.update(
            **{
                'page_id': notionPageId,
                'properties': {
                    NOTION_DATE: {
                        'type': 'date',
                        'date': {
                            'start': dateToString(eventStartTime),
                            'end': None
                        }
                    }
                }
            }
        )
    elif eventStartTime.hour == 0 and eventStartTime.minute == 0 and eventEndTime.hour == 0 and eventEndTime.minute == 0:
        eventEndTime = eventEndTime - timedelta(days=1) # The end date is 00:00 the next day so this must be adjusted

        updatedNotionEventUpdate = notion.pages.update(
            **{
                'page_id': notionPageId,
                'properties': {
                    NOTION_DATE: {
                        'type': 'date',
                        'date': {
                            'start': dateToString(eventStartTime),
                            'end': dateToString(eventEndTime)
                        }
                    }
                }
            }
        )
    elif eventStartTime == eventEndTime:
        updatedNotionEventUpdate = notion.pages.update(
            **{
                'page_id': notionPageId,
                'properties': {
                    NOTION_DATE: {
                        "type": 'date',
                        'date': {
                            'start': addTimeZoneForNotion(dateTimeToString(eventStartTime)),
                            'end': None
                        }
                    }
                }
            }
        )
    else:
        updatedNotionEventUpdate = notion.pages.update(
            **{
                'page_id': notionPageId,
                'properties': {
                    NOTION_DATE: {
                        'type': 'date',
                        'date': {
                            'start': addTimeZoneForNotion(dateTimeToString(eventStartTime)),
                            'end': addTimeZoneForNotion(dateTimeToString(eventEndTime))
                        }
                    }
                }
            }
        )

    print(f'Updating this event in Notion Calendar: {eventName}\n')
    return updatedNotionEvent
