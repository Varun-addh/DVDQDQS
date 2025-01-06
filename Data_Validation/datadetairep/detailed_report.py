import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import io
import base64

# Function to dynamically represent memory usage
def format_memory_size(bytes_size):
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']
    index = 0
    while bytes_size >= 1024 and index < len(units) - 1:
        bytes_size /= 1024
        index += 1
    return f"{bytes_size:.2f} {units[index]}"


def generate_alerts(df):
    alerts = []

    # Missing Values
    missing_values = df.isnull().sum()
    for col, count in missing_values.items():
        if count > 0:
            percentage = (count / len(df)) * 100
            alerts.append(f"ALERT: '{col}' has {count} missing values ({percentage:.2f}%).")

    #Duplicate Rows 
    duplicate_rows = df.duplicated().sum()
    if duplicate_rows > 0:
        alerts.append(f"ALERT: Dataset contains {duplicate_rows} duplicate rows ({(duplicate_rows / len(df)) * 100:.2f}%).")

    #High Correlation
    correlation_matrix = df.corr(numeric_only=True)
    threshold = 0.85 
    overall_correlations = {}
    for col1 in correlation_matrix.columns:
        for col2 in correlation_matrix.columns:
            if col1 != col2 and abs(correlation_matrix.loc[col1, col2]) > threshold:
                alerts.append(
                    f"ALERT: '{col1}' is highly correlated with '{col2}' (correlation: {correlation_matrix.loc[col1, col2]:.2f})."
                )
                if col1 not in overall_correlations:
                    overall_correlations[col1] = 0
                if col2 not in overall_correlations:
                    overall_correlations[col2] = 0
                overall_correlations[col1] += 1
                overall_correlations[col2] += 1

    for col, count in overall_correlations.items():
        if count > 1:  
            alerts.append(f"ALERT: '{col}' is overall highly correlated with multiple columns ({count} columns).")

    #Negative Values
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    for col in numeric_columns:
        if (df[col] < 0).any():
            negative_count = (df[col] < 0).sum()
            alerts.append(f"ALERT: '{col}' contains {negative_count} negative values.")

    # Low Variance
    for col in df.columns: 
        if df[col].nunique() == 1:
            alerts.append(f"ALERT: '{col}' has low variance, with only one unique value across the dataset.")
        elif df[col].nunique() < 5 and df[col].dtype == 'object': 
            alerts.append(f"ALERT: '{col}' has low cardinality (only {df[col].nunique()} unique values).") 

    # Unique Value Columns
    for col in df.columns:
        try:
            # Handle empty or all-null columns
            if df[col].isnull().all():
                alerts.append(f"ALERT: '{col}' is entirely empty or contains only missing values.")
                continue

            # Handle numeric, categorical, and mixed-type columns
            unique_count = df[col].nunique(dropna=True)  # Exclude NaNs from unique count
            total_count = len(df[col])

            if unique_count == total_count:
                alerts.append(f"ALERT: '{col}' has unique values across all rows (unique distribution).")
            elif unique_count > total_count * 0.95:  # Mostly unique values
                alerts.append(f"ALERT: '{col}' is nearly unique ({unique_count} unique values, {total_count - unique_count} duplicates).")
        except Exception as e:
            # Log any issues with a column that cannot be processed
            alerts.append(f"WARNING: Could not process column '{col}' due to {str(e)}.")

    # Outliers (using IQR) 
    for col in numeric_columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        if len(outliers) > 0:
            alerts.append(f"ALERT: '{col}' has {len(outliers)} potential outliers.")

    #Skewness and Kurtosis
    for col in numeric_columns:
        skewness = df[col].skew()
        kurtosis = df[col].kurtosis()
        if abs(skewness) > 1:  # Threshold for significant skewness
            alerts.append(f"ALERT: '{col}' is significantly skewed (skewness: {skewness:.2f}).")
        if abs(kurtosis) > 3:  # Threshold for significant kurtosis
            alerts.append(f"ALERT: '{col}' has high kurtosis (kurtosis: {kurtosis:.2f}).")

    return alerts


