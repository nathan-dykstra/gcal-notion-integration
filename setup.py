

#####################
### INITIAL SETUP ###
#####################


# Path to the folder you created for this project (include the trailing '/')
PROJECT_LOCATION = ''

# Whether or not to sync deleted calendar events
# If this is set to "False", then the program will not sync deleted events
# If this is set to "True", then the program will sync deleted events
SYNC_DELETED_EVENTS = True

# ----------------------------------------- NOTION SETUP ------------------------------------------

NOTION_TOKEN = ''

# Database ID of Notion Calendar database (everything between 'https://www.notion.so/my-notion-workspace/' and '?v=...', exclusive)
NOTION_DATABASE_ID = ''

# URL root of new page in Notion Calendar database (everything up to and including '&p=')
NOTION_PAGE_URL_ROOT = ''

# ------------------------------------- GOOGLE CALENDAR SETUP -------------------------------------

# Choose your timezone (use the link below to find your timezone)
# http://www.timezoneconverter.com/cgi-bin/zonehelp.tzc
TIMEZONE = 'America/Toronto'

# The timezone difference between GMT and your timezone.
# For example, the offset for EDT is '-04:00' and the offset for EST '-05:00'.
# If your timezone has time changes, then you will have to update this (for example Eastern Time changes from EST to EDT)
TIMEZONE_OFFSET_FROM_GMT = '-04:00'

# The number of weeks to go back in history to sync your calendar events
# If this is set to -1, then the program will attempt to sync ALL your historical calendar events
# If this is set to a non-negative integer, then the program will attempt to sync your calendar events since PAST_WEEKS_TO_SYNC weeks ago
# Recommendation: 
#   1. The recommended value is 52 when initially running the program, to sync all your data from the past year.
#   2. The recommended value is 1 after your initial sync is complete, since you will likely only update current events.
PAST_WEEKS_TO_SYNC = 1

# The number of weeks to go into the future to sync your calendar events
# If this is set to -1, then the program will attempt to sync ALL your future calendar events
# If this is set to a non-negative integer, then the program will attempt to sync your calendar events up to PAST_WEEKS_TO_SYNC weeks in the future
# Recommendation: 
#   1. The recommended value is 52 when initially running the program, to sync all your data for the upcoming year
#   2. The recommended value is 10 after your initial sync is complete
FUTURE_WEEKS_TO_SYNC = 10

# ------------------------------------ MULTIPLE CALENDAR SETUP ------------------------------------

# Default Notion calendar name and Google Calendar ID
DEFAULT_CALENDAR_NAME = ''
DEFAULT_CALENDAR_ID = ''

# Notion Calendar name and ID used for events that are shared from a Google Calendar that you don't own
UNKNOWN_CALENDAR_NAME = ''
UNKNOWN_CALENDAR_ID = ''

# These are all of the Google Calendars you want to sync with your Notion Calendar database
# Format: 'Notion Calendar Name' : 'Google Calendar ID'
CALENDAR_DICTIONARY = {
    DEFAULT_CALENDAR_NAME : DEFAULT_CALENDAR_ID,
    UNKNOWN_CALENDAR_NAME : UNKNOWN_CALENDAR_ID,
    'My Notion Calendar' : 'google-calendar-id@group.calendar.google.com'
}

# ------------------------------------- NOTION DATABASE SETUP -------------------------------------

# Basic calendar event fields
NOTION_EVENT_NAME = 'Summary'
NOTION_CALENDAR_NAME = 'Calendar'
NOTION_DATE = 'Date'
NOTION_CREATOR = 'Creator'
NOTION_ATTENDEES = 'Attendees'
NOTION_VIDEO_CALL_LINK = 'Video Call Link'
NOTION_LOCATION = 'Location'
NOTION_DESCRIPTION = 'Description'
NOTION_CANCELLED = 'Cancelled'

# Additional fields to facilitate the integration
NOTION_SYNCED = 'Synced'
NOTION_NEEDS_GCAL_UPDATE = 'Needs GCal Update'
NOTION_GCAL_EVENT_ID = 'GCal Event ID'
NOTION_GCAL_CALENDAR_ID = 'GCal Calendar ID'
NOTION_LAST_SYNCED = 'Last Synced'
