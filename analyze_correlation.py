import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf


def get_market_data(start_date, end_date):
    """
    Fetch market data using pandas and ensure proper column naming
    """
    indices = {
        'ASX200': '^AXJO',
        'ALL-ORD': '^AORD',
        'ASX300': '^AXKO'
    }

    market_data = {}
    for name, symbol in indices.items():
        try:
            # Download data
            df = yf.download(symbol, start=start_date, end=end_date)

            # Extract and rename Close column
            if isinstance(df.columns, pd.MultiIndex):
                close_data = df['Close', symbol]
            else:
                close_data = df['Close']

            market_data[name] = pd.Series(
                close_data.values,
                index=df.index,
                name='Close'
            )

        except Exception as e:
            st.warning(f"Could not fetch data for {name}: {str(e)}")

    return market_data


def calculate_correlations(stock_data, market_data, window):
    """
    Calculate correlations using pandas
    """
    # Convert stock data to pandas series
    stock_prices = pd.Series(stock_data['Close'].values, index=pd.to_datetime(stock_data['Date']))

    # Calculate stock returns
    stock_returns = stock_prices.pct_change().dropna()

    correlations = {}
    rolling_correlations = {}

    for market_name, market_prices in market_data.items():
        try:
            # Calculate market returns
            market_returns = market_prices.pct_change().dropna()

            # Align the series
            stock_aligned, market_aligned = stock_returns.align(market_returns)

            # Calculate static correlation
            static_corr = stock_aligned.corr(market_aligned)
            correlations[market_name] = static_corr

            # Calculate rolling correlation
            roll_corr = stock_aligned.rolling(window=window).corr(market_aligned)
            rolling_correlations[market_name] = roll_corr

        except Exception as e:
            st.warning(f"Error calculating correlation for {market_name}: {str(e)}")

    return correlations, rolling_correlations


def visualize_correlations(correlations, rolling_correlations):
    """
    Create visualizations for correlations
    """
    # Static correlations heatmap
    fig_static = go.Figure(data=go.Heatmap(
        z=[[v] for v in correlations.values()],
        y=list(correlations.keys()),
        x=['Correlation'],
        colorscale='RdBu',
        zmin=-1, zmax=1,
        text=[[f"{v:.3f}"] for v in correlations.values()],
        texttemplate="%{text}",
        textfont={"size": 12, "color": "black"}
    ))

    fig_static.update_layout(
        title="Market Correlations",
        height=400
    )
    st.plotly_chart(fig_static, use_container_width=True)

    # Rolling correlations
    fig_rolling = go.Figure()
    for market_name, rolling_corr in rolling_correlations.items():
        fig_rolling.add_trace(go.Scatter(
            x=rolling_corr.index,
            y=rolling_corr.values,
            name=market_name,
            mode='lines'
        ))

    fig_rolling.update_layout(
        title="Rolling Correlations",
        xaxis_title="Date",
        yaxis_title="Correlation",
        yaxis=dict(range=[-1, 1]),
        height=500,
        showlegend=True
    )
    st.plotly_chart(fig_rolling, use_container_width=True)


def analyze_correlations():
    """
    Main function to analyze correlations
    """
    if 'stock_data' in st.session_state:
        # Get stock data
        stock_data = st.session_state['stock_data'].copy()

        # Convert price columns to numeric if needed
        price_columns = ['Open', 'High', 'Low', 'Close']
        for col in price_columns:
            if col in stock_data.columns:
                if stock_data[col].dtype == object:
                    stock_data[col] = pd.to_numeric(
                        stock_data[col].astype(str).str.replace('$', ''),
                        errors='coerce'
                    )

        # Parameters
        window = st.sidebar.slider("Rolling Window (days)", 5, 252, 20)

        # Get market data
        with st.spinner('Fetching market data...'):
            market_data = get_market_data(
                stock_data['Date'].min(),
                stock_data['Date'].max()
            )

        if market_data:
            # Calculate correlations
            correlations, rolling_correlations = calculate_correlations(
                stock_data, market_data, window
            )

            # Visualize results
            st.markdown(f"### Correlation Analysis for {st.session_state['ticker']}")
            visualize_correlations(correlations, rolling_correlations)
    else:
        st.warning('⚠️ No data available. Please select a ticker first!')

analyze_correlations()