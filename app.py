import streamlit as st
from streamlit_option_menu import option_menu
import time
import pandas as pd
import numpy as np
from prophet import Prophet
import pandas as pd
import yfinance as yf
import altair as alt
import matplotlib.pyplot as plt

stock_dict = {
    "Infosys": "INFY.NS",
    "Tata Consultancy Services": "TCS.NS",
    "Wipro": "WIPRO.NS",
    "HCL Technologies": "HCLTECH.NS",
    "Tech Mahindra": "TECHM.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India": "SBIN.NS",
    "Axis Bank": "AXISBANK.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Hero MotoCorp": "HEROMOTOCORP.NS",
    "Bajaj Auto": "BAJAJAUTO.NS",
    "Mahindra & Mahindra": "M&M.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Cipla": "CIPLA.NS",
    "Dr. Reddy's Laboratories": "DRREDDY.NS",
    "Lupin": "LUPIN.NS",
    "Aurobindo Pharma": "AUROPHARMA.NS",
    "Hindustan Unilever": "HUL.NS",
    "ITC": "ITC.NS",
    "Procter & Gamble": "PG.NS",
    "Nestle India": "NESTLEIND.NS",
    "Britannia Industries": "BRITANNIA.NS",
    "Reliance Industries": "RELIANCE.NS",
    "Oil & Natural Gas Corporation": "ONGC.NS",
    "Coal India": "COALINDIA.NS",
    "NALCO": "NALCO.NS",
    "Vedanta": "VEDL.NS",
    "Reliance Communications": "RCOM.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Idea Cellular": "IDEA.NS",
    "Tata Steel": "TATASTEEL.NS",
    "JSW Steel": "JSWSTEEL.NS"
}

def forecasting(stock,duration):
    with st.status(label="Please Wait..",expanded=True) as status:
                st.write("Downloading the data")
                from datetime import date
                start_date="2021-01-01"
                if stock=='HDFC Bank':
                     start_date="2019-01-01"
                stock_data = yf.download(stock_dict[stock],start=f'{start_date}',end=date.today())
                st.write("Downloaded Successfully!")
                df = stock_data.reset_index()[['Date', 'Close']]
                df.columns = ['ds', 'y']
                df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
                st.write("Hang on!")
                # Create and fit Prophet model
                model = Prophet(seasonality_prior_scale=0.1)
                model.fit(df)
                st.write("Almost Done..")
                # Make future predictions
                future = model.make_future_dataframe(periods=int(duration))  # predict for next year
                forecast = model.predict(future)
                
                
                status.update(
            label="Report Ready!", state="complete", expanded=False
        )
    return model,future,forecast,df
                



with st.sidebar:
    user_input=option_menu(
        menu_title="Home",
        options=['Overview',"Forecast Details"],
        menu_icon=["house-heart-fill"],
        icons=['house','graph-up-arrow']
    )
# ______________________________________________   Home    ___________________________________________


if user_input=='Overview':
    st.title("Live Stock Forecasting Overview")
    ticker=st.selectbox(label="Select a Stock",options=[key for key in stock_dict.keys()])
    period_options = ['1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
    period = st.select_slider(
            'Select period:',
            options=period_options,
            value='1y'
        )
    proceed=st.button(label="Proceed")
    if proceed:
            # Period selection slider
        stock_data = yf.Ticker(stock_dict[ticker])
        hist = stock_data.history(period=period)
        chart = alt.Chart(hist.reset_index()).mark_line().encode(
        x='Date',
        y='Close',
        tooltip=['Date', 'Close']
            ).configure(
                    background='#4F42B5',
                    view={'strokeWidth': 0}  # Remove border
                ).properties(
                width=700
    )
        st.write(f'**{ticker} Overview**')

        stats = stock_data.info
        industry = stats['industry']
        description = stats['longBusinessSummary']
        TotalEmployees = stats['fullTimeEmployees']
        current_price = stats['currentPrice']
        monthly_change=0
        daily_change = (current_price - hist['Close'][-2]) / hist['Close'][-2] * 100
        weekly_change = (current_price - hist['Close'][-7]) / hist['Close'][-7] * 100
        if period!='1mo':
          monthly_change = (current_price - hist['Close'][-30]) / hist['Close'][-30] * 100
        fifty_two_week_high = stats['fiftyTwoWeekHigh']
        fifty_two_week_low = stats['fiftyTwoWeekLow']
        market_cap = stats['marketCap']

        st.altair_chart(chart)
        st.metric('Industry',industry)
        st.write(f'**Description**: {description}')
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Current Price', current_price)
        col2.metric('Daily Change', f'{daily_change:.2f}%')
        col3.metric('Weekly Change', f'{weekly_change:.2f}%')
        if period=='1mo':
            col4.metric("Monthly Changes","NA")
        else:
            col4.metric('Monthly Change', f'{monthly_change:.2f}%')

        col1, col2, col3 = st.columns(3)
        col1.metric('Market Cap', market_cap)
        col2.metric('52-week High', fifty_two_week_high)
        col3.metric('52-week Low', fifty_two_week_low)

        col1,col2=st.columns(2)
        col1.metric('Total Employees', TotalEmployees)
        

    


# ________________________________________ Forecast Details _______________________________________________

if user_input=='Forecast Details':
    st.title("Forecast Using Prophet")
    stock=st.selectbox(label="Select a Stock",options=[key for key in stock_dict.keys()])
    duration=st.selectbox(label="Select Duration",options=['30',"90","180","365"])
    proceed=st.button(label="Proceed")
    if proceed:
        model,future,forecast,df=forecasting(stock,duration)
        
        st.header(f"{duration} Days Forecast Report")
        # Plot forecast
        
        chart = alt.Chart(forecast).mark_line().encode(
            x=alt.X('ds', title='Date'),
            y=alt.Y('yhat', title='Price (INR)'),
            tooltip=['ds', 'yhat']
        ).configure(
            background='#4F42B5',
            view={'strokeWidth': 0}  # Remove border
        ).properties(
            width='container'
        )
        st.altair_chart(chart,use_container_width=True)
        
        st.write(f"**Trends**")
        # Plot component contributions
        fig2 = model.plot_components(forecast)
        st.pyplot(fig2)

        st.write("**Predicted Lower and Upper Limit**")
        fig3, ax = plt.subplots()
        ax.plot(forecast['ds'], forecast['yhat'], label='yhat')
        ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.3, label='Confidence Interval')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (INR)')
        ax.legend()
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        st.pyplot(fig3)

        st.write("**Historical Vs Predicted Chart**")
        fig4, ax = plt.subplots()
        ax.plot(df['ds'], df['y'], label='Original')
        ax.plot(forecast['ds'], forecast['yhat'], label='Predicted')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (INR)')
        ax.legend()
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        st.pyplot(fig4)


st.subheader("Disclaimer")
st.warning("""The information and data provided in this project are for educational and informational purposes only. The project's predictions, forecasts, and analyses are based on historical data and should not be considered as investment advice.  It is recommended that you conduct your own research, consult with financial experts, and consider your own risk tolerance before making any investment decisions.""")

                                            

