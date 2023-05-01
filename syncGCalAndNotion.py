from setup import *

# This script calls each individual section in sequence

print("\nStarting Google Calendar + Notion sync!\n")

print("----------------------------------------------------------------------\n")
import apiConnections

if SYNC_DELETED_EVENTS:
    print("----------------------------------------------------------------------\n")
    import syncDeletions

print("----------------------------------------------------------------------\n")
import importToGCal

print("----------------------------------------------------------------------\n")
import importToNotion

print("----------------------------------------------------------------------\n")
import updateGCal

print("----------------------------------------------------------------------\n")
import updateNotion

print("----------------------------------------------------------------------\n")
print("Finished Google Calendar + Notion sync!\n")
exit()
