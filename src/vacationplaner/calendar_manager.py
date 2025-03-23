"""
Calendar manager for VacationPlaner.
Handles calendar data, date parsing, and date logic.
"""

import calendar
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Union, Optional, Set
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
    
    def _parse_vacation_blocks(self) -> List[Tuple[date, date, str, int]]:
        """
        Parse vacation blocks from configuration.
        
        Returns:
            List of (start_date, end_date, description, block_id) tuples.
        """
        blocks = []
        for i, block in enumerate(self.vacation_config['vacationBlocks']):
            try:
                start_date = self._parse_date(block['start'])
                end_date = self._parse_date(block['end'])
                description = block['description']
                blocks.append((start_date, end_date, description, i))
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
    
    def get_vacation_block_id(self, day: date) -> Optional[int]:
        """
        Get the vacation block ID for a given day.
        
        Args:
            day: Date to check.
            
        Returns:
            Vacation block ID or None if the day is not in a vacation block.
        """
        for start, end, _, block_id in self.vacation_blocks:
            if start <= day <= end:
                return block_id
        return None
    
    def is_vacation(self, day: date) -> bool:
        """
        Check if a given day is a vacation day.
        
        Args:
            day: Date to check.
            
        Returns:
            True if the day is a vacation day, False otherwise.
        """
        return self.get_vacation_block_id(day) is not None
    
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
        for start, end, description, _ in self.vacation_blocks:
            if start <= day <= end:
                return description
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
                'description': None,
                'vacation_block': None
            }
        
        current_date = date(year, month, day)
        vacation_block = self.get_vacation_block_id(current_date)
        
        # Determine the day type with weekend having priority over vacation for coloring
        if self.is_holiday(current_date):
            day_type = 'holiday'
        elif self.is_weekend(current_date):
            day_type = 'weekend'
        elif self.is_vacation(current_date):
            day_type = 'vacation'
        else:
            day_type = 'weekday'
        
        return {
            'type': day_type,
            'display': str(day),
            'description': self.get_holiday_description(current_date) if day_type == 'holiday' else self.get_vacation_description(current_date) if day_type == 'vacation' else None,
            'vacation_block': vacation_block
        }
    
    def calculate_statistics(self) -> Dict:
        """
        Calculate calendar statistics.
        
        Returns:
            Dictionary with calendar statistics.
        """
        # Initialize counters
        total_days = 0
        workdays = 0
        weekends = 0
        holidays = 0
        vacation_days = 0
        vacation_workdays = 0  # Vacation days that are also workdays
        
        # Start date of the year
        start_date = date(self.year, 1, 1)
        
        # End date of the year
        end_date = date(self.year, 12, 31)
        
        # Track days in vacation blocks
        vacation_block_days = set()
        for start, end, _, _ in self.vacation_blocks:
            current_date = start
            while current_date <= end:
                vacation_block_days.add(current_date)
                current_date += timedelta(days=1)
        
        # Calculate statistics
        current_date = start_date
        while current_date <= end_date:
            total_days += 1
            
            # Check if it's a holiday
            if current_date in self.holidays:
                holidays += 1
            
            # Check if it's a weekend
            if self.is_weekend(current_date):
                weekends += 1
            else:
                workdays += 1
                
                # Check if it's a vacation workday
                if current_date in vacation_block_days:
                    vacation_workdays += 1
            
            # Check if it's a vacation day (including weekends)
            if current_date in vacation_block_days:
                vacation_days += 1
            
            current_date += timedelta(days=1)
        
        # Calculate days off and days at work
        days_off = weekends + holidays + vacation_workdays
        days_at_work = workdays - vacation_workdays
        
        # Calculate individual vacation block statistics
        vacation_blocks_stats = []
        for i, (start, end, description, block_id) in enumerate(self.vacation_blocks):
            block_days = 0
            block_workdays = 0
            current_date = start
            
            while current_date <= end:
                block_days += 1
                if not self.is_weekend(current_date) and current_date not in self.holidays:
                    block_workdays += 1
                current_date += timedelta(days=1)
            
            vacation_blocks_stats.append({
                'id': block_id,
                'description': description,
                'start': start.strftime('%Y-%m-%d'),
                'end': end.strftime('%Y-%m-%d'),
                'total_days': block_days,
                'workdays': block_workdays
            })
        
        return {
            'total_days': total_days,
            'workdays': workdays,
            'weekends': weekends,
            'holidays': holidays,
            'vacation_days': vacation_days,
            'vacation_workdays': vacation_workdays,
            'days_off': days_off,
            'days_at_work': days_at_work,
            'vacation_blocks': vacation_blocks_stats
        }
