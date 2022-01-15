import pandas as pd

# Read raw historical prices from CSV file
P = pd.read_csv('data/prices.csv').set_index('Date')

# Compute daily returns from the raw prices
R = P.diff() / P.shift(1)

# Backfill UPRO and TMP using estimnated SPYx3 and LTTx3 from daily returns
SPYx3 = R['SPY'].apply(lambda x: x * 3 + 0.025 / 252 if x != 0 else 0)
LTTx3 = R['LTT'].apply(lambda x: x * 3 - 0.080 / 252 if x != 0 else 0)
R['UPRO'] = R['UPRO'].fillna(SPYx3)
R['TMF'] = R['TMF'].fillna(LTTx3)

# Load dividend data from CSV file
div = {}
for symbol, row in pd.read_csv('data/dividends.csv').set_index('Symbol').iterrows():
  date = row['Pay Date']
  if date not in P.index: continue
  price = P.loc[date, symbol]
  div[symbol] = div.get(symbol, {})
  div[symbol][row['Pay Date']] = row['Adj. Amount'] / price

# Compute Effect of Dividend Reinvestment
records = []
for date, row in R.iterrows():
  records.append(dict(Date=date, **{k: v + div.get(symbol, {}).get(date, 0) for k, v in row.to_dict().items()}))
D = pd.DataFrame.from_records(records).set_index('Date')

# Cash is a constant value
R['CASH'] = 0
D['CASH'] = 0

# Save data as CSV files
R.dropna(how='all').to_csv('daily-returns.csv')
D.dropna(how='all').to_csv('daily-returns-with-dividends-reinvested.csv')
