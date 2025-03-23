"""
Configuration manager for VacationPlaner.
Handles loading, parsing, and validating configuration files.
"""

import os
import json
import glob
from datetime import date, datetime
from typing import Dict, List, Optional, Union, Any
import logging
from icalendar import Calendar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConfigManager:
    """Handles loading and managing configuration files for vacation planner."""
    
    def __init__(self, conf_path: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            conf_path: Path to the configuration directory. If None, will use default path.
        """
        if conf_path is None:
            # Get default path relative to this file
            self.conf_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "conf")
            )
        else:
            self.conf_path = os.path.abspath(conf_path)
        
        logger.info(f"Configuration path: {self.conf_path}")
        
        if not os.path.exists(self.conf_path):
            logger.error(f"Configuration path does not exist: {self.conf_path}")
            raise FileNotFoundError(f"Configuration path does not exist: {self.conf_path}")
    
    def load_vacation_config(self, filepath: str = None) -> Dict:
        """
        Load vacation configuration file.
        
        Args:
            filepath: Path to the vacation configuration file. If None, will prompt user.
            
        Returns:
            Dict containing vacation configuration.
            
        Raises:
            FileNotFoundError: If no configuration files are found.
            ValueError: If the selected configuration is invalid.
        """
        if filepath and os.path.exists(filepath):
            logger.info(f"Loading vacation config from specified file: {filepath}")
            with open(filepath, 'r') as f:
                config = json.load(f)
                self._validate_vacation_config(config)
                return config
        
        # Find all vacation config files
        config_files = glob.glob(os.path.join(self.conf_path, "vacation-planer*.json"))
        
        if not config_files:
            logger.error("No vacation configuration files found!")
            raise FileNotFoundError("No vacation configuration files found in the configuration directory.")
        
        logger.info(f"Found {len(config_files)} vacation configuration files")
        
        # If only one file found, use it automatically
        if len(config_files) == 1:
            logger.info(f"Using the only available config file: {config_files[0]}")
            with open(config_files[0], 'r') as f:
                config = json.load(f)
                self._validate_vacation_config(config)
                return config
                
        # Otherwise prompt user for selection
        print("\nAvailable configuration files:")
        for i, file in enumerate(config_files, 1):
            print(f"{i}. {os.path.basename(file)}")
        
        while True:
            try:
                choice = int(input("\nSelect a configuration file (enter number): ")) - 1
                if 0 <= choice < len(config_files):
                    with open(config_files[choice], 'r') as f:
                        config = json.load(f)
                        self._validate_vacation_config(config)
                        return config
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
            except json.JSONDecodeError:
                print("Error parsing the selected file. It may be corrupted.")
    
    def load_holiday_config(self, region: str = None, year: Union[int, str] = None) -> Dict:
        """
        Load holiday configuration file.
        
        Args:
            region: Optional region to filter by.
            year: Optional year to filter by.
            
        Returns:
            Dict containing holiday configuration.
            
        Raises:
            FileNotFoundError: If no configuration files are found.
            ValueError: If the selected configuration is invalid.
        """
        # Find both JSON and iCal files
        holiday_files = glob.glob(os.path.join(self.conf_path, "holidays-*.json"))
        holiday_files.extend(glob.glob(os.path.join(self.conf_path, "*.ics")))
        
        if not holiday_files:
            logger.error("No holiday configuration files found!")
            raise FileNotFoundError("No holiday configuration files found in the configuration directory.")
            
        logger.info(f"Found {len(holiday_files)} holiday configuration files")
        
        # If region and year are provided, try to find exact match
        if region and year:
            year_str = str(year)
            json_match = os.path.join(self.conf_path, f"holidays-{region.lower()}-{year_str}.json")
            ical_match = os.path.join(self.conf_path, f"holidays-{region.lower()}-{year_str}.ics")
            
            # Also look for partial matches in filenames
            potential_matches = []
            region_lower = region.lower()
            
            for file in holiday_files:
                filename = os.path.basename(file).lower()
                if region_lower in filename and year_str in filename:
                    potential_matches.append(file)
            
            if os.path.exists(json_match):
                logger.info(f"Found exact JSON match: {json_match}")
                return self._load_json_holiday_file(json_match)
            elif os.path.exists(ical_match):
                logger.info(f"Found exact iCal match: {ical_match}")
                return self._load_ical_holiday_file(ical_match)
            elif potential_matches:
                logger.info(f"Found partial matches: {potential_matches}")
                # Use the first match
                selected_file = potential_matches[0]
                if selected_file.endswith('.json'):
                    return self._load_json_holiday_file(selected_file)
                elif selected_file.endswith('.ics'):
                    return self._load_ical_holiday_file(selected_file)
        
        # If only one file found, use it automatically
        if len(holiday_files) == 1:
            logger.info(f"Using the only available holiday file: {holiday_files[0]}")
            selected_file = holiday_files[0]
            if selected_file.endswith('.json'):
                return self._load_json_holiday_file(selected_file)
            elif selected_file.endswith('.ics'):
                return self._load_ical_holiday_file(selected_file)
        
        # Otherwise prompt user for selection
        print("\nAvailable holiday configuration files:")
        for i, file in enumerate(holiday_files, 1):
            print(f"{i}. {os.path.basename(file)}")
        
        while True:
            try:
                choice = int(input("\nSelect a holiday configuration file (enter number): ")) - 1
                if 0 <= choice < len(holiday_files):
                    selected_file = holiday_files[choice]
                    if selected_file.endswith('.json'):
                        return self._load_json_holiday_file(selected_file)
                    elif selected_file.endswith('.ics'):
                        return self._load_ical_holiday_file(selected_file)
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
            except Exception as e:
                print(f"Error loading file: {str(e)}")
    
    def _load_json_holiday_file(self, filepath: str) -> Dict:
        """
        Load and parse JSON holiday file.
        
        Args:
            filepath: Path to the JSON holiday file.
            
        Returns:
            Dict containing holiday configuration.
        """
        logger.info(f"Loading JSON holiday file: {filepath}")
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
                self._validate_holiday_config(config)
                return config
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON holiday file: {e}")
            raise ValueError(f"Invalid JSON format in holiday file: {filepath}")
    
    def _load_ical_holiday_file(self, filepath: str) -> Dict:
        """
        Load and parse iCal holiday file and convert to the same format as JSON.
        
        Args:
            filepath: Path to the iCal holiday file.
            
        Returns:
            Dict containing holiday configuration.
        """
        logger.info(f"Loading iCal holiday file: {filepath}")
        try:
            # Initialize holiday config
            holiday_config = {}
            
            # Extract region from filename
            filename = os.path.basename(filepath)
            region = filename.replace('.ics', '')
            holiday_config['region'] = region
            
            with open(filepath, 'r') as f:
                cal = Calendar.from_ical(f.read())
                
                holidays_list = []
                years = set()
                
                for component in cal.walk():
                    if component.name == "VEVENT":
                        date_obj = component.get('dtstart').dt
                        if isinstance(date_obj, datetime):
                            date_obj = date_obj.date()
                        
                        years.add(date_obj.year)
                        
                        name = str(component.get('summary'))
                        date_str = date_obj.strftime('%Y-%m-%d')
                        
                        # Add holiday as dictionary to list
                        holidays_list.append({
                            "date": date_str,
                            "description": name
                        })
                
                # Set the year in the config
                if years:
                    holiday_config['year'] = min(years)
                    
                # Store the holidays list in the config
                holiday_config['holidays'] = holidays_list
                
                self._validate_holiday_config(holiday_config)
                return holiday_config
        except Exception as e:
            logger.error(f"Error parsing iCal holiday file: {e}")
            raise ValueError(f"Invalid iCal format in holiday file: {filepath}")
    
    def _validate_vacation_config(self, config: Dict) -> None:
        """
        Validate vacation configuration.
        
        Args:
            config: Vacation configuration dictionary.
            
        Raises:
            ValueError: If configuration is invalid.
        """
        required_fields = ['firstName', 'lastName', 'year', 'region', 'vacationBlocks']
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field in vacation config: {field}")
                raise ValueError(f"Missing required field in vacation config: {field}")
        
        # Validate year
        if not isinstance(config['year'], int):
            logger.error("Year must be an integer")
            raise ValueError("Year must be an integer")
        
        # Validate vacation blocks
        if not isinstance(config['vacationBlocks'], list):
            logger.error("vacationBlocks must be a list")
            raise ValueError("vacationBlocks must be a list")
        
        for block in config['vacationBlocks']:
            required_block_fields = ['description', 'start', 'end']
            for field in required_block_fields:
                if field not in block:
                    logger.error(f"Missing required field in vacation block: {field}")
                    raise ValueError(f"Missing required field in vacation block: {field}")
            
            # Validate date formats
            try:
                start_date = datetime.strptime(block['start'], "%Y-%m-%d").date()
                end_date = datetime.strptime(block['end'], "%Y-%m-%d").date()
                
                # Validate date order
                if start_date > end_date:
                    logger.error(f"Start date {start_date} is after end date {end_date}")
                    raise ValueError(f"Start date {start_date} is after end date {end_date}")
                
                # Check if dates are in the configured year
                if start_date.year != config['year'] or end_date.year != config['year']:
                    logger.warning(f"Vacation block dates don't match configured year. Block: {block['description']}")
            except ValueError as e:
                logger.error(f"Invalid date format in vacation block: {e}")
                raise ValueError(f"Invalid date format in vacation block: {block}")
    
    def _validate_holiday_config(self, config: Dict) -> None:
        """
        Validate holiday configuration.
        
        Args:
            config: Holiday configuration dictionary.
            
        Raises:
            ValueError: If configuration is invalid.
        """
        required_fields = ['region', 'year', 'holidays']
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field in holiday config: {field}")
                raise ValueError(f"Missing required field in holiday config: {field}")
        
        # Validate holidays
        if not isinstance(config['holidays'], list):
            logger.error("holidays must be a list")
            raise ValueError("holidays must be a list")
        
        for holiday in config['holidays']:
            required_holiday_fields = ['date', 'description']
            for field in required_holiday_fields:
                if field not in holiday:
                    logger.error(f"Missing required field in holiday: {field}")
                    raise ValueError(f"Missing required field in holiday: {field}")
            
            # Validate date format
            try:
                holiday_date = datetime.strptime(holiday['date'], "%Y-%m-%d").date()
                
                # Check if date is in the configured year
                if isinstance(config['year'], int) and holiday_date.year != config['year']:
                    logger.warning(f"Holiday date doesn't match configured year. Holiday: {holiday['description']}")
            except ValueError as e:
                logger.error(f"Invalid date format in holiday: {e}")
                raise ValueError(f"Invalid date format in holiday: {holiday}")
