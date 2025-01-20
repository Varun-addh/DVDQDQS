import pandas as pd
import re

def completeness_score(column):
    """Calculate the completeness score of a column."""
    if len(column) == 0:
        return 0.0  # Return 0% if the column is empty
    return (len(column) - column.isnull().sum()) / len(column) * 100

def uniqueness_score(column):
    """Calculate the uniqueness score of a column."""
    if len(column) == 0:
        return 0.0  # Return 0% if the column is empty
    return column.nunique() / len(column) * 100

def validity_score(column, validation_function=None):
    """Calculate the validity score of a column based on a validation function."""
    if len(column) == 0:
        return 0.0  # Return 0% if the column is empty

    if validation_function is None:
        if pd.api.types.is_numeric_dtype(column):
            validation_function = lambda x: not pd.isna(x)
        elif pd.api.types.is_datetime64_any_dtype(column):
            validation_function = lambda x: not pd.isna(x)
        else:
            validation_function = lambda x: isinstance(x, str) and x.strip() != ""
    
    valid_entries = column.apply(validation_function).sum()
    return valid_entries / len(column) * 100

# def timeliness_score(column, threshold_date):
#     """Calculate the timeliness score of a datetime column."""
#     if pd.api.types.is_datetime64_any_dtype(column):
#         if threshold_date is None:
#             raise ValueError("Threshold date must be provided and cannot be None.")
        
#         threshold_date = pd.to_datetime(threshold_date).tz_localize(None)
#         timely_entries = (column >= threshold_date).sum()
#         return timely_entries / len(column) * 100

#     return 100.0  # If not a datetime column, assume 100% timeliness

def accuracy_score(df, df2, column_name, threshold=None):
    """Calculates the accuracy score between two DataFrames for a specific column."""
    
    # Check if the column exists in both DataFrames
    missing_columns = []
    if column_name not in df.columns:
        missing_columns.append(f"'{column_name}' in the first DataFrame")
    if column_name not in df2.columns:
        missing_columns.append(f"'{column_name}' in the second DataFrame")
    
    if missing_columns:
        raise ValueError(f"Column(s) missing: " + ", ".join(missing_columns))
    
    # Extract the columns to compare
    col1 = df[column_name]
    col2 = df2[column_name]
    
    # Total rows
    total_entries = len(col1)
    
    # Create masks for different cases
    both_missing = col1.isna() & col2.isna()
    non_missing = ~col1.isna() & ~col2.isna()
    mismatched = col1[non_missing] != col2[non_missing]
    
    # Calculate correct entries
    correct_entries = both_missing.sum() + (col1[non_missing] == col2[non_missing]).sum()
    
    # Calculate accuracy percentage
    accuracy_percentage = (correct_entries / total_entries) * 100 if total_entries > 0 else 100
    
    return accuracy_percentage


# def accuracy_score(df, df2, column_name, threshold=None):
#     """Calculates the accuracy score between two DataFrames for a specific column."""
    
#     # Check if the column exists in both DataFrames
#     missing_columns = []
#     if column_name not in df.columns:
#         missing_columns.append(f"'{column_name}' in the first DataFrame")
#     if column_name not in df2.columns:
#         missing_columns.append(f"'{column_name}' in the second DataFrame")
    
#     if missing_columns:
#         raise ValueError(f"Column(s) missing: " + ", ".join(missing_columns))
    
#     # Extract the columns to compare
#     col1 = df[column_name]
#     col2 = df2[column_name]
    
#     # Create a mask for non-missing values in both columns
#     non_missing_mask = ~col1.isna() & ~col2.isna()
    
#     # Count correct matches only for non-missing values
#     correct_entries = (col1[non_missing_mask] == col2[non_missing_mask]).sum()
    
#     # Total entries to consider include non-missing and mismatched entries
#     total_entries = len(col1)
    
#     # Calculate accuracy percentage
#     accuracy_percentage = (correct_entries / total_entries) * 100 if total_entries > 0 else 0
    
#     return accuracy_percentage



def consistency_score(df, df2, column1, column2=None):
    """Calculates the consistency score by comparing two columns."""
    
    if column2 is None:
        column2 = column1  # If column2 is not provided, compare column1 with itself

    # Ensure that both columns exist in their respective DataFrames
    if column1 not in df.columns or column2 not in df2.columns:
        raise ValueError(f"Columns '{column1}' or '{column2}' are not found in their respective DataFrames.")

    # Compare the two columns row by row
    consistency = 0
    total = len(df)

    for i in range(total):
        val1 = df.iloc[i][column1]
        val2 = df2.iloc[i][column2]

        # If both values are NaN, consider them consistent
        if pd.isna(val1) and pd.isna(val2):
            consistency += 1
        # If both values are the same (non-NaN), consider them consistent
        elif val1 == val2:
            consistency += 1
        # If one value is NaN and the other is not, consider it inconsistent
        elif pd.isna(val1) or pd.isna(val2):
            consistency += 0
        # If values are different (and neither are NaN), consider it inconsistent
        else:
            consistency += 0

    # Calculate consistency percentage
    consistency_percentage = (consistency / total) * 100 if total > 0 else 100
    return consistency_percentage

def calculate_scores(df, df2, selected_metrics=None, threshold_date=None):

    if selected_metrics is None:
        selected_metrics = ["Completeness", "Validity", "Uniqueness", "Accuracy", "Consistency"]
    
    if threshold_date is None:
        threshold_date = pd.to_datetime("today")
    
    detailed_scores = {}
    for col in df.columns:
        column_data = df[col]
        column_scores = {}

        if "Completeness" in selected_metrics:
            column_scores["Completeness"] = completeness_score(column_data)

        if "Uniqueness" in selected_metrics:
            column_scores["Uniqueness"] = uniqueness_score(column_data)

        if "Validity" in selected_metrics:
            column_scores["Validity"] = validity_score(
                column_data,
                lambda x: bool(
                    re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", str(x))
                ),
            ) if "email" in col.lower() else 100

        if "Accuracy" in selected_metrics:
            column_scores["Accuracy"] = accuracy_score(df, df2, col)

        if "Consistency" in selected_metrics:
            column_scores["Consistency"] = consistency_score(df, df2, col)

        detailed_scores[col] = column_scores

    scores_df = pd.DataFrame(detailed_scores).T
    return scores_df

def overall_quality_score(scores_df, selected_metrics=None):
    """Calculate the overall quality score based on selected metrics."""
    if selected_metrics is None:
        selected_metrics = scores_df.columns  # Use all metrics if none are specified
    return scores_df[selected_metrics].mean().mean()
