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
data['Entry'] = data['Date[L]'].shift(-1)
data['Entry_Price'] = data['Open'].shift(-1)
data['Day_PCT'] = ((data['Last'].shift(-1) - data['Open'].shift(-1))/ data['Open'].shift(-1))*100

number_STD = 3
for i in range(number_STD):
    column_name = 'Stds_' + str(i+1)
    #num_std = (i+)
    data[column_name] = (pd.rolling_mean(data.Last, 20) + (pd.rolling_std(data.Last, 20) * (i+1) ))
for i in range(number_STD):
    column_name = 'Stds_Neg_' + str(i+1)
    data[column_name] = (pd.rolling_mean(data.Last, 20) - (pd.rolling_std(data.Last, 20) * ((i+1)) ))
    
future_days = 4 # This is the days looking forward after T. So if you want to have 5 days in total put 4 
for i in range(future_days):
    column_name = 'Day_PCT_Long+' + str(i+2)
    shift_value = -(i+2)
    data[column_name] = ( (data['Last'].shift(shift_value) - data['Open'].shift(-1) ) / data['Open'].shift(-1) ) *100

data['Day_PCT_Short'] = (-((data['Last'].shift(-1) - data['Open'].shift(-1))/ data['Open'].shift(-1))*100)
for i in range(future_days):
    column_name_short = 'Day_PCT_Short+' + str(i+2)
    shift_value_short = -(i+2)
    data[column_name_short] = (-((data['Last'].shift(shift_value_short) - data['Open'].shift(-1))/ data['Open'].shift(-1))* 100)

#Select Parameters (Mask) can be a mix and more can be added.
Long = ((data.Short_MA < data.Last) & (data.Long_MA < data.Last)&  
(data.Stds_2 < data.Last) & (data.Stds_3 > data.Last)) 
Short = ((data.Short_MA > data.Last) & (data.Long_MA > data.Last) &(data.Stds_Neg_2 > data.Last) & 
         (data.Stds_Neg_3 < data.Last))

#Create new DataFrames
Long_Stock = data[Long]
Short_Stock = data[Short]

#Clean Data: delete rows for other strategy (long/short)
#For Long
del Long_Stock['PCT_CHG']
del Long_Stock['Day_PCT_Short']
del Long_Stock['Day_PCT_Short+2']
del Long_Stock['Day_PCT_Short+3']
del Long_Stock['Day_PCT_Short+4']
del Long_Stock['Day_PCT_Short+5']
#For Short
del Short_Stock['PCT_CHG']
del Short_Stock['Day_PCT']
del Short_Stock['Day_PCT_Long+2']
del Short_Stock['Day_PCT_Long+3']
del Short_Stock['Day_PCT_Long+4']
del Short_Stock['Day_PCT_Long+5']
Long_Stock['Day_Diff'] = Long_Stock['Date[L]'] - Long_Stock['Date[L]'].shift(1)
Short_Stock['Day_Diff'] = Short_Stock['Date[L]'] - Short_Stock['Date[L]'].shift(1) #For short one must remember that returns 
#need to be * -1.

#Time Deltas 64 ns
ns_1_day = 86400000000000
ns_2_days = 172800000000000
ns_3_days = 259200000000000
ns_4_days = 345600000000000

#Filter weekends and consecutive days(so we get only the signal)
not_weekend_condition_Long = ((Long_Stock.Day_Diff != ns_1_day) & (Long_Stock.Day_Diff != ns_3_days) & 
                              (Long_Stock.Day_Diff != ns_2_days)& (Long_Stock.Day_Diff != ns_4_days))
not_weekend_condition_Short = ((Short_Stock.Day_Diff != ns_1_day) & (Short_Stock.Day_Diff != ns_3_days) & 
                              (Short_Stock.Day_Diff != ns_2_days)& (Short_Stock.Day_Diff != ns_4_days))

Long_Stock1 = Long_Stock[not_weekend_condition_Long]
Short_Stock1 = Short_Stock[not_weekend_condition_Short] #For short one must remember that returns 
#need to be * -1.

#get the len of each to see how the filtering is working.
len(data)
len(Long_Stock)
len(Long_Stock1)
len(Short_Stock)
len(Short_Stock1)

