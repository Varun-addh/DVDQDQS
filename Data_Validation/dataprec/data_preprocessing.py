import pandas as pd

def preprocess_column(column, dtype, date_format=None, errors='coerce'):
    """
    Preprocesses a single column based on its data type.

    Args:
        column (pd.Series): The column to preprocess.
        dtype (str): The desired data type ('date', 'numeric', 'text', 'category').
        date_format (str, optional): Date format string (e.g., '%Y-%m-%d'). Defaults to None.
        errors (str, optional): How to handle conversion errors ('coerce', 'raise', 'ignore'). Defaults to 'coerce'.

    Returns:
        pd.Series: The preprocessed column.
    """
    if dtype == "date":
        return pd.to_datetime(column, format=date_format, errors=errors)
    elif dtype == "numeric":
        return pd.to_numeric(column, errors=errors)
    elif dtype == "text":
        return column.astype(str).str.strip().str.lower()
    elif dtype == "category":
        return column.astype('category')
    else:
        return column

def preprocess_dataset(df, date_columns=None, numeric_columns=None, text_columns=None, 
                        date_formats=None, categorical_columns=None):
    
    date_columns = date_columns or []
    numeric_columns = numeric_columns or []
    text_columns = text_columns or []
    date_formats = date_formats or {}
    categorical_columns = categorical_columns or []

    for col in date_columns:
        if col in df.columns:
            df[col] = preprocess_column(df[col], "date", date_format=date_formats.get(col))

    for col in numeric_columns:
        if col in df.columns:
            df[col] = preprocess_column(df[col], "numeric")

    for col in text_columns:
        if col in df.columns:
            df[col] = preprocess_column(df[col], "text")

    for col in categorical_columns:
        if col in df.columns:
            df[col] = preprocess_column(df[col], "category")

    return df