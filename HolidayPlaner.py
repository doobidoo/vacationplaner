import calendar
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, datetime, timedelta
from icalendar import Calendar, Event
import json
import os
import glob
from pathlib import Path


def load_config():
    # List all config files in the current directory
    config_files = glob.glob("vacation-planner-*.json")
    
    if not config_files:
        print("No configuration files found!")
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

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

# Load configuration
config = load_config()
if not config:
    print("No valid configuration selected. Exiting.")
    exit()

# Parse configuration
year = config['year']
vacation_blocks = [(parse_date(block['start']), parse_date(block['end'])) 
                  for block in config['vacationBlocks']]


# Define holidays and vacation blocks
holidays = [
    date(2025, 1, 1), date(2025, 1, 2), date(2025, 4, 18), date(2025, 4, 21),
    date(2025, 5, 1), date(2025, 5, 29), date(2025, 6, 9), date(2025, 8, 1),
    date(2025, 12, 25), date(2025, 12, 26)
]

vacation_blocks = [
    (date(2025, 1, 2), date(2025, 1, 3)),    # Neujahrsblock
    (date(2025, 4, 14), date(2025, 4, 17)),   # Osterblock
    (date(2025, 5, 2), date(2025, 5, 2)),     # Mai-Brücke
    (date(2025, 5, 30), date(2025, 5, 30)),   # Auffahrtsbrücke
    (date(2025, 6, 26), date(2025, 6, 27)),   # Geburtstag
    (date(2025, 7, 28), date(2025, 7, 31)),   # Sommerblock 1
    (date(2025, 8, 4), date(2025, 8, 8)),     # Sommerblock 2
    (date(2025, 10, 6), date(2025, 10, 10)),  # Herbstblock
    (date(2025, 12, 22), date(2025, 12, 24)), # Weihnachtsblock 1
    (date(2025, 12, 29), date(2025, 12, 31))  # Weihnachtsblock 2
]

# Colors for different types of days
colors = {
    "holiday": "#FFDDC1",   # Light orange for holidays
    "vacation": "#C1FFD7",  # Light green for vacation
    "weekend": "#C1D4FF",   # Light blue for weekends
    "weekday": "#FFFFFF"    # White for regular weekdays
}

# Helper to determine if a day is part of a vacation block
def is_vacation(day):
    for start, end in vacation_blocks:
        if start <= day <= end:
            return True
    return False

# Optimized calendar rendering with better alignment and a legend
year = 2025
months = range(1, 13)
fig, axes = plt.subplots(4, 3, figsize=(11.7, 8.3))  # Adjust layout for better space usage
fig.suptitle(f"Ferienplanung {year} - {config['region']}\n{config['firstName']} {config['lastName']}", fontsize=16)

for month, ax in zip(months, axes.flatten()):
    month_cal = calendar.Calendar().monthdayscalendar(year, month)
    ax.set_title(calendar.month_name[month], fontsize=14, y=0.98)
    ax.axis("off")

    # Create a grid for the days with colors
    table_data = []
    cell_colors = []
    for week in month_cal:
        row = []
        row_colors = []
        for day in week:
            if day == 0:
                row.append("")
                row_colors.append(colors["weekday"])  # Empty cell
            else:
                current_date = date(year, month, day)
                if current_date in holidays:
                    row.append(str(day))
                    row_colors.append(colors["holiday"])
                elif is_vacation(current_date):
                    row.append(str(day))
                    row_colors.append(colors["vacation"])
                elif current_date.weekday() >= 5:
                    row.append(str(day))
                    row_colors.append(colors["weekend"])
                else:
                    row.append(str(day))
                    row_colors.append(colors["weekday"])
        table_data.append(row)
        cell_colors.append(row_colors)

    # Render the table with colors  <-- THIS WAS MISSING
    table = ax.table(
        cellText=table_data,
        cellLoc='center',
        cellColours=np.array(cell_colors),
        loc='center',
        colWidths=[0.12] * 7
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.2)  # Adjust scale for better spacing

# Add a legend below the calendar
legend_elements = [
    plt.Line2D([0], [0], color=colors["holiday"], lw=4, label='Feiertage (F)'),
    plt.Line2D([0], [0], color=colors["vacation"], lw=4, label='Urlaubstage (U)'),
    plt.Line2D([0], [0], color=colors["weekend"], lw=4, label='Wochenenden (W)'),
]
fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=10, frameon=False)



