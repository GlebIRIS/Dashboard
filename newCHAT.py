import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set the page configuration
st.set_page_config(
    page_title="Your App Title",
    page_icon="https://irisgalerie.com/cdn/shop/articles/629accd8e699b00bbf1ebdd7_TE_CC_81MOIGNAGES_201_20_1_-min.jpg?v=1655289134",
    layout="wide",  # You can choose "wide" or "centered"
    initial_sidebar_state="auto"  # You can choose "auto", "expanded", or "collapsed"
)

# Function to plot revenue
def plot_revenue(data, group_by_column):
    if group_by_column in ['Year', 'Month', 'Week']:
        revenue_data = data.groupby(group_by_column)['Sales excl Tax EUR'].sum().sort_index()
    else:
        revenue_data = data.groupby(group_by_column)['Sales excl Tax EUR'].sum().sort_values(ascending=False)

    fig = go.Figure(data=[go.Bar(x=revenue_data.index, y=revenue_data.values)])
    fig.update_layout(title=f'Total Sales by {group_by_column}', xaxis_title=group_by_column, yaxis_title='Total Sales')
    st.plotly_chart(fig)


# Function to calculate and plot comparative analysis for Sales, Quantity, #Tickets, or APT
def plot_evolution(data_grouped, dimension, selected_countries, selected_stores, x_axis, metric):
    if not selected_countries:
        st.write("Please select at least one country to compare.")
        return

    if x_axis == 'Month':
        data_grouped['X-axis'] = data_grouped['Year'].astype(str) + '-' + data_grouped['Month'].astype(str).str.zfill(2)
        x_axis_column = 'X-axis'
    elif x_axis == 'Day':
        data_grouped['X-axis'] = data_grouped['Date'].dt.strftime('%Y-%m-%d')
        x_axis_column = 'X-axis'
    elif x_axis == 'Week Number':
        data_grouped['X-axis'] = data_grouped['Year'].astype(str) + '-W' + data_grouped['Week'].astype(str).str.zfill(2)
        x_axis_column = 'X-axis'

    if dimension == 'Country':
        data_pivot = data_grouped.pivot_table(index=x_axis_column, columns='Country', values=metric,
                                              aggfunc='sum')
    elif dimension == 'Store':
        data_grouped = data_grouped[
            data_grouped['Country'].isin(selected_countries) & data_grouped['Store'].isin(selected_stores)]
        data_pivot = data_grouped.pivot_table(index=x_axis_column, columns='Store', values=metric,
                                              aggfunc='sum')

    fig = go.Figure()

    if dimension == 'Country':
        for country in selected_countries:
            fig.add_trace(go.Scatter(x=data_pivot.index, y=data_pivot[country], mode='lines+markers', name=country))
    elif dimension == 'Store':
        for store in selected_stores:
            fig.add_trace(go.Scatter(x=data_pivot.index, y=data_pivot[store], mode='lines+markers', name=store))

    if dimension == 'Country':
        fig.update_layout(title=f'{metric} by {dimension} (Evolution)', xaxis_title=x_axis,
                          yaxis_title=metric)
    elif dimension == 'Store':
        fig.update_layout(title=f'{metric} by {dimension} (Evolution)', xaxis_title=x_axis,
                          yaxis_title=metric)

    fig.update_layout(
        title=f'{metric} by {dimension} (Evolution)',
        xaxis_title=x_axis,
        yaxis_title=metric,
        height=1000,  # Adjust the height as needed
        width=2000  # Adjust the width as needed
    )

    st.plotly_chart(fig)

    st.header("Data Table (Evolution)")
    data_table_evo = data_pivot.reset_index()
    st.dataframe(data_table_evo)


def plot_year_to_year(data_grouped, dimension, selected_countries, selected_stores, x_axis, metric):
    if not selected_countries and not selected_stores:
        st.write("Please select at least one country or store to compare.")
        return

    if x_axis == 'Month':
        x_axis_column = 'Month'
    elif x_axis == 'Day':
        data_grouped['X-axis'] = data_grouped['Date'].dt.dayofyear
        x_axis_column = 'X-axis'
    elif x_axis == 'Week Number':
        x_axis_column = 'Week'

    data_table = pd.DataFrame()

    if selected_countries and dimension == 'Country':
        data_grouped_country = data_grouped[data_grouped['Country'].isin(selected_countries)].copy()
        data_pivot_country = data_grouped_country.pivot_table(index=x_axis_column, columns=['Country', 'Year'],
                                                              values=metric, aggfunc='sum')
        data_table_country = pd.DataFrame(index=data_pivot_country.index)
        for country in selected_countries:
            for year in data_grouped_country['Year'].unique():
                if (country, year) in data_pivot_country.columns:
                    data_table_country[f'{country}-{year}'] = data_pivot_country[(country, year)].values
        data_table = pd.concat([data_table, data_table_country], axis=1)

    if selected_stores and dimension == 'Store':
        data_grouped_store = data_grouped[data_grouped['Store'].isin(selected_stores)].copy()
        data_pivot_store = data_grouped_store.pivot_table(index=x_axis_column, columns=['Store', 'Year'],
                                                          values=metric, aggfunc='sum')
        data_table_store = pd.DataFrame(index=data_pivot_store.index)
        for store in selected_stores:
            for year in data_grouped_store['Year'].unique():
                if (store, year) in data_pivot_store.columns:
                    data_table_store[f'{store}-{year}'] = data_pivot_store[(store, year)].values
        data_table = pd.concat([data_table, data_table_store], axis=1)

    # Now let's generate the chart based on the selected data
    fig = go.Figure()

    if selected_countries and dimension == 'Country':
        for country in selected_countries:
            for year in data_grouped_country['Year'].unique():
                if (country, year) in data_pivot_country.columns:
                    fig.add_trace(
                        go.Scatter(x=data_pivot_country.index, y=data_pivot_country[(country, year)],
                                   mode='lines+markers',
                                   name=f'{country}-{year}'))

    if selected_stores and dimension == 'Store':
        for store in selected_stores:
            for year in data_grouped_store['Year'].unique():
                if (store, year) in data_pivot_store.columns:
                    fig.add_trace(
                        go.Scatter(x=data_pivot_store.index, y=data_pivot_store[(store, year)], mode='lines+markers',
                                   name=f'{store}-{year}'))

    fig.update_layout(title=f'{metric} by {dimension} (Year-to-Year)', xaxis_title=x_axis, yaxis_title=metric)

    # Display the data table in the same format as the Evolution data table
    st.header("Data Table (Year-to-Year)")
    st.dataframe(data_table.transpose())

    # Update layout to make the chart bigger
    fig.update_layout(
        title=f'{metric} by {dimension} (Year-to-Year)',
        xaxis_title=x_axis,
        yaxis_title=metric,
        height=1000,  # Adjust the height as needed
        width=2000  # Adjust the width as needed
    )

    st.plotly_chart(fig)


