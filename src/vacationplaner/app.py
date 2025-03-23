"""
Main application module for VacationPlaner.
"""

import os
import sys
import argparse
import logging
from typing import Dict, Optional, Tuple
from .config_manager import ConfigManager
from .calendar_manager import CalendarManager
from .visualizer import CalendarVisualizer
from .ics_generator import ICSGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VacationPlanerApp:
    """Main application class for VacationPlaner."""
    
    def __init__(
        self,
        conf_path: Optional[str] = None,
        output_path: Optional[str] = None,
        vacation_config_path: Optional[str] = None,
        holiday_config_path: Optional[str] = None
    ):
        """
        Initialize the VacationPlaner application.
        
        Args:
            conf_path: Path to configuration directory (optional).
            output_path: Path to output directory (optional).
            vacation_config_path: Path to vacation configuration file (optional).
            holiday_config_path: Path to holiday configuration file (optional).
        """
        # Determine paths
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        
        self.conf_path = conf_path or os.path.join(base_dir, "conf")
        self.output_path = output_path or os.path.join(base_dir, "vacationplans")
        
        logger.info(f"Configuration path: {self.conf_path}")
        logger.info(f"Output path: {self.output_path}")
        
        # Initialize components
        self.config_manager = ConfigManager(self.conf_path)
        self.vacation_config = None
        self.holiday_config = None
        self.calendar_manager = None
        self.visualizer = None
        self.ics_generator = None
        
        # Load specified configs if provided
        if vacation_config_path:
            try:
                self.load_vacation_config(vacation_config_path)
            except Exception as e:
                logger.error(f"Failed to load vacation config: {e}")
        
        if holiday_config_path:
            try:
                self.load_holiday_config(holiday_config_path)
            except Exception as e:
                logger.error(f"Failed to load holiday config: {e}")
    
    def load_vacation_config(self, path: Optional[str] = None) -> Dict:
        """
        Load vacation configuration.
        
        Args:
            path: Path to vacation configuration file (optional).
            
        Returns:
            Vacation configuration dictionary.
        """
        try:
            self.vacation_config = self.config_manager.load_vacation_config(path)
            logger.info(f"Loaded vacation config for {self.vacation_config['firstName']} {self.vacation_config['lastName']}")
            return self.vacation_config
        except Exception as e:
            logger.error(f"Error loading vacation config: {e}")
            raise
    
    def load_holiday_config(self, path: Optional[str] = None) -> Dict:
        """
        Load holiday configuration.
        
        Args:
            path: Path to holiday configuration file (optional).
            
        Returns:
            Holiday configuration dictionary.
        """
        # If vacation config is loaded, use its region and year
        region = None
        year = None
        
        if self.vacation_config:
            region = self.vacation_config.get('region')
            year = self.vacation_config.get('year')
        
        try:
            if path:
                # If path is provided, load directly
                if path.endswith('.json'):
                    self.holiday_config = self.config_manager._load_json_holiday_file(path)
                elif path.endswith('.ics'):
                    self.holiday_config = self.config_manager._load_ical_holiday_file(path)
                else:
                    raise ValueError(f"Unsupported holiday config file format: {path}")
            else:
                # Otherwise use the config manager
                self.holiday_config = self.config_manager.load_holiday_config(region, year)
            
            logger.info(f"Loaded holiday config for {self.holiday_config['region']} {self.holiday_config['year']}")
            return self.holiday_config
        except Exception as e:
            logger.error(f"Error loading holiday config: {e}")
            raise
    
    def initialize(self) -> bool:
        """
        Initialize the application components.
        
        Returns:
            True if initialization successful, False otherwise.
        """
        try:
            # Load configs if not already loaded
            if not self.vacation_config:
                self.load_vacation_config()
            
            if not self.holiday_config:
                self.load_holiday_config()
            
            # Validate configuration compatibility
            self._validate_configs()
            
            # Initialize components
            year = self.vacation_config['year']
            self.calendar_manager = CalendarManager(year, self.holiday_config, self.vacation_config)
            self.visualizer = CalendarVisualizer(self.calendar_manager, self.output_path)
            self.ics_generator = ICSGenerator(self.calendar_manager, self.output_path)
            
            logger.info("VacationPlaner application initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def _validate_configs(self) -> None:
        """
        Validate compatibility between vacation and holiday configs.
        
        Raises:
            ValueError: If configurations are incompatible.
        """
        if not self.vacation_config or not self.holiday_config:
            raise ValueError("Both vacation and holiday configurations must be loaded")
        
        # Check year compatibility
        v_year = self.vacation_config['year']
        h_year = self.holiday_config['year']
        
        if v_year != h_year:
            logger.warning(f"Year mismatch: vacation config year ({v_year}) != holiday config year ({h_year})")
            # Still continue, just a warning
        
        # Check region compatibility (case-insensitive partial match)
        v_region = self.vacation_config['region'].lower()
        h_region = self.holiday_config['region'].lower()
        
        if v_region not in h_region and h_region not in v_region:
            logger.warning(f"Region mismatch: vacation config region ({v_region}) and holiday config region ({h_region})")
            # Still continue, just a warning
    
    def create_visualization(self, show: bool = True) -> Dict[str, str]:
        """
        Create and save the calendar visualization.
        
        Args:
            show: Whether to display the visualization.
            
        Returns:
            Dictionary with paths to output files.
        """
        if not self.visualizer:
            raise ValueError("Application not initialized. Call initialize() first.")
        
        return self.visualizer.create_visualization(show)
    
    def create_ics(self, include_weekends: bool = True) -> str:
        """
        Create and save the ICS calendar file.
        
        Args:
            include_weekends: Whether to include weekends in the ICS file.
            
        Returns:
            Path to the generated ICS file.
        """
        if not self.ics_generator:
            raise ValueError("Application not initialized. Call initialize() first.")
        
        return self.ics_generator.generate_ics(include_weekends)
    
    def run(self, create_viz: bool = True, create_ics: bool = True, show_viz: bool = True) -> Tuple[Dict[str, str], str]:
        """
        Run the complete VacationPlaner workflow.
        
        Args:
            create_viz: Whether to create the visualization.
            create_ics: Whether to create the ICS file.
            show_viz: Whether to display the visualization.
            
        Returns:
            Tuple with paths to visualization files and ICS file.
        """
        if not self.initialize():
            logger.error("Failed to initialize application")
            sys.exit(1)
        
        viz_files = None
        ics_file = None
        
        if create_viz:
            viz_files = self.create_visualization(show_viz)
            logger.info(f"Created visualization files: {viz_files}")
        
        if create_ics:
            ics_file = self.create_ics()
            logger.info(f"Created ICS file: {ics_file}")
        
        return viz_files, ics_file


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="VacationPlaner - A tool for managing and visualizing holidays and vacation days")
    
    parser.add_argument("--conf", help="Path to configuration directory")
    parser.add_argument("--output", help="Path to output directory")
    parser.add_argument("--vacation-config", help="Path to vacation configuration file")
    parser.add_argument("--holiday-config", help="Path to holiday configuration file")
    parser.add_argument("--no-viz", action="store_true", help="Skip visualization generation")
    parser.add_argument("--no-ics", action="store_true", help="Skip ICS file generation")
    parser.add_argument("--no-show", action="store_true", help="Don't display visualization")
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    app = VacationPlanerApp(
        conf_path=args.conf,
        output_path=args.output,
        vacation_config_path=args.vacation_config,
        holiday_config_path=args.holiday_config
    )
    
    app.run(
        create_viz=not args.no_viz,
        create_ics=not args.no_ics,
        show_viz=not args.no_show
    )


if __name__ == "__main__":
    main()
