# gcal-notion-integration

## Overview

Hey everyone! This is an integration between Notion and Google Calendar that I've been working on recently. It provides free, unlimited two-way synchronization between your Notion Calendar database and your Google Calendar.

I want to give some credit to [akarri2001](https://github.com/akarri2001). I've been looking for a Notion + Google Calendar integration for a while, but I haven't been satisfied with the free products. When I decided to create my own, I came across akarri2001's [Notion-and-Google-Calendar-2-Way-Sync](https://github.com/akarri2001/Notion-and-Google-Calendar-2-Way-Sync) project which helped a lot with setting up the API connections. Cheers akarri2001!

I have built a Google Tasks integration as well available [here](https://github.com/nathan-dykstra/gtasks-notion-integration).

## Features
- Sync Google Calendar events to Notion calendar database.
  - Synced events will be updated in Notion if you change them in Google Calendar.
  - No limit on what events will be synced - you can sync all your historical and future events if you want! (Up to 500 events per calendar).
- Sync Notion calendar events to Google Calendar.
  - Synced events will be updated in Google Calendar if you change them in Notion.
- Syncs the following properties: event name, description, location, creator, attendees, Google Meet link* (see limitations), and some other properties that make the integration work.
- Multiple calendar support:
  - Specify each Google Calendar you want to sync with Notion, and the program will only look in those calendars when adding/updating events.
  - If an event is shared with your Google Calendar, it will be added to the "Unknown" calendar in Notion since the event is not owned by your Google account.
  - Supports changing events from one calendar to another (in Notion and Google Calendar).
- Syncs cancelled/deleted events* (see limitations).
- Can create and sync events with a single date only, or a single date + time, or two dates, or two dates + times.
  - Events will be added as "All-Day" events in Google Calendar when appropriate.
- No date limits on what events will be synced - you can sync all your historical and future events if you want! (Up to 500 events per calendar for the Google to Notion sync).
- Ability to add date ranges so the program will only sync events that are a specified number of weeks into the past/future - makes the program run much quicker (and you will probably never update past events anyways).
- Ability to run individual sections of the code separately (the code is broken into five main steps). For example, you can just do a one-time import of your Google Calendar events to Notion. The commands are in Usage Notes.
- Run the program at scheduled intervals using tools like Windows Event Scheduler (instructions will be included in the setup documentation).

## Limitations
- NEW: Syncing events from Google's calendars (like Holidays, Birthdays, etc.) doesn't work right now (this did work when I first made the program but must've been broken by an API update...). Will attempt to fix when I have time.
- Events that are added in Notion without a date will not be synced. Notion supports calendar events without a date, but Google Calendar does not.
- Currently this program will sync video call links (i.e. Google Meets) from Google Calendar to Notion, but it doesn't work the other way.
- Recurring Google Calendar events are broken up into their individual occurrences when synced with Notion. Unfortunately Notion doesn't currently have a recurring event feature (so if you have a Google Calendar event that repeats 10 times, you'll end up with 10 separate events in Notion).
- You'll have to use [my Notion calendar database template](https://nathan-dykstra-personal.notion.site/3414bbbb4d6a4766b2691f6a5ba55263?v=b3228cb5c87f4f9ea88d027ee632f2a1&pvs=73).
  - You can change the property names if you'd like.
  - You can add extra properties to the Notion database, but they will not be synced with Google Calendar.
- The Notion API does not allow deleting pages. To sync deleted events, I added a "Cancelled" property in Notion.
  - If an event is deleted in Google Calendar, the "Cancelled" checkbox will be checked in Notion.
  - If the "Cancelled" checkbox is checked in Notion, the event will be deleted from Google Calendar.
  - The Notion calendar database views are configured to filter out "Cancelled" events, so you don't see them by default.

## Setup Instructions

Step-by-step setup instructions will be available shortly. The setup process will probably take around 30 minutes. It does involve editing a few lines of code, but the changes are very minor and will be well-documented in the instructions - so even if you are not tech savvy, you can probably still get it working!

## Usage Notes
To run: 
```sh
python syncGCalAndNotion.py
```
- To run each individual section separately: 
  - Sync deleted events only: `python syncDeletions.py`
  - Import events from Notion to Google Calendar: `python importToGCal.py`
  - Import events from Google Calendar to Notion: `python importToNotion.py`
  - Sync updates from Notion to Google Calendar: `python updateGCal.py`
  - Sync update from Google Calendar to Notion: `python updateNotion.py`
- If you choose not to add date range restrictions, the sync will take a lot longer depending on how many calendar events you have (I ran the program without any date range restrictions, which imported almost 500 Google Calendar events to Notion. It worked fine, but took 5-10 minutes to complete).
- If you add new attendees to an event in Notion, change the colour to "Light gray."
- You don't need to specify the event creator in Notion. This is filled out automatically with the creator of the Google Calendar event (so even if you specify your own creator in Notion, it will be overwritten).
- You'll have to re-authenticate your Google account every few weeks.
  - You can manually re-authenticate by running `python gCalApiToken.py`, just like you did when you set it up.
- You'll notice that several properties are hidden by default in the Notion calendar event pages. They help facilitate the sync and are updated automatically when running the program. Please do not edit the content of those properties, or the program might not function correctly!
