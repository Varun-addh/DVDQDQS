import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

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

# Function to generate the combined report
def generate_combined_report(df, detailed_report_content, quality_summary_content, output_path="combined_report.html"):
    try:
        # Add serial numbers (S.No) to the DataFrame
        df.insert(0, 'S.No', range(1, len(df) + 1))

        # Generate statistics
        column_statistics = generate_statistics(df)

        # Generate HTML for the first and last 10 rows of the dataset
        first_10_rows_html = df.head(10).to_html(index=False)
        last_10_rows_html = df.tail(10).to_html(index=False)

        # Correlation visualization
        correlation_visualization_html = ""
        numeric_columns = df.select_dtypes(include=['int64', 'float64'])

        if numeric_columns.shape[1] > 1:
            # Compute correlation matrix
            corr_matrix = numeric_columns.corr()

            fig, ax = plt.subplots(figsize=(10, 6))

            sns.heatmap(
                corr_matrix, 
                annot=True, 
                cmap='YlGnBu', 
                fmt=".2f", 
                linewidths=0.5, 
                ax=ax,
                cbar_kws={"shrink": 0.8}
            )
            ax.set_title('Correlation Matrix Heatmap', fontsize=18, fontweight='bold')
            plt.tight_layout()

            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", dpi=100)
            buffer.seek(0)
            heatmap_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close()

            pairplot_fig = sns.pairplot(
                numeric_columns,
                diag_kind='kde',
                kind='reg',
                plot_kws={'line_kws': {'color': 'red'}, 'scatter_kws': {'alpha': 0.6}},
                palette='husl'
            )
            pairplot_fig.fig.suptitle("Pair Plot of Numeric Columns", fontsize=18, fontweight="bold")
            pairplot_fig.fig.subplots_adjust(top=0.95)  

            buffer = io.BytesIO()
            pairplot_fig.fig.savefig(buffer, format="png", dpi=100)
            buffer.seek(0)
            pairplot_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close()

            correlation_visualization_html = f"""
<div class='correlation-section' style="font-family: Arial, sans-serif; color: #333; margin: 20px 0;">
    <h3 style="text-align: center; font-size: 1.8em; margin-bottom: 20px; border-bottom: 2px solid #ccc; padding-bottom: 10px;">Correlation Analysis</h3>
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px;">
        <div style="flex: 1; min-width: 300px; background: #fff; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); border-radius: 10px; overflow: hidden; border: 1px solid #eaeaea;">
            <h4 style="text-align: center; background-color: #fff; color: #333; margin: 0; padding: 15px 0; font-size: 1.2em; font-weight: bold; border-bottom: 1px solid #eaeaea;">Heatmap</h4>
            <img src="data:image/png;base64,{heatmap_img}" alt="Correlation Heatmap" style="width: 100%; height: auto; display: block;">
        </div>
        <div style="flex: 1; min-width: 300px; background: #fff; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); border-radius: 10px; overflow: hidden; border: 1px solid #eaeaea;">
            <h4 style="text-align: center; background-color: #fff; color: #333; margin: 0; padding: 15px 0; font-size: 1.2em; font-weight: bold; border-bottom: 1px solid #eaeaea;">Pair Plot</h4>
            <img src="data:image/png;base64,{pairplot_img}" alt="Pair Plot" style="width: 100%; height: auto; display: block;">
        </div>
    </div>
</div>
"""


        # Generate dropdown menu
        dropdown_html = """
        <select id='column-select' onchange='filterColumnStats(this.value)'>
            <option value='all' selected>All Columns</option>
        """
        for stats in column_statistics:
            dropdown_html += f"<option value='{stats['Column Name']}'>{stats['Column Name']}</option>"
        dropdown_html += "</select>"

        # Generate HTML for column statistics
        column_html = ""
        for stats in column_statistics:
            column_html += f"""
            <div class='column-container' data-column='{stats["Column Name"]}'>
                <h3>{stats["Column Name"]}</h3>
                <table class="stats-table">
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Missing Cells</td><td>{stats['Missing Cells']} ({stats['Missing Cells (%)']})</td></tr>
                    <tr><td>Duplicate Values</td><td>{stats['Duplicate Values']} ({stats['Duplicate Values (%)']})</td></tr>
                    <tr><td>Distinct Values</td><td>{stats['Distinct Values']} ({stats['Distinct Values (%)']})</td></tr>
                    <tr><td>Memory Size</td><td>{stats['Memory Size']}</td></tr>
                </table>
            </div>
            """

        column_statistics_html = f"""
        <div>
            <button onclick="showRows('first-rows')">First Rows</button>
            <button onclick="showRows('last-rows')">Last Rows</button>
        </div>
        <div id='first-rows' class='row-table' style='display:none; overflow-x:auto;'>
            <div class="scrollable-table">
                {first_10_rows_html}
            </div>
        </div>
        <div id='last-rows' class='row-table' style='display:none; overflow-x:auto;'>
            <div class="scrollable-table">
                {last_10_rows_html}
            </div>
        </div>
        {dropdown_html}
        {column_html}
        {correlation_visualization_html}
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
        function showRows(rowId) {{
            const allTables = document.querySelectorAll('.row-table');
            allTables.forEach(table => table.style.display = 'none');
            document.getElementById(rowId).style.display = 'block';
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
            {column_statistics_html}
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