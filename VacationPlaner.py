import calendar
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, datetime, timedelta
from icalendar import Calendar, Event
import json
import glob
from typing import Dict, List, Tuple

class HolidayPlanner:
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

    def load_holiday_config(self, region: str = None, year: str = None) -> Dict:
        """Load holiday configuration file"""
        holiday_files = glob.glob("holidays-*.json")
        
        if not holiday_files:
            print("No holiday configuration files found!")
            return None
        
        # If region and year are provided, try to find exact match
        if region and year:
            exact_match = f"holidays-{region.lower()}-{year}.json"
            if exact_match in holiday_files:
                with open(exact_match, 'r') as f:
                    return json.load(f)
        
        print("\nAvailable holiday configuration files:")
        for i, file in enumerate(holiday_files, 1):
            print(f"{i}. {file}")
        
        while True:
            try:
                choice = int(input("\nSelect a holiday configuration file (enter number): ")) - 1
                if 0 <= choice < len(holiday_files):
                    with open(holiday_files[choice], 'r') as f:
                        return json.load(f)
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def load_vacation_config(self) -> Dict:
        """Load vacation configuration file"""
        config_files = glob.glob("vacation-planner-*.json")
        
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
        """Initialize the planner with configurations"""
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
        if self.config['region'] != self.holidays_config['region']:
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
            f"vacationplan {self.year} - {self.config['region']}\n"
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
        plt.savefig(f"vacation_{self.year}_{self.config['firstName']}_{self.config['lastName']}.png", dpi=300) #Save the figure

        # Create the calendar files
        plt.savefig(f"vacation_{self.year}_{self.config['firstName']}_{self.config['lastName']}.pdf", 
                    bbox_inches='tight', 
                    orientation='landscape')
        plt.show()

def create_ics(planner):
    """Create the ICS file"""
    filename = f"vacation_{planner.year}_{planner.config['firstName']}_{planner.config['lastName']}.ics"
    
    cal = Calendar()
    cal.add('prodid', '-//My Calendar//EN')
    cal.add('version', '2.0')

    for month in range(1, 13):
        month_cal = calendar.Calendar().monthdayscalendar(planner.year, month)
        for week in month_cal:
            for day in week:
                if day != 0:
                    current_date = date(planner.year, month, day)
                    event = Event()
                    
                    # Set as whole day event
                    event.add('dtstart', current_date, parameters={'VALUE': 'DATE'})
                    event.add('dtend', current_date + timedelta(days=1), parameters={'VALUE': 'DATE'})
                    
                    # Add common properties
                    event.add('transp', 'TRANSPARENT')
                    event.add('x-microsoft-cdo-busystatus', 'OOF')
                    event.add('x-microsoft-cdo-alldayevent', 'TRUE')
                    event.add('organizer', f"{planner.config['firstName']} {planner.config['lastName']}")
                    
                    if current_date in planner.holidays:
                        holiday_desc = planner.get_holiday_description(current_date)
                        event.add('summary', f"{holiday_desc} - {planner.config['firstName']} {planner.config['lastName']}")
                        event.add('description', f"{holiday_desc} - Out of Office - {planner.config['firstName']} {planner.config['lastName']}")
                        event.add('status', 'CONFIRMED')
                        event.add('class', 'PUBLIC')
                    elif planner.is_vacation(current_date):
                        event.add('summary', f"Vacation - {planner.config['firstName']} {planner.config['lastName']}")
                        event.add('description', f"Personal Vacation - Out of Office - {planner.config['firstName']} {planner.config['lastName' ]}")
                        event.add('status', 'CONFIRMED')
                        event.add('class', 'PRIVATE')
                    elif current_date.weekday() >= 5:
                        event.add('summary', f"Weekend - {planner.config['firstName' ]} {planner.config['lastName']}")
                        event.add('description', f"Weekend - Out of Office - {planner.config['firstName' ]} {planner.config['lastName' ]}")
                        event.add('status', 'CONFIRMED')
                        event.add('class', 'PUBLIC')
                    else:
                        continue

                    # Add to calendar
                    cal.add_component(event)

    with open(filename, 'wb') as f:
        f.write(cal.to_ical())

def main():
    planner = HolidayPlanner()
    planner.initialize()

    # Create visualization
    planner.create_calendar_visualization() # Call the method on the instance

    # Create ICS file
    create_ics(planner)

if __name__ == "__main__":
    main()