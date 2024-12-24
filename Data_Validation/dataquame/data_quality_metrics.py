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

def timeliness_score(column, threshold_date):
    """Calculate the timeliness score of a datetime column."""
    if pd.api.types.is_datetime64_any_dtype(column):
        if threshold_date is None:
            raise ValueError("Threshold date must be provided and cannot be None.")
        
        threshold_date = pd.to_datetime(threshold_date).tz_localize(None)
        timely_entries = (column >= threshold_date).sum()
        return timely_entries / len(column) * 100

    return 100.0  # If not a datetime column, assume 100% timeliness

def accuracy_score(df, df2, column_name, threshold=None):
    """Calculates the accuracy score between two DataFrames for a specific column."""

    # Check if both columns exist in the respective DataFrames
    if column_name not in df.columns or column_name not in df2.columns:
        raise ValueError(f"Column '{column_name}' not found in both DataFrames.")

    # Handling the case where we compare numeric values with a threshold
    if pd.api.types.is_numeric_dtype(df[column_name]) and threshold is not None:
        correct_entries = (abs(df[column_name] - df2[column_name]) <= threshold).sum()
    else:
        # Compare string or categorical columns directly (ignoring NaN comparisons)
        correct_entries = (df[column_name] == df2[column_name]).sum()

    # Count the total number of non-NaN entries in both columns
    total_entries = len(df[column_name])
    total_valid_entries = len(df[column_name].dropna())

    # Calculate accuracy percentage
    accuracy_percentage = (correct_entries / total_valid_entries) * 100 if total_valid_entries > 0 else 100
    return accuracy_percentage

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

def calculate_scores(df,df2, threshold_date=None, reference_columns=None):
    """Calculates data quality scores for each column in a DataFrame."""
    if threshold_date is None:
        threshold_date = pd.to_datetime("today")

    detailed_scores = {}

    for col in df.columns:
        column_data = df[col]

        # Calculate scores for each column
        column_scores = {
            "Completeness": completeness_score(column_data),
            "Timeliness": timeliness_score(column_data, threshold_date) if pd.api.types.is_datetime64_any_dtype(column_data) else 100,
            "Validity": validity_score(
                column_data,
                lambda x: bool(
                    re.match(
                        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", str(x)
                    )
                ),
            ) if "email" in col.lower() else 100,
            "Accuracy": accuracy_score(df, df2, col,threshold=None),
            "Uniqueness": uniqueness_score(column_data),
            "Consistency": consistency_score(df,df2, col)
        }

        detailed_scores[col] = column_scores

    scores_df = pd.DataFrame(detailed_scores).T
    return scores_df

def overall_quality_score(scores_df):
    """Calculate the overall quality score as the mean of all scores."""
    return scores_df.mean().mean()


