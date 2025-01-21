import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, pacf
from scipy import stats


def clean_stock_data(df):
    """Clean and prepare stock data"""
    # Clean column names
    df.columns = [col.strip().replace("'", "").replace(",", "") for col in df.columns]
    return df


def calculate_monthly_patterns(stock_data):
    """Calculate monthly statistics and patterns"""
    # Add month information
    monthly_data = stock_data.copy()
    monthly_data['Month'] = monthly_data.index.month
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Calculate statistics
    monthly_stats = monthly_data.groupby('Month')['Close'].agg([
        'mean', 'std', 'min', 'max', 'count'
    ]).round(2)

    # Calculate returns
    monthly_data['Return'] = monthly_data['Close'].pct_change()
    monthly_returns = monthly_data.groupby('Month')['Return'].mean() * 100

    # Calculate statistical significance
    stats_data = []
    for month in range(1, 13):
        month_returns = monthly_data[monthly_data['Month'] == month]['Return']
        t_stat, p_value = stats.ttest_1samp(month_returns.dropna(), 0)
        stats_data.append({
            'Month': month_names[month - 1],
            'Average_Return': monthly_returns[month],
            'T_Statistic': t_stat,
            'P_Value': p_value,
            'Sample_Size': len(month_returns.dropna())
        })

    seasonal_stats = pd.DataFrame(stats_data)
    return monthly_stats, monthly_returns, seasonal_stats


def plot_monthly_patterns(monthly_stats, monthly_returns, seasonal_stats):
    """Create comprehensive monthly pattern plots"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Monthly Average Prices',
            'Monthly Returns (%)',
            'Statistical Significance',
            'Monthly Return Distribution'
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Monthly prices
    fig.add_trace(
        go.Bar(
            x=months,
            y=monthly_stats['mean'],
            error_y=dict(type='data', array=monthly_stats['std']),
            name='Average Price'
        ),
        row=1, col=1
    )

    # Monthly returns
    fig.add_trace(
        go.Bar(
            x=months,
            y=monthly_returns,
            name='Average Return',
            marker_color=['red' if x < 0 else 'green' for x in monthly_returns]
        ),
        row=1, col=2
    )

    # T-statistics
    fig.add_trace(
        go.Bar(
            x=seasonal_stats['Month'],
            y=seasonal_stats['T_Statistic'],
            name='T-Statistic',
            marker_color=['red' if abs(x) > 1.96 else 'gray' for x in seasonal_stats['T_Statistic']]
        ),
        row=2, col=1
    )

    # Add significance lines
    fig.add_hline(y=1.96, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=-1.96, line_dash="dash", line_color="red", row=2, col=1)

    # Returns distribution
    fig.add_trace(
        go.Box(
            x=months,
            y=monthly_returns,
            name='Returns Distribution'
        ),
        row=2, col=2
    )

    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="Monthly Patterns Analysis"
    )

    # Update axes labels
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Return (%)", row=1, col=2)
    fig.update_yaxes(title_text="T-Statistic", row=2, col=1)
    fig.update_yaxes(title_text="Return (%)", row=2, col=2)

    return fig


def perform_seasonal_decomposition(data, period, model='additive'):
    """Perform seasonal decomposition"""
    decomposition = seasonal_decompose(
        data,
        period=period,
        model=model
    )

    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=('Original', 'Trend', 'Seasonal', 'Residual'),
        vertical_spacing=0.1,
        row_width=[0.25, 0.25, 0.25, 0.25]
    )

    # Original data
    fig.add_trace(
        go.Scatter(x=data.index, y=data, mode='lines', name='Original'),
        row=1, col=1
    )

    # Trend
    fig.add_trace(
        go.Scatter(x=data.index, y=decomposition.trend, mode='lines', name='Trend'),
        row=2, col=1
    )

    # Seasonal
    fig.add_trace(
        go.Scatter(x=data.index, y=decomposition.seasonal, mode='lines', name='Seasonal'),
        row=3, col=1
    )

    # Residual
    fig.add_trace(
        go.Scatter(x=data.index, y=decomposition.resid, mode='lines', name='Residual'),
        row=4, col=1
    )

    fig.update_layout(height=900, showlegend=True)
    return fig


def plot_acf_pacf(data, lags):
    """Create ACF and PACF plots"""
    acf_values = acf(data, nlags=lags)
    pacf_values = pacf(data, nlags=lags)
    conf_int = 1.96 / np.sqrt(len(data))

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Autocorrelation Function (ACF)',
                        'Partial Autocorrelation Function (PACF)'),
        vertical_spacing=0.15
    )

    # ACF plot
    fig.add_trace(
        go.Bar(x=np.arange(lags + 1), y=acf_values, name='ACF'),
        row=1, col=1
    )
    fig.add_hline(y=conf_int, line_dash="dash", line_color="red", row=1, col=1)
    fig.add_hline(y=-conf_int, line_dash="dash", line_color="red", row=1, col=1)

    # PACF plot
    fig.add_trace(
        go.Bar(x=np.arange(lags + 1), y=pacf_values, name='PACF'),
        row=2, col=1
    )
    fig.add_hline(y=conf_int, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=-conf_int, line_dash="dash", line_color="red", row=2, col=1)

    fig.update_layout(height=600, showlegend=False)
    return fig


def analyze_seasonality():
    """Main function for seasonality analysis"""
    if 'stock_data' in st.session_state:
        st.title(f"Seasonality Analysis for {st.session_state['ticker']}")

        try:
            # Prepare data
            stock_data = st.session_state['stock_data'].copy()
            stock_data = clean_stock_data(stock_data)
            stock_data['Date'] = pd.to_datetime(stock_data['Date'])
            stock_data.set_index('Date', inplace=True)

            # Parameters
            st.sidebar.header("Analysis Parameters")
            period = st.sidebar.slider("Seasonality Period", 2, 52, 12)
            decomp_model = st.sidebar.selectbox(
                "Decomposition Model",
                ['additive', 'multiplicative']
            )
            lags = st.sidebar.slider("Number of Lags", 1, 100, 40)

            # Monthly patterns analysis
            st.header("Monthly Patterns")
            monthly_stats, monthly_returns, seasonal_stats = calculate_monthly_patterns(stock_data)
            fig_monthly = plot_monthly_patterns(monthly_stats, monthly_returns, seasonal_stats)
            st.plotly_chart(fig_monthly, use_container_width=True)

            # Show significant patterns
            significant_patterns = seasonal_stats[seasonal_stats['P_Value'] < 0.05]
            if not significant_patterns.empty:
                st.subheader("Significant Seasonal Patterns")
                st.dataframe(
                    significant_patterns[['Month', 'Average_Return', 'T_Statistic', 'P_Value']]
                    .round(3)
                    .sort_values('P_Value')
                )

            # Seasonal decomposition
            st.header("Seasonal Decomposition")
            if len(stock_data) >= period * 2:
                fig_decomp = perform_seasonal_decomposition(
                    stock_data['Close'],
                    period=period,
                    model=decomp_model
                )
                st.plotly_chart(fig_decomp, use_container_width=True)
            else:
                st.warning(f"Need at least {period * 2} observations for decomposition")

            # Autocorrelation analysis
            st.header("Autocorrelation Analysis")
            if len(stock_data) > lags:
                returns = stock_data['Close'].pct_change().dropna()
                fig_corr = plot_acf_pacf(returns, lags)
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("Need more observations for correlation analysis")

        except Exception as e:
            st.error(f"Error in analysis: {str(e)}")
            st.write("Please check your data and parameters")

    else:
        st.warning('⚠️ No data available. Please select a ticker first!')


analyze_seasonality()