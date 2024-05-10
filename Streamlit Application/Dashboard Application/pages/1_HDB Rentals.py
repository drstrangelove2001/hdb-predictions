import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt, timedelta
import geopandas as gpd
from streamlit_folium import folium_static
from custom_scripts.heatmap import heatmap

PLOT_COLOR = (246/255, 51/255, 102/255)

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

st.title('Trends among HDB in Singapore 2021-2023')

st.sidebar.subheader('Choose the statistic you want to visualize')

aggregator = st.sidebar.radio(
    label_visibility='collapsed',
    label='no_label',
    options=["***Average Monthly Rent***", "***Rental Transaction Volume***"],
    index=0,
    horizontal=True
)

rental_data = pd.read_csv('data/RentingOutOfFlats.csv')
rental_data['rent_approval_date'] = pd.to_datetime(rental_data['rent_approval_date'])
rental_data['rent_approval_date'] = rental_data['rent_approval_date'].dt.to_period('M')

rental_data = rental_data.drop_duplicates()

all_flat_types = sorted(rental_data['flat_type'].unique())

st.sidebar.subheader('Filter on any of these parameters')
flat_types = st.sidebar.multiselect('Select flat type(s)', all_flat_types, all_flat_types)

time = st.sidebar.slider(key='time', label='Select period of time', format="MMM 'YY", min_value=dt(year=2021, month=1, day=1), max_value=dt(year=2023, month=12, day=1), step=timedelta(days=30), value=(dt(year=2021, month=1, day=1), dt(year=2023, month=12, day=1)))

rental_data_modified = rental_data[rental_data['flat_type'].isin(flat_types)]

time_filter_start, time_filter_end = pd.to_datetime(time[0]).to_period('M'), pd.to_datetime(time[1]).to_period('M')

rental_data_date_filtered = rental_data_modified[(rental_data_modified['rent_approval_date'] >= time_filter_start) & (rental_data_modified['rent_approval_date'] <= time_filter_end)]

map_data = gpd.read_file('data/MasterPlan2019PlanningAreaBoundaryNoSea.geojson')

if aggregator == '***Average Monthly Rent***':
    if flat_types:
        rental_data_rates_grouped_by_time = rental_data_date_filtered.groupby('rent_approval_date')['monthly_rent'].mean()
        if time_filter_end != time_filter_start:
            fig1 = plt.figure(figsize=(20,10))
            rental_data_rates_grouped_by_time.plot(color='red')
            plt.title('Time Period Wise Trends')
            plt.xlabel('Rent Approval Period')
            plt.ylabel('Rental Prices (SGD)')
            plt.grid(linestyle='--')
            plt.scatter(rental_data_date_filtered['rent_approval_date'], rental_data_date_filtered['monthly_rent'], color='lightblue')
            st.pyplot(fig1)
        else:
            st.error('Line plot does not exist for the filtered time period')
        
        colx, coly, colz = st.columns([0.5,1,0.5])
        avg_rent_by_town_plot = rental_data_date_filtered.groupby('town')['monthly_rent'].mean().sort_values()
        with coly:
            town_df = pd.DataFrame()
            town_df['PLN_AREA_N'] = avg_rent_by_town_plot.index
            town_df['monthly_rent'] = avg_rent_by_town_plot.values

            map_data = pd.merge(left=map_data, right=town_df, on='PLN_AREA_N', how='left')
            rent_heatmap = heatmap(map_data, 'monthly_rent')
            folium_static(rent_heatmap)

        col1, col2 = st.columns([0.55, 0.45])
        with col1:
            fig2 = plt.figure(figsize=(10, 15))
            avg_rent_by_town_plot.plot(kind='barh', color='g')
            plt.title('Town Wise Trends')
            plt.xlabel('Average Monthly Rent (SGD)')
            plt.xlim(min(avg_rent_by_town_plot.values)-100, max(avg_rent_by_town_plot.values)+100)
            plt.ylabel('Town')
            plt.grid(linestyle='--')

            st.pyplot(fig2)

        with col2:
            rental_data_month_year = rental_data_date_filtered
            rental_data_month_year['month'] = [x.strftime('%b') for x in rental_data_month_year['rent_approval_date']]
            months = rental_data_month_year['month'].unique()
            avg_rent_by_month_plot = rental_data_month_year.groupby('month')['monthly_rent'].mean().sort_index()

            fig3 = plt.figure(figsize=(10, 5.8))
            avg_rent_by_month_plot.plot(kind='bar', color='c')
            plt.title('Month Wise Trends')
            plt.xlabel('Month')
            plt.ylabel('Average Monthly Rent (SGD)')
            plt.xticks(ticks=range(len(months)), labels=months, rotation=45)
            plt.grid(linestyle='--')

            st.pyplot(fig3)

            avg_rent_by_flat_type_plot = rental_data_date_filtered.groupby('flat_type')['monthly_rent'].mean().sort_index()
            fig4 = plt.figure(figsize=(10, 5.8))
            avg_rent_by_flat_type_plot.plot(kind='bar', color=PLOT_COLOR)
            plt.title('Flat Type Wise Trends')
            plt.xlabel('Flat Type')
            plt.ylabel('Average Monthly Rent (SGD)')
            plt.grid(linestyle='--')

            st.pyplot(fig4)
    else:
        st.error('Filter at least one flat type to visualize!')
