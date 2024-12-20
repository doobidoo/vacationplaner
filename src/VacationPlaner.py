import os
import calendar
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, datetime, timedelta
from icalendar import Calendar, Event
import json
import glob
from typing import Dict, List, Tuple, Union

print("Current Working Directory:", os.getcwd())
class VacationPlaner:
    def __init__(self):
        self.config = None
        self.holidays_config = None
        self.holidays = []
        self.vacation_blocks = []
        self.year = None
        self.colors = {  # Moved colors to class for better access
            "holiday": "#FFDDC1",
            "vacation": "#C1FFD7",
            "weekend": "#C1D4FF",
            "weekday": "#FFFFFF"
        }
        self.conf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "conf"))
        self.vacationplans_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vacationplans"))


    def check(self):
        print("Current Working Directory:", os.getcwd())
        print("Conf path:", self.conf_path)
        print("Vacation plans path:", self.vacationplans_path)
        print("Holiday config:", self.holidays_config)
        print("Vacation config:", self.config)
        print("Holidays:", self.holidays)
        print("Vacation blocks:", self.vacation_blocks)
        print("Colors:", self.colors)
        print("Year:", self.year)


    def load_holiday_config(self, region: str = None, year: str = None) -> Dict:
        
        # Find both JSON and iCal files
        holiday_files = glob.glob(os.path.join(self.conf_path, "holidays-*.json"))
        holiday_files.extend(glob.glob(os.path.join(self.conf_path, "*.ics")))
        
        if not holiday_files:
            print("No holiday configuration files found!")
            return None
        
        # If region and year are provided, try to find exact match
        if region and year:
            json_match = f"holidays-{region.lower()}-{year}.json"
            ical_match = f"holidays-{region.lower()}-{year}.ics"
            
            if json_match in holiday_files:
                return self._load_json_file(json_match)
            elif ical_match in holiday_files:
                return self._load_ical_file(ical_match)
        
        print("\nAvailable holiday configuration files:")
        for i, file in enumerate(holiday_files, 1):
            print(f"{i}. {file}")
        
        while True:
            try:
                choice = int(input("\nSelect a holiday configuration file (enter number): ")) - 1
                if 0 <= choice < len(holiday_files):
                    selected_file = holiday_files[choice]
                    if selected_file.endswith('.json'):
                        return self._load_json_file(selected_file)
                    elif selected_file.endswith('.ics'):
                        return self._load_ical_file(selected_file)
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def _load_json_file(self, filepath: str) -> Dict:
        """Load and parse JSON holiday file"""
        with open(filepath, 'r') as f:
            return json.load(f)

    def _load_ical_file(self, filepath: str) -> Dict:
        """Load and parse iCal holiday file and convert to the same format as JSON"""
        # Initialize holidays_config if it doesn't exist
        if self.holidays_config is None:
            self.holidays_config = {}
            
        # Extract region from filename
        filename = os.path.basename(filepath)
        region = filename.replace('.ics', '')
        self.holidays_config['region'] = region
        
        with open(filepath, 'r') as f:
            cal = Calendar.from_ical(f.read())
            
            holidays_list = []  # Changed to list instead of dict
            years = set()
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    date = component.get('dtstart').dt
                    if isinstance(date, datetime):
                        date = date.date()
                    
                    years.add(date.year)
                    
                    name = str(component.get('summary'))
                    date_str = date.strftime('%Y-%m-%d')
                    
                    # Add holiday as dictionary to list
                    holidays_list.append({
                        "date": date_str,
                        "description": name
                    })
            
            # Set the year in the config (convert to integer)
            if years:
                self.holidays_config['year'] = min(years)  # Remove str() conversion
                
            # Store the holidays list in the config
            self.holidays_config['holidays'] = holidays_list
            
            return self.holidays_config

    def load_vacation_config(self) -> Dict:
        """Load vacation configuration file"""
        #self.check()
        config_files = glob.glob(os.path.join(self.conf_path, "vacation-planer*.json"))
        print(config_files)
        
        if not config_files:
            print("No vacation configuration files found!")
            return None
        
        print("\nAvailable configuration files:")
        for i, file in enumerate(config_files, 1):
            print(f"{i}. {file}")
        
        while True:
            try:
                choice = int(input("\nSelect a configuration file (enter number): ")) - 1
                if 0 <= choice < len(config_files):
                    with open(config_files[choice], 'r') as f:
                        return json.load(f)
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def parse_date(self, date_str: str) -> date:
        """Parse date string to date object"""
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    def initialize(self):
        """Initialize the planer with configurations"""
        # Load vacation config first
        self.config = self.load_vacation_config()
        if not self.config:
            print("No valid vacation configuration selected. Exiting.")
            exit()

        # Load holiday config using region and year from vacation config
        self.holidays_config = self.load_holiday_config(
            self.config.get('region'), 
            str(self.config.get('year'))
        )
        if not self.holidays_config:
            print("No valid holiday configuration selected. Exiting.")
            exit()

        # Validate matching years and regions
        if self.config['year'] != self.holidays_config['year']:
            print("Warning: Year mismatch between vacation and holiday configs!")

        # Convert both regions to lowercase for case-insensitive comparison
        config_region = self.config['region'].lower()
        holiday_region = self.holidays_config['region'].lower()

        # Check if either region is a substring of the other
        if holiday_region not in config_region and config_region not in holiday_region:
            print("Warning: Region mismatch between vacation and holiday configs!")

        # Set class variables
        self.year = self.config['year']
        self.holidays = [self.parse_date(holiday['date']) for holiday in self.holidays_config['holidays']]
        self.vacation_blocks = [(self.parse_date(block['start']), self.parse_date(block['end'])) 
                              for block in self.config['vacationBlocks']]

    def is_vacation(self, day: date) -> bool:
        """Check if a given day is a vacation day"""
        for start, end in self.vacation_blocks:
            if start <= day <= end:
                return True
        return False

    def get_holiday_description(self, day: date) -> str:
        """Get the description of a holiday"""
        for holiday in self.holidays_config['holidays']:
            if self.parse_date(holiday['date']) == day:
                return holiday['description']
        return "Holiday"
  

    def create_calendar_visualization(self): # Moved to class
        """Create the calendar visualization"""
        months = range(1, 13)
        fig, axes = plt.subplots(4, 3, figsize=(11.7, 8.3))
        fig.suptitle(
            f"Vacationplan {self.year} - {self.config['region']}\n"
            f"{self.config['firstName']} {self.config['lastName']}",
            fontsize=14, y=0.98
        )

        for month, ax in zip(months, axes.flatten()):
            month_cal = calendar.Calendar().monthdayscalendar(self.year, month)
            ax.set_title(calendar.month_name[month], fontsize=14, y=0.98)
            ax.axis("off")

            table_data = []
            cell_colors = []
            for week in month_cal:
                row = []
                row_colors = []
                for day in week:
                    if day == 0:
                        row.append("")
                        row_colors.append(self.colors["weekday"])
                    else:
                        current_date = date(self.year, month, day)
                        if current_date in self.holidays:
                            row.append(str(day))
                            row_colors.append(self.colors["holiday"])
                        elif self.is_vacation(current_date):
                            row.append(str(day))
                            row_colors.append(self.colors["vacation"])
                        elif current_date.weekday() >= 5:
                            row.append(str(day))
                            row_colors.append(self.colors["weekend"])
                        else:
                            row.append(str(day))
                            row_colors.append(self.colors["weekday"])
                table_data.append(row)
                cell_colors.append(row_colors)

            table = ax.table(
                cellText=table_data,
                cellLoc='center',
                cellColours=np.array(cell_colors),
                loc='center',
                colWidths=[0.12] * 7
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.2)

        legend_elements = [
            plt.Line2D([0], [0], color=self.colors["holiday"], lw=4, label='Feiertage (F)'),
            plt.Line2D([0], [0], color=self.colors["vacation"], lw=4, label='Urlaubstage (U)'),
            plt.Line2D([0], [0], color=self.colors["weekend"], lw=4, label='Wochenenden (W)'),
        ]
        fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=10, frameon=False)
        plt.tight_layout(rect=[0, 0.05, 1, 0.95]) # Adjust layout to prevent legend overlap
        pngfilename = f"vacation_{self.year}_{self.config['firstName']}_{self.config['lastName']}.png" #Save the figure
        plt.savefig(os.path.join(self.vacationplans_path, pngfilename), dpi=300)
        #plt.savefig(f"vacation_{self.year}_{self.config['firstName']}_{self.config['lastName']}.png", dpi=300) #Save the figure

        # Create the calendar files
        calendarfilename = f"vacation_{self.year}_{self.config['firstName']}_{self.config['lastName']}.pdf"
        filename = os.path.join(self.vacationplans_path, calendarfilename)
        #plt.savefig(f"vacation_{self.year}_{self.config['firstName']}_{self.config['lastName']}.pdf", 
        plt.savefig(filename, 
                    bbox_inches='tight', 
                    orientation='landscape')
        plt.show()

    def create_ics(self):
        """Create the ICS file"""
        icsfilename = f"vacation_{self.year}_{self.config['firstName']}_{self.config['lastName']}.ics"
        filename = os.path.join(self.vacationplans_path, icsfilename)
        cal = Calendar()
        cal.add('prodid', '-//My Calendar//EN')
        cal.add('version', '2.0')

        for month in range(1, 13):
            month_cal = calendar.Calendar().monthdayscalendar(self.year, month)
            for week in month_cal:
                for day in week:
                    if day != 0:
                        current_date = date(self.year, month, day)
                        event = Event()
                        
                        # Set as whole day event
                        event.add('dtstart', current_date, parameters={'VALUE': 'DA