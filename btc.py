"""
This contains a copy/paste of the Bitcoin Raven notebook code
that generates the Dataframe (see README for links).

On each update, the header is also updated as well as the constant
`LAST_MODIFIED` date, so that it can be printed in the dashboard

Steps to copy/paste in new code:
1. Update `LAST_MODIFIED
2. Copy new code from the notebook, following the `!!! COPY HERE !!!` lines. Copy:
    - header ** DO NOT COPY THE API KEY FROM THE HEADER **
    - imports, if they changed, excluding !pip lines
    - functions, and
    - code that creates the `df` variable
    - code that plots. Replace `fig.show()` with `return fig`.
3. Update data fetch line to read api key from environment variable:
    ```
    df = quandl.get("BCHAIN/MKPRU", api_key=os.environ["API_KEY_QUANDL"]).reset_index()
    ```
4. Update some functions and function calls to have `df` as inputs. See `!!! MODIFY HERE !!!`
    - ossValue
    - normalizationhalving
"""

# Update this on each copy-paste to match the header
LAST_MODIFIED = "2021-10-24"

import os

"""
!!! COPY HERE !!! Header
"""
##########################################################
#          Last Update: 24 Oct 2021                      #
#              400d MA added                             #
##########################################################
# Mayer Multiple (included in final calculation)         #
# Puell Multiple (included in final calculation)         #
# Price/52W EMA  (included in final calculation)         #
# Sharpe Ratio   (included in final calculation)         #
# Sortino Ratio  (NOT included in final calculation)     #
# Power Law      (included in final calculation)         #
# 400d MA        (included in final calculation)         #
##########################################################


"""
!!! COPY HERE !!! Imports, if changed
"""
import pandas as pd
import numpy as np
import quandl as quandl
from datetime import date
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

#
df = pd.DataFrame()

"""
!!! COPY HERE !!! Functions
"""
def normalization(data):
    normalized = (data - data.min()) / (data.max() - data.min())
    return normalized

"""
!!! MODIFY HERE !!! - Maintain the function defintion to have input `df` as shown below
"""
# def ossValue(days):
def ossValue(df, days):
    X = np.array(np.log10(df.ind[:days])).reshape(-1, 1)
    y = np.array(np.log10(df.Value[:days]))
    reg = LinearRegression().fit(X, y)
    values = reg.predict(X)
    return values[-1]


"""
!!! MODIFY HERE !!! - Maintain the function defintion to have input `df_in` as shown below
"""
# def normalizationhalving(Normlist):
    # global df
def normalizationhalving(df_in, Normlist):
    df = df_in.copy()  # Lazy copy until I remove SettingWithCopyWarning
    df1 = df[df["Date"] <= "2011-10-19"]
    df2 = df[(df["Date"] > "2011-10-19") & (df["Date"] <= "2015-01-14")]
    df3 = df[(df["Date"] > "2015-01-14") & (df["Date"] <= "2018-12-15")]
    df4 = df[df["Date"] > "2018-12-15"]
    for item in Normlist:
        df1[item].update(normalization(df1[item]))
        df2[item].update(normalization(df2[item]))
        df3[item].update(normalization(df3[item]))
        df4[item].update(normalization(df4[item]))
    df = pd.concat([df1, df2, df3, df4])
    return df

def generate_data():
    # Shouldn't need to modify this one unless it's changed in the notebook
    df = quandl.get("BCHAIN/MKPRU", api_key=os.environ["API_KEY_QUANDL"]).reset_index()


    """
    !!! COPY HERE !!! Lines between `df = quandl ...` and functions
    """
    btcdata = yf.download(tickers='BTC-USD', period="1d", interval="1m")["Close"]
    lastprice = btcdata.iloc[-1]
    df.loc[len(df)] = [date.today(), lastprice]

    df = df[df["Value"] > 0]
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values(by="Date", inplace=True)
    f_date = pd.to_datetime(date(2010, 1, 1))
    E_date = pd.to_datetime(date(2009, 1, 3))  # genesis
    delta = f_date - E_date
    df = df[df.Date > f_date]
    df.reset_index(inplace=True)

    """
    !!! COPY HERE !!! Copy from `bitcoin = ...`, to the `df["avg"] = ...` line
    """
    ############## 400MA ########################################
    df['400MA'] = 0
    for i in range(0, df.shape[0]):
        df['400MA'][i] = df['Value'][0 if i < 400 else (i - 400): i].dropna().mean()

    df['400MArisk'] = 0
    for i in range(0, df.shape[0]):
        df['400MArisk'][i] = (df['Value'][i] / df['400MA'][i])

    ############## Mayer Multiple ########################################
    df["Mayer"] = df["Value"] / df["Value"].rolling(200).mean()

    ############## Puell Multiple ########################################
    df["btcIssuance"] = 7200 / 2 ** (np.floor(df["index"] / 1458))
    df["usdIssuance"] = df["btcIssuance"] * df["Value"]
    df["MAusdIssuance"] = df["usdIssuance"].rolling(window=365).mean()
    df["PuellMultiple"] = df["usdIssuance"] / df["MAusdIssuance"]

    ############### Price/52W MA ########################################
    df["Price/52w"] = df["Value"] / df["Value"].ewm(span=365).mean()

    ############## Sharpe Ratio ########################################
    df["Return%"] = df["Value"].pct_change() * 100
    df["Sharpe"] = (df["Return%"].rolling(365).mean() - 1) / df["Return%"].rolling(365).std()

    ############# Sortino #############################################
    dfs = df[df["Return%"] < 0]
    df["Sortino"] = (df["Return%"].rolling(365).mean() - 1) / dfs["Return%"].rolling(365).std()

    ############# Power Law ###########################################
    df["ind"] = [x + delta.days for x in range(len(df))]
    """
    !!! MODIFY HERE !!! - Change `ossValue(x + 1)` to `ossValue(df, x + 1)`
    """
    df["PowerLaw"] = np.log10(df.Value) - [ossValue(df, x + 1) for x in range(len(df))]

    #################### avg ################################
    """
    !!! MODIFY HERE !!! - Add `df` as first argument to `normalizationhalving`
    """
    df.update(normalizationhalving(df, ["PuellMultiple", "Price/52w", "PowerLaw", "Sharpe", "Sortino", "Mayer","400MArisk"]))
    df["avg"] = df[["PuellMultiple", "Price/52w", "PowerLaw", "Sharpe", "Mayer", "400MArisk"]].mean(axis=1)

    return df


