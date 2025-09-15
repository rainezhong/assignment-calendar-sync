"""Generate ICS calendar files from assignments - no Google API needed!"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
import pytz
from pathlib import Path


class ICSGenerator:
    """Generate standard ICS calendar files that can be imported anywhere"""
    
    def __init__(self, timezone='America/New_York'):
        self.timezone = pytz.timezone(timezone)
        self.events = []
    
    def add_assignment(self, assignment: Dict):
        """Add an assignment as a calendar event"""
        if not assignment.get('due_date'):
            return
        
        # Generate unique ID for this event
        uid = self._generate_uid(assignment)
        
        # Format the event
        event = self._format_event(assignment, uid)
        self.events.append(event)
    
    def _generate_uid(self, assignment: Dict) -> str:
        """Generate a unique ID for the event"""
        # Create unique ID from assignment details
        text = f"{assignment['course']}_{assignment['name']}_{assignment.get('due_date', '')}"
        return hashlib.md5(text.encode()).hexdigest() + "@assignmentsync"
    
    def _format_event(self, assignment: Dict, uid: str) -> str:
        """Format assignment as ICS event"""
        due_date = assignment['due_date']
        
        # Ensure timezone awareness
        if due_date.tzinfo is None:
            due_date = self.timezone.localize(due_date)
        
        # Create event at due time (or 11:59 PM if no time specified)
        if due_date.hour == 0 and due_date.minute == 0:
            due_date = due_date.replace(hour=23, minute=59)
        
        # Event starts 30 minutes before due
        start_date = due_date - timedelta(minutes=30)
        
        # Format dates for ICS
        dtstart = start_date.strftime('%Y%m%dT%H%M%S')
        dtend = due_date.strftime('%Y%m%dT%H%M%S')
        dtstamp = datetime.now().strftime('%Y%m%dT%H%M%SZ')
        
        # Create description
        description = f"Course: {assignment['course']}\\n"
        description += f"Assignment: {assignment['name']}\\n"
        if assignment.get('url'):
            description += f"Link: {assignment['url']}\\n"
        if assignment.get('points'):
            description += f"Points: {assignment['points']}\\n"
        
        # Build event
        event = [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART;TZID={self.timezone.zone}:{dtstart}",
            f"DTEND;TZID={self.timezone.zone}:{dtend}",
            f"SUMMARY:📚 {assignment['name']} - {assignment['course']}",
            f"DESCRIPTION:{description}",
            "STATUS:CONFIRMED",
            "BEGIN:VALARM",
            "TRIGGER:-PT1H",  # 1 hour before
            "ACTION:DISPLAY",
            f"DESCRIPTION:Assignment due: {assignment['name']}",
            "END:VALARM",
            "END:VEVENT"
        ]
        
        return "\n".join(event)
    
    def generate_ics(self, filename: str = None) -> str:
        """Generate complete ICS file content"""
        
        # ICS header
        ics_content = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Assignment Calendar Sync//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            f"X-WR-CALNAME:School Assignments",
            f"X-WR-TIMEZONE:{self.timezone.zone}",
            "",
            # Timezone definition
            f"BEGIN:VTIMEZONE",
            f"TZID:{self.timezone.zone}",
            "BEGIN:STANDARD",
            "DTSTART:20231105T020000",
            "TZOFFSETFROM:-0400",
            "TZOFFSETTO:-0500",
            "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU",
            "END:STANDARD",
            "BEGIN:DAYLIGHT",
            "DTSTART:20240310T020000",
            "TZOFFSETFROM:-0500",
            "TZOFFSETTO:-0400",
            "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU",
            "END:DAYLIGHT",
            "END:VTIMEZONE",
            ""
        ]
        
        # Add all events
        for event in self.events:
            ics_content.append(event)
            ics_content.append("")
        
        # ICS footer
        ics_content.append("END:VCALENDAR")
        
        full_content = "\n".join(ics_content)
        
        # Save to file if filename provided
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(full_content)
            print(f"✅ Calendar file saved: {filename}")
        
        return full_content
    
    def save_and_open(self, assignments: List[Dict]):
        """Save ICS file and optionally open it"""
        if not assignments:
            print("No assignments to export")
            return
        
        # Add all assignments
        for assignment in assignments:
            self.add_assignment(assignment)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"assignments_{timestamp}.ics"
        
        # Save file
        self.generate_ics(filename)
        
        # Get absolute path
        abs_path = os.path.abspath(filename)
        
        print("\n" + "="*60)
        print("📅 CALENDAR FILE CREATED")
        print("="*60)
        print(f"File: {abs_path}")
        print("\nWhat to do next:")
        print("1. Double-click the file to open in your default calendar app")
        print("2. Or import it manually:")
        print("   - Google Calendar: Settings → Import & Export → Import")
        print("   - Apple Calendar: File → Import")
        print("   - Outlook: File → Open & Export → Import/Export")
        print("="*60)
        
        # Offer to open the file
        response = input("\nOpen the calendar file now? (y/n): ").lower()
        if response == 'y':
            import subprocess
            import platform
            
            try:
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', abs_path])
                elif platform.system() == 'Windows':
                    subprocess.run(['start', abs_path], shell=True)
                else:  # Linux
                    subprocess.run(['xdg-open', abs_path])
                print("✅ Opening calendar file...")
            except:
                print("Please open the file manually")
        
        return abs_path