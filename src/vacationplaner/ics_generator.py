"""
ICS generator module for VacationPlaner.
Creates ICS calendar files for import into calendar applications.
"""

import os
import calendar
from datetime import date, datetime, timedelta
from typing import Dict, Optional
import logging
from icalendar import Calendar, Event
from .calendar_manager import CalendarManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ICSGenerator:
    """Generates ICS calendar files."""
    
    def __init__(self, calendar_manager: CalendarManager, output_path: str):
        """
        Initialize the ICS generator.
        
        Args:
            calendar_manager: Calendar manager instance.
            output_path: Path to save output files.
        """
        self.calendar_manager = calendar_manager
        self.output_path = os.path.abspath(output_path)
        
        # Ensure output directory exists
        if not os.path.exists(self.output_path):
            logger.info(f"Creating output directory: {self.output_path}")
            os.makedirs(self.output_path)
        
        logger.info(f"ICS generator initialized with output path: {self.output_path}")
    
    def generate_ics(self, include_weekends: bool = True) -> str:
        """
        Generate ICS calendar file.
        
        Args:
            include_weekends: Whether to include weekend days in the ICS file.
            
        Returns:
            Path to generated ICS file.
        """
        year = self.calendar_manager.year
        vacation_config = self.calendar_manager.vacation_config
        
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//VacationPlaner//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        
        # Add events for each day
        for month in range(1, 13):
            month_cal = self.calendar_manager.get_monthly_calendar(month)
            for week in month_cal:
                for day in week:
                    if day != 0:  # Skip days outside the month
                        current_date = date(year, month, day)
                        day_info = self.calendar_manager.get_day_info(year, month, day)
                        
                        # Skip weekdays that are not holidays or vacation days
                        if day_info['type'] == 'weekday':
                            continue
                        
                        # Skip weekends if not included
                        if day_info['type'] == 'weekend' and not include_weekends:
                            continue
                        
                        # Create event for the day
                        event = self._create_event(current_date, day_info)
                        
                        # Add to calendar
                        cal.add_component(event)
        
        # Generate filename and save
        basename = f"vacation_{year}_{vacation_config['firstName']}_{vacation_config['lastName']}"
        ics_filename = os.path.join(self.output_path, f"{basename}.ics")
        
        logger.info(f"Saving ICS file to: {ics_filename}")
        with open(ics_filename, 'wb') as f:
            f.write(cal.to_ical())
        
        return ics_filename
    
    def _create_event(self, event_date: date, day_info: Dict) -> Event:
        """
        Create an event for a specific day.
        
        Args:
            event_date: Date of the event.
            day_info: Information about the day.
            
        Returns:
            Event object.
        """
        vacation_config = self.calendar_manager.vacation_config
        name = f"{vacation_config['firstName']} {vacation_config['lastName']}"
        
        event = Event()
        
        # Set as whole day event
        event.add('dtstart', event_date, parameters={'VALUE': 'DATE'})
        event.add('dtend', event_date + timedelta(days=1), parameters={'VALUE': 'DATE'})
        
        # Add common properties
        event.add('transp', 'TRANSPARENT')
        event.add('x-microsoft-cdo-busystatus', 'OOF')  # Out of office
        event.add('x-microsoft-cdo-alldayevent', 'TRUE')
        event.add('organizer', name)
        
        # Set event details based on day type
        if day_info['type'] == 'holiday':
            holiday_desc = day_info['description'] or "Holiday"
            event.add('summary', f"{holiday_desc} - {name}")
            event.add('description', f"{holiday_desc} - Out of Office - {name}")
            event.add('status', 'CONFIRMED')
            event.add('class', 'PUBLIC')
            event.add('categories', 'Holiday')
        
        elif day_info['type'] == 'vacation':
            vacation_desc = day_info['description'] or "Vacation"
            event.add('summary', f"{vacation_desc} - {name}")
            event.add('description', f"{vacation_desc} - Out of Office - {name}")
            event.add('status', 'CONFIRMED')
            event.add('class', 'PRIVATE')
            event.add('categories', 'Vacation')
        
        elif day_info['type'] == 'weekend':
            event.add('summary', f"Weekend - {name}")
            event.add('description', f"Weekend - Out of Office - {name}")
            event.add('status', 'CONFIRMED')
            event.add('class', 'PUBLIC')
            event.add('categories', 'Weekend')
        
        # Add unique identifier
        event.add('uid', f"{event_date.isoformat()}-{day_info['type']}-{name}")
        
        return event
