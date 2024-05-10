import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns


map_data = gpd.read_file('data/MasterPlan2019PlanningAreaBoundaryNoSea.geojson')
map_data.rename(columns={'PLN_AREA_N': 'town'})

METRIC_MAP = {
    'monthly_rent': 'Monthly Rent',
    'resale_price': 'Resale Price'
}

BIN_WIDTH_MAP = {
    'monthly_rent': 500,
    'resale_price': 20000
}

data = pd.DataFrame()

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

st.title('Compare HDBs across towns')

trend = st.radio(
        label='Select a metric to compare HDBs on',
        options=["***Rental Trends***", "***Resale Trends***"],
        index=0,
        horizontal=True)

metric = 'monthly_rent'

if trend == '***Rental Trends***':
    data = pd.read_csv('data/RentingOutOfFlats.csv')
    data['rent_approval_date'] = pd.to_datetime(data['rent_approval_date'])
    data['rent_approval_date'] = data['rent_approval_date'].dt.to_period('M')
else:
    resale_time_period = st.radio(
        label='Select time period of resale data to visualize',
        options=["***1990-1999***", "***2000-2011***", "***2012-2018***", "***2019-2024***"],
        index=0,
        horizontal=True).strip('*')
    data = pd.read_csv(f'data/ResaleFlatPrices{resale_time_period}.csv')
    data['month'] = pd.to_datetime(data['month'])
    data['month'] = data['month'].dt.to_period('M')
    metric = 'resale_price'

data['selected'] = False
data = data.drop_duplicates()

all_towns = sorted(data['town'].unique())
all_flat_types = sorted(data['flat_type'].unique())

col1, col2 = st.columns(2)
with col1:
    townA = st.selectbox(key='townA', label='Select town A to compare', options=all_towns)
with col2:
    townB = st.selectbox(key='townB', label='Select town B to compare', options=all_towns)

if townA == townB:
    st.error('Filter two different towns')
else:
    cola, colb, colc = st.columns([1,1.5,1])
    maskA = map_data['PLN_AREA_N'] == townA
    maskB = map_data['PLN_AREA_N'] == townB
    fig, ax = plt.subplots()
    map_data.plot(alpha=0.5, edgecolor='k', ax=ax)
    ax.set_axis_off()
    townA_patch, townB_patch = mpatches.Patch(color='red', label=townA), mpatches.Patch(color='blue', label=townB)
    handles, labels = ax.get_legend_handles_labels()
    handles.append(townA_patch)
    labels.append(townA)
    handles.append(townB_patch)
    labels.append(townB)
    ax.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=3)
    map_data[maskA].plot(ax=ax, color='red', legend=True, legend_kwds={'label': "Town A"})
    map_data[maskB].plot(ax=ax, color='blue', legend=True, legend_kwds={'label': "Town B"})
    with colb:
        st.pyplot(fig)
    colx, coly, colz = st.columns([1,3,1])
    with coly:
        flat_types = st.multiselect('Select flat type(s)', all_flat_types, all_flat_types)
    if flat_types:
        col3, col4, col5, col6 = st.columns([4,1,1,4])
        data_modified = data[data['flat_type'].isin(flat_types)]
        with col3:
            townA_df = data_modified[data_modified['town'] == townA]
            st.subheader(townA)
            st.metric(label=f"Average {METRIC_MAP[metric]}", value='SGD ' + str(round(townA_df[metric].mean())))
            st.metric(label=f"Median {METRIC_MAP[metric]}", value='SGD ' + str(round(townA_df[metric].median())))
            st.metric(label=f"{METRIC_MAP[metric]} Range", value='SGD ' + str(townA_df[metric].min()) + ' to SGD ' + str(townA_df[metric].max()) )
            st.metric(label="Number of transactions", value=townA_df.shape[0])
        with col6:
            townB_df = data_modified[data_modified['town'] == townB]
            st.subheader(townB)
            st.metric(label=f"Average {METRIC_MAP[metric]}", value='SGD ' + str(round(townB_df[metric].mean())))
            st.metric(label=f"Median {METRIC_MAP[metric]}", value='SGD ' + str(round(townB_df[metric].median())))
            st.metric(label=f"{METRIC_MAP[metric]} Range", value='SGD ' + str(townB_df[metric].min()) + ' to SGD ' + str(townB_df[metric].max()) )
            st.metric(label="Number of transactions", value=townB_df.shape[0])
        col7, col8, col9 = st.columns([1,3,1])
        with col8:
            figy, ax = plt.subplots()
            histo = sns.histplot(data=data_modified, x=metric, hue="town", hue_order=[townA, townB], binwidth=BIN_WIDTH_MAP[metric], kde=True, element="step")
            plt.title(f'Distribution of HDBs with Different Ranges of {METRIC_MAP[metric]}')
            plt.xlabel(f'{METRIC_MAP[metric]} (SGD)')
            plt.ylabel('Number of HDBs')
            st.pyplot(figy)
    else:
        st.error('Select at least one flat type to compare the towns.')

st.sidebar.markdown('''
Data taken from https://beta.data.gov.sg/. 
''')