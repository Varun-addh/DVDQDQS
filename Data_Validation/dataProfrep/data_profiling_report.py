import pandas as pd


def generate_statistics(df):
    """Generate detailed statistics for each column."""
    report = []
    

    for column in df.columns:
        data = df[column]
        n_rows = len(data)

        stats = {
            "Column Name": column,
            "Total Rows": n_rows,
            "Missing": data.isnull().sum(),
            "Missing (%)": (data.isnull().sum() / n_rows) * 100,
            "Duplicate": data.duplicated().sum(),
            "Duplicate (%)": (data.duplicated().sum() / n_rows) * 100,
            "Unique": data.nunique(),
            "Unique (%)": (data.nunique() / n_rows) * 100,
        }
        report.append(stats)

    return report


def generate_combined_report(df, detailed_report_content, quality_summary_content, output_path="combined_report.html"):
    """Generate a combined data quality report with individual sections for each column."""
    try:
       
        column_statistics = generate_statistics(df)

        dropdown_html = "<select id='column-select' onchange='showColumnStats(this.value)'>"
        column_html = ""
        for stats in column_statistics:
            dropdown_html += f"<option value='{stats['Column Name']}'>{stats['Column Name']}</option>"
            column_html += f"""
            <div id='{stats['Column Name']}-stats' class='column-container' style='display:none;'>
                <h3>{stats['Column Name']}</h3>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Rows</td><td>{stats['Total Rows']}</td></tr>
                    <tr><td>Missing Values</td><td>{stats['Missing']} ({stats['Missing (%)']:.2f}%)</td></tr>
                    <tr><td>Duplicate Values</td><td>{stats['Duplicate']} ({stats['Duplicate (%)']:.2f}%)</td></tr>
                    <tr><td>Unique Values</td><td>{stats['Unique']} ({stats['Unique (%)']:.2f}%)</td></tr>
                </table>
            </div>
            """
        dropdown_html += "</select>"

        final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detailed Data Quality Report</title>
    <link rel="stylesheet" href="Data_Validation\\dataProfrep\\Dpr.css">
    
    <script>
        function showSection(sectionId) {{
            const sections = document.querySelectorAll('.section-content');
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById(sectionId).classList.add('active');
        }}
        function showColumnStats(columnId) {{
            const columns = document.querySelectorAll('.column-container');
            columns.forEach(col => col.style.display = 'none');
            document.getElementById(columnId + '-stats').style.display = 'block';
        }}
    </script>
</head>
<body>
    <div class="navbar">
        <a onclick="showSection('detailed-report')">Detailed Report</a>
        <a onclick="showSection('quality-summary')">Quality Summary</a>
        <a onclick="showSection('column-statistics')">Column Statistics</a>
    </div>
    <div class="content">
        <div id="detailed-report" class="section-content active">
            <div>{detailed_report_content}</div>
        </div>
        <div id="quality-summary" class="section-content">
            <div>{quality_summary_content}</div>
        </div>
        <div id="column-statistics" class="section-content">
            <h2>Column Statistics</h2>
            {dropdown_html}
            {column_html}
        </div>
    </div>
</body>
</html>
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        print(f"Detailed report saved successfully to {output_path}")
    except Exception as e:
        print(f"Error generating combined report: {e}")
