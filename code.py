import pandas as pd
import numpy as np

#import file
data = pd.read_excel('ED&F Man\Equity Files\AAPL\AAPL_EOD.xlsx', 'Documents', parse_date=True)
data.head()

#clean up data from Tickhistory

del data['Qualifiers']
del data['#RIC']
del data['Settle']
del data['Type']
del data['Time[L]']
data = data.dropna()
data.head()

#Add new columns and MA's.

data['PCT_CHG'] = data.Last.pct_change()
data['Short_MA'] = pd.rolling_mean(data.Last, int(raw_input('Select the Short MA periods ')))
data['Long_MA'] = pd.rolling_mean(data.Last, int(raw_input('Select the Long MA periods ')))
data['Entry'] = data['Date[L]'].shift(-1)
data['Entry_Price'] = data['Open'].shift(-1)
data['Day_PCT'] = ((data['Last'].shift(-1) - data['Open'].shift(-1))/ data['Open'].shift(-1))*100
data['52_Wk_High'] = pd.rolling_max(data.High, 250)
data['52_Wk_Low'] = pd.rolling_min(data.Low, 250)

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
    data[column_name_short] = (-((data['Last'].shift(shift_value_short) - data['Open'].shift(-1))/
                                 data['Open'].shift(-1))* 100)
                                 
#Select Parameters (Mask) can be a mix and more can be added.
Long = ((data.Short_MA < data.Last) & (data.Long_MA < data.Last)&  
(data.Stds_2 < data.Last) & (data.Stds_3 > data.Last))
Short = ((data.Short_MA > data.Last) & (data.Long_MA > data.Last) &(data.Stds_Neg_2 > data.Last) & 
         (data.Stds_Neg_3 < data.Last))
"""
#Parameters that can be added as a mix for criteria.
How close the to 52 wk H/L is the stock? Test for percents and STD
(data.Last >= data['52_Wk_High'] * float(raw_input('How close in % to its high? Ex: 0.90 equals within 10% of the high ')))
(data.Last <= data['52_Wk_Low'] * float(raw_input('How close in % to its low? Ex: 1.10 equals within 10% of the low ')))
data.Last >= (data['52_Wk_High'] - pd.rolling_std(data.Last, int(raw_input('The standard deviation of how many periods? '))))
data.Last <= (data['52_Wk_Low'] + pd.rolling_std(data.Last, int(raw_input('The standard deviation of how many periods? '))))
pd.rolling_mean(data.PCT_CHG, int(raw_input('Of how many days do you want the Avg.% move? ')))
(data.Last - data.Open) >= ((data.High - data.Open)
* (float(raw_input('Close at what percentile of the daily move? ')))) #this percentile move is to the UPSIDE!!!!!!
pd.rolling_mean(data.PCT_CHG, int(raw_input('Of how many days do you want the Avg.% move? ')))
(data.Open - data.Last) >= ((data.Open - data.Low)
* (float(raw_input('Close at what percentile of the daily move? '))))#this percentile move is to the DOWNSIDE!!!!!!
"""

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
del Long_Stock['Stds_1']
del Long_Stock['Stds_2']
del Long_Stock['Stds_3']
del Long_Stock['Stds_Neg_1']
del Long_Stock['Stds_Neg_2']
del Long_Stock['Stds_Neg_3']
del Long_Stock['52_Wk_High']
del Long_Stock['52_Wk_Low']

#For Short
del Short_Stock['PCT_CHG']
del Short_Stock['Day_PCT']
del Short_Stock['Day_PCT_Long+2']
del Short_Stock['Day_PCT_Long+3']
del Short_Stock['Day_PCT_Long+4']
del Short_Stock['Day_PCT_Long+5']
del Short_Stock['Stds_1']
del Short_Stock['Stds_2']
del Short_Stock['Stds_3']
del Short_Stock['Stds_Neg_1']
del Short_Stock['Stds_Neg_2']
del Short_Stock['Stds_Neg_3']
del Short_Stock['52_Wk_High']
del Short_Stock['52_Wk_Low']
Long_Stock['Day_Diff'] = Long_Stock['Date[L]'] - Long_Stock['Date[L]'].shift(1)
Short_Stock['Day_Diff'] = Short_Stock['Date[L]'] - Short_Stock['Date[L]'].shift(1) 

