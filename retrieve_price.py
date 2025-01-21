from datetime import datetime, timedelta
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


@st.cache_data
def retrieve_data(ticker, start_date, end_date):
    """
    Retrieve stock data for Australian market
    """
    try:
        # Download data
        ticker_df = yf.download(ticker,
                                start=start_date,
                                end=end_date + timedelta(days=1))

        if ticker_df.empty:
            st.error(f"No data found for {ticker}")
            return pd.DataFrame()

        # Flatten multi-index columns if they exist
        if isinstance(ticker_df.columns, pd.MultiIndex):
            ticker_df.columns = [' '.join(col).strip() for col in ticker_df.columns]

        # Remove ticker symbols from column names
        ticker_df.columns = [col.split()[0] if len(col.split()) > 1 else col for col in ticker_df.columns]

        # Extract date component and create a Date column
        ticker_df['Date'] = ticker_df.index.date
        ticker_df = ticker_df.reset_index(drop=True)

        # Round prices to 3 decimal places
        price_columns = ['Open', 'High', 'Low', 'Close']
        ticker_df[price_columns] = ticker_df[price_columns].round(3)

        # Add ticker column for reference
        ticker_df['ticker'] = ticker

        return ticker_df

    except Exception as e:
        st.error(f"Error retrieving data for {ticker}: {str(e)}")
        return pd.DataFrame()


def display_price_metrics(stock_data):
    """
    Display detailed price metrics with dates
    """
    # Get latest and previous day data
    latest_data = stock_data.iloc[-1]
    prev_data = stock_data.iloc[-2]

    # Calculate price changes
    daily_change = latest_data['Close'] - prev_data['Close']
    daily_change_pct = (daily_change / prev_data['Close']) * 100

    # Create metrics display in a clean layout
    st.markdown("### Latest Price Information")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            f"Closing Price ({latest_data['Date']})",
            f"${latest_data['Close']:.2f}",
            f"${daily_change:.2f} ({daily_change_pct:.2f}%)"
        )
    with col2:
        st.metric(
            f"Daily Range ({latest_data['Date']})",
            f"${latest_data['High']:.2f}",
            f"Low: ${latest_data['Low']:.2f}"
        )
    with col3:
        st.metric(
            "Trading Volume",
            f"{latest_data['Volume']:,.0f}",
            f"Date: {latest_data['Date']}"
        )


def visualize_data(stock_data, chart_type):
    if stock_data.empty:
        st.warning("No data available for visualization")
        return

    if chart_type == "Line Chart":
        fig = px.line(stock_data,
                      x='Date',
                      y='Close',
                      title=f'Line Chart of Closing Prices - {stock_data["ticker"].iloc[0].replace(".AX", "")}')

        # Add price labels on hover
        fig.update_traces(
            hovertemplate="<br>".join([
                "Date: %{x}",
                "Price: $%{y:.2f}",
            ])
        )

        # Update layout
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Closing Price (AUD)',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Candlestick":
        fig = go.Figure(data=[go.Candlestick(
            x=stock_data['Date'],
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close']
        )])

        # Update layout with more details
        fig.update_layout(
            title=f'Candlestick Chart - {stock_data["ticker"].iloc[0].replace(".AX", "")}',
            xaxis_title='Date',
            yaxis_title='Price (AUD)',
            xaxis_rangeslider_visible=True,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Area Chart":
        fig = px.area(stock_data,
                      x='Date',
                      y='Volume',
                      title=f'Trading Volume - {stock_data["ticker"].iloc[0].replace(".AX", "")}')

        # Add volume labels on hover
        fig.update_traces(
            hovertemplate="<br>".join([
                "Date: %{x}",
                "Volume: %{y:,.0f}",
            ])
        )

        # Update layout
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Volume',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Histogram":
        stock_data['Return'] = stock_data['Close'].pct_change().dropna()
        fig = px.histogram(
            stock_data,
            x='Return',
            title=f'Distribution of Daily Returns - {stock_data["ticker"].iloc[0].replace(".AX", "")}',
            labels={'Return': 'Daily Returns (%)'},
            nbins=50
        )

        # Add return labels on hover
        fig.update_traces(
            hovertemplate="<br>".join([
                "Return: %{x:.2%}",
                "Count: %{y}",
            ])
        )

        # Update layout
        fig.update_layout(
            showlegend=False,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)


# Main execution flow
if 'ticker' not in st.session_state:
    st.error("No ticker available in session state")
    st.stop()

with st.sidebar:
    st.subheader("Date Range")
    start_date = st.date_input(
        "Starting Date",
        min_value=datetime(1980, 1, 1).date(),
        max_value=datetime.now().date(),
        value=datetime.now().date() - timedelta(days=365)
    )

    end_date = st.date_input(
        "Ending Date",
        min_value=start_date,
        max_value=datetime.now().date(),
        value=datetime.now().date()
    )

    st.subheader('Chart Type')
    chart_type = st.selectbox(
        "Select Chart Type",
        ["Line Chart", "Candlestick", "Area Chart", "Histogram"]
    )

ticker = st.session_state['ticker']
stock_data = retrieve_data(ticker, start_date, end_date)

if not stock_data.empty:
    st.markdown(f"### {ticker.replace('.AX', '')} Stock Data")

    # Display enhanced price metrics
    display_price_metrics(stock_data)

    # Display data table
    with st.expander("View Historical Price Data"):
        st.dataframe(
            stock_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']],
            hide_index=True,
            use_container_width=True
        )

    # Display enhanced charts
    visualize_data(stock_data, chart_type)
    st.session_state['stock_data'] = stock_data