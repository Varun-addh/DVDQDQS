import pandas as pd

# Load dataset
def load_dataset(path):
    try:
        df = pd.read_csv(path, engine="python", on_bad_lines="skip", encoding="utf-8")
        df.columns = df.columns.str.strip()  # Strip column names
        return df
    except Exception as e:
        raise ValueError(f"Error reading the file: {e}")
