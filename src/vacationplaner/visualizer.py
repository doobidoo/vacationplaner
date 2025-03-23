"""
Visualization module for VacationPlaner.
Handles creating calendar visualizations.
"""

import os
import calendar
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from typing import Dict, List, Optional, Any
import logging
from .calendar_manager import CalendarManager
import locale

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure matplotlib for proper Unicode handling
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['pdf.fonttype'] = 42  # TrueType fonts
matplotlib.rcParams['ps.fonttype'] = 42   # TrueType fonts

# Try to set locale for proper display of month names
try:
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')  # German locale
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'de_DE')  # Fallback
    except locale.Error:
        logger.warning("Could not set German locale for month names")


class CalendarVisualizer:
    """Creates visual calendar representations."""
    
    def __init__(self, calendar_manager: CalendarManager, output_path: str):
        """
        Initialize the calendar visualizer.
        
        Args:
            calendar_manager: Calendar manager instance.
            output_path: Path to save output files.
        """
        self.calendar_manager = calendar_manager
        self.output_path = os.path.abspath(output_path)
        
        # Ensure output directory exists
        if not os.path.exists(self.output_path):
            logger.info(f"Creating output directory: {self.output_path}")
            os.makedirs(self.output_path)
        
        # Customizable colors for different day types
        self.colors = {
            "holiday": "#FFDDC1",    # Light orange
            "vacation": "#C1FFD7",    # Light green
            "weekend": "#C1D4FF",     # Light blue
            "weekday": "#FFFFFF",     # White
            "outside": "#FFFFFF"      # White for days outside the month
        }
        
        # Border colors for vacation blocks (will cycle through these)
        self.border_colors = [
            "#007700",  # Dark green
            "#0000AA",  # Dark blue
            "#AA0000",  # Dark red
            "#AA00AA",  # Purple
            "#00AAAA",  # Teal
            "#AA7700",  # Brown
            "#000000",  # Black
        ]
        
        # German month names with umlauts
        self.month_names = {
            1: "Januar", 2: "Februar", 3: "März", 4: "April",
            5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
            9: "September", 10: "Oktober", 11: "November", 12: "Dezember"
        }
        
        logger.info(f"Calendar visualizer initialized with output path: {self.output_path}")
    
    def set_colors(self, color_dict: Dict[str, str]) -> None:
        """
        Set custom colors for visualization.
        
        Args:
            color_dict: Dictionary mapping day types to color codes.
        """
        self.colors.update(color_dict)
        logger.info(f"Updated visualization colors: {self.colors}")
    
    def create_visualization(self, show: bool = True) -> Dict[str, str]:
        """
        Create the calendar visualization.
        
        Args:
            show: Whether to show the plot window.
            
        Returns:
            Dictionary with paths to generated files.
        """
        year = self.calendar_manager.year
        vacation_config = self.calendar_manager.vacation_config
        
        # Calculate statistics
        stats = self.calendar_manager.calculate_statistics()
        
        # Use specific paper size for better printing
        # A4 paper size in inches (8.27 × 11.69)
        fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
        
        # Create a grid with 5 rows, 3 columns
        # First 4 rows for months, last row for stats
        grid = plt.GridSpec(5, 3, height_ratios=[4, 4, 4, 4, 1.5], 
                            left=0.03, right=0.97, bottom=0.08, top=0.92,
                            wspace=0.05, hspace=0.15)
        
        # Add title with year, region, and name
        fig.suptitle(
            f"Vacationplan {year} - {vacation_config['region']}\n"
            f"{vacation_config['firstName']} {vacation_config['lastName']}",
            fontsize=14, y=0.98
        )
        
        # Create a visualization for each month (first 4 rows, all columns)
        month_axes = []
        for row in range(4):
            for col in range(3):
                month_idx = row * 3 + col
                if month_idx < 12:  # We have 12 months
                    month = month_idx + 1  # Month numbering starts at 1
                    ax = fig.add_subplot(grid[row, col])
                    month_axes.append(ax)
                    self._visualize_month(year, month, ax)
        
        # Create statistics panel in the bottom row, spanning all columns
        ax_stats = fig.add_subplot(grid[4, :])
        self._visualize_statistics(ax_stats, stats)
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], color=self.colors["holiday"], lw=4, label='Holidays'),
            plt.Line2D([0], [0], color=self.colors["vacation"], lw=4, label='Vacation days'),
            plt.Line2D([0], [0], color=self.colors["weekend"], lw=4, label='Weekends'),
            plt.Line2D([0], [0], color='white', lw=0, markerfacecolor='white', marker='s', 
                      markeredgewidth=2, markeredgecolor='black', markersize=10, label='Vacation blocks have colored borders')
        ]
        fig.legend(
            handles=legend_elements,
            loc='lower center',
            ncol=4,
            fontsize=9,
            frameon=False,
            bbox_to_anchor=(0.5, 0.02)
        )
        
        # Generate filenames
        basename = f"vacation_{year}_{vacation_config['firstName']}_{vacation_config['lastName']}"
        png_filename = os.path.join(self.output_path, f"{basename}.png")
        pdf_filename = os.path.join(self.output_path, f"{basename}.pdf")
        
        # Save figures with basic parameters only
        logger.info(f"Saving PNG visualization to: {png_filename}")
        plt.savefig(png_filename, dpi=300)
        
        logger.info(f"Saving PDF visualization to: {pdf_filename}")
        plt.savefig(pdf_filename)
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close()
        
        return {
            'png': png_filename,
            'pdf': pdf_filename
        }
    
    def _visualize_month(self, year: int, month: int, ax) -> None:
        """
        Create visualization for a specific month.
        
        Args:
            year: Year.
            month: Month number (1-12).
            ax: Matplotlib axis to draw on.
        """
        # Get month calendar
        month_cal = self.calendar_manager.get_monthly_calendar(month)
        
        # Set title using German month names with proper encoding
        ax.set_title(self.month_names[month], fontsize=14, y=0.98)
        ax.axis("off")
        
        # Prepare table data and colors
        table_data = []
        cell_colors = []
        
        # Create data structure to track vacation blocks for border coloring
        vacation_block_cells = {}  # Maps block_id to list of cell positions (row, col)
        
        for row_idx, week in enumerate(month_cal):
            row = []
            row_colors = []
            
            for col_idx, day in enumerate(week):
                day_info = self.calendar_manager.get_day_info(year, month, day)
                
                # Add to table data
                row.append(day_info['display'])
                row_colors.append(self.colors[day_info['type']])
                
                # Track vacation block cells for later border coloring
                if day_info['vacation_block'] is not None:
                    block_id = day_info['vacation_block']
                    if block_id not in vacation_block_cells:
                        vacation_block_cells[block_id] = []
                    vacation_block_cells[block_id].append((row_idx, col_idx))
                
            table_data.append(row)
            cell_colors.append(row_colors)
        
        # Create the table with optimal size for printing
        table = ax.table(
            cellText=table_data,
            cellLoc='center',
            cellColours=np.array(cell_colors),
            loc='center',
            colWidths=[0.13] * 7
        )
        
        # Format the table
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.2)
        
        # Add borders to vacation block cells
        for block_id, cells in vacation_block_cells.items():
            # Get border color for this block (cycle through colors)
            border_color = self.border_colors[block_id % len(self.border_colors)]
            
            # Add border to each cell in this vacation block
            for row_idx, col_idx in cells:
                cell = table[(row_idx, col_idx)]
                cell.set_edgecolor(border_color)
                cell.set_linewidth(2.0)
                
    def _visualize_statistics(self, ax, stats: Dict[str, Any]) -> None:
        """
        Create visualization for statistics.
        
        Args:
            ax: Matplotlib axis to draw on.
            stats: Dictionary with statistics.
        """
        ax.axis('off')
        
        # Extract statistics
        total_days = stats['total_days']
        workdays = stats['workdays']
        weekends = stats['weekends']
        holidays = stats['holidays']
        vacation_days = stats['vacation_days']
        vacation_workdays = stats['vacation_workdays']
        days_off = stats['days_off']
        days_at_work = stats['days_at_work']
        
        # Calculate percentages
        workdays_percent = workdays / total_days * 100
        weekends_percent = weekends / total_days * 100
        holidays_percent = holidays / total_days * 100
        vacation_workdays_percent = vacation_workdays / total_days * 100
        days_off_percent = days_off / total_days * 100
        days_at_work_percent = days_at_work / total_days * 100
        
        # Prepare statistics text
        stats_text = (
            f"Year Summary:\n"
            f"Total days: {total_days}\n"
            f"Workdays: {workdays} ({workdays_percent:.1f}%)\n"
            f"Weekends: {weekends} ({weekends_percent:.1f}%)\n"
            f"Holidays: {holidays} ({holidays_percent:.1f}%)\n"
            f"Vacation days (workdays only): {vacation_workdays} ({vacation_workdays_percent:.1f}%)\n"
            f"Total days off: {days_off} ({days_off_percent:.1f}%)\n"
            f"Total days at work: {days_at_work} ({days_at_work_percent:.1f}%)"
        )
        
        # Add vacation blocks statistics
        vacation_blocks_text = "Vacation Blocks:\n"
        for block in stats['vacation_blocks']:
            # Replace common German terms that might have umlauts
            description = block['description']
            description = description.replace('Brucke', 'Brücke')
            description = description.replace('Auffahrtsbrucke', 'Auffahrtsbrücke')
            description = description.replace('Mai-Brucke', 'Mai-Brücke')
            description = description.replace('Marz', 'März')
            
            vacation_blocks_text += (
                f"• {description}: {block['start']} to {block['end']} - "
                f"{block['workdays']} workdays ({block['total_days']} total days)\n"
            )
        
        # Create a 2-column layout with proper text positioning
        left_col = ax.text(
            0.05, 0.5, stats_text,
            verticalalignment='center',
            horizontalalignment='left',
            transform=ax.transAxes,
            fontsize=9
        )
        
        right_col = ax.text(
            0.55, 0.5, vacation_blocks_text,
            verticalalignment='center',
            horizontalalignment='left',
            transform=ax.transAxes,
            fontsize=9
        )