else:
    if flat_types:
        if time_filter_end != time_filter_start:
            rental_transactions_with_time = rental_data_date_filtered.groupby('rent_approval_date').size()
            fig5 = plt.figure(figsize=(20,10))
            rental_transactions_with_time.plot()
            plt.title('Rental Transactions Performed Over Time')
            plt.ylabel('Number of transactions')
            plt.xlabel('Rent Approval Period')
            plt.grid(linestyle='--')

            st.pyplot(fig5)
            colx, coly = st.columns(2)
            transactions_by_town_plot = rental_data_date_filtered.groupby('town').size().sort_values()
            with colx:
                town_df = pd.DataFrame()
                town_df['PLN_AREA_N'] = transactions_by_town_plot.index
                town_df['count'] = transactions_by_town_plot.values
                
                map_data = pd.merge(left=map_data, right=town_df, on='PLN_AREA_N', how='left')
                count_heatmap = heatmap(map_data, 'count')
                folium_static(count_heatmap)
            
            with coly:
                transactions_by_flat_type_plot = rental_data_date_filtered.groupby('flat_type').size().sort_values()

                fig6 = plt.figure(figsize=(10, 5.8))
                transactions_by_flat_type_plot.plot(kind='pie', autopct='%1.0f%%', ylabel=None)
                plt.title('Percentage of Rental Transactions for Different Flat Types')
                plt.ylabel('')

                st.pyplot(fig6)
            
            col1, col2 = st.columns([0.55, 0.45])
            with col1:
                fig2 = plt.figure(figsize=(10, 15))
                transactions_by_town_plot.plot(kind='barh', color='g')
                plt.title('Town Wise Trends')
                plt.xlabel('Rental Transactions')
                plt.xlim(min(transactions_by_town_plot.values)-100, max(transactions_by_town_plot.values)+100)
                plt.ylabel('Town')
                plt.grid(linestyle='--')

                st.pyplot(fig2)

            with col2:
                rental_data_month_year = rental_data_date_filtered
                rental_data_month_year['month'] = [x.strftime('%b') for x in rental_data_month_year['rent_approval_date']]
                months = rental_data_month_year['month'].unique()
                transactions_by_town_plot = rental_data_month_year.groupby('month').size().sort_values()

                fig3 = plt.figure(figsize=(10, 5.8))
                transactions_by_town_plot.plot(kind='bar', color='c')
                plt.title('Month Wise Trends')
                plt.xlabel('Month')
                plt.ylabel('Rental Transactions')
                plt.xticks(ticks=range(len(months)), labels=months, rotation=45)
                plt.grid(linestyle='--')

                st.pyplot(fig3)          
        else:
            st.error('Filter a finite time period')
    else:
        st.error('Filter at least one flat type to visualize!')

st.sidebar.markdown('''
---
Data taken from https://beta.data.gov.sg/. 
''')