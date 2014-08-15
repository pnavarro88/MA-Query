import pandas as pd
import numpy as np

#import file

data = pd.read_excel('ADI_EOD.xlsx', 'ADI_EOD', parse_date=True)

#clean up data from Tickhistory

del data['Qualifiers']
del data['#RIC']
del data['Settle']
del data['Type']
data = data.dropna()

#Add new columns and MA's.

data['PCT_CHG'] = data.Last.pct_change()
data['Short_MA'] = pd.rolling_mean(data.Last, 20)
data['Long_MA'] = pd.rolling_mean(data.Last, 50)

#Select Parameters (Mask)
Long = ((data.Short_MA < data.Last) & (data.Long_MA < data.Last))
Short = ((data.Short_MA > data.Last) & (data.Long_MA > data.Last))

#Create new DataFrames
Long_Stock = data[Long]
Short_Stock = data[Short]

#Calculate returns
Long_Stock['Day_Gain'] = (Long_Stock.PCT_CHG * 200000)
Long_Stock['Cumulative_PL'] = Long_Stock.Day_Gain.cumsum()
Short_Stock['Day_Gain'] = -1 * (Short_Stock.PCT_CHG * 200000)
Short_Stock['Cumulative_PL'] = Short_Stock.Day_Gain.cumsum()

#Plot Gain distribution
Short_Stock.Day_Gain.hist()
Long_Stock.Day_Gain.hist()

#Plot returns
Short_Stock.Cumulative_PL.plot()
Long_Stock.Cumulative_PL.plot()
