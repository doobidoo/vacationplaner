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

![Vacation Planner Example](https://github.com/user-attachments/assets/38d59b3e-a868-476d-aaf3-d7da13c69774)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd vacationplaner
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     .\.venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the main script:
```bash
python src/VacationPlaner.py
```

This will:
1. Prompt you to select a vacation configuration file
2. Prompt you to select a holiday configuration file
3. Generate visualization files (PNG and PDF)
4. Generate an ICS calendar file
5. Display the visualization

### Command Line Options

You can also run the tool with command-line options:

```bash
python src/VacationPlaner.py --vacation-config path/to/config.json --holiday-config path/to/holidays.json --no-show
```

Available options:
- `--conf`: Custom path to configuration directory
- `--output`: Custom path to output directory
- `--vacation-config`: Specific vacation configuration file
- `--holiday-config`: Specific holiday configuration file
- `--no-viz`: Skip visualization generation
- `--no-ics`: Skip ICS file generation
- `--no-show`: Don't display visualization (but still save files)

## Configuration Files

### Vacation Configuration

Create a JSON file in the `conf/` directory with the following structure:

```json
{
    "firstName": "John",
    "lastName": "Doe",
    "year": 2025,
    "region": "Kanton Thurgau",
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
        }
    ]
}
```

### Holiday Configuration

You can use either a JSON file or an iCal file for holidays.

#### JSON Format

```json
{
    "region": "Kanton Thurgau",
    "year": 2025,
    "holidays": [
        {
            "date": "2025-01-01",
            "description": "Neujahr"
        },
        {
            "date": "2025-04-18",
            "description": "Karfreitag"
        }
    ]
}
```

#### iCal Format

You can use standard iCal files (`.ics`) with `VEVENT` components. The tool will extract the holiday dates and descriptions.

## Output Files

The tool generates the following files in the `vacationplans/` directory:
- `vacation_YEAR_FIRSTNAME_LASTNAME.png`: Visual calendar overview
- `vacation_YEAR_FIRSTNAME_LASTNAME.pdf`: PDF version of the calendar
- `vacation_YEAR_FIRSTNAME_LASTNAME.ics`: Calendar file for import

## Project Structure

- `src/`: Source code directory
  - `VacationPlaner.py`: Main entry point
  - `vacationplaner/`: Main package
    - `app.py`: Main application class
    - `calendar_manager.py`: Handles calendar data and logic
    - `config_manager.py`: Manages configuration loading
    - `ics_generator.py`: Generates ICS files
    - `visualizer.py`: Creates calendar visualizations
- `conf/`: Configuration files directory
- `vacationplans/`: Output files directory
- `requirements.txt`: Python dependencies

## Troubleshooting

### Missing packages

If you encounter errors about missing packages, ensure you're running in the activated virtual environment and have installed all requirements:
```bash
pip install -r requirements.txt
```

### Timezone issues

If you encounter timezone-related errors, ensure you have installed the tzdata package:
```bash
pip install tzdata
```

### Visualization problems

If the calendar visualization doesn't display correctly, check that you have installed all necessary dependencies:
```bash
pip install matplotlib numpy Pillow
```

### File paths issues

If the tool can't find configuration files or can't save output files, check:
1. That you're running the script from the repository root directory
2. That the `conf/` and `vacationplans/` directories exist
3. That you have write permissions for the output directory

## Notes

- The tool is configured for Swiss holidays in Thurgau, but can be adapted for other regions
- All events are set as all-day events
- Weekend days are automatically detected and marked
- The ICS file includes proper status indicators for calendar applications

## License

This project is provided as-is without any warranty. You are free to use, modify, and distribute it as needed.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.
