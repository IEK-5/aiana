# #
import pandas as pd
from gspread_pandas import Spread

df: pd.DataFrame = Spread('apv_refs').sheet_to_df()
df['Year'].value_counts().sort_index().plot.bar()
