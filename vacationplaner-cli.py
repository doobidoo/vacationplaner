#!/usr/bin/env python3
"""
Command-line interface for VacationPlaner.
"""

import sys
import os
import argparse
import logging
from src.vacationplaner.app import VacationPlanerApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="VacationPlaner - A tool for managing and visualizing holidays and vacation days"
    )
    
    parser.add_argument(
        "--conf", 
        help="Path to configuration directory"
    )
    parser.add_argument(
        "--output", 
        help="Path to output directory"
    )
    parser.add_argument(
        "--vacation-config", 
        help="Path to vacation configuration file"
    )
    parser.add_argument(
        "--holiday-config", 
        help="Path to holiday configuration file"
    )
    parser.add_argument(
        "--no-viz", 
        action="store_true", 
        help="Skip visualization generation"
    )
    parser.add_argument(
        "--no-ics", 
        action="store_true", 
        help="Skip ICS file generation"
    )
    parser.add_argument(
        "--no-show", 
        action="store_true", 
        help="Don't display visualization"
    )
    parser.add_argument(
        "--include-weekends", 
        action="store_true", 
        help="Include weekends in ICS file"
    )
    parser.add_argument(
        "--version", 
        action="store_true", 
        help="Display version information"
    )
    
    return parser.parse_args()


def main():
    """Main function for command-line interface."""
    args = parse_arguments()
    
    # Handle version display
    if args.version:
        print("VacationPlaner v1.0.0")
        return 0
    
    try:
        # Create application instance
        app = VacationPlanerApp(
            conf_path=args.conf,
            output_path=args.output,
            vacation_config_path=args.vacation_config,
            holiday_config_path=args.holiday_config
        )
        
        # Run with specified options
        viz_files, ics_file = app.run(
            create_viz=not args.no_viz,
            create_ics=not args.no_ics,
            show_viz=not args.no_show
        )
        
        # Print success message
        print("\nVacationPlaner completed successfully!")
        
        if viz_files:
            print(f"Generated visualization files:")
            print(f"  - PNG: {viz_files['png']}")
            print(f"  - PDF: {viz_files['pdf']}")
        
        if ics_file:
            print(f"Generated ICS file:")
            print(f"  - ICS: {ics_file}")
        
        print("\nFiles are ready for use. Thank you for using VacationPlaner!")
        
        return 0
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    
    except Exception as e:
        logger.exception("An error occurred:")
        print(f"\nError: {e}")
        print("Check the log for more details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
