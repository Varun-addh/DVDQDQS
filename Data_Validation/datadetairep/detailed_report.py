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

        # Add navigation bar (Updated order)
        html_content.append("""<div class="navigation-bar"><ul>
            <li><a href="#dataset-statistics">Dataset Statistics</a></li>
            <li><a href="#detailed-scores">Column-Wise Quality Scores</a></li>
            <li><a href="#average-scores">Average Quality Scores</a></li>
            <li><a href="#missing-values">Missing Values Analysis</a></li>
            <li><a href="#visualizations">Visualizations</a></li>
        </ul></div>""")
        
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


        html_content.append(f"""<div id="overall-score" class="overall-score-container">
            <p class="overall-score-label">Overall Data Quality Score</p>
            <div class="overall-score-value">{overall_score:.2f}%</div>
        </div>""")
        

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