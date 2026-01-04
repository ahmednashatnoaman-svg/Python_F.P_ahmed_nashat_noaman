import pandas as pd
import os

class DataManager:
    def __init__(self):
        pass

    def load_data(self, filepath):
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return None
        try:
            print(f"Loading {filepath}...")
            df = pd.read_csv(filepath)
            print(f"Loaded {len(df)} rows.")
            return df
        except Exception as e:
            print(f"Error: {e}")
            return None

    def save_data(self, df, filepath):
        if df is None: return
        try:
            df.to_csv(filepath, index=False)
            print(f"Saved to {filepath}")
        except Exception as e:
            print(f"Error saving: {e}")
