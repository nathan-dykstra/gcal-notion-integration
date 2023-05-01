# gcal-notion-integration

## Overview

Hey everyone! This is an integration between Notion and Google Calendar that I've been working on recently. It provides two-way synchronization between your Notion Calendar database and your Google Calendar.

Right off the bat, I want to give credit to [akarri2001](https://github.com/akarri2001). I've been looking for a Notion + Google Calendar integration for a while, but I haven't been satisfied with the free tier of products like Zapier. When I decided to create my own, I came across [akarri2001's](https://github.com/akarri2001) [Notion-and-Google-Calendar-2-Way-Sync](https://github.com/akarri2001/Notion-and-Google-Calendar-2-Way-Sync) project. That helped me a lot with setting up the API connections and gave me tons of ideas for how to organize my code and implement some of the features. Cheers [akarri2001](https://github.com/akarri2001)!

## Features
- Sync your Google Calendar events to your Notion Calendar database (including importing your past calendar events).
  - Synced events will be updated in Notion if you change them in Google Calendar.
  - No limit on what events will be synced - you can sync all of your historical and future events if you want! (Up to 500 events per calendar).
- Sync your Notion Calendar events to your Google Calendar (including importing your past events).
  - Synced events will be updated in Google Calendar if you change them in Notion.
- No date limits on what events will be synced - you can sync all of your historical and future events if you want! (Up to 500 events per calendar for the Google to Notion sync).
- Ability to add date ranges, so after your initial sync, the program will only sync dates that are a specified number of weeks into the past/future - makes the program run much quicker (and you will probably never update past events anyways).
- Multiple calendar support:
  - Specify each Google Calendar you would like to sync with Notion.
  - The program will only look in these calendars when adding/updating events in Notion.
  - If an event is shared with your Google Calendar, it will be added to the "Unknown" calendar tag in Notion since the event is actually owned by the calendar that shared it with you, not your calendar.
  - Supports changing events from one calendar to another (in Notion and Google Calendar).
- Can create and sync events with a single date only, or a single date + time, or two dates, or two dates + times.
  - Events will be added as "All-Day" events in Google Calendar when appropriate.
- Set the program to run at scheduled intervals using tools like Windows Event Scheduler (instructions for how to do this will be included in the "Setup Instructions" section when I finish that documentation)

## Limitations
- Events that are added in Notion without a date will not be synced. While Notion supports calendar events without a date, Google Calendar does not.
- Currently this program will sync video call links (i.e. Google Meets) from your Google Calendar to Notion, however it does not work the other way (at least not yet)
- Recurring Google Calendar events are broken up into their individual occurrences when synced with Notion. Unfortunately Notion does not currently have a recurring event feature (so if you have a Google Calendar event that repeats 10 times, then you'll end up with 10 separate events in Notion)
  - The event info will all sync properly, you'll just end up with a bunch of identical events in Notion, except they're on different dates.
  - If Notion adds recurring events then I might update the program to add proper support.

## Setup Instructions

Step-by-step setup instructions will be available shortly. The setup process will probably take around 30 minutes. It does involve editing a few lines of code, but the changes are very minor and will be well-documented in the instructions - so even if you are not super tech savvy, you can probably still get it working!

## Usage Notes
- You'll have to use my Notion calendar database template that will be provided in the instructions, but you can change the field names if you'd like - instructions will be found in the setup documentation.
- If you choose not to add date range restrictions, the sync will take a lot longer depending on how many calendar events you have (I ran the program without any date range restrictions, which imported almost 500 Google Calendar events to Notion. It worked fine, but took 5-10 minutes to complete).
  - This is one of the reasons why I recommend only doing a full sync without date restrictions the first time you run the program.
- Just like your Google apps, you will have to re-authenticate your Google account every few weeks.
  - You can manually run the script to re-authenticate by running `python gCalApiToken.py`.
  - If you are running the program manually, then it should prompt you to follow a URL to re-authenticate your Google account which will give you a code to paste back into the command prompt or terminal (just like when you set it up)
  - If you have scheduled the program, then you will notice that the code is not running and your events are not syncing. You'll have to manually run the program once, and follow the steps in the bullet point above.
    - I'll try to figure out if it's possible to make it notify you somehow when this happens
- You'll notice that several fields are hidden in the Notion calendar event page. The fields help to facilitate the sync and are updated automatically when running the program. Please do not edit the content of these fields, or the program might not function correctly!

I hope you find this useful! Feel free to add suggestions for features you would like, and I will consider adding them. Or dig into the code and modify it however you want :)

FYI I will also be working on a Google Tasks + Notion feature to sync your tasks, reminders, and to-dos.
