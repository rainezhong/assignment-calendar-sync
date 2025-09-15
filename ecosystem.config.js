module.exports = {
  apps: [
    {
      name: 'assignment-sync-scheduler',
      script: './scheduler.js',
      cwd: '/Users/raine/assignment-calendar-sync',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '100M',
      env: {
        NODE_ENV: 'production'
      },
      log_file: './logs/scheduler-combined.log',
      out_file: './logs/scheduler-out.log',
      error_file: './logs/scheduler-error.log',
      time: true,
      merge_logs: true,
      // Restart if it crashes
      min_uptime: '10s',
      max_restarts: 10,
      // Cron restart (daily at 7:55 AM to ensure fresh start)
      cron_restart: '55 7 * * *'
    }
  ]
};