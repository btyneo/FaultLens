from data.ingest import get_dataframe, RAW_DIR
import pandas as pd  
_df = None 

def load_data():
    global _df              
    if _df is None:         
        print("loading...")
        _df = get_dataframe(RAW_DIR)
    return _df            


def retrieve(time_window: dict) -> pd.DataFrame:
    df = load_data()

    # router gives "2020-04-18T00:00:00Z" -> timezone-aware UTC;
    # the index is timezone-naive, so strip the tz to make them comparable
    start = pd.Timestamp(time_window["start"]).tz_localize(None)
    end = pd.Timestamp(time_window["end"]).tz_localize(None)

    return df.loc[start:end]