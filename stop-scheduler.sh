#!/bin/bash

echo "🛑 Stopping Assignment Calendar Sync Scheduler..."

# Stop the scheduler
pm2 stop assignment-sync-scheduler

echo "✅ Scheduler stopped successfully!"
echo ""
echo "📊 Status:"
pm2 status

echo ""
echo "🚀 To restart: ./start-scheduler.sh or pm2 start assignment-sync-scheduler"
echo "🗑️  To delete permanently: pm2 delete assignment-sync-scheduler"