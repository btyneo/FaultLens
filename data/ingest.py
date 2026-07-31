import pandas as pd 
import numpy as np 
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent  # folder containing ingest.py
RAW_DIR = SCRIPT_DIR / "raw" 

def get_dataframe(raw_dir):
    csv_files = sorted(Path(raw_dir).glob("*.csv"))
    frames = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(frames, ignore_index=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    df = df.sort_values('timestamp')
    df = df.drop_duplicates()
    df = df.drop_duplicates('timestamp')
    df = df.dropna(subset=['timestamp'])
    df = df.set_index('timestamp')
    df = df.drop(columns=['Unnamed: 0'])
    return df 

if __name__ == "__main__":
    df = get_dataframe(RAW_DIR)
    print(df.info())
    print(df.head())