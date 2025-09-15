#!/bin/bash

# Add daily sync to crontab
# Runs every day at 8:00 AM

# Current crontab
crontab -l > /tmp/current_cron 2>/dev/null || touch /tmp/current_cron

# Add our job if it doesn't exist
if ! grep -q "assignment-calendar-sync" /tmp/current_cron; then
    echo "# Assignment Calendar Sync - Daily at 8 AM" >> /tmp/current_cron
    echo "0 8 * * * cd /Users/raine/assignment-calendar-sync/python && /usr/bin/python3 combined_sync.py >> /Users/raine/assignment-calendar-sync/logs/cron-sync.log 2>&1" >> /tmp/current_cron
    
    # Install new crontab
    crontab /tmp/current_cron
    echo "✅ Daily sync scheduled for 8:00 AM"
else
    echo "ℹ️  Daily sync already scheduled"
fi

# Cleanup
rm /tmp/current_cron