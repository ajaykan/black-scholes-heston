import pandas as pd
import datetime as dt
import numpy as np
from scipy.stats import norm

# OpenBB Docs: https://docs.openbb.co/sdk

# example simulation for AAPL

RFR = pow(np.e, 0.0383)-1 # continous risk-free rate where current 1-year risk-free rate is 3.83%

PRICE = 185

VOLATILITY = 0.175

STRIKE_LOWER = 150
STRIKE_UPPER = 220

def tte(expiration): # return time until end of year expressed as percentage
    assert(type(expiration) == dt.date)
    today = dt.date.today()
    pct = (expiration-today).days
    return pct / 365

def calculate_options_price(price, strike, expiration, volatility, call=True):
    tte_ = tte(expiration)
    d1 = (np.log(price/strike) + tte_ * (RFR + 0.5*volatility**2)) / (volatility * np.sqrt(tte_))
    d2 = d1 - (volatility * np.sqrt(tte_))
    price_call = price *  norm.cdf(d1) - strike * pow(np.e, -RFR*tte_) * norm.cdf(d2)
    price_put = strike * pow(np.e, -RFR*tte_) * norm.cdf(-d2) - price * norm.cdf(-d1)
    if call:
        return price_call
    else:
        return price_put

# get theoretical prices of 12/15/2023 AAPL 185C and 185P
print(calculate_options_price(PRICE, 170, dt.date(2023, 12, 15), VOLATILITY))

data = pd.read_csv("data/{ticker}/{date}.csv".format(ticker="AAPL", date=str(dt.date.today())))
dec_exp = data[data['expiration'] == '2023-12-15'][data['strike'] >= STRIKE_LOWER][data['strike'] <= STRIKE_UPPER]


# print(dec_exp)

# create lst with price

lst = []

for index, row in dec_exp.iterrows():
    strike = row['strike']
    call = row['optionType'] == 'call'
    last_price = row['lastPrice']
    if last_price == 0:
        continue
    bs_price = round(calculate_options_price(PRICE, strike, dt.date(2023, 12, 15), VOLATILITY, call=call), 4)
    lst.append([strike, call, last_price, bs_price, bs_price - last_price])

df = pd.DataFrame(lst, columns = ['Strike', 'Call', "Last Price", "BS Price", "Difference"])
df = df.sort_values(by="Difference")
print(df)