import streamlit as st

# st.Page() is a function in Streamlit used to define a page in a multiple pages app.
#   The first and only required argument defines page source, which can be a Python file or function,
#       here is a .py file
#   'title': The title of the page. If it's None(default), the page title(in the browser tab) and label
#       (in the navigation menu) will be inferrred from the filename or callable name in page
#   'icon': An optional emoji or icon to display next to the page title and label.
#   'url_path':  The page's URL pathname, which is the path relative to the app's root URL.
#   'default'(bool):  Whether this page is the default page to be shown when the app is loaded.
basic_info = st.Page("basic_info.py",
                     title="Company Info",
                     url_path="home",
                     icon="🏢",
                     default=True)

retrieve_price = st.Page("retrieve_price.py",
                         title="Stock Price",
                         url_path="price",
                         icon="💹")

desc_stat = st.Page("descriptive_stat.py",
                    title="Descriptive Statistic",
                    url_path="desc",
                    icon="📊")

analyze_return_dist = st.Page("return_distribution.py",
                              title="Return Distribution Analysis",
                              url_path="return",
                              icon="📈")

analyze_corr = st.Page("analyze_correlation.py",
                       title="Correlation Analysis",
                       url_path="corr",
                       icon="🌐")

analyze_seasonality = st.Page("analyze_seasonality.py",
                              title="Seasonality Analysis",
                              url_path="seas",
                              icon="🌱")

linear_reg_analysis = st.Page("linear_regression_analysis.py",
                             title="Linear Regression Analysis",
                             url_path="linear_reg",
                              icon="📉")

page_list = [basic_info, retrieve_price, desc_stat, analyze_return_dist, analyze_corr, analyze_seasonality,
             linear_reg_analysis]

# Configure the available pages
pg = st.navigation(page_list)

# executing and rendering the multi-page navigation
pg.run()

# Visualize the footer
st.markdown("""
    <style>
        .footer {
            font-size: 14px;
            text-align: center;
            padding: 10px;
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: black;
            color: white;
        }
    </style>
    <div class="footer">
        <p>Australian Main Stock Analysis Platform &copy; 2024</p>
    </div>
""", unsafe_allow_html=True)