from Data_Validation.dataloD.data_loader import load_dataset
from Data_Validation.dataquame.data_quality_metrics import calculate_scores, overall_quality_score
from Data_Validation.datadetairep.detailed_report import generate_detailed_report
from Data_Validation.dataquaclms.quality_summary import generate_quality_summary
from Data_Validation.dataProfrep.data_profiling_report import generate_combined_report
import matplotlib
import io
import requests
import zipfile
# Ensure matplotlib works in headless environments
matplotlib.use("Agg")

if __name__ == "__main__":
    try:
        if(1):
            response = requests.get("https://www.kaggle.com/api/v1/datasets/download/dongrelaxman/amazon-reviews-dataset")
            zf = zipfile.ZipFile(io.BytesIO(response.content))
            zf.extractall("Data_Validation\\Ds'S")
        # Step 1: Load the datasets
        dataset_path = "Data_Validation\\Ds'S\\amazon_delivery - Copy.csv"
        dataset_path2 = "Data_Validation\\Ds'S\\amazon_delivery 1.csv"
        df = load_dataset(dataset_path)
        df2 = load_dataset(dataset_path2)

        # Validate if the datasets are loaded properly
        if df is None or df.empty:
            raise ValueError(f"The dataset at {dataset_path} is empty or failed to load. Check the file path and content.")
        if df2 is None or df2.empty:
            raise ValueError(f"The dataset at {dataset_path2} is empty or failed to load. Check the file path and content.")

        # Step 2: Calculate detailed scores for each column
        detailed_scores_df = calculate_scores(df, df2)

        # Step 3: Calculate the overall data quality score
        overall_score = overall_quality_score(detailed_scores_df)

        # Step 4: Generate the detailed report content
        detailed_report_content = generate_detailed_report(df, detailed_scores_df, overall_score)

        # Step 5: Generate the quality summary content
        quality_summary_content = generate_quality_summary(df, detailed_scores_df)

        # Step 6: Generate the combined report with all sections
        output_path = "combined_data_quality_report.html"
        generate_combined_report(df, detailed_report_content, quality_summary_content,output_path)

        print(f"Data quality report generated successfully and saved as '{output_path}'!")

    except FileNotFoundError as e:
        print(f"Error: {e}. Check if the file paths '{dataset_path}' and '{dataset_path2}' exist.")
    except Exception as e:
        print(f"An error occurred: {e}")