#plot results for long 
Long_Stock1['Day_PCT'].cumsum().plot(legend=True, title='Cumulative % move')
Long_Stock1['Day_PCT_Long+2'].cumsum().plot(legend=True)
Long_Stock1['Day_PCT_Long+3'].cumsum().plot(legend=True)
Long_Stock1['Day_PCT_Long+4'].cumsum().plot(legend=True)
Long_Stock1['Day_PCT_Long+5'].cumsum().plot(legend=True)

#plot results for short
Short_Stock1['Day_PCT_Short'].cumsum().plot(legend=True, title='Cumulative % move')
Short_Stock1['Day_PCT_Short+2'].cumsum().plot(legend=True)
Short_Stock1['Day_PCT_Short+3'].cumsum().plot(legend=True)
Short_Stock1['Day_PCT_Short+4'].cumsum().plot(legend=True)
Short_Stock1['Day_PCT_Short+5'].cumsum().plot(legend=True)

#Get Avg. Move 
Avg_1_Day = Long_Stock1['Day_PCT'].mean()
Avg_2_Days = Long_Stock1['Day_PCT_Long+2'].mean()
Avg_3_Days = Long_Stock1['Day_PCT_Long+3'].mean()
Avg_4_Days = Long_Stock1['Day_PCT_Long+4'].mean()
Avg_5_Days = Long_Stock1['Day_PCT_Long+5'].mean()

Avg = pd.DataFrame(index=['1'])
Avg['Avg_1_Day'] = Avg_1_Day
Avg['Avg_2_Day'] = Avg_2_Days
Avg['Avg_3_Day'] = Avg_3_Days
Avg['Avg_4_Day'] = Avg_4_Days
Avg['Avg_5_Day'] = Avg_5_Days

#Get Avg. Move 
Avg_1_Day_Short = Short_Stock1['Day_PCT_Short'].mean()
Avg_2_Days_Short = Short_Stock1['Day_PCT_Short+2'].mean()
Avg_3_Days_Short = Short_Stock1['Day_PCT_Short+3'].mean()
Avg_4_Days_Short = Short_Stock1['Day_PCT_Short+4'].mean()
Avg_5_Days_Short = Short_Stock1['Day_PCT_Short+5'].mean()

Avg_Short = pd.DataFrame(index=['1'])
Avg_Short['Avg_1_Day_Short'] = Avg_1_Day_Short
Avg_Short['Avg_2_Day_Short'] = Avg_2_Days_Short
Avg_Short['Avg_3_Day_Short'] = Avg_3_Days_Short
Avg_Short['Avg_4_Day_Short'] = Avg_4_Days_Short
Avg_Short['Avg_5_Day_Short'] = Avg_5_Days_Short

#Stats
Long_Stock1.describe()
Short_Stock1.describe()

#get probability of next day being the up for long down for short
Up_Day = (Long_Stock1.Day_PCT > 0.0)
Down_Day = (Short_Stock1.Day_PCT_Short < 0.0)
Up = Long_Stock1[Up_Day]
Down = Short_Stock1[Down_Day]
Probability_of_Up_Day = (float(len(Up)) / len(Long_Stock1))*100
Probability_of_Down_Day = (float(len(Down)) / len(Short_Stock1))*100
Probability_of_Up_Day
Probability_of_Down_Day

#plots hist of T days after signal
Avg.plot(kind='bar', title='Average Move T Days After Event')
Avg_Short.plot(kind='bar', title='Average Move T Days After Event')

#pct change distribution
Long_Stock1.Day_PCT.hist(bins=100)
Short_Stock1.Day_PCT_Short.hist(bins=100)



#Calculate returns
Long_Stock1['Day_Gain'] = ((Long_Stock1.Day_PCT/100) * 200000 )
Long_Stock1['Cumulative_PL'] = Long_Stock1.Day_Gain.cumsum()
Short_Stock1['Day_Gain'] = (((Short_Stock1.Day_PCT_Short)/100) * 200000)
Short_Stock1['Cumulative_PL'] = Short_Stock1.Day_Gain.cumsum()
#Long_Stock1.head()
#Short_Stock1.head()

#plot returns
Long_Stock1.Day_Gain.cumsum().plot(legend=True) #Cumulative and cumsum of Day gain are the same just did the different for legend
Short_Stock1.Cumulative_PL.plot(legend=True, title='Portfolio P/L')

#Plot Gain distribution
Short_Stock.Day_Gain.hist()
Long_Stock.Day_Gain.hist()

#Plot returns
Short_Stock.Cumulative_PL.plot()
Long_Stock.Cumulative_PL.plot()
