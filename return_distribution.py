import streamlit as st
import polars as pl
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import numpy as np


def calculate_returns(pl_df: pl.DataFrame, period: str = 'daily') -> pl.DataFrame:
    """
    Calculate returns for different periods
    period: 'daily', 'weekly', or 'monthly'
    """
    pl_df = pl_df.with_columns([
        pl.col('Date').str.strptime(pl.Date, '%Y-%m-%d').alias('DateCol')
    ])

    if period == 'daily':
        returns = pl_df.select([
            pl.col('Date'),
            pl.col('Close').pct_change().fill_null(0).alias('Return')
        ])
    else:
        # Add period columns for grouping
        pl_df = pl_df.with_columns([
            pl.col('DateCol').dt.year().alias('Year'),
            pl.col('DateCol').dt.week().alias('Week'),
            pl.col('DateCol').dt.month().alias('Month')
        ])

        if period == 'weekly':
            grouped = pl_df.group_by(['Year', 'Week']).agg([
                pl.col('Close').last().alias('Price'),
                pl.col('Date').last().alias('Date')
            ]).sort('Date')
        else:  # monthly
            grouped = pl_df.group_by(['Year', 'Month']).agg([
                pl.col('Close').last().alias('Price'),
                pl.col('Date').last().alias('Date')
            ]).sort('Date')

        returns = grouped.select([
            pl.col('Date'),
            pl.col('Price').pct_change().fill_null(0).alias('Return')
        ])

    return returns


def analyze_returns_distribution(returns: pl.DataFrame, period: str) -> dict:
    """
    Analyze the distribution of returns with proper period scaling
    """
    returns_array = returns.select('Return').to_numpy().flatten()

    # Scale factors for different periods
    if period == 'Weekly':
        scale_factor = 52  # weeks in a year
    elif period == 'Monthly':
        scale_factor = 12  # months in a year
    else:  # Daily
        scale_factor = 252  # trading days in a year

    # Calculate scaled statistics
    mean_return = np.mean(returns_array)
    std_dev = np.std(returns_array)

    # Annualize mean and std dev
    annualized_mean = mean_return * scale_factor
    annualized_std = std_dev * np.sqrt(scale_factor)

    basic_stats = {
        f'{period} Mean (%)': float(mean_return * 100),
        f'Annualized Mean (%)': float(annualized_mean * 100),
        f'{period} Std Dev (%)': float(std_dev * 100),
        'Annualized Volatility (%)': float(annualized_std * 100),
        f'{period} Minimum (%)': float(np.min(returns_array) * 100),
        f'{period} Maximum (%)': float(np.max(returns_array) * 100),
        'Skewness': float(stats.skew(returns_array)),
        'Excess Kurtosis': float(stats.kurtosis(returns_array))
    }

    # Normality tests
    shapiro_stat, shapiro_p = stats.shapiro(returns_array)
    jb_stat, jb_p = stats.jarque_bera(returns_array)

    normality_tests = {
        'Shapiro-Wilk p-value': shapiro_p,
        'Jarque-Bera p-value': jb_p
    }

    return {'basic_stats': basic_stats, 'normality_tests': normality_tests}