# Function to calculate Number of Tickets and APT
def calculate_tickets_and_apt(data):
    # Calculate Number of Tickets
    data['#tickets'] = data[data['Sales excl Tax EUR'] > 0].groupby('Order ID')['Order ID'].transform('count')

    # Calculate APT (Average Purchase Ticket)
    data['APT'] = data['Sales excl Tax EUR'] / data['#tickets']

    return data


def run_app():
    st.title('Retail Company Revenue Analysis')

    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y')
        data['Year'] = data['Date'].dt.year
        data['Month'] = data['Date'].dt.month
        data['Week'] = data['Date'].dt.isocalendar().week

        # Calculate #tickets and APT
        data = calculate_tickets_and_apt(data)

        tab1, tab2, tab3 = st.tabs(["General Analysis", "Evolution", "Year-to-Year"])

        with tab1:
            st.header("General Revenue Analysis")
            analysis_type = st.selectbox('Select Analysis Type', ['Country', 'Category', 'Year', 'Month', 'Week'])
            if analysis_type:
                plot_revenue(data, analysis_type)

        with tab2:
            st.header("Evolution Comparative Analysis")
            dimension = st.selectbox('Compare by', ['Country', 'Store'], key='evo_dimension')
            x_axis = st.selectbox('Select X-axis', ['Month', 'Day', 'Week Number'], key='evo_x_axis')
            metric = st.selectbox('Select Metric', ['Sales excl Tax EUR', 'Quantity', '#tickets', 'APT'], key='evo_metric')
            selected_countries_evo = st.multiselect('Select Countries to Compare', data['Country'].unique(),
                                                    key='evo_countries')

            if dimension == 'Store':
                selected_stores_evo = st.multiselect('Select Stores to Compare',
                                                     data[data['Country'].isin(selected_countries_evo)][
                                                         'Store'].unique(), key='evo_stores')

            if st.button('Generate Evolution Chart'):
                data_grouped_evo = data[data['Country'].isin(selected_countries_evo)].copy()
                if dimension == 'Store':
                    plot_evolution(data_grouped_evo, dimension, selected_countries_evo, selected_stores_evo, x_axis, metric)
                else:
                    plot_evolution(data_grouped_evo, dimension, selected_countries_evo, [], x_axis, metric)

                # Display the data table transposed
                st.write("Evolution Data Table:")
                st.write(data_grouped_evo.pivot_table(index='X-axis', columns='Country', values=metric, aggfunc='sum').transpose())

        with tab3:
            st.header("Year-to-Year Comparative Analysis")
            dimension = st.selectbox('Compare by', ['Country', 'Store'], key='y2y_dimension')
            x_axis = st.selectbox('Select X-axis', ['Month', 'Day', 'Week Number'], key='y2y_x_axis')
            metric = st.selectbox('Select Metric', ['Sales excl Tax EUR', 'Quantity', '#tickets', 'APT'], key='y2y_metric')
            selected_countries_y2y = st.multiselect('Select Countries to Compare', data['Country'].unique(),
                                                    key='y2y_countries')

            if dimension == 'Store':
                selected_stores_y2y = st.multiselect('Select Stores to Compare',
                                                     data[data['Country'].isin(selected_countries_y2y)][
                                                         'Store'].unique(), key='y2y_stores')

            if st.button('Generate Year-to-Year Chart'):
                data_grouped_y2y = data[data['Country'].isin(selected_countries_y2y)].copy()
                if dimension == 'Store':
                    plot_year_to_year(data_grouped_y2y, dimension, selected_countries_y2y, selected_stores_y2y, x_axis, metric)
                else:
                    plot_year_to_year(data_grouped_y2y, dimension, selected_countries_y2y, [], x_axis, metric)

                # Display the data table transposed
                st.write("Year-to-Year Data Table:")
                st.write(data_grouped_y2y.pivot_table(index='X-axis', columns=['Country', 'Year'], values=metric, aggfunc='sum').transpose())

    else:
        st.sidebar.write("Please upload a CSV file to proceed.")

run_app()
