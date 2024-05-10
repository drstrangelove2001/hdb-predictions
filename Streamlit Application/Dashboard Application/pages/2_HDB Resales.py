import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt, timedelta
import geopandas as gpd
from streamlit_folium import folium_static
from custom_scripts.heatmap import heatmap

PLOT_COLOR = (246/255, 51/255, 102/255)
PLOT_COLOR_BLUE= (30/255, 144/255, 255/255)

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

st.title('Trends among HDB Resales in Singapore')

st.sidebar.subheader('Choose the statistic you want to visualize')

aggregator = st.sidebar.radio(
    label_visibility='collapsed',
    label='no_label',
    options=["***Average Resale Price***", "***Resale Transaction Volume***"],
    index=0,
    horizontal=True
)
time_period_ranges = {
    "1990-1999": (dt(year=1990, month=1, day=1), dt(year=1999, month=12, day=31)),
    "2000-2011": (dt(year=2000, month=1, day=1), dt(year=2011, month=12, day=31)),
    "2012-2018": (dt(year=2012, month=1, day=1), dt(year=2018, month=12, day=31)),
    "2019-2024": (dt(year=2019, month=1, day=1), dt(year=2024, month=2, day=24)),
}

st.sidebar.subheader('Select the time period of resale data')

resale_time_period = st.sidebar.radio(
        label_visibility='collapsed',
        label='no_label',
        options=["***1990-1999***", "***2000-2011***", "***2012-2018***", "***2019-2024***"],
        index=0,
        horizontal=True).strip('*')

resale_data = pd.read_csv(f'data/ResaleFlatPrices{resale_time_period}.csv')
resale_data['month'] = pd.to_datetime(resale_data['month'])
resale_data['month'] = resale_data['month'].dt.to_period('M')
resale_data['remaining_lease']= (99 + resale_data['lease_commence_date']) - resale_data['month'].dt.year
resale_data = resale_data.drop_duplicates()

all_flat_types = sorted(resale_data['flat_type'].unique())

st.sidebar.subheader('Filter on any of these parameters')
flat_types = st.sidebar.multiselect('Select flat type(s)', all_flat_types, all_flat_types)

start_date, end_date = time_period_ranges[resale_time_period]
time = st.sidebar.slider(key='time', 
                         label='Select period of time', 
                         format="MMM 'YY", 
                         min_value=start_date, 
                         max_value=end_date, 
                         step=timedelta(days=30), 
                         value=(start_date, end_date))

resale_data_modified = resale_data[resale_data['flat_type'].isin(flat_types)]

time_filter_start, time_filter_end = pd.to_datetime(time[0]).to_period('M'), pd.to_datetime(time[1]).to_period('M')

resale_data_date_filtered = resale_data_modified[(resale_data_modified['month'] >= time_filter_start) & (resale_data_modified['month'] <= time_filter_end)]

map_data = gpd.read_file('data/MasterPlan2019PlanningAreaBoundaryNoSea.geojson')

if aggregator == '***Average Resale Price***':
    if flat_types:
        resale_data_rates_grouped_by_time = resale_data_date_filtered.groupby('month')['resale_price'].mean()
        if time_filter_end != time_filter_start:
            fig1 = plt.figure(figsize=(20,10))
            resale_data_rates_grouped_by_time.plot(color='red')
            plt.title('Time Period Wise Trends')
            plt.xlabel('Resale Period')
            plt.ylabel('Resale Prices (SGD)')
            plt.grid(linestyle='--')
            plt.scatter(resale_data_date_filtered['month'], resale_data_date_filtered['resale_price'], color='lightblue')
            st.pyplot(fig1)
        else:
            st.error('Line plot does not exist for the filtered time period')
        
        colx, coly, colz = st.columns([0.5,1,0.5])
        avg_resale_by_town_plot = resale_data_date_filtered.groupby('town')['resale_price'].mean().sort_values()
        with coly:
            town_df = pd.DataFrame()
            town_df['PLN_AREA_N'] = avg_resale_by_town_plot.index
            town_df['resale_price'] = avg_resale_by_town_plot.values

            map_data = pd.merge(left=map_data, right=town_df, on='PLN_AREA_N', how='left')
            resale_heatmap = heatmap(map_data, 'resale_price')
            folium_static(resale_heatmap)
            
        col1, col2 = st.columns([0.55, 0.45])
        with col1:
            fig2 = plt.figure(figsize=(10, 15))
            avg_resale_by_town_plot.plot(kind='barh', color='g')
            plt.title('Town Wise Trends')
            plt.xlabel('Average Resale (SGD)')
            plt.xlim(min(avg_resale_by_town_plot.values)-100, max(avg_resale_by_town_plot.values)+100)
            plt.ylabel('Town')
            plt.grid(linestyle='--')

            st.pyplot(fig2)

            resale_data_date_filtered['lease_segment'] = pd.cut(resale_data_date_filtered['remaining_lease'], 
                                                    bins=range(0, 105, 5), 
                                                    labels=[f"{i}-{i+4}" for i in range(0, 100, 5)])
            avg_price_by_lease_segment = resale_data_date_filtered.groupby('lease_segment')['resale_price'].mean().sort_index()
            avg_price_by_lease_segment = avg_price_by_lease_segment.dropna()
            fig7 = plt.figure(figsize=(10, 5.8))
            avg_price_by_lease_segment.plot(kind='bar', color=PLOT_COLOR_BLUE)
            plt.title('Average Resale Price by Remaining Lease Segment')
            plt.xlabel('Remaining Lease (Years)')
            plt.ylabel('Average Resale Price (SGD)')
            plt.grid(linestyle='--')
            st.pyplot(fig7)
        with col2:
            resale_data_month_year = resale_data_date_filtered
            resale_data_month_year['month'] = [x.strftime('%b') for x in resale_data_month_year['month']]
            months = resale_data_month_year['month'].unique()
            avg_resale_by_month_plot = resale_data_month_year.groupby('month')['resale_price'].mean().sort_index()

            fig3 = plt.figure(figsize=(10, 5.8))
            avg_resale_by_month_plot.plot(kind='bar', color='c')
            plt.title('Month Wise Trends')
            plt.xlabel('Month')
            plt.ylabel('Average Resale (SGD)')
            plt.xticks(ticks=range(len(months)), labels=months, rotation=45)
            plt.grid(linestyle='--')

            st.pyplot(fig3)

            avg_rent_by_flat_type_plot = resale_data_date_filtered.groupby('flat_type')['resale_price'].mean().sort_index()
            fig4 = plt.figure(figsize=(10, 5.8))
            avg_rent_by_flat_type_plot.plot(kind='bar', color=PLOT_COLOR)
            plt.title('Flat Type Wise Trends')
            plt.xlabel('Flat Type')
            plt.ylabel('Average Resale Price (SGD)')
            plt.grid(linestyle='--')

            st.pyplot(fig4)
    else:
        st.error('Filter at least one flat type to visualize!')