#Time Deltas 64 ns
ns_1_day = 86400000000000
ns_2_days = 172800000000000
ns_3_days = 259200000000000
ns_4_days = 345600000000000

not_weekend_condition_Long = ((Long_Stock.Day_Diff != ns_1_day) & (Long_Stock.Day_Diff != ns_3_days) & 
                              (Long_Stock.Day_Diff != ns_2_days)& (Long_Stock.Day_Diff != ns_4_days))
not_weekend_condition_Short = ((Short_Stock.Day_Diff != ns_1_day) & (Short_Stock.Day_Diff != ns_3_days) & 
                              (Short_Stock.Day_Diff != ns_2_days)& (Short_Stock.Day_Diff != ns_4_days))
                              
Long_Stock1 = Long_Stock[not_weekend_condition_Long]
Short_Stock1 = Short_Stock[not_weekend_condition_Short] 

#check number of trades
len(data)
len(Long_Stock)
len(Long_Stock1)#trades
len(Short_Stock)
len(Short_Stock1) #trades

#plot Graphs
Long_Stock1['Day_PCT'].cumsum().plot(legend=True, title='Cumulative % move for Long Trades')
Long_Stock1['Day_PCT_Long+2'].cumsum().plot(legend=True)
Long_Stock1['Day_PCT_Long+3'].cumsum().plot(legend=True)
Long_Stock1['Day_PCT_Long+4'].cumsum().plot(legend=True)
Long_Stock1['Day_PCT_Long+5'].cumsum().plot(legend=True)

Short_Stock1['Day_PCT_Short'].cumsum().plot(legend=True, title='Cumulative % move for Short Trades')
Short_Stock1['Day_PCT_Short+2'].cumsum().plot(legend=True)
Short_Stock1['Day_PCT_Short+3'].cumsum().plot(legend=True)
Short_Stock1['Day_PCT_Short+4'].cumsum().plot(legend=True)

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


#stats
Long_Stock1.describe()
Short_Stock1.describe()

Up_Day = (Long_Stock1.Day_PCT > 0.0)
Down_Day = (Short_Stock1.Day_PCT_Short < 0.0)
Up = Long_Stock1[Up_Day]
Down = Short_Stock1[Down_Day]
Probability_of_Up_Day = (float(len(Up)) / len(Long_Stock1))*100
Probability_of_Down_Day = (float(len(Down)) / len(Short_Stock1))*100

Probability_of_Up_Day #when long signal
Probability_of_Down_Day #when short signal


#plot T days after on hist
Avg.plot(kind='bar', title='Average Move T Days After Event')
Avg_Short.plot(kind='bar', title='Average Move T Days After Event')

#plots distribution
Long_Stock1.Day_PCT.hist(bins=100)
Short_Stock1.Day_PCT_Short.hist(bins=100)

#Calculate returns
Long_Stock1['Day_Gain'] = ((Long_Stock1.Day_PCT/100) * 200000 )
Long_Stock1['Cumulative_PL'] = Long_Stock1.Day_Gain.cumsum()
Short_Stock1['Day_Gain'] = (((Short_Stock1.Day_PCT_Short)/100) * 200000)
Short_Stock1['Cumulative_PL'] = Short_Stock1.Day_Gain.cumsum()
Long_Stock1.head()
#Short_Stock1.head()

#plots returns
Long_Stock1.Day_Gain.cumsum().plot(legend=True) #Cumulative and cumsum of Day gain are the same just did the different for legend
Short_Stock1.Cumulative_PL.plot(legend=True, title='Portfolio P/L')


