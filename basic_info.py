import streamlit as st
import pandas as pd

import yfinance as yf

# Define Industries and stocks
industries = {
    'Banks': ['ANZ.AX', 'CBA.AX', 'NAB.AX', 'WBC.AX', 'BOQ.AX', 'BEN.AX'],
    'Financial Services': ['MQG.AX', 'SQ2.AX', 'ASX.AX', 'SOL.AX', 'CCP.AX', 'EQT.AX'],
    'Insurance': ['QBE.AX', 'SUN.AX', 'IAG.AX', 'MPL.AX', 'SDF.AX', 'AUB.AX'],
    'Software & Services': ['WTC.AX', 'XRO.AX', 'NXT.AX', 'TNE.AX', '360.AX', 'MAQ.AX'],
    'Media & Entertainment': ['REA.AX', 'NWS.AX', 'CAR.AX', 'SEK.AX', 'NEC.AX']
}


def fetch_company_info(ticker):
    """
    Retrieve comprehensive company information

    Parameter:
        ticker: Stock ticker symbol

    Return:
        DataFrame with company details
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        data = {
            'Name': info.get('longName', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Country': info.get('country', 'N/A'),
            'City': info.get('city', 'N/A'),
            'State': info.get('state', 'N/A'),
            'Website': info.get('website', 'N/A'),
            'Business Summary': info.get('longBusinessSummary', 'No summary available'),
            'Market Cap': info.get('marketCap', 'N/A'),
            'PE Ratio': info.get('trailingPE', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
        }

        return pd.DataFrame([data])

    except Exception as e:
        st.error(f"Error fetching information for {ticker}: {e}")
        return pd.DataFrame()


def display_company_info(comp_info):
    """
    Display company information in an attractive, structured layout.

    Parameter:
        comp_info: DataFrame containing company details
    """
    if comp_info.empty:
        st.warning("There was no company information!")
        return

    # Extract company details
    details = comp_info.iloc[0]

    # Create a visually appealing card-like display
    st.markdown(f"""
    <div style="
        background-color: aliceblue; 
        border-radius: 15px; 
        padding: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);">

    <h2 style="color: #1E429F; margin-bottom: 20px; text-align: center;">{details['Name']}</h2>

    <div style="display: flex; justify-content: space-between;">
        <div style="flex: 1; margin-right: 20px;">
            <h3 style="color: #2C3E50;">Company Basics</h3>
            <p><strong>Sector:</strong> {details['Sector']}</p>
            <p><strong>Industry:</strong> {details['Industry']}</p>
            <p><strong>Country:</strong> {details['Country']}</p>
        </div>
        <div style="flex: 1; margin-right: 20px;">
            <h3 style="color: #2C3E50;">Financial Indicators</h3>
            <p><strong>Market Cap (AUS):</strong> {details['Market Cap']}</p>
            <p><strong>PE Ratio:</strong> {details['PE Ratio']}</p>
            <p><strong>Dividend Yield:</strong> {details['Dividend Yield']}</p>
        </div>
    </div>

    <div style="margin-top: 20px;">
        <h3 style="color: #2C3E50;">Business Summary</h3>
        <p style="text-align: justify;">{details['Business Summary']}</p>
    </div>

    <div style="margin-top: 20px; text-align: center;">
        <a href="{details['Website']}" target="_blank" style="
            background-color: #1E429F; 
            color: white; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 5px;
        ">Visit Website</a>
    </div>
    </div>
    """, unsafe_allow_html=True)  # unsafe_allow_html=True allows rendering raw HTML.
                                  # Without it, HTML tags would be escaped and displayed as plain text.


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Australian Stock Insights",
        page_icon="📈",
        layout="wide"
    )

    # Custom CSS for additional styling
    st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title with custom styling
    st.markdown("""
    <h1 style="
        color: #1E429F; 
        text-align: center; 
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">🏢 Australian Stock Market Insights</h1>
    """, unsafe_allow_html=True)

    # Sidebar for selection
    with st.sidebar:
        st.header("Stock Selection")
        selected_industry = st.selectbox("Select Industry", list(industries.keys()))
        st.session_state['ticker'] = st.selectbox("Select Ticker", industries[selected_industry])

    # Fetch and display stock information
    if 'ticker' in st.session_state:
        company_info = fetch_company_info(st.session_state['ticker'])
        display_company_info(company_info)
    else:
        st.warning('No ticker selected')


main()
