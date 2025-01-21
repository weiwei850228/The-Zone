import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime


def perform_linear_regression(df):
    """Perform linear regression on the closing price."""
    # Convert date to numerical format for regression
    df['Date_Numeric'] = pd.to_datetime(df['Date']).map(datetime.toordinal)

    # Prepare data for regression
    X = df['Date_Numeric'].values.reshape(-1, 1)
    y = df['Close'].values.reshape(-1, 1)

    # Perform linear regression
    model = LinearRegression()
    model.fit(X, y)

    # Calculate predicted values
    df['Predicted_Price'] = model.predict(X)

    # Calculate R-squared
    r_squared = model.score(X, y)

    # Calculate confidence intervals (95%)
    n = len(df)
    mse = np.sum((df['Close'] - df['Predicted_Price']) ** 2) / (n - 2)
    x_mean = np.mean(X)

    # Standard error of prediction
    std_err = np.sqrt(mse * (1 + 1 / n + (X - x_mean) ** 2 / np.sum((X - x_mean) ** 2)))

    # 95% prediction interval
    df['Upper_Bound'] = df['Predicted_Price'] + 1.96 * std_err.flatten()
    df['Lower_Bound'] = df['Predicted_Price'] - 1.96 * std_err.flatten()

    return df, r_squared, model.coef_[0][0]


def create_regression_plot(df, r_squared, slope):
    """Create an interactive plot with stock data and regression analysis."""
    # Create figure with secondary y-axis for volume
    fig = make_subplots(rows=2, cols=1,
                        vertical_spacing=0.1,
                        row_heights=[0.7, 0.3],
                        subplot_titles=("Closing Price Regression Analysis", "Volume"))

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="OHLC"
        ),
        row=1, col=1
    )

    # Add regression line
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Predicted_Price'],
            name="Regression Line",
            line=dict(color='red', width=2)
        ),
        row=1, col=1
    )

    # Add confidence intervals
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Upper_Bound'],
            name='Upper Bound',
            line=dict(dash='dash', color='gray'),
            opacity=0.3
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Lower_Bound'],
            name='Lower Bound',
            line=dict(dash='dash', color='gray'),
            fill='tonexty',
            opacity=0.3
        ),
        row=1, col=1
    )

    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=df['Date'],
            y=df['Volume'],
            name='Volume'
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        title=f"Stock Price Analysis (R² = {r_squared:.4f}, Slope = {slope:.4f})",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis2_title="Date",
        yaxis2_title="Volume",
        height=800,
        showlegend=True,
        hovermode='x unified'
    )

    return fig


# Main Streamlit app
st.title("Stock Price Regression Analysis")

if 'stock_data' in st.session_state:
    # Make a copy and ensure numeric columns
    stock_data = st.session_state['stock_data'].copy()

    # Convert Date column to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(stock_data['Date']):
        try:
            stock_data['Date'] = pd.to_datetime(stock_data['Date'])
        except Exception as e:
            st.error(f"Error converting Date column to datetime: {str(e)}")
            st.stop()

    # Sort data by date
    stock_data = stock_data.sort_values('Date')

    # Verify required columns
    required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in stock_data.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        st.stop()

    # Ensure we have valid min and max dates
    min_date = stock_data['Date'].min()
    max_date = stock_data['Date'].max()

    # Only create the date range slider if we have valid dates
    if min_date != max_date:
        date_range = st.slider(
            "Select Date Range",
            min_value=min_date.date(),
            max_value=max_date.date(),
            value=(min_date.date(), max_date.date())
        )

        # Filter data based on date range
        mask = (stock_data['Date'].dt.date >= date_range[0]) & (stock_data['Date'].dt.date <= date_range[1])
        filtered_data = stock_data.loc[mask]
    else:
        st.warning("Dataset contains only one date point. Showing all data.")
        filtered_data = stock_data

    try:
        # Perform regression analysis
        analyzed_data, r_squared, slope = perform_linear_regression(filtered_data)

        # Create and display the plot
        fig = create_regression_plot(analyzed_data, r_squared, slope)
        st.plotly_chart(fig, use_container_width=True)

        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("R-squared Value", f"{r_squared:.4f}")
        with col2:
            st.metric("Slope", f"{slope:.4f}")
        with col3:
            daily_return = analyzed_data['Close'].pct_change().mean() * 100
            st.metric("Avg Daily Return", f"{daily_return:.2f}%")

        # Technical Analysis Insights
        st.subheader("Analysis Insights")

        # Trend analysis
        trend_strength = abs(slope)
        trend_direction = "upward" if slope > 0 else "downward"

        # Calculate additional metrics
        volatility = analyzed_data['Close'].pct_change().std() * np.sqrt(252) * 100  # Annualized volatility

        st.write(f"**Trend Analysis:**")
        st.write(f"- The stock shows a {trend_direction} trend with a slope of {slope:.4f}")
        st.write(f"- Annualized Volatility: {volatility:.2f}%")

        # Volume Analysis
        avg_volume = analyzed_data['Volume'].mean()
        recent_volume = analyzed_data['Volume'].iloc[-5:].mean()
        volume_trend = "higher" if recent_volume > avg_volume else "lower"

        st.write(f"**Volume Analysis:**")
        st.write(f"- Recent volume is {volume_trend} than average")
        st.write(f"- Average Volume: {avg_volume:,.0f}")
        st.write(f"- Recent Average Volume: {recent_volume:,.0f}")

        # Price Position Analysis
        latest_price = analyzed_data['Close'].iloc[-1]
        predicted_price = analyzed_data['Predicted_Price'].iloc[-1]

        st.write(f"**Price Position Analysis:**")
        if latest_price > analyzed_data['Upper_Bound'].iloc[-1]:
            st.write("- The stock is currently trading above its predicted range (potentially overbought)")
        elif latest_price < analyzed_data['Lower_Bound'].iloc[-1]:
            st.write("- The stock is currently trading below its predicted range (potentially oversold)")
        else:
            st.write("- The stock is trading within its predicted range")

    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
else:
    st.error("No stock data found in session state. Please ensure data is loaded properly.")