def generate_detailed_report(df, detailed_scores_df, overall_score):
    try:
        # Step 1: Calculate Dataset Statistics and Variable Types
        dataset_statistics = {
            "Number of Rows": len(df),
            "Number of Columns": df.shape[1],
            "Missing Cells": df.isnull().sum().sum(),
            "Missing Cells (%)": f"{(df.isnull().sum().sum() / (len(df) * df.shape[1])) * 100:.2f}%",  # Missing cells percentage
            "Unique Values": len(pd.unique(df.values.ravel())),  # Unique values in the dataset
            "Unique Values (%)": f"{(len(pd.unique(df.values.ravel())) / (len(df) * df.shape[1])) * 100:.2f}%",  # Unique values percentage
            "Duplicate Rows": df.duplicated().sum(),
            "Duplicate Rows (%)": f"{(df.duplicated().sum() / len(df)) * 100:.2f}%",  # Duplicate rows percentage
            "Total Memory Usage": format_memory_size(df.memory_usage(deep=True).sum())  # Memory usage
        }

        variable_types = {
            "Text": sum(df.dtypes == 'object'),
            "Categorical": sum(df.dtypes == 'category'),
            "Numeric": sum(df.dtypes == 'int64') + sum(df.dtypes == 'float64'),
            "Boolean": sum(df.dtypes == 'bool'),
            "Datetime": sum(df.dtypes == 'datetime64[ns]')
        }

        metrics = ['Completeness', 'Timeliness', 'Validity', 'Accuracy', 'Uniqueness', 'Consistency']

        # Step 3: Initialize HTML Content
        html_content = []

        # Add external CSS file
        html_content.append("""<link rel="stylesheet" type="text/css" href="Data_Validation\\datadetairep\\Gde.css">""")

        # Add navigation bar
        html_content.append("""<div class="navigation-bar"><ul>
            <li><a href="#dataset-statistics">Dataset Statistics</a></li>
            <li><a href="#detailed-scores">Column-Wise Quality Scores</a></li>
            <li><a href="#average-scores">Average Quality Scores</a></li>
            <li><a href="#missing-values">Missing Values Analysis</a></li>
            <li><a href="#visualizations">Visualizations</a></li>
        </ul></div>""")

        # Generate alerts
        alerts = generate_alerts(df)
        alerts_count = len(alerts)

        # Overview and Alerts Buttons Section
        html_content.append(f"""
        <div class="button-container" style="display: flex; gap: 10px; padding: 10px;">
            <button class="overview-button" onclick="toggleOverview()" 
                    style="padding: 10px 20px; font-size: 14px; border-radius: 5px; border: none; background-color: #3498db; color: white; cursor: pointer;">
                Overview
            </button>
            <button id="alerts-button" class="alerts-button" onclick="toggleAlerts()" 
                    style="padding: 10px 20px; font-size: 14px; border-radius: 5px; border: none; background-color: #e74c3c; color: white; cursor: pointer;">
                Alerts({alerts_count})
            </button>
        </div>
        """)

        html_content.append("""
<div id="alerts-section" style="display: none; padding: 30px; background: linear-gradient(145deg, #fdfbfb, #ebedee); border-radius: 20px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1), 0 -5px 15px rgba(255, 255, 255, 0.6); font-family: 'Poppins', sans-serif; color: #34495e;">
    <h2 style="text-align: center; color: #2c3e50; font-weight: 700; margin-bottom: 25px; letter-spacing: 1.2px; text-transform: uppercase;">🚨 Dataset Alerts</h2>
    <div id="alerts-content" style="padding: 20px; border-top: 2px solid rgba(0, 0, 0, 0.1);">
        <p style="text-align: center; color: rgba(44, 62, 80, 0.6); font-style: italic;">Scanning for alerts...</p>
    </div>
</div>

""")

        alerts_js = ", ".join([f'"{alert}"' for alert in alerts])

        # JavaScript for toggling sections and displaying alerts
        html_content.append(f"""
        <script>
            function toggleOverview() {{
                const sections = ['dataset-statistics', 'detailed-scores', 'average-scores', 'missing-values', 'visualizations','overall-score'];
                sections.forEach(section => {{
                    const elem = document.getElementById(section);
                    if (elem) elem.style.display = 'block';
                }});
                document.getElementById('alerts-section').style.display = 'none';
            }}

            function toggleAlerts() {{
                const datasetStatistics = document.getElementById('dataset-statistics');
                const detailedScores = document.getElementById('detailed-scores');
                const averageScores = document.getElementById('average-scores');
                const missingValues = document.getElementById('missing-values');
                const visualizations = document.getElementById('visualizations');
                const alertsSection = document.getElementById('alerts-section');
                const overallScore = document.getElementById('overall-score');

                if (datasetStatistics) datasetStatistics.style.display = 'none';
                if (detailedScores) detailedScores.style.display = 'none';
                if (averageScores) averageScores.style.display = 'none';
                if (missingValues) missingValues.style.display = 'none';
                if (visualizations) visualizations.style.display = 'none';
                if(overallScore) overallScore.style.display = 'none';
                if (alertsSection) {{
                    alertsSection.style.display = 'block';

                    const alertsContent = document.getElementById('alerts-content');
                    const alerts = [{alerts_js}];

                    if (alerts.length > 0) {{
                        let alertList = '<ul>';
                        alerts.forEach(alert => {{
                            alertList += `<li>${{alert}}</li>`; 
                        }});
                        alertList += '</ul>';
                        alertsContent.innerHTML = alertList;
                    }} else {{
                        alertsContent.innerHTML = '<p>No alerts found for this dataset.</p>';
                    }}
                }}
            }}
        </script>
        """)


        # Step 4: Dataset Statistics and Variable Types Section
        html_content.append("""<div id='dataset-statistics' class='statistics-container' style="display: flex; justify-content: space-between; gap: 20px; padding: 20px; background-color: #f4f6f9; max-width: 1200px; margin: 20px auto; border-radius: 12px; box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);">
             <div class='statistics-section' style="flex: 1; padding: 20px; background-color: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); transition: transform 0.2s ease, box-shadow 0.2s ease;">
                 <h6 class='section-title' style="font-size: 1.2em; font-weight: bold; color: #2c3e50; margin-bottom: 20px; border-bottom: 3px solid #3498db; padding-bottom: 10px;">Dataset Statistics</h6>
                 <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">""")

        for key, value in dataset_statistics.items():
            if isinstance(value, dict):  # Handle dictionary values (Unique Values and Data Types)
                html_content.append(f"<tr><td colspan='2' style='padding: 8px; font-size: 1.0em; color: #34495e; text-align: left; font-weight: 500;'>{key}</td></tr>")
                for sub_key, sub_value in value.items():
                    html_content.append(f"<tr><td style='padding: 8px; font-size: 1.0em; color: #34495e; text-align: left; font-weight: 500;'>{sub_key}</td><td style='padding: 8px; font-size: 1.0em; color: #7f8c8d; text-align: left;'>{sub_value}</td></tr>")
            else:
                html_content.append(f"<tr style='border-bottom: 1px solid #e9ecef; transition: background-color 0.2s ease;'><td style='padding: 8px; font-size: 1.0em; color: #34495e; text-align: left; font-weight: 500;'>{key}</td><td style='padding: 8px; font-size: 1.0em; color: #7f8c8d; text-align: left;'>{value}</td></tr>")

        html_content.append("""</table></div>
             <div class='statistics-section' style="flex: 1; padding: 20px; background-color: #fff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); transition: transform 0.2s ease, box-shadow 0.2s ease;">
                 <h6 class='section-title' style="font-size: 1.2em; font-weight: bold; color: #2c3e50; margin-bottom: 20px; border-bottom: 3px solid #2ecc71; padding-bottom: 10px;">Variable Types</h6>
                 <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">""")

        for key, value in variable_types.items():
            html_content.append(f"<tr style='border-bottom: 1px solid #e9ecef; transition: background-color 0.2s ease;'><td style='padding: 8px; font-size: 1.0em; color: #34495e; text-align: left; font-weight: 500;'>{key}</td><td style='padding: 8px; font-size: 1.0em; color: #7f8c8d; text-align: left;'>{value}</td></tr>")

        html_content.append("""</table></div></div>
         <style>
             .statistics-section:hover { transform: scale(1.02); box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15); }
             tr:hover { background-color: #f1f5f8; }
         </style>""")


        html_content.append(f"""
    <div id="overall-score" class="overall-score-container">
        <p class="overall-score-label">Overall Data Quality Score</p>
        <div class="overall-score-circle-container">
            <svg width="120" height="120" class="circle">
                <circle cx="60" cy="60" r="50" stroke="lightgray" stroke-width="6"></circle>
                <circle cx="60" cy="60" r="50" stroke="yellow" stroke-width="6" stroke-dasharray="314" stroke-dashoffset="{314 - (314 * overall_score) / 100}" class="progress-circle"></circle>
            </svg>
            <div class="score-text">{overall_score:.2f}%</div>
        </div>
    </div>
""")   

        # Step 4: Detailed Column-Wise Quality Scores Section
        html_content.append("<div id='detailed-scores'><h3 class='section-title'>Detailed Column-Wise Quality Scores</h3>")
        html_content.append("<table>")
        html_content.append("<tr><th>Column</th>" + "".join(f"<th>{metric}</th>" for metric in metrics) + "</tr>")
        for col, scores in detailed_scores_df.iterrows():
            html_content.append("<tr>" + f"<td>{col}</td>" + "".join(f"<td>{scores.get(metric, 0):.2f}%</td>" for metric in metrics) + "</tr>")
        html_content.append("</table></div>")

        # Step 5: Overall Average Quality Scores Section
        html_content.append("<div id='average-scores'><h3 class='section-title'>Overall Average Quality Scores</h3>")
        html_content.append("<table>")
        html_content.append("<tr><th>Metric</th><th>Average Score (%)</th></tr>")
        for metric in metrics:
            overall_metric_score = detailed_scores_df[metric].mean()
            html_content.append(f"<tr><td>{metric}</td><td>{overall_metric_score:.2f}%</td></tr>")
        html_content.append("</table></div>")

        # Step 6: Move Missing Values Analysis Section here (after Average Scores)
        missing_data = df.isnull().sum()
        present_data = df.notnull().sum()
        features = df.columns

        plt.figure(figsize=(14, 10))  
        bar_width = 0.8

        bar1 = plt.bar(features, present_data, color="#3498db", label="Present Values", width=bar_width)
        bar2 = plt.bar(features, missing_data, bottom=present_data, color="#e74c3c", label="Missing Values", width=bar_width)

        for bar in bar1:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height / 2,
                f'{int(height)}',
                ha='center',
                va='center',
                fontsize=12,
                fontweight='bold',
                color='white',
                bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.3')
            )

        for bar in bar2:
            height = bar.get_height()
            if height > 0:
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + height / 2,
                    f'{int(height)}',
                    ha='center',
                    va='center',
                    fontsize=12,
                    fontweight='bold',
                    color='white',
                    bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.3')
                )

        plt.xlabel("Columns", fontsize=14)
        plt.ylabel("Number of values", fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.legend(loc="upper right", fontsize=12)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100)
        buffer.seek(0)
        missing_values_chart = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()
        plt.close()

        html_content.append(f"""<div id="missing-values" class="missing-values-container">
            <h3 class="section-title">Missing Values Analysis</h3>
            <p class="section-description">The chart below visualizes the number of present and missing values for each feature in the dataset.</p>
            <div class="chart-wrapper">
                <img src="data:image/png;base64,{missing_values_chart}" alt="Missing Values Chart" class="missing-values-chart">
            </div>
        </div>""")

        html_content.append("""<div id="visualizations">
            <h3 class='section-title'>Select a Column to View Visualizations</h3>
            <select id="column-select" onchange="showChart(this.value)">
                <option value="">Select a Column</option>""")
 
        charts_data = {}
        for col, scores in detailed_scores_df.iterrows():
            html_content.append(f"<option value='{col}'>{col}</option>")
            values = [scores.get(metric, 0) for metric in metrics]
 
            # Generate Bar Chart
            plt.figure(figsize=(18, 12))  

            plt.bar(metrics, values, color='#3498db')
            plt.title(f"{col}")
            plt.xticks(rotation=45)
            plt.tight_layout(rect=[0, 0, 1, 0.96]) 

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            bar_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close()
 
           
            plt.figure(figsize=(18, 12))  

            sns.heatmap(np.array(values).reshape(1, -1), annot=True, fmt=".2f", cmap="coolwarm", cbar=False, xticklabels=metrics, yticklabels=[col])
            plt.title(f"{col}")
            plt.tight_layout(rect=[0, 0, 1, 0.96])  

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            heatmap = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close()
 
            charts_data[col] = {'bar_chart': bar_chart, 'heatmap': heatmap}
 
        html_content.append("</select></div>")
 
        # Charts Section
        html_content.append("<div class='chart-container' id='chart-container'>")
        for col, charts in charts_data.items():
            html_content.append(f"""<div id="{col}-charts" style="display:none;" class="charts-side-by-side">
                <div class="chart">
                    <h3>Bar Chart</h3>
                    <img src='data:image/png;base64,{charts['bar_chart']}' alt='{col} Bar Chart'>
                </div>
                <div class="chart">
                    <h3>Heatmap</h3>
                    <img src='data:image/png;base64,{charts['heatmap']}' alt='{col} Heatmap'>
                </div>
            </div>""")
        html_content.append("</div>")  # End Chart Container
 
        html_content.append("""<script>
            function showChart(column) {
                const charts = document.querySelectorAll("[id$='-charts']");
                charts.forEach(chart => chart.style.display = 'none');
               
                if (column) {
                    const selectedChart = document.getElementById(`${column}-charts`);
                    document.getElementById("chart-container").style.display = 'block';
                    selectedChart.style.display = 'flex';
                } else {
                    document.getElementById("chart-container").style.display = 'none';
                }
            }
        </script>""")

        
 
        return "\n".join(html_content)
 
    except Exception as e:
        print(f"Error generating report: {e}")
        return ""