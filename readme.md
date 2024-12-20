# VacationPlaner

VacationPlaner is a Python-based tool that helps you manage and visualize holidays and vacation days. It generates both a visual calendar representation and an ICS file that can be imported into various calendar applications.

## Features

- Creates visual calendar overview of the entire year
- Generates ICS calendar files compatible with most calendar applications
- Distinguishes between different types of days:
  - Public holidays
  - Personal vacation days
  - Weekends
  - Regular workdays
- Color-coded visualization:
  - Holidays: Light orange (#FFDDC1)
  - Vacation: Light green (#C1FFD7)
  - Weekends: Light blue (#C1D4FF)
  - Workdays: White (#FFFFFF)

Sample:
![grafik](https://github.com/user-attachments/assets/38d59b3e-a868-476d-aaf3-d7da13c69774)

## File Structure

### src/VacationPlaner.py
The main Python script that handles the calendar generation and visualization.

Important: establish the dependencies first
```
    pip install -r requirements.txt
```

### conf/holidays-RegionName-YYYY.json
Configuration file for public holidays. Structure:
```json
{
    "region": "Kanton Thurgau",
    "year": 2025,
    "holidays": [
        {
            "date": "2025-01-01",
            "description": "Neujahr"
        },
        // ... more holidays ...
    ]
}
```

To modify holidays:
1. Follow the existing JSON structure
2. Use the format "YYYY-MM-DD" for dates
3. Provide a description for each holiday
4. Make sure the year matches the configuration

### conf/ferien_region_*.ics
Alternatively, you may use existing .ics files with the public holidays and school vacations

### Comparison between the rgions of vaction and holiday config files

The comparison will be flexible while still catching completely mismatched regions. 
- "Kanton Thurgau" will match with "THURGAU"
- "DE" will match with "Deutschland"
- "USA" will match with "United States"
etc.

### conf/vacation-planer-Firstname_Lastname.json
Configuration file for personal vacation days. Structure:
```json
{
    "firstName": "John",
    "lastName": "Doe",
    "year": 2025,
    "region": "Region Name",
    "vacationBlocks": [
        {
            "description": "Neujahrsblock",
            "start": "2025-01-02",
            "end": "2025-01-03"
        },
        {
            "description": "Osterblock",
            "start": "2025-04-14",
            "end": "2025-04-17"
        },
        // ... more vacation blocks ...
    ]
}
```
To modify holidays:
1. Follow the existing JSON structure
2. Use the format "YYYY-MM-DD" for dates
3. Provide a description for each vacation block
4. Make sure the year matches the configuration
5. Make sure the region matches the configuration
6. Make sure the first and last name match the configuration

### vacation_2025_Firstname_Lastname.ics
The generated ICS calendar file. Contains:
- Public holidays
- Personal vacation days
- Weekends
- All-day events with status indicators

To modify the ICS file:
1. It's recommended to modify the source configurations rather than the ICS file directly
2. If manual modification is needed:
   - Follow the iCalendar format
   - Each event requires BEGIN:VEVENT and END:VEVENT tags
   - Use DATE format for DTSTART and DTEND
   - Maintain the existing property structure for compatibility

## Usage

1. Configure your holidays in a JSON file following the structure of holidays-thurgau-2025.json
2. Run VacationPlaner.py:
   ```bash
   python VacationPlaner.py
   ```
3. Select the appropriate configuration files when prompted
4. The script will generate:
   - A visual calendar (PNG and PDF)
   - An ICS file for calendar import

## Output Files

- `vacation_YEAR_FIRSTNAME_LASTNAME.png`: Visual calendar overview
- `vacation_YEAR_FIRSTNAME_LASTNAME.pdf`: PDF version of the calendar
- `vacation_YEAR_FIRSTNAME_LASTNAME.ics`: Calendar file for import

## Dependencies

- Python 3.x
- matplotlib
- numpy
- icalendar
- calendar (standard library)
- json (standard library)
- datetime (standard library)

## Notes

- The tool is configured for Swiss holidays in Thurgau, but can be adapted for other regions
- All events are set as all-day events
- Weekend days are automatically detected and marked
- The ICS file includes proper status indicators for calendar applications