#Create DateFrame for results with stops and tgts
Results = pd.DataFrame(index=Long_Stock1.index)
Results['Strategy'] = 'Long'
Results['Entry_Date'] = Long_Stock1.Entry
Results['Entry_Price'] = Long_Stock1.Entry_Price
Results['Target_Price'] = Long_Stock1.Entry_Price * 1.02 #raw_input('Enter 1 + percent you want the target to be ')
Results['Number_of_Shares'] = ceil(200000 / Long_Stock1.Entry_Price)
Results['Open'] = data.Open.shift(-1) #needs to be on data cause it has all the days & needs shift -1 because we get long on the next days open
Results['High'] = data.High.shift(-1) #needs to be on data cause it has all the days & needs shift -1 because we get long on the next days open
Results['Low'] = data.Low.shift(-1)
Results['Close'] = data.Last.shift(-1)
Results['Stop_Price'] = 0.0#(Results.Entry_Price * 0.98)
Results['Max_Gain'] = (Results.High - Results.Entry_Price) * Results.Number_of_Shares
Results['Max_Loss'] = (Results.Low - Results.Entry_Price) * Results.Number_of_Shares
Results['EOD_PL'] = (Results.Close - Results.Entry_Price) * Results.Number_of_Shares
Results ['Actions'] = 0 
Results['Total_PL'] = 0

#create a for loop for stop price that modifies it for its trailing stop. It will always be 2% of the high.
for key in Results.Stop_Price.keys():
    if Results.High[key] > Results.Entry_Price[key]:
        Results.Stop_Price[key] = Results.High[key] * 0.98
    else:
        Results.Stop_Price[key] = ((Results.Entry_Price[key]) * 0.98)

#Create a for look that looks at stops and targets and determines whether or not we hit tgt, stopped out, stopped on trailing
# or continue on the trade and tells us in the actions column
for key in Results.High.keys():
    if Results.High[key] > Results.Target_Price[key]:
        Results.Actions[key] =  'TGT Hit, You\'r out!'
    elif Results.Low[key] < Results.Stop_Price[key]:
        Results.Actions[key] = 'Stopped out'
    else:
        Results.Actions[key] = 'Trade still on'

#Created a for loop for calculating the P/L when the trade is closed else it will be left blanc for the time until a solution
#for that problem. 
for key in Results.Total_PL.keys():
    if Results.Actions[key] == 'TGT Hit, You\'r out!':
        Results.Total_PL[key] = (Results.Target_Price[key] - Results.Entry_Price[key]) * Results.Number_of_Shares[key]
    elif Results.Actions[key] == 'Stopped out':
        Results.Total_PL[key] = (Results.Stop_Price[key] - Results.Entry_Price[key]) * Results.Number_of_Shares[key]
    else:
        still_on = Results.Actions == 'Trade still on'
        continued = Results[still_on]

        Results1 = pd.DataFrame(index=continued.index)
        Results1['Strategy'] = 'Long'
        Results1['Entry_Date'] = Long_Stock1.Entry
        Results1['Entry_Price'] = Long_Stock1.Entry_Price
        Results1['Target_Price'] = Long_Stock1.Entry_Price * 1.02 #raw_input('Enter 1 + percent you want the target to be ')
        Results1['Number_of_Shares'] = ceil(200000 / Long_Stock1.Entry_Price)
        Results1['Open'] = data.Open.shift(-2) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
        Results1['High'] = data.High.shift(-2) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
        Results1['Low'] = data.Low.shift(-2)
        Results1['Close'] = data.Last.shift(-2)
        Results1['Stop_Price'] = Results.Stop_Price
        Results1['Max_Gain'] = Results.Max_Gain
        Results1['Max_Loss'] = Results.Max_Loss
        Results1['EOD_PL'] = (Results1.Close - Results1.Entry_Price) * Results1.Number_of_Shares
        Results1['Actions'] = 0 
        Results1['Total_PL'] = 0

#create a for loop for stop price that modifies it for its trailing stop. It will always be 2% of the high.

        for key in Results1.Stop_Price.keys():
            if Results1.Stop_Price[key] > (Results1.High[key] * 0.98):
                pass
            else:
                Results1.Stop_Price[key] = (Results1.High[key] * 0.98 )
        
        for key in Results1.Max_Gain.keys():
            if Results1.Max_Gain[key] > ((Results1.High[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]):
                pass
            else:
                Results1.Max_Gain[key] = (Results1.High[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]
        
        for key in Results1.Max_Loss.keys():
            if Results1.Max_Loss[key] < ((Results1.Low[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]):
                pass
            else:
                (Results1.Low[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]

#Create a for look that looks at stops and targets and determines whether or not we hit tgt, stopped out, stopped on trailing
# or continue on the trade and tells us in the actions column
        for key in Results1.High.keys():
            if Results1.High[key] > Results1.Target_Price[key]:
                Results1.Actions[key] =  'TGT Hit, You\'r out!'
            elif Results1.Low[key] < Results1.Stop_Price[key]:
                Results1.Actions[key] = 'Stopped out'
            else:
                Results1.Actions[key] = 'Trade still on'

        for key in Results1.Total_PL.keys():
            if Results1.Actions[key] == 'TGT Hit, You\'r out!':
                Results1.Total_PL[key] = (Results1.Target_Price[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]
            elif Results1.Actions[key] == 'Stopped out':
                Results1.Total_PL[key] = (Results1.Stop_Price[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]
            else:
                still_on = Results1.Actions == 'Trade still on'
                continued = Results1[still_on]

                Results2 = pd.DataFrame(index=continued.index)
                Results2['Strategy'] = 'Long'
                Results2['Entry_Date'] = Long_Stock1.Entry
                Results2['Entry_Price'] = Long_Stock1.Entry_Price
                Results2['Target_Price'] = Long_Stock1.Entry_Price * 1.02 #raw_input('Enter 1 + percent you want the target to be ')
                Results2['Number_of_Shares'] = ceil(200000 / Long_Stock1.Entry_Price)
                Results2['Open'] = data.Open.shift(-3) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
                Results2['High'] = data.High.shift(-3) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
                Results2['Low'] = data.Low.shift(-3)
                Results2['Close'] = data.Last.shift(-3)
                Results2['Stop_Price'] = Results1.Stop_Price
                Results2['Max_Gain'] = Results1.Max_Gain
                Results2['Max_Loss'] = Results1.Max_Loss
                Results2['EOD_PL'] = (Results2.Close - Results2.Entry_Price) * Results2.Number_of_Shares
                Results2['Actions'] = 0 
                Results2['Total_PL'] = 0

#create a for loop for stop price that modifies it for its trailing stop. It will always be 2% of the high.

                for key in Results2.Stop_Price.keys():
                    if Results2.Stop_Price[key] > (Results2.High[key] * 0.98):
                        pass
                    else:
                        Results2.Stop_Price[key] = (Results2.High[key] * 0.98 )
        
                for key in Results2.Max_Gain.keys():
                    if Results2.Max_Gain[key] > ((Results2.High[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]):
                        pass
                    else:
                        Results2.Max_Gain[key] = (Results2.High[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]
        
                for key in Results2.Max_Loss.keys():
                    if Results2.Max_Loss[key] < ((Results2.Low[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]):
                        pass
                    else:
                        (Results2.Low[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]
    
#Create a for look that looks at stops and targets and determines whether or not we hit tgt, stopped out, stopped on trailing
# or continue on the trade and tells us in the actions column
                for key in Results2.High.keys():
                    if Results2.High[key] > Results2.Target_Price[key]:
                        Results2.Actions[key] =  'TGT Hit, You\'r out!'
                    elif Results2.Low[key] < Results2.Stop_Price[key]:
                        Results2.Actions[key] = 'Stopped out'
                    else:
                        Results2.Actions[key] = 'Trade still on'

                for key in Results2.Total_PL.keys():
                    if Results2.Actions[key] == 'TGT Hit, You\'r out!':
                        Results2.Total_PL[key] = (Results2.Target_Price[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]
                    elif Results2.Actions[key] == 'Stopped out':
                        Results2.Total_PL[key] = (Results2.Stop_Price[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]
                    else:
                        still_on = Results2.Actions == 'Trade still on'
                        continued = Results2[still_on]

                        Results3 = pd.DataFrame(index=continued.index)
                        Results3['Strategy'] = 'Long'
                        Results3['Entry_Date'] = Long_Stock1.Entry
                        Results3['Entry_Price'] = Long_Stock1.Entry_Price
                        Results3['Target_Price'] = Long_Stock1.Entry_Price * 1.02 #raw_input('Enter 1 + percent you want the target to be ')
                        Results3['Number_of_Shares'] = ceil(200000 / Long_Stock1.Entry_Price)
                        Results3['Open'] = data.Open.shift(-2) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
                        Results3['High'] = data.High.shift(-2) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
                        Results3['Low'] = data.Low.shift(-2)
                        Results3['Close'] = data.Last.shift(-2)
                        Results3['Stop_Price'] = Results2.Stop_Price
                        Results3['Max_Gain'] = Results2.Max_Gain
                        Results3['Max_Loss'] = Results2.Max_Loss
                        Results3['EOD_PL'] = (Results3.Close - Results3.Entry_Price) * Results3.Number_of_Shares
                        Results3['Actions'] = 0 
                        Results3['Total_PL'] = 0

#create a for loop for stop price that modifies it for its trailing stop. It will always be 2% of the high.

                        for key in Results3.Stop_Price.keys():
                            if Results3.Stop_Price[key] > (Results3.High[key] * 0.98):
                                pass
                            else:
                                Results3.Stop_Price[key] = (Results3.High[key] * 0.98 )
        
                        for key in Results3.Max_Gain.keys():
                            if Results3.Max_Gain[key] > ((Results3.High[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]):
                                pass
                            else:
                                Results3.Max_Gain[key] = (Results3.High[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]
        
                        for key in Results3.Max_Loss.keys():
                            if Results3.Max_Loss[key] < ((Results3.Low[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]):
                                pass
                            else:
                                (Results3.Low[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]

#Create a for look that looks at stops and targets and determines whether or not we hit tgt, stopped out, stopped on trailing
# or continue on the trade and tells us in the actions column
                        for key in Results3.High.keys():
                            if Results3.High[key] > Results3.Target_Price[key]:
                                Results3.Actions[key] =  'TGT Hit, You\'r out!'
                            elif Results3.Low[key] < Results3.Stop_Price[key]:
                                Results3.Actions[key] = 'Stopped out'
                            else:
                                Results3.Actions[key] = 'Trade still on'

                        for key in Results3.Total_PL.keys():
                            if Results3.Actions[key] == 'TGT Hit, You\'r out!':
                                Results3.Total_PL[key] = (Results3.Target_Price[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]
                            elif Results3.Actions[key] == 'Stopped out':
                                Results3.Total_PL[key] = (Results3.Stop_Price[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]
                            else:
                                 Results3.Total_PL[key] = (Results3.Close[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key] 
                                    # just remove the append to results part for more days.
#The idea to test is cutting the trade after 3-5 days if still open

closed_trades = (Results.Actions == 'TGT Hit, You\'r out!') | (Results.Actions == 'Stopped out')
Results = Results[closed_trades]
closed_trades1 = (Results1.Actions == 'TGT Hit, You\'r out!') | (Results1.Actions == 'Stopped out')
Results1 = Results1[closed_trades1]
Results = Results.append(Results1)
closed_trades2 = (Results2.Actions == 'TGT Hit, You\'r out!') | (Results2.Actions == 'Stopped out')
Results2 = Results2[closed_trades2]
Results = Results.append(Results2)
#closed_trades3 = (Results3.Actions == 'TGT Hit, You\'r out!') | (Results3.Actions == 'Stopped out')
#Results3 = Results3[closed_trades3]
Results = Results.append(Results3)                           


#This is the number of long trades must match with the number of long trades shown above.
len(Results)

#plots long only results
#Long only
Results = Results.sort_index()
Results.Total_PL.cumsum().plot(title='Long Trades Only')

#created DataFrame for short results with tgt and stops
Results_Short = pd.DataFrame(index=Short_Stock1.index)
Results_Short['Strategy'] = 'Short'
Results_Short['Entry_Date'] = Short_Stock1.Entry
Results_Short['Entry_Price'] = Short_Stock1.Entry_Price
Results_Short['Target_Price'] = Short_Stock1.Entry_Price * 0.98 #raw_input('Enter 1 - percent you want the target to be ')
Results_Short['Number_of_Shares'] = ceil(200000 / Short_Stock1.Entry_Price) * (-1)
Results_Short['Open'] = data.Open.shift(-1) #needs to be on data cause it has all the days & needs shift -1 because we get long on the next days open
Results_Short['High'] = data.High.shift(-1) #needs to be on data cause it has all the days & needs shift -1 because we get long on the next days open
Results_Short['Low'] = data.Low.shift(-1)
Results_Short['Close'] = data.Last.shift(-1)
Results_Short['Stop_Price'] = 0.0#(Results.Entry_Price * 1.02)
Results_Short['Max_Gain'] = (Results_Short.Low - Results_Short.Entry_Price) * Results_Short.Number_of_Shares
Results_Short['Max_Loss'] = (Results_Short.High - Results_Short.Entry_Price) * Results_Short.Number_of_Shares
Results_Short['EOD_PL'] = (Results_Short.Close - Results_Short.Entry_Price) * Results_Short.Number_of_Shares
Results_Short['Actions'] = 0 
Results_Short['Total_PL'] = 0

#create a for loop for stop price that modifies it for its trailing stop. It will always be 2% of the high.
for key in Results_Short.Stop_Price.keys():
    if Results_Short.Low[key] < Results_Short.Entry_Price[key]:
        Results_Short.Stop_Price[key] = Results_Short.Low[key] * 1.02
    else:
        Results_Short.Stop_Price[key] = ((Results_Short.Entry_Price[key]) * 1.02)

#Create a for look that looks at stops and targets and determines whether or not we hit tgt, stopped out, stopped on trailing
# or continue on the trade and tells us in the actions column
for key in Results_Short.High.keys():
    if Results_Short.Low[key] < Results_Short.Target_Price[key]:
        Results_Short.Actions[key] =  'TGT Hit, You\'r out!'
    elif Results_Short.High[key] > Results_Short.Stop_Price[key]:
        Results_Short.Actions[key] = 'Stopped out'
    else:
        Results_Short.Actions[key] = 'Trade still on'

#Created a for loop for calculating the P/L when the trade is closed else it will be left blanc for the time until a solution
#for that problem. 
for key in Results_Short.Total_PL.keys():
    if Results_Short.Actions[key] == 'TGT Hit, You\'r out!':
        Results_Short.Total_PL[key] = (Results_Short.Target_Price[key] - Results_Short.Entry_Price[key]) * Results_Short.Number_of_Shares[key]
    elif Results_Short.Actions[key] == 'Stopped out':
        Results_Short.Total_PL[key] = (Results_Short.Stop_Price[key] - Results_Short.Entry_Price[key]) * Results_Short.Number_of_Shares[key]
    else:
        still_on = Results_Short.Actions == 'Trade still on'
        continued = Results_Short[still_on]

        Results1 = pd.DataFrame(index=continued.index)
        Results1['Strategy'] = 'Short'
        Results1['Entry_Date'] = Short_Stock1.Entry
        Results1['Entry_Price'] = Short_Stock1.Entry_Price
        Results1['Target_Price'] = Short_Stock1.Entry_Price * 0.98 #raw_input('Enter 1 - percent you want the target to be ')
        Results1['Number_of_Shares'] = ceil(200000 / Short_Stock1.Entry_Price) * (-1)
        Results1['Open'] = data.Open.shift(-2) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
        Results1['High'] = data.High.shift(-2) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
        Results1['Low'] = data.Low.shift(-2)
        Results1['Close'] = data.Last.shift(-2)
        Results1['Stop_Price'] = Results_Short.Stop_Price
        Results1['Max_Gain'] = Results_Short.Max_Gain
        Results1['Max_Loss'] = Results_Short.Max_Loss
        Results1['EOD_PL'] = (Results1.Close - Results1.Entry_Price) * Results1.Number_of_Shares
        Results1['Actions'] = 0 
        Results1['Total_PL'] = 0

#create a for loop for stop price that modifies it for its trailing stop. It will always be 2% of the high.

        for key in Results1.Stop_Price.keys():
            if Results1.Low[key] < Results1.Entry_Price[key]:
                Results1.Stop_Price[key] = Results1.Low[key] * 1.02
            else:
                Results1.Stop_Price[key] = ((Results1.Entry_Price[key]) * 1.02)
        
        for key in Results1.Max_Gain.keys():
            if Results1.Max_Gain[key] > ((Results1.Low[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]):
                pass
            else:
                Results1.Max_Gain[key] = (Results1.Low[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]
        
        for key in Results1.Max_Loss.keys():
            if Results1.Max_Loss[key] < ((Results1.High[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]):
                pass
            else:
                (Results1.High[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]

#Create a for look that looks at stops and targets and determines whether or not we hit tgt, stopped out, stopped on trailing
# or continue on the trade and tells us in the actions column
        for key in Results1.Low.keys():
            if Results1.Low[key] < Results1.Target_Price[key]:
                Results1.Actions[key] =  'TGT Hit, You\'r out!'
            elif Results1.High[key] > Results1.Stop_Price[key]:
                Results1.Actions[key] = 'Stopped out'
            else:
                Results1.Actions[key] = 'Trade still on'

        for key in Results1.Total_PL.keys():
            if Results1.Actions[key] == 'TGT Hit, You\'r out!':
                Results1.Total_PL[key] = (Results1.Target_Price[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]
            elif Results1.Actions[key] == 'Stopped out':
                Results1.Total_PL[key] = (Results1.Stop_Price[key] - Results1.Entry_Price[key]) * Results1.Number_of_Shares[key]
            else:            
                still_on = Results1.Actions == 'Trade still on'
                continued = Results1[still_on]

                Results2 = pd.DataFrame(index=continued.index)
                Results2['Strategy'] = 'Long'
                Results2['Entry_Date'] = Short_Stock1.Entry
                Results2['Entry_Price'] = Short_Stock1.Entry_Price
                Results2['Target_Price'] = Short_Stock1.Entry_Price * 0.98 #raw_input('Enter 1 + percent you want the target to be ')
                Results2['Number_of_Shares'] = ceil(200000 / Short_Stock1.Entry_Price)
                Results2['Open'] = data.Open.shift(-3) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
                Results2['High'] = data.High.shift(-3) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
                Results2['Low'] = data.Low.shift(-3)
                Results2['Close'] = data.Last.shift(-3)
                Results2['Stop_Price'] = Results1.Stop_Price
                Results2['Max_Gain'] = Results1.Max_Gain
                Results2['Max_Loss'] = Results1.Max_Loss
                Results2['EOD_PL'] = (Results2.Close - Results2.Entry_Price) * Results2.Number_of_Shares
                Results2['Actions'] = 0 
                Results2['Total_PL'] = 0
                

#create a for loop for stop price that modifies it for its trailing stop. It will always be 2% of the high.

                for key in Results2.Stop_Price.keys():
                    if Results2.Low[key] < Results2.Entry_Price[key]:
                        Results2.Stop_Price[key] = Results2.Low[key] * 1.02
                    else:
                        Results2.Stop_Price[key] = ((Results2.Entry_Price[key]) * 1.02)
        
                for key in Results2.Max_Gain.keys():
                    if Results2.Max_Gain[key] > ((Results2.Low[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]):
						pass
                    else:
                        Results2.Max_Gain[key] = (Results2.Low[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]
        
                for key in Results2.Max_Loss.keys():
                    if Results2.Max_Loss[key] < ((Results2.High[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]):
						pass
                    else:
                        (Results2.High[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]

#Create a for look that looks at stops and targets and determines whether or not we hit tgt, stopped out, stopped on trailing
# or continue on the trade and tells us in the actions column
                for key in Results2.Low.keys():
                    if Results2.Low[key] < Results2.Target_Price[key]:
                        Results2.Actions[key] =  'TGT Hit, You\'r out!'
                    elif Results2.High[key] > Results2.Stop_Price[key]:
                        Results2.Actions[key] = 'Stopped out'
                    else:
                        Results2.Actions[key] = 'Trade still on'

                for key in Results2.Total_PL.keys():
                    if Results2.Actions[key] == 'TGT Hit, You\'r out!':
                        Results2.Total_PL[key] = (Results2.Target_Price[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]
                    elif Results2.Actions[key] == 'Stopped out':
                        Results2.Total_PL[key] = (Results2.Stop_Price[key] - Results2.Entry_Price[key]) * Results2.Number_of_Shares[key]
                    else:
                        still_on = Results2.Actions == 'Trade still on'
                        continued = Results2[still_on]

                        Results3 = pd.DataFrame(index=continued.index)
                        Results3['Strategy'] = 'Short'
                        Results3['Entry_Date'] = Short_Stock1.Entry
                        Results3['Entry_Price'] = Short_Stock1.Entry_Price
                        Results3['Target_Price'] = Short_Stock1.Entry_Price *0.98 #raw_input('Enter 1 + percent you want the target to be ')
                        Results3['Number_of_Shares'] = ceil(200000 / Short_Stock1.Entry_Price)
                        Results3['Open'] = data.Open.shift(-2) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
                        Results3['High'] = data.High.shift(-2) #needs to be on data cause it has all the days & 
        #needs shift -1 because we get long on the next days open
                        Results3['Low'] = data.Low.shift(-2)
                        Results3['Close'] = data.Last.shift(-2)
                        Results3['Stop_Price'] = Results2.Stop_Price
                        Results3['Max_Gain'] = Results2.Max_Gain
                        Results3['Max_Loss'] = Results2.Max_Loss
                        Results3['EOD_PL'] = (Results3.Close - Results3.Entry_Price) * Results3.Number_of_Shares
                        Results3['Actions'] = 0 
                        Results3['Total_PL'] = 0

#create a for loop for stop price that modifies it for its trailing stop. It will always be 2% of the high.

                        for key in Results3.Stop_Price.keys():
                            if Results3.Low[key] < Results3.Entry_Price[key]:
                                Results3.Stop_Price[key] = Results3.Low[key] * 1.02
                            else:
                                Results3.Stop_Price[key] = ((Results3.Entry_Price[key]) * 1.02)
        
                        for key in Results3.Max_Gain.keys():
                            if Results3.Max_Gain[key] > ((Results3.Low[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]):
                                pass
                            else:
                                Results3.Max_Gain[key] = (Results3.Low[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]
        
                        for key in Results3.Max_Loss.keys():
                            if Results3.Max_Loss[key] < ((Results3.High[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]):
                                pass
                            else:
                                (Results3.High[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]

#Create a for look that looks at stops and targets and determines whether or not we hit tgt, stopped out, stopped on trailing
# or continue on the trade and tells us in the actions column
                        for key in Results3.Low.keys():
                            if Results3.Low[key] < Results3.Target_Price[key]:
                                Results3.Actions[key] =  'TGT Hit, You\'r out!'
                            elif Results3.High[key] > Results3.Stop_Price[key]:
                                Results3.Actions[key] = 'Stopped out'
                            else:
                                Results3.Actions[key] = 'Trade still on'

                        for key in Results3.Total_PL.keys():
                            if Results3.Actions[key] == 'TGT Hit, You\'r out!':
                                Results3.Total_PL[key] = (Results3.Target_Price[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]
                            elif Results3.Actions[key] == 'Stopped out':
                                Results3.Total_PL[key] = (Results3.Stop_Price[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key]
                            else:
                                Results3.Total_PL[key] = (Results3.Close[key] - Results3.Entry_Price[key]) * Results3.Number_of_Shares[key] 
                                    # just remove the append to results part for more days.
#The idea to test is cutting the trade after 3-5 days if still open

closed_trades = (Results_Short.Actions == 'TGT Hit, You\'r out!') | (Results_Short.Actions == 'Stopped out')
Results_Short = Results_Short[closed_trades]
Results = Results.append(Results_Short)
closed_trades1 = (Results1.Actions == 'TGT Hit, You\'r out!') | (Results1.Actions == 'Stopped out')
Results1 = Results1[closed_trades1]
Results = Results.append(Results1)
closed_trades2 = (Results2.Actions == 'TGT Hit, You\'r out!') | (Results2.Actions == 'Stopped out')
Results2 = Results2[closed_trades2]
Results = Results.append(Results2)
closed_trades3 = (Results3.Actions == 'TGT Hit, You\'r out!') | (Results3.Actions == 'Stopped out')
#Results3 = Results3[closed_trades3]
Results = Results.append(Results3)  

#check that the number of trade is the same as the total
len(Results)

#Sort index and plot all the results
Results = Results.sort_index()
Results.Total_PL.cumsum().plot(title='All Trades')


