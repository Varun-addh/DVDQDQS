from ydata_profiling import ProfileReport
from ydata_profiling.config import Settings
import os

def generate_ydata_profiling_report(df, detailed_report_content, quality_summary_content, output_path="data_quality_report.html"):
    try:
        # Configure the YData Profiling settings
        config = Settings(
            missing_diagrams={"bar": False, "matrix": False, "heatmap": False}
        )
        profile = ProfileReport(df, title="YData Profiling Report", explorative=True, config=config)

        # Save the profiling report to a temporary file
        temp_path = "temp_report.html"
        profile.to_file(temp_path)

        # Extract only the body of the report
        with open(temp_path, "r", encoding="utf-8") as f:
            report_html = f.read()

        start_body = report_html.find("<body>") + len("<body>")
        end_body = report_html.find("</body>")
        profile_body_content = report_html[start_body:end_body]

        # Custom HTML structure with navigation and content sections
        custom_sections = f"""
<link rel="stylesheet" href="Data_Validation\\dataProfrep\\Dpr.css">

<!-- Navbar -->
<div class="navbar">
    <a href="#" onclick="showSection('detailed-report')"><i class="fas fa-list"></i>Data Quality Report</a>
    <a href="#" onclick="showSection('quality-summary')"><i class="fas fa-check-circle"></i> Quality Summary</a>
    <a href="#" onclick="showSection('ydata-profiling')"><i class="fas fa-chart-pie"></i> Data Profiling Report</a>
</div>

<!-- Sections -->
<div id="detailed-report" class="section-content active">
    <div class="detailed-report-content">
        {detailed_report_content}
    </div>
</div>

<div id="quality-summary" class="section-content">
    <div class="quality-summary">{quality_summary_content}</div>
</div>

<div id="ydata-profiling" class="section-content">
    <div class="profile-report-container">
        {profile_body_content}
    </div>
</div>

<script>
    function showSection(sectionId) {{
        const sections = document.querySelectorAll('.section-content');
        sections.forEach(section => section.classList.remove('active'));
        document.getElementById(sectionId).classList.add('active');
    }}
</script>

<script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
"""

        # Replace the body content of the temporary report with the custom sections
        final_html = report_html[:start_body] + custom_sections + report_html[end_body:]

        # Save the final report to the specified output path
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        # Remove the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        print(f"Report saved successfully to {output_path}")
    except Exception as e:
        print(f"Error generating YData profiling report: {e}")   