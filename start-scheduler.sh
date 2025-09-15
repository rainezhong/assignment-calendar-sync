#!/bin/bash

echo "🚀 Starting Assignment Calendar Sync Scheduler..."

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 is not installed. Installing PM2..."
    npm install -g pm2
fi

# Start the scheduler
pm2 start ecosystem.config.js

echo "✅ Scheduler started successfully!"
echo ""
echo "📊 Status:"
pm2 status

echo ""
echo "📝 To view logs: pm2 logs assignment-sync-scheduler"
echo "🛑 To stop: ./stop-scheduler.sh or pm2 stop assignment-sync-scheduler"