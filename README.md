# gcal-notion-integration

## Overview

Hey everyone! This is an integration between Notion and Google Calendar that I've been working on recently. It provides free, unlimited two-way synchronization between your Notion Calendar database and your Google Calendar.

Right off the bat, I want to give some credit to [akarri2001](https://github.com/akarri2001). I've been looking for a Notion + Google Calendar integration for a while, but I haven't been satisfied with the free tier of products like Zapier. When I decided to create my own, I came across [akarri2001's](https://github.com/akarri2001) [Notion-and-Google-Calendar-2-Way-Sync](https://github.com/akarri2001/Notion-and-Google-Calendar-2-Way-Sync) project. That helped me a lot with setting up the API connections and gave me tons of inspiration for how to organize my code and implement some of the features. Cheers [akarri2001](https://github.com/akarri2001)!

## Features
- Sync your Google Calendar events to your Notion Calendar database (including importing your past calendar events).
  - Synced events will be updated in Notion if you change them in Google Calendar.
  - No limit on what events will be synced - you can sync all of your historical and future events if you want! (Up to 500 events per calendar).
- Sync your Notion Calendar events to your Google Calendar (including importing your past events).
  - Synced events will be updated in Google Calendar if you change them in Notion.
- Syncs the following properties: event name, description, location, creator, attendees, Google Meet link* (see limitations), and some other properties that make the integration work.
- Multiple calendar support:
  - Specify each Google Calendar you would like to sync with Notion.
  - The program will only look in these calendars when adding/updating events in Notion.
  - If an event is shared with your Google Calendar, it will be added to the "Unknown" calendar tag in Notion since the event is actually owned by the calendar that shared it with you, not your calendar.
  - Supports changing events from one calendar to another (in Notion and Google Calendar).
- Syncs cancelled/deleted events* (see limitations).
- Can create and sync events with a single date only, or a single date + time, or two dates, or two dates + times.
  - Events will be added as "All-Day" events in Google Calendar when appropriate.
- No date limits on what events will be synced - you can sync all of your historical and future events if you want! (Up to 500 events per calendar for the Google to Notion sync).
- Ability to add date ranges, so after your initial sync, the program will only sync dates that are a specified number of weeks into the past/future - makes the program run much quicker (and you will probably never update past events anyways).
- Ability to run individual sections of the code separately (the code is broken into five main steps). For example, it is possible to just do a one-time import of your Google Calendar events to Notion, without doing the rest of the sync. The commands are in Usage Notes.
- Set the program to run at scheduled intervals using tools like Windows Event Scheduler (instructions for how to do this will be included in the "Setup Instructions" section when I finish that documentation)

## Limitations
- Events that are added in Notion without a date will not be synced. While Notion supports calendar events without a date, Google Calendar does not.
- Currently this program will sync video call links (i.e. Google Meets) from your Google Calendar to Notion, however it does not work the other way (at least not yet)
- Recurring Google Calendar events are broken up into their individual occurrences when synced with Notion. Unfortunately Notion does not currently have a recurring event feature (so if you have a Google Calendar event that repeats 10 times, then you'll end up with 10 separate events in Notion)
  - The event info will all sync properly, you'll just end up with a bunch of identical events in Notion, except they're on different dates.
  - If Notion adds recurring events then I might update the program to add proper support.
- You'll have to use my Notion calendar database template (which will be provided in the instructions).
  - You can change the property names if you'd like (see setup instructions when they are released)
  - You can also add extra properties to the Notion database, but they will not be synced with Google Calendar.
  - If you have an existing Notion calendar database, you can modify the properties to make it work with this sync program (see setup instructions when they are released)
- The Notion API does not allow deleting pages. To sync deleted events, I added a "Cancelled" property in Notion.
  - When an event is deleted in Google Calendar, the "Cancelled" checkbox will be checked in Notion.
  - When the "Cancelled" checkbox is checked in Notion, the event will be deleted from Google Calendar.
  - The Notion calendar database views are set up to filter out "Cancelled" events, so you won't see them by default.

## Setup Instructions

Step-by-step setup instructions will be available shortly. The setup process will probably take around 30 minutes. It does involve editing a few lines of code, but the changes are very minor and will be well-documented in the instructions - so even if you are not tech savvy, you can probably still get it working!

## Usage Notes
- To run: `python syncGCalAndNotion.py`.
- To run each individual section separately: 
  - Sync deleted events only: `python syncDeletions.py`
  - Import events from Notion to Google Calendar: `python importToGCal.py`
  - Import events from Google Calendar to Notion: `python importToNotion.py`
  - Sync updates from Notion to Google Calendar: `python updateGCal.py`
  - Sync update from Google Calendar to Notion: `python updateNotion.py`
- If you choose not to add date range restrictions, the sync will take a lot longer depending on how many calendar events you have (I ran the program without any date range restrictions, which imported almost 500 Google Calendar events to Notion. It worked fine, but took 5-10 minutes to complete).
  - This is one of the reasons why I recommend only doing a full sync without date restrictions the first time you run the program.
- If you add new attendees to an event in Notion, just make sure to change the colour to "Light gray."
- You do not ever need to specify the event creator in Notion. This is filled out automatically with the creator of the Google Calendar event (so even if you specify your own creator, it will be overwritten with the actual Google Calendar event creator).
- Just like your Google apps, you will have to re-authenticate your Google account every few weeks.
  - You can manually run the script to re-authenticate by running `python gCalApiToken.py`.
  - If you are running the program manually, then it should prompt you to follow a URL to re-authenticate your Google account which will give you a code to paste back into the command prompt or terminal (just like when you set it up).
  - If you have scheduled the program, then you will notice that the code is not running and your events are not syncing. You'll have to manually run the program once, and follow the steps in the bullet point above.
    - I'll try to figure out if it's possible to make it notify you somehow when this happens.
- You'll notice that several properties are hidden by default in the Notion calendar event page. They help facilitate the sync and are updated automatically when running the program. Please do not edit the content of those properties, or the program might not function correctly!

I hope you find this useful! Feel free to add suggestions for features you would like, and I will consider adding them. Or dig into the code and modify it however you want on your own :)

FYI I will also be working on a Google Tasks + Notion feature to sync your tasks, reminders, and to-dos.
