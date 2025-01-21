import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def calculate_statistics(data):
    """Calculate key statistics for the dataset"""
    stats = {
        'Mean': data['Close'].mean(),
        'Median': data['Close'].median(),
        'Std Dev': data['Close'].std(),
        'Min': data['Close'].min(),
        'Max': data['Close'].max(),
        'Returns Mean': data['Close'].pct_change().mean() * 100,
        'Returns Std': data['Close'].pct_change().std() * 100,
        'Volatility (Annual)': data['Close'].pct_change().std() * np.sqrt(252) * 100,
        'Volume Mean': data['Volume'].mean(),
        'Volume Median': data['Volume'].median()
    }
    return pd.Series(stats)


def create_ohlcv_chart(df, title):
    """Create OHLCV chart with moving averages"""
    # Calculate moving averages
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()

    fig = make_subplots(rows=2, cols=1,
                        row_heights=[0.7, 0.3],
                        vertical_spacing=0.1,
                        subplot_titles=(title, 'Volume'))

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )

    # Add moving averages
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MA5'],
            name='5-day MA',
            line=dict(color='orange', width=1)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MA20'],
            name='20-day MA',
            line=dict(color='blue', width=1)
        ),
        row=1, col=1
    )

    # Volume chart
    colors = ['red' if row['Open'] > row['Close'] else 'green' for idx, row in df.iterrows()]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        template='plotly_white'
    )

    return fig


st.title("Basic Descriptive Statistics Analysis")

if 'stock_data' in st.session_state:
    # Get the data
    df = st.session_state['stock_data'].copy()

    # Convert Date column to datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # Create weekly data
    weekly_df = df.resample('W').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })

    # Tabs for different timeframes
    tab1, tab2 = st.tabs(["Daily Analysis", "Weekly Analysis"])

    with tab1:
        st.header("Daily Price Analysis")

        # Display daily chart
        daily_fig = create_ohlcv_chart(df, "Daily OHLC with Moving Averages")
        st.plotly_chart(daily_fig, use_container_width=True)

        # Daily statistics
        st.subheader("Daily Statistics")
        daily_stats = calculate_statistics(df)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Price", f"${daily_stats['Mean']:.2f}")
            st.metric("Daily Returns", f"{daily_stats['Returns Mean']:.2f}%")
        with col2:
            st.metric("Annual Volatility", f"{daily_stats['Volatility (Annual)']:.2f}%")
            st.metric("Daily Std Dev", f"{daily_stats['Std Dev']:.2f}")
        with col3:
            st.metric("Avg Daily Volume", f"{daily_stats['Volume Mean']:,.0f}")
            st.metric("Price Range", f"${daily_stats['Max'] - daily_stats['Min']:.2f}")

    with tab2:
        st.header("Weekly Price Analysis")

        # Display weekly chart
        weekly_fig = create_ohlcv_chart(weekly_df, "Weekly OHLC with Moving Averages")
        st.plotly_chart(weekly_fig, use_container_width=True)

        # Weekly statistics
        st.subheader("Weekly Statistics")
        weekly_stats = calculate_statistics(weekly_df)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Weekly Price", f"${weekly_stats['Mean']:.2f}")
            st.metric("Weekly Returns", f"{weekly_stats['Returns Mean']:.2f}%")
        with col2:
            st.metric("Weekly Volatility", f"{weekly_stats['Volatility (Annual)']:.2f}%")
            st.metric("Weekly Std Dev", f"{weekly_stats['Std Dev']:.2f}")
        with col3:
            st.metric("Avg Weekly Volume", f"{weekly_stats['Volume Mean']:,.0f}")
            st.metric("Weekly Price Range", f"${weekly_stats['Max'] - weekly_stats['Min']:.2f}")

        # Display comparative statistics
        st.subheader("Comparative Analysis")
        comp_df = pd.DataFrame({
            'Daily': daily_stats,
            'Weekly': weekly_stats
        }).round(2)
        st.dataframe(comp_df)

        # Additional weekly specific metrics
        weekly_returns = weekly_df['Close'].pct_change()
        pos_weeks = (weekly_returns > 0).sum()
        total_weeks = len(weekly_returns.dropna())

        st.metric(
            "Positive Weeks Ratio",
            f"{(pos_weeks / total_weeks * 100):.1f}%",
            f"{pos_weeks} out of {total_weeks} weeks"
        )

else:
    st.error("No stock data found. Please ensure data is loaded properly.")