"""
Calendar manager for VacationPlaner.
Handles calendar data, date parsing, and date logic.
"""

import calendar
from datetime import date, datetime
from typing import Dict, List, Tuple, Union, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CalendarManager:
    """Manages calendar data and date operations."""
    
    def __init__(self, year: int, holiday_config: Dict, vacation_config: Dict):
        """
        Initialize the calendar manager.
        
        Args:
            year: The year for the calendar.
            holiday_config: Holiday configuration dictionary.
            vacation_config: Vacation configuration dictionary.
        """
        self.year = year
        self.holiday_config = holiday_config
        self.vacation_config = vacation_config
        
        # Parse dates from configurations
        self.holidays = self._parse_holidays()
        self.vacation_blocks = self._parse_vacation_blocks()
        
        logger.info(f"Calendar initialized for year {year} with {len(self.holidays)} holidays "
                   f"and {len(self.vacation_blocks)} vacation blocks")
    
    def _parse_date(self, date_str: str) -> date:
        """
        Parse date string to date object.
        
        Args:
            date_str: Date string in format YYYY-MM-DD.
            
        Returns:
            date: Parsed date object.
            
        Raises:
            ValueError: If date format is invalid.
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Invalid date format: {date_str}")
            raise ValueError(f"Invalid date format: {date_str}")
    
    def _parse_holidays(self) -> List[date]:
        """
        Parse holidays from configuration.
        
        Returns:
            List of holiday dates.
        """
        holidays = []
        for holiday in self.holiday_config['holidays']:
            try:
                holiday_date = self._parse_date(holiday['date'])
                holidays.append(holiday_date)
            except ValueError as e:
                logger.warning(f"Skipping holiday with invalid date: {e}")
        return holidays
    
    def _parse_vacation_blocks(self) -> List[Tuple[date, date]]:
        """
        Parse vacation blocks from configuration.
        
        Returns:
            List of (start_date, end_date) tuples.
        """
        blocks = []
        for block in self.vacation_config['vacationBlocks']:
            try:
                start_date = self._parse_date(block['start'])
                end_date = self._parse_date(block['end'])
                blocks.append((start_date, end_date))
            except ValueError as e:
                logger.warning(f"Skipping vacation block with invalid date: {e}")
        return blocks
    
    def is_holiday(self, day: date) -> bool:
        """
        Check if a given day is a holiday.
        
        Args:
            day: Date to check.
            
        Returns:
            True if the day is a holiday, False otherwise.
        """
        return day in self.holidays
    
    def is_vacation(self, day: date) -> bool:
        """
        Check if a given day is a vacation day.
        
        Args:
            day: Date to check.
            
        Returns:
            True if the day is a vacation day, False otherwise.
        """
        for start, end in self.vacation_blocks:
            if start <= day <= end:
                return True
        return False
    
    def is_weekend(self, day: date) -> bool:
        """
        Check if a given day is a weekend day.
        
        Args:
            day: Date to check.
            
        Returns:
            True if the day is a weekend day, False otherwise.
        """
        return day.weekday() >= 5  # 5 = Saturday, 6 = Sunday
    
    def get_holiday_description(self, day: date) -> Optional[str]:
        """
        Get the description of a holiday.
        
        Args:
            day: Date to check.
            
        Returns:
            Holiday description or None if the day is not a holiday.
        """
        for holiday in self.holiday_config['holidays']:
            try:
                holiday_date = self._parse_date(holiday['date'])
                if holiday_date == day:
                    return holiday['description']
            except ValueError:
                continue
        return None
    
    def get_vacation_description(self, day: date) -> Optional[str]:
        """
        Get the description of a vacation day.
        
        Args:
            day: Date to check.
            
        Returns:
            Vacation description or None if the day is not a vacation day.
        """
        for block in self.vacation_config['vacationBlocks']:
            try:
                start_date = self._parse_date(block['start'])
                end_date = self._parse_date(block['end'])
                if start_date <= day <= end_date:
                    return block['description']
            except ValueError:
                continue
        return None
    
    def get_monthly_calendar(self, month: int) -> List[List[int]]:
        """
        Get the calendar for a given month.
        
        Args:
            month: Month number (1-12).
            
        Returns:
            List of weeks, where each week is a list of days (0 for days outside the month).
        """
        if not 1 <= month <= 12:
            logger.error(f"Invalid month: {month}")
            raise ValueError(f"Invalid month: {month}")
        
        return calendar.Calendar().monthdayscalendar(self.year, month)
    
    def get_day_info(self, year: int, month: int, day: int) -> Dict:
        """
        Get information about a specific day.
        
        Args:
            year: Year.
            month: Month.
            day: Day.
            
        Returns:
            Dictionary with information about the day.
        """
        if day == 0:  # Day outside the month
            return {
                'type': 'outside',
                'display': '',
                'description': None
            }
        
        current_date = date(year, month, day)
        
        if self.is_holiday(current_date):
            return {
                'type': 'holiday',
                'display': str(day),
                'description': self.get_holiday_description(current_date)
            }
        elif self.is_vacation(current_date):
            return {
                'type': 'vacation',
                'display': str(day),
                'description': self.get_vacation_description(current_date)
            }
        elif self.is_weekend(current_date):
            return {
                'type': 'weekend',
                'display': str(day),
                'description': None
            }
        else:
            return {
                'type': 'weekday',
                'display': str(day),
                'description': None
            }