def visualize_returns_distribution(returns_data: dict, period: str):
    """
    Create visualizations for returns distribution
    """
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            f'{period} Returns Distribution',
            f'{period} Returns QQ Plot',
            f'{period} Returns Time Series',
            f'Rolling Volatility'
        )
    )

    returns_array = returns_data['returns'].select('Return').to_numpy().flatten()
    dates = returns_data['returns'].select('Date').to_numpy().flatten()

    # Histogram with KDE
    hist_values, hist_bins = np.histogram(returns_array, bins=50, density=True)
    kde_x = np.linspace(min(returns_array), max(returns_array), 100)
    kde = stats.gaussian_kde(returns_array)

    fig.add_trace(
        go.Histogram(
            x=returns_array,
            name='Returns',
            histnorm='probability density',
            nbinsx=50,
            showlegend=False
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=kde_x,
            y=kde(kde_x),
            name='KDE',
            line=dict(color='red'),
            showlegend=False
        ),
        row=1, col=1
    )

    # QQ Plot
    qq = stats.probplot(returns_array)
    fig.add_trace(
        go.Scatter(
            x=qq[0][0],
            y=qq[0][1],
            mode='markers',
            name='QQ Plot',
            showlegend=False
        ),
        row=1, col=2
    )

    # Add theoretical line
    theoretical_line = np.linspace(min(qq[0][0]), max(qq[0][0]))
    fig.add_trace(
        go.Scatter(
            x=theoretical_line,
            y=qq[1][0] + qq[1][1] * theoretical_line,
            line=dict(color='red'),
            name='Theoretical',
            showlegend=False
        ),
        row=1, col=2
    )

    # Returns Time Series
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=returns_array,
            mode='lines',
            name='Returns',
            showlegend=False
        ),
        row=2, col=1
    )

    # Rolling Volatility
    rolling_vol = pd.Series(returns_array).rolling(
        window=20 if period == 'Daily' else 5
    ).std() * np.sqrt(252 if period == 'Daily' else 52 if period == 'Weekly' else 12)

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=rolling_vol,
            mode='lines',
            name='Rolling Volatility',
            line=dict(color='orange'),
            showlegend=False
        ),
        row=2, col=2
    )

    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text=f"{period} Returns Analysis"
    )

    # Update axes labels
    fig.update_xaxes(title_text="Returns", row=1, col=1)
    fig.update_yaxes(title_text="Density", row=1, col=1)
    fig.update_xaxes(title_text="Theoretical Quantiles", row=1, col=2)
    fig.update_yaxes(title_text="Sample Quantiles", row=1, col=2)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Returns", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=2)
    fig.update_yaxes(title_text="Annualized Volatility", row=2, col=2)

    return fig


def display_analysis_results(returns_data: pl.DataFrame, analysis_results: dict, period: str):
    """
    Display returns data with analysis results
    """
    st.markdown(f"### {period} Returns Analysis")

    # Display visualization
    fig = visualize_returns_distribution(returns_data, period)
    st.plotly_chart(fig, use_container_width=True)

    # Display returns data with statistics
    with st.expander(f"View {period} Returns Data"):
        # Display returns table
        st.dataframe(
            returns_data['returns'].to_pandas().style.format({
                'Return': '{:.4%}'
            })
        )

        if period != 'Daily':
            # Add specific period information
            if period == 'Weekly':
                period_info = returns_data['returns'].with_columns([
                    pl.col('Date').str.strptime(pl.Date, '%Y-%m-%d').dt.strftime('Week %W, %Y').alias('Period')
                ])
            else:  # Monthly
                period_info = returns_data['returns'].with_columns([
                    pl.col('Date').str.strptime(pl.Date, '%Y-%m-%d').dt.strftime('%B %Y').alias('Period')
                ])

            st.markdown(f"#### {period} Period Information")
            st.dataframe(
                period_info.select(['Period', 'Return']).to_pandas().style.format({
                    'Return': '{:.4%}'
                })
            )

        # Display statistics at the bottom
        st.markdown("#### Statistical Summary")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Basic Statistics**")
            stats_df = pd.DataFrame([analysis_results['basic_stats']]).T
            stats_df.columns = ['Value']
            st.dataframe(stats_df.style.format("{:.4f}"))

        with col2:
            st.markdown("**Normality Tests**")
            tests_df = pd.DataFrame([analysis_results['normality_tests']]).T
            tests_df.columns = ['p-value']
            st.dataframe(tests_df.style.format("{:.4f}"))


if 'stock_data' in st.session_state:
    # Convert to Polars DataFrame
    pl_dataframe = pl.from_pandas(st.session_state['stock_data'])
    pl_dataframe = pl_dataframe.with_columns(
        pl.col('Date').dt.strftime('%Y-%m-%d').alias('Date')
    )

    # Calculate returns for different periods and analyze them
    returns_data = {}
    for period in ['Daily', 'Weekly', 'Monthly']:
        returns = calculate_returns(pl_dataframe, period.lower())
        analysis = analyze_returns_distribution(returns, period)
        returns_data[period] = {
            'returns': returns,
            'analysis': analysis
        }

    # Create tabs for different periods
    tabs = st.tabs(['Daily Returns', 'Weekly Returns', 'Monthly Returns'])

    for tab, period in zip(tabs, ['Daily', 'Weekly', 'Monthly']):
        with tab:
            period_data = returns_data[period]
            # Display analysis results including visualizations and data
            display_analysis_results(period_data, period_data['analysis'], period)
else:
    st.warning('⚠️ No data available. Please select a ticker in the menu of "Company Info" !')