#!/usr/bin/env python3
"""
VacationPlaner - A tool for managing and visualizing holidays and vacation days.

This is the main entry point for the VacationPlaner application.
"""

import sys
import os
import logging

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the vacationplaner module
from vacationplaner.app import VacationPlanerApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for VacationPlaner."""
    try:
        # Create and run the application
        app = VacationPlanerApp()
        viz_files, ics_file = app.run()
        
        # Print summary of created files
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
