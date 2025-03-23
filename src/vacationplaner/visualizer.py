"""
Visualization module for VacationPlaner.
Handles creating calendar visualizations.
"""

import os
import calendar
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional
import logging
from .calendar_manager import CalendarManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
            "holiday": "#FFDDC1",  # Light orange
            "vacation": "#C1FFD7",  # Light green
            "weekend": "#C1D4FF",   # Light blue
            "weekday": "#FFFFFF",   # White
            "outside": "#FFFFFF"    # White for days outside the month
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
        
        # Create figure with subplots for each month
        months = range(1, 13)
        fig, axes = plt.subplots(4, 3, figsize=(11.7, 8.3))  # A4 landscape
        
        # Add title with year, region, and name
        fig.suptitle(
            f"Vacationplan {year} - {vacation_config['region']}\n"
            f"{vacation_config['firstName']} {vacation_config['lastName']}",
            fontsize=14, y=0.98
        )
        
        # Create a visualization for each month
        for month, ax in zip(months, axes.flatten()):
            self._visualize_month(year, month, ax)
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], color=self.colors["holiday"], lw=4, label='Holidays'),
            plt.Line2D([0], [0], color=self.colors["vacation"], lw=4, label='Vacation days'),
            plt.Line2D([0], [0], color=self.colors["weekend"], lw=4, label='Weekends'),
        ]
        fig.legend(
            handles=legend_elements,
            loc='lower center',
            ncol=3,
            fontsize=10,
            frameon=False
        )
        
        # Adjust layout to prevent legend overlap
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        
        # Generate filenames
        basename = f"vacation_{year}_{vacation_config['firstName']}_{vacation_config['lastName']}"
        png_filename = os.path.join(self.output_path, f"{basename}.png")
        pdf_filename = os.path.join(self.output_path, f"{basename}.pdf")
        
        # Save figures
        logger.info(f"Saving PNG visualization to: {png_filename}")
        plt.savefig(png_filename, dpi=300)
        
        logger.info(f"Saving PDF visualization to: {pdf_filename}")
        plt.savefig(pdf_filename, bbox_inches='tight', orientation='landscape')
        
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
        
        # Set title
        ax.set_title(calendar.month_name[month], fontsize=14, y=0.98)
        ax.axis("off")
        
        # Prepare table data
        table_data = []
        cell_colors = []
        
        for week in month_cal:
            row = []
            row_colors = []
            
            for day in week:
                day_info = self.calendar_manager.get_day_info(year, month, day)
                
                row.append(day_info['display'])
                row_colors.append(self.colors[day_info['type']])
                
            table_data.append(row)
            cell_colors.append(row_colors)
        
        # Create the table
        table = ax.table(
            cellText=table_data,
            cellLoc='center',
            cellColours=np.array(cell_colors),
            loc='center',
            colWidths=[0.12] * 7
        )
        
        # Format the table
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.2)
