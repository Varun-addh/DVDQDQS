import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Utility to format memory size
def format_memory_size(bytes_size):
    """Format the memory size into KB, MB, GB, or TB based on size."""
    if bytes_size < 1024:
        return f"{bytes_size} Bytes"
    elif bytes_size < 1024 ** 2:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 ** 3:
        return f"{bytes_size / (1024 ** 2):.2f} MB"
    elif bytes_size < 1024 ** 4:
        return f"{bytes_size / (1024 ** 3):.2f} GB"
    else:
        return f"{bytes_size / (1024 ** 4):.2f} TB"

# Function to generate column statistics
def generate_statistics(df):
    """Generate detailed statistics for each column."""
    report = []
    for column in df.columns:
        data = df[column]
        n_rows = len(data)
        distinct_values = data.nunique()
        memory_size = data.memory_usage(deep=True)

        stats = {
            "Column Name": column,
            "Missing Cells": data.isnull().sum(),
            "Missing Cells (%)": f"{(data.isnull().sum() / n_rows) * 100:.2f}%",
            "Duplicate Values": data.duplicated().sum(),
            "Duplicate Values (%)": f"{(data.duplicated().sum() / n_rows) * 100:.2f}%",
            "Distinct Values": distinct_values,
            "Distinct Values (%)": f"{(distinct_values / n_rows) * 100:.2f}%",
            "Memory Size": format_memory_size(memory_size),
        }
        report.append(stats)
    return report

# Function to generate visualizations
def generate_combined_report(df, detailed_report_content, quality_summary_content, output_path="combined_report.html"):
    try:
        # Generate statistics
        column_statistics = generate_statistics(df)

        # Create dropdown menu
        dropdown_html = """
        <select id='column-select' onchange='filterColumnStats(this.value)'>
            <option value='all' selected>All Columns</option>
        """
        for stats in column_statistics:
            dropdown_html += f"<option value='{stats['Column Name']}'>{stats['Column Name']}</option>"
        dropdown_html += "</select>"

        # Create HTML for all columns and individual sections
        column_html = ""
        for stats in column_statistics:
            column_name = stats["Column Name"]

            column_html += f"""
            <div class='column-container' data-column='{column_name}'>
                <h3>{column_name}</h3>
                <table class="stats-table">
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Missing Cells</td><td>{stats['Missing Cells']} ({stats['Missing Cells (%)']})</td></tr>
                    <tr><td>Duplicate Values</td><td>{stats['Duplicate Values']} ({stats['Duplicate Values (%)']})</td></tr>
                    <tr><td>Distinct Values</td><td>{stats['Distinct Values']} ({stats['Distinct Values (%)']})</td></tr>
                    <tr><td>Memory Size</td><td>{stats['Memory Size']}</td></tr>
                </table>
            </div>
            """

        # Final HTML structure
        final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Quality Report</title>
    <link rel="stylesheet" href="Data_Validation\\dataProfrep\\Dpr.css">
    <script>
        function filterColumnStats(selectedValue) {{
            const allContainers = document.querySelectorAll('.column-container');
            if (selectedValue === 'all') {{
                allContainers.forEach(container => container.style.display = 'block');
            }} else {{
                allContainers.forEach(container => {{
                    container.style.display = container.getAttribute('data-column') === selectedValue ? 'block' : 'none';
                }});
            }}
        }}
        function showSection(sectionId) {{
            const sections = document.querySelectorAll('.section-content');
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById(sectionId).classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="navbar">
        <a href="javascript:void(0);" onclick="showSection('detailed-report')">Detailed Report</a>
        <a href="javascript:void(0);" onclick="showSection('quality-summary')">Quality Summary</a>
        <a href="javascript:void(0);" onclick="showSection('column-statistics')">Column Statistics</a>
    </div>
    <div class="content">
        <div id="detailed-report" class="section-content active">
            {detailed_report_content}
        </div>
        <div id="quality-summary" class="section-content">
            {quality_summary_content}
        </div>
        <div id="column-statistics" class="section-content">
            {dropdown_html}
            {column_html}
        </div>
    </div>
</body>
</html>
"""

        # Save the report
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        print(f"Detailed report saved successfully to {output_path}")
    except Exception as e:
        print(f"Error generating combined report: {e}")
