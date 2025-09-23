import pandas as pd

def fetch_google_sheet(url: str, column: int) -> pd.DataFrame:
    """
    Đọc dữ liệu TSV từ Google Sheet về dạng pandas DataFrame
    """


    df = pd.read_csv(url, sep="\t", encoding="utf-8", skiprows=1, usecols=[column])  
    return df