else:
    if flat_types:
        if time_filter_end != time_filter_start:
            rental_transactions_with_time = resale_data_date_filtered.groupby('month').size()
            fig5 = plt.figure(figsize=(20,10))
            rental_transactions_with_time.plot()
            plt.title('Resale Transactions Performed Over Time')
            plt.ylabel('Number of transactions')
            plt.xlabel('Resale Period')
            plt.grid(linestyle='--')

            st.pyplot(fig5)
            colx, coly = st.columns(2)
            transactions_by_town_plot = resale_data_date_filtered.groupby('town').size().sort_values()
            with colx:
                town_df = pd.DataFrame()
                town_df['PLN_AREA_N'] = transactions_by_town_plot.index
                town_df['count'] = transactions_by_town_plot.values

                map_data = pd.merge(left=map_data, right=town_df, on='PLN_AREA_N', how='left')
                count_heatmap = heatmap(map_data, 'count')
                folium_static(count_heatmap)
            
            with coly:
                transactions_by_flat_type_plot = resale_data_date_filtered.groupby('flat_type').size().sort_values()

                fig6 = plt.figure(figsize=(10, 5.8))
                transactions_by_flat_type_plot.plot(kind='pie', autopct='%1.0f%%', ylabel=None)
                plt.title('Percentage of Resale Transactions for Different Flat Types')
                plt.ylabel('')

                st.pyplot(fig6)
            
            col1, col2 = st.columns([0.55, 0.45])
            with col1:
                fig2 = plt.figure(figsize=(10, 15))
                transactions_by_town_plot.plot(kind='barh', color='g')
                plt.title('Town Wise Trends')
                plt.xlabel('Resale Transactions')
                plt.xlim(min(transactions_by_town_plot.values)-100, max(transactions_by_town_plot.values)+100)
                plt.ylabel('Town')
                plt.grid(linestyle='--')

                st.pyplot(fig2)

            with col2:
                resale_data_month_year = resale_data_date_filtered
                resale_data_month_year['month'] = [x.strftime('%b') for x in resale_data_month_year['month']]
                months = resale_data_month_year['month'].unique()
                transactions_by_town_plot = resale_data_month_year.groupby('month').size().sort_values()

                fig3 = plt.figure(figsize=(10, 5.8))
                transactions_by_town_plot.plot(kind='bar', color='c')
                plt.title('Month Wise Trends')
                plt.xlabel('Month')
                plt.ylabel('Resale Transactions')
                plt.xticks(ticks=range(len(months)), labels=months, rotation=45)
                plt.grid(linestyle='--')

                st.pyplot(fig3)

                resale_data_date_filtered['lease_segment'] = pd.cut(resale_data_date_filtered['remaining_lease'], 
                                                    bins=range(0, 105, 5), 
                                                    labels=[f"{i}-{i+4}" for i in range(0, 100, 5)])
                transaction_counts = resale_data_date_filtered.groupby('lease_segment').size()
                transaction_counts = transaction_counts[transaction_counts > 0]
                fig8, ax = plt.subplots(figsize=(10, 5.8))
                transaction_counts.plot(kind='bar', color=PLOT_COLOR_BLUE, ax=ax)
                ax.set_title('Number of Resale Transactions by Remaining Lease')
                ax.set_xlabel('Remaining Lease (Years)')
                ax.set_ylabel('Number of Transactions')
                ax.grid(linestyle='--')
                st.pyplot(fig8)

        else:
            st.error('Filter a finite time period')
    else:
        st.error('Filter at least one flat type to visualize!')

st.sidebar.markdown('''
---
Data taken from https://beta.data.gov.sg/. 
''')