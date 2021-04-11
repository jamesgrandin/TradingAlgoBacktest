import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

#Initializing

APIkey="5C0UONZ0TJ3FKCHZ"
Ticker= "MSFT"
datainterval = '5min' #allowable intervals include 1min, 5minute, 15min, 30min, and 60min.
startdatetime="2021-03-22 09:30:00" #choose 5 day intervals M-F to test weekly performance
enddatetime="2021-03-26 16:00:00"


#getting time series data for desired ticker at desired resolution (datainterval)

TS = TimeSeries(key=APIkey, output_format='pandas') #getting time series data

data, metadata =TS.get_intraday(symbol=Ticker, interval=datainterval,outputsize="full") #names the columns and gets intraday data for symbol MSFT (generalize this later)
d1=data[::-1] #for some reason the time series data is list in reverse in the dataframe, this corrects that
d1subset=d1[startdatetime:enddatetime]


#creating technical indicators for buy and sell signals

TI=TechIndicators(key=APIkey,output_format='pandas') #getting technical indicator and setting output to pandas dataframe

dataSMA200, metadataSMA200 = TI.get_sma(symbol=Ticker, interval=datainterval, time_period=200) #200 periodSMA
dataSMA200subset = dataSMA200[startdatetime:enddatetime]

dataSMA, metadataSMA = TI.get_sma(symbol=Ticker, interval=datainterval, time_period=50) #50 periodSMA
dataSMAsubset = dataSMA[startdatetime:enddatetime]

dataEMA, metadataEMA = TI.get_ema(symbol=Ticker, interval=datainterval,time_period=10) #20 PeriodEMA
dataEMAsubset = dataEMA[startdatetime:enddatetime]

# dataRSI, metadataRSI = TI.get_rsi(symbol=Ticker, interval=datainterval,time_period=14)
# dataRSIsubset = dataRSI[startdatetime:enddatetime]


### creating data frame with all of closing price and technical indicators

total_df = pd.concat([d1subset["4. close"],dataSMAsubset,dataSMA200subset, dataEMAsubset], axis=1)
total_df.columns=["Closing_Price","50_SMA","200_SMA","10_EMA"]


#create buy and sell signals based off of moving average crossover.
#genereates BUY signal when 10 EMA crosses 50SMA while above 200 SMA, SELL when crossing back below 50SMA
#Also generates BUY signal when 10 EMA crosses above 200 SMA, signifying the the stock has strong momentum, sells if 10EMA crosses below 50SMA or 200SMA

signals = pd.DataFrame(index=total_df.index) #initializing
signals["signals"]=np.where((total_df['10_EMA'][::]>total_df['50_SMA']) & (total_df['200_SMA'][::]<total_df['10_EMA'][::]),1.0,0.0)


##BUY and SELL signal dataframe column (1=BUY, -1=SELL, 0=Do nothing)

signals['positions']=signals['signals'].diff()


### plotting data with buy/sell signals

fig = plt.figure()
fig.patch.set_facecolor('white')
ax1 = fig.add_subplot(211,  ylabel='Price in $', title=Ticker)
total_df['Closing_Price'].plot(ax=ax1, color='k', lw=0.2)
total_df['50_SMA'].plot(ax=ax1, color='g', lw=0.2)
total_df['200_SMA'].plot(ax=ax1, color='m', lw=0.2)
total_df['10_EMA'].plot(ax=ax1, color='c', lw=0.2)

ax1.plot(signals.loc[signals.positions == 1.0].index,
             total_df["10_EMA"][signals.positions == 1.0],
             '^', markersize=10, color='g')
ax1.plot(signals.loc[signals.positions == -1.0].index,
             total_df["10_EMA"][signals.positions == -1.0],
             'v', markersize=10, color='r')



#positions based on buy and sell signals
#all this code is just me trying and failing to figure out how to get a dataframe containing rolling portfolio balance to plot
# i think i might need a loop but ive been having trouble figuring out the logic, my programming skills are a little rusty

initial_capital=100000.0
shares=100

positions = pd.DataFrame(index=signals.index).fillna(0.0)
positions[Ticker] = shares*signals['positions'].fillna(0.0)
positions['OpenClosePosition']= positions[Ticker]*total_df['Closing_Price'].fillna(0.0)
positions['RollingPostionValue']= shares*signals['signals']*total_df['Closing_Price'].fillna(0.0)

portfolio = pd.DataFrame(index=total_df.index)
portfolio['Available $']=+=initial_capital-positions["OpenClosePosition"]

p=positions['RollingPostionValue'].diff()

#backtest the portfolio (generate PnL)


pnl=(positions.diff()[Ticker]*total_df['Closing_Price']





