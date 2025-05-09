import pandas as pd

STRIKES_FILE = 'strikes.csv'

def load_strikes():
    try:
        return pd.read_csv(STRIKES_FILE)
    except FileNotFoundError:
        # create an empty DataFrame
        return pd.DataFrame(columns=['user_id', 'num_strikes'])

def save_strikes(strikes_df):
    strikes_df.to_csv(STRIKES_FILE, index=False)