def generate_figure(df):

    """
    !!! COPY HERE !!! Copy the `#### Plot ####` section. Replace `fig.show()` with `return fig`.
    """
    #################### Plot ################################
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    xaxis = df.Date

    fig.add_trace(go.Scatter(x=xaxis, y=df.Value, name="Price", line=dict(color="gold")), secondary_y=False)
    #fig.add_trace(go.Scatter(x=xaxis, y=df["PuellMultiple"], name="Puell Multiple", line=dict(color="white")), secondary_y=True)### Puell Multiple
    #fig.add_trace(go.Scatter(x=xaxis, y=df["Price/52w"], name="Risk_MA", line=dict(color="white")), secondary_y=True)### 50d/50W MA
    #fig.add_trace(go.Scatter(x=xaxis, y=df["PowerLaw"], name="power law", line=dict(color="white")), secondary_y=True)## Power Law
    #fig.add_trace(go.Scatter(x=xaxis, y=df["Sharpe"], name="Sharpe", line=dict(color="white")), secondary_y=True)## Sharpe Ratio
    #fig.add_trace(go.Scatter(x=xaxis, y=df["Sortino"], name="Sortino", line=dict(color="white")), secondary_y=True)## Sortino Ratio
    #fig.add_trace(go.Scatter(x=xaxis, y=df["Mayer"], name="Mayer", mode="lines", line=dict(color="white")), secondary_y=True) ## Mayer Multiple
    fig.add_trace(go.Scatter(x=xaxis, y=df["avg"], name="Risk", mode="lines", line=dict(color="white")), secondary_y=True)

    fig.add_hrect(y0=0.4, y1=0.3, line_width=0, fillcolor="green", opacity=0.2, secondary_y=True)
    fig.add_hrect(y0=0.3, y1=0.2, line_width=0, fillcolor="green", opacity=0.3, secondary_y=True)
    fig.add_hrect(y0=0.2, y1=0.1, line_width=0, fillcolor="green", opacity=0.4, secondary_y=True)
    fig.add_hrect(y0=0.1, y1=0, line_width=0, fillcolor="green", opacity=0.5, secondary_y=True)
    fig.add_hrect(y0=0.6, y1=0.7, line_width=0, fillcolor="red", opacity=0.3, secondary_y=True)
    fig.add_hrect(y0=0.7, y1=0.8, line_width=0, fillcolor="red", opacity=0.4, secondary_y=True)
    fig.add_hrect(y0=0.8, y1=0.9, line_width=0, fillcolor="red", opacity=0.5, secondary_y=True)
    fig.add_hrect(y0=0.9, y1=1.0, line_width=0, fillcolor="red", opacity=0.6, secondary_y=True)

    AnnotationText = f"****Last BTC price: {round(df['Value'].iloc[-1])}**** Risk: {round(df['avg'].iloc[-1],2)}****"

    fig.update_layout(xaxis_title='Date', yaxis_title='Price',
                    yaxis2_title='Risk',
                    yaxis1=dict(type='log', showgrid=False),
                    yaxis2=dict(showgrid=True, tickmode='linear', tick0=0.0, dtick=0.1),
                    template="plotly_dark",
                    title={'text': AnnotationText, 'y': 0.9, 'x': 0.5},
                    height=600
    )

    return fig