def create_ics(config, filename=None):
    if filename is None:
        filename = f"ferien_{year}_{config['firstName']}_{config['lastName']}.ics"
    
    cal = Calendar()
    cal.add('prodid', '-//My Calendar//EN')
    cal.add('version', '2.0')

    for month in range(1, 13):
        month_cal = calendar.Calendar().monthdayscalendar(year, month)
        for week in month_cal:
            for day in week:
                if day != 0:
                    current_date = date(year, month, day)
                    event = Event()
                    
                    # Set as whole day event
                    event.add('dtstart', current_date, parameters={'VALUE': 'DATE'})
                    event.add('dtend', current_date + timedelta(days=1), parameters={'VALUE': 'DATE'})
                    
                    # Add common properties for out of office
                    event.add('transp', 'TRANSPARENT')
                    event.add('x-microsoft-cdo-busystatus', 'OOF')
                    event.add('x-microsoft-cdo-alldayevent', 'TRUE')
                    
                    # Add organizer information
                    event.add('organizer', f"{config['firstName']} {config['lastName']}")
                    
                    if current_date in holidays:
                        event.add('summary', f"Holiday - {config['firstName']} {config['lastName']}")
                        event.add('description', f"Public Holiday - Out of Office - {config['firstName']} {config['lastName']}")
                        event.add('status', 'CONFIRMED')
                        event.add('class', 'PUBLIC')
                    elif is_vacation(current_date):
                        event.add('summary', f"Vacation - {config['firstName']} {config['lastName']}")
                        event.add('description', f"Personal Vacation - Out of Office - {config['firstName']} {config['lastName']}")
                        event.add('status', 'CONFIRMED')
                        event.add('class', 'PRIVATE')
                    elif current_date.weekday() >= 5:
                        event.add('summary', f"Weekend - {config['firstName']} {config['lastName']}")
                        event.add('description', f"Weekend - Out of Office - {config['firstName']} {config['lastName']}")
                        event.add('status', 'CONFIRMED')
                        event.add('class', 'PUBLIC')
                    else:
                        continue
                    
                    cal.add_component(event)

    with open(filename, 'wb') as f:
        f.write(cal.to_ical())

    cal = Calendar()
    cal.add('prodid', '-//My Calendar//EN')
    cal.add('version', '2.0')

    for month in range(1, 13):
        month_cal = calendar.Calendar().monthdayscalendar(year, month)
        for week in month_cal:
            for day in week:
                if day != 0:
                    current_date = date(year, month, day)
                    event = Event()
                    
                    # Set as whole day event
                    event.add('dtstart', current_date, parameters={'VALUE': 'DATE'})
                    event.add('dtend', current_date + timedelta(days=1), parameters={'VALUE': 'DATE'})
                    
                    # Add common properties for out of office
                    event.add('transp', 'TRANSPARENT')  # Show as free
                    event.add('x-microsoft-cdo-busystatus', 'OOF')  # Out of office status
                    event.add('x-microsoft-cdo-alldayevent', 'TRUE')  # Marks as all-day in Outlook
                    
                    if current_date in holidays:
                        event.add('summary', 'Holiday')
                        event.add('description', 'Public Holiday - Out of Office')
                        event.add('status', 'CONFIRMED')
                        event.add('class', 'PUBLIC')
                    elif is_vacation(current_date):
                        event.add('summary', 'Vacation')
                        event.add('description', 'Personal Vacation - Out of Office')
                        event.add('status', 'CONFIRMED')
                        event.add('class', 'PRIVATE')
                    elif current_date.weekday() >= 5:
                        event.add('summary', 'Weekend')
                        event.add('description', 'Weekend - Out of Office')
                        event.add('status', 'CONFIRMED')
                        event.add('class', 'PUBLIC')
                    else:
                        continue  # Skip regular weekdays to avoid cluttering the calendar
                    
                    cal.add_component(event)

    with open(filename, 'wb') as f:
        f.write(cal.to_ical())



# plt.tight_layout(rect=[0, 0.06, 1, 0.96])  # Adjust layout to include the legend

# Create the calendar files
plt.savefig(f"calendar_{year}_{config['firstName']}_{config['lastName']}.pdf", 
            bbox_inches='tight', 
            orientation='landscape')
plt.show()

create_ics(config)