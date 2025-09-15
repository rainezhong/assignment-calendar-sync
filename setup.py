#!/usr/bin/env python3
"""
Quick setup wizard for Assignment Calendar Sync
Run this first to configure the app!
"""

import os
import sys
from pathlib import Path


def setup_wizard():
    """Interactive setup wizard"""
    
    print("\n" + "="*60)
    print("🎓 ASSIGNMENT CALENDAR SYNC - SETUP")
    print("="*60)
    print("Let's get you set up! This will only take a minute.")
    print("="*60)
    
    # Check if .env exists
    env_path = Path('.env')
    if env_path.exists():
        response = input("\n⚠️  .env file already exists. Overwrite? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled")
            return
    
    config_lines = []
    
    # Step 1: Choose authentication method
    print("\n📚 STEP 1: How do you log into Gradescope?")
    print("1. Through my school's login page (SSO)")
    print("2. With email and password directly")
    
    choice = input("\nEnter 1 or 2: ").strip()
    
    if choice == '1':
        config_lines.append("# Gradescope - Using SSO")
        config_lines.append("GRADESCOPE_USE_SSO=true")
        config_lines.append("GRADESCOPE_EMAIL=")
        config_lines.append("GRADESCOPE_PASSWORD=")
        print("✅ SSO authentication selected")
    else:
        email = input("\nEnter your Gradescope email: ").strip()
        password = input("Enter your Gradescope password: ").strip()
        
        config_lines.append("# Gradescope - Direct login")
        config_lines.append("GRADESCOPE_USE_SSO=false")
        config_lines.append(f"GRADESCOPE_EMAIL={email}")
        config_lines.append(f"GRADESCOPE_PASSWORD={password}")
        print("✅ Direct login configured")
    
    # Step 2: Canvas (optional)
    print("\n📖 STEP 2: Do you use Canvas? (optional)")
    use_canvas = input("Setup Canvas? (y/n): ").lower()
    
    if use_canvas == 'y':
        print("\nTo get your Canvas token:")
        print("1. Log into Canvas")
        print("2. Go to Account → Settings")
        print("3. Click '+ New Access Token' under Approved Integrations")
        print("4. Create a token and copy it")
        
        token = input("\nPaste your Canvas token (or press Enter to skip): ").strip()
        
        if token:
            url = input("Enter your Canvas URL (e.g., https://canvas.school.edu): ").strip()
            config_lines.append("\n# Canvas API")
            config_lines.append(f"CANVAS_API_TOKEN={token}")
            config_lines.append(f"CANVAS_API_URL={url}")
            print("✅ Canvas configured")
    else:
        config_lines.append("\n# Canvas API (not configured)")
        config_lines.append("CANVAS_API_TOKEN=")
        config_lines.append("CANVAS_API_URL=")
    
    # Step 3: Basic settings
    print("\n⚙️  STEP 3: Basic Settings")
    
    print("\nHow many days ahead should we look for assignments?")
    days = input("Days ahead (default 30): ").strip() or "30"
    config_lines.append("\n# Settings")
    config_lines.append(f"SYNC_DAYS_AHEAD={days}")
    
    print("\nWhat timezone are you in?")
    print("1. Eastern (America/New_York)")
    print("2. Central (America/Chicago)")
    print("3. Mountain (America/Denver)")
    print("4. Pacific (America/Los_Angeles)")
    print("5. Other")
    
    tz_choice = input("Enter 1-5 (default 1): ").strip() or "1"
    timezones = {
        '1': 'America/New_York',
        '2': 'America/Chicago',
        '3': 'America/Denver',
        '4': 'America/Los_Angeles'
    }
    
    if tz_choice in timezones:
        timezone = timezones[tz_choice]
    else:
        timezone = input("Enter timezone (e.g., Europe/London): ").strip()
    
    config_lines.append(f"TIMEZONE={timezone}")
    config_lines.append("DEFAULT_REMINDER_MINUTES=60")
    config_lines.append("HEADLESS_BROWSER=false")  # Show browser for debugging
    config_lines.append("DEBUG_MODE=false")
    
    # Add Google Calendar placeholders (not required for simple mode)
    config_lines.append("\n# Google Calendar API (not required for simple mode)")
    config_lines.append("GOOGLE_CLIENT_ID=")
    config_lines.append("GOOGLE_CLIENT_SECRET=")
    config_lines.append("GOOGLE_CALENDAR_ID=primary")
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write('\n'.join(config_lines))
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\nYour app is configured and ready to use!")
    print("\nTo fetch your assignments and create a calendar file:")
    print("  python python/simple_sync.py")
    print("\nThe app will create a .ics file that you can import into:")
    print("  • Google Calendar")
    print("  • Apple Calendar")
    print("  • Outlook")
    print("  • Any calendar app!")
    print("="*60)
    
    # Offer to run now
    response = input("\nRun the sync now? (y/n): ").lower()
    if response == 'y':
        os.system('python python/simple_sync.py')


if __name__ == '__main__':
    try:
        setup_wizard()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)