"""Simple date parser utility for Gradescope date formats"""

from datetime import datetime
import re


def parse_gradescope_date(date_text):
    """
    Parse common Gradescope date formats into datetime objects
    
    Handles formats like:
    - "Due: Jan 15, 2024 at 11:59 PM"
    - "January 15, 2024"
    - "Jan 15, 2024"
    - "01/15/2024"
    - "2024-01-15"
    - "15 Jan 2024"
    
    Args:
        date_text (str): Raw date text from Gradescope
        
    Returns:
        datetime: Parsed datetime object, or None if unparseable
    """
    if not date_text or not isinstance(date_text, str):
        return None
    
    # Clean up the text
    text = date_text.strip()
    
    # Remove common prefixes
    text = re.sub(r'^(Due:\s*|Due\s*)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
    # Try different parsing strategies
    parsers = [
        _parse_full_format,      # "Jan 15, 2024 at 11:59 PM"
        _parse_month_day_year,   # "January 15, 2024"
        _parse_short_format,     # "Jan 15, 2024" 
        _parse_numeric_formats,  # "01/15/2024", "2024-01-15"
        _parse_day_month_year,   # "15 Jan 2024"
        _parse_with_dateutil     # Fallback to dateutil
    ]
    
    for parser in parsers:
        try:
            result = parser(text)
            if result:
                return result
        except:
            continue
    
    return None


def _parse_full_format(text):
    """Parse 'Jan 15, 2024 at 11:59 PM' format"""
    # Pattern: Month Day, Year at Time AM/PM
    pattern = r'([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})\s+at\s+(\d{1,2}):(\d{2})\s+(AM|PM)'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        month_str, day, year, hour, minute, ampm = match.groups()
        
        # Convert month name to number
        month_num = _month_name_to_number(month_str)
        if not month_num:
            return None
        
        # Handle 12-hour format
        hour = int(hour)
        if ampm.upper() == 'PM' and hour != 12:
            hour += 12
        elif ampm.upper() == 'AM' and hour == 12:
            hour = 0
        
        return datetime(
            year=int(year),
            month=month_num,
            day=int(day),
            hour=hour,
            minute=int(minute)
        )
    
    return None


def _parse_month_day_year(text):
    """Parse 'January 15, 2024' format"""
    # Pattern: Full month name Day, Year
    pattern = r'([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})'
    match = re.search(pattern, text)
    
    if match:
        month_str, day, year = match.groups()
        
        month_num = _month_name_to_number(month_str)
        if not month_num:
            return None
        
        return datetime(
            year=int(year),
            month=month_num,
            day=int(day)
        )
    
    return None


def _parse_short_format(text):
    """Parse 'Jan 15, 2024' format (3-letter month)"""
    # Pattern: 3-letter month Day, Year
    pattern = r'([A-Za-z]{3})\s+(\d{1,2}),?\s+(\d{4})'
    match = re.search(pattern, text)
    
    if match:
        month_str, day, year = match.groups()
        
        month_num = _month_name_to_number(month_str)
        if not month_num:
            return None
        
        return datetime(
            year=int(year),
            month=month_num,
            day=int(day)
        )
    
    return None


def _parse_numeric_formats(text):
    """Parse numeric formats like '01/15/2024' or '2024-01-15'"""
    formats = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD or YYYY/MM/DD
    ]
    
    for i, pattern in enumerate(formats):
        match = re.search(pattern, text)
        if match:
            if i == 0:  # MM/DD/YYYY format
                month, day, year = match.groups()
            else:  # YYYY-MM-DD format
                year, month, day = match.groups()
            
            try:
                return datetime(
                    year=int(year),
                    month=int(month),
                    day=int(day)
                )
            except ValueError:
                continue
    
    return None


def _parse_day_month_year(text):
    """Parse '15 Jan 2024' format"""
    # Pattern: Day Month Year
    pattern = r'(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})'
    match = re.search(pattern, text)
    
    if match:
        day, month_str, year = match.groups()
        
        month_num = _month_name_to_number(month_str)
        if not month_num:
            return None
        
        return datetime(
            year=int(year),
            month=month_num,
            day=int(day)
        )
    
    return None


def _parse_with_dateutil(text):
    """Fallback parser using dateutil if available"""
    try:
        from dateutil import parser
        return parser.parse(text)
    except:
        return None


def _month_name_to_number(month_str):
    """Convert month name/abbreviation to number"""
    month_map = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'sept': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    return month_map.get(month_str.lower())


def test_date_parser():
    """Test function for the date parser"""
    test_cases = [
        # Common Gradescope formats
        "Due: Jan 15, 2024 at 11:59 PM",
        "Due: January 15, 2024 at 11:59 PM", 
        "January 15, 2024",
        "Jan 15, 2024",
        "15 Jan 2024",
        "01/15/2024",
        "2024-01-15",
        "March 1, 2024 at 12:00 AM",
        "Dec 31, 2023 at 11:59 PM",
        
        # Edge cases
        "Due: Feb 29, 2024",  # Leap year
        "May 1, 2024",
        "1 May 2024",
        
        # Invalid cases
        "Not a date",
        "",
        None,
        "Invalid date format"
    ]
    
    print("=" * 60)
    print("Testing Gradescope Date Parser")
    print("=" * 60)
    
    success_count = 0
    total_valid = 0
    
    for test_case in test_cases:
        print(f"\nInput: {repr(test_case)}")
        
        result = parse_gradescope_date(test_case)
        
        if result:
            print(f"✓ Parsed: {result}")
            print(f"  Formatted: {result.strftime('%Y-%m-%d %H:%M:%S')}")
            success_count += 1
        else:
            print("✗ Could not parse")
        
        # Count cases we expect to parse successfully
        if test_case and isinstance(test_case, str) and any(c.isdigit() for c in test_case):
            total_valid += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {success_count} successful parses out of {len(test_cases)} test cases")
    
    # Test some specific edge cases
    print("\n" + "-" * 40)
    print("Testing specific edge cases:")
    
    edge_cases = [
        ("Due: Jan 1, 2024 at 12:00 AM", datetime(2024, 1, 1, 0, 0)),
        ("Due: Dec 31, 2024 at 11:59 PM", datetime(2024, 12, 31, 23, 59)),
        ("January 15, 2024", datetime(2024, 1, 15, 0, 0))
    ]
    
    for test_input, expected in edge_cases:
        result = parse_gradescope_date(test_input)
        if result == expected:
            print(f"✓ {test_input} -> {result}")
        else:
            print(f"✗ {test_input} -> {result} (expected {expected})")
    
    print("=" * 60)
    return success_count


if __name__ == '__main__':
    test_date_parser()