import streamlit as st
import pandas as pd
import joblib
import numpy as np

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

@st.cache_resource(show_spinner='Initializing machine learning models...')
def load_ml_model(fileDir):
    ml_pred = joblib.load(fileDir)
    return ml_pred

def create_df_for_prediction(town, lease_comm, flat_model, year, street, storey_range, flat_type, floor_area):
    region = regions_mapper[town]
    remaining_lease = (99 + lease_comm) - year
    amenities = streets_amenities[(streets_amenities['town'] == town) & (streets_amenities['street_name'] == street)]
    mrt_dist = amenities['mrt_dist'].iloc[0]
    school_dist = amenities['school_dist'].iloc[0]
    mall_dist = amenities['mall_dist'].iloc[0]
    upcoming_mrt_dist = amenities['upcoming_mrt_dist'].iloc[0]
    cpi = cpi_df[(cpi_df['year'] == year) & (cpi_df['month'] == months[month])]['cpi'].iloc[0]
    month_sin = np.sin((months[month]-1)*(2.*np.pi/12))
    month_cos = np.cos((months[month]-1)*(2.*np.pi/12))

    reg_val = {col: 1 if col == 'region_' + region else 0 for col in prefixed_regions}
    town_val = {col: 1 if col == 'town_' + town else 0 for col in prefixed_towns}
    model_val = {col: 1 if col == 'model_' + flat_model else 0 for col in prefixed_models}
    row = {'flat_type': flat_types[flat_type], 'storey_range': storey_range, 'floor_area_sqm': floor_area, 'lease_commence_date': lease_comm, 'remaining_lease': remaining_lease, 'mrt_dist': mrt_dist,
        'school_dist': school_dist, 'mall_dist': mall_dist, 'upcoming_mrt_dist': upcoming_mrt_dist, 'cpi': cpi}
    print(row)
    row.update(model_val)
    row.update(reg_val)
    row.update(town_val)
    row.update({'month_sin': month_sin, 'month_cos': month_cos})
    dct = {k:[v] for k,v in row.items()}
    return pd.DataFrame(dct)


reqd_cols = ['flat_type', 'storey_range', 'floor_area_sqm', 'lease_commence_date',
       'remaining_lease', 'mrt_dist', 'school_dist', 'mall_dist',
       'upcoming_mrt_dist', 'cpi', 'month_sin', 'month_cos']

regions_mapper = {'ANG MO KIO':'North East', 'BEDOK':'East', 'BISHAN':'Central', 'BUKIT BATOK':'West', 'BUKIT MERAH':'Central',
       'BUKIT PANJANG':'West', 'BUKIT TIMAH':'Central', 'CHOA CHU KANG':'West',
       'CLEMENTI':'West', 'GEYLANG':'Central', 'HOUGANG':'North East', 'JURONG EAST':'West', 'JURONG WEST':'West',
       'KALLANG/WHAMPOA':'Central', 'MARINE PARADE':'Central', 'PASIR RIS':'East', 'PUNGGOL':'North East',
       'QUEENSTOWN':'Central', 'SEMBAWANG':'North', 'SENGKANG':'North East', 'SERANGOON':'North East', 'TAMPINES':'East',
       'TOA PAYOH':'Central', 'WOODLANDS':'North', 'YISHUN':'North'}

prefixed_regions = ['region_Central', 'region_East', 'region_North', 'region_North East', 'region_West']

months = {'January': 1, 'Febraury': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

flat_types = {'2-ROOM': 1, '3-ROOM': 2, '4-ROOM': 3, '5-ROOM': 4, 'EXECUTIVE': 5, 'MULTI-GENERATION': 6}

flat_models = ['3Gen', 'Apartment', 'Improved-Maisonette', 'Maisonette', 'Model A', 'Model A-Maisonette', 'New Generation', 'Premium Apartment Loft', 'Premium Maisonette', 'Special', 'Standard']

prefixed_models = ['model_' + model for model in flat_models]

towns = list(regions_mapper.keys())

prefixed_towns = ['town_' + town for town in towns]

streets_amenities = pd.read_csv('auxillary/streets_towns_amenities.csv')

cpi_df = pd.read_csv('auxillary/cpi_mod.csv')

rf_pred, vot_pred, stk_pred = load_ml_model('models/resale/random_forest_model.pkl'), load_ml_model('models/resale/voting_regressor.pkl'), load_ml_model('models/resale/stacking_regressor.pkl')

clx, cly, clz = st.columns([1.08,1.6,1])
with cly:
    st.title('Predict HDB resale prices')
        
st.divider()
colA, colB, colC = st.columns([1, 1.5, 1])

with colB:    
    town = st.selectbox(key='town', label='Select town', index=None, options=towns)

if town:
    colx, coly, colz = st.columns([1,1.5,1])

    with coly:
        streets = streets_amenities[streets_amenities['town'] == town]['street_name']
        street = st.selectbox(key='street', label='Select street', index=None, options=streets)

    st.html("""<br></br>""")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        flat_type = st.selectbox(key='flat_type', label='Select flat type', options=list(flat_types.keys()), index=None)
    with col2:
        flat_model = st.selectbox(key='flat_model', label='Select flat model', options=flat_models, index=None)
    with col3:
        storey_range = st.number_input(key='storey_range', label='Enter storey range', value=2, step=1)
    with col4:
        floor_area = st.number_input(key='floor_area', label='Enter floor area (in sqm)', value=84.0)

    col5, col6, col7 = st.columns(3)
    with col5:
        lease_comm = st.number_input(key='lease_comm', label='Enter lease commencement year', step=1, value=1987)
    with col6:
        year = st.selectbox(key='year', label='Year at which resale is expected', options=[2024, 2023, 2022, 2021])
    with col7:
        month = st.selectbox(key='month', label='Month at which resale is expected', options=list(months.keys()) if year < 2024 else ['January', 'Febraury'])

    st.divider()
    clmA, clmB = st.columns([0.05,1])
    with clmB:
        if all([street, flat_type, flat_model, storey_range, floor_area, lease_comm, year, month]):
            df = create_df_for_prediction(town, lease_comm, flat_model, year, street, storey_range, flat_type, floor_area)

            rf_pred_val = rf_pred.predict(df)
            vot_pred_val = vot_pred.predict(df)
            stk_pred_val = stk_pred.predict(df)

            col8, col9, col10 = st.columns([1,1,1])
            with col9:
                st.subheader("Predicted Resale Prices")
            
            clm1, clm2, clm3, clm4 = st.columns([0.1,1,1,1])
            with clm2:
                st.metric(label=f"Random Forest model predicted price: ", value='SGD ' + str(round(rf_pred_val[0])))
            with clm3:
                st.metric(label=f"Voting regressor model predicted price: ", value='SGD ' + str(round(vot_pred_val[0])))
            with clm4:
                st.metric(label=f"Stacking regressor model predicted price: ", value='SGD ' + str(round(stk_pred_val[0])))