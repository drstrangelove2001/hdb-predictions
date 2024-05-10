import streamlit as st
import pandas as pd
import joblib
import numpy as np

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

@st.cache_resource(show_spinner='Initializing machine learning models...')
def load_ml_model(fileDir):
    ml_pred = joblib.load(fileDir)
    return ml_pred

def create_df_for_prediction(town, year, street, flat_type, month):
    region = regions_mapper[town]
    amenities = streets_amenities[(streets_amenities['town'] == town) & (streets_amenities['street_name'] == street)]
    mrt_dist = amenities['mrt_dist'].iloc[0]
    school_dist = amenities['school_dist'].iloc[0]
    mall_dist = amenities['mall_dist'].iloc[0]
    upcoming_mrt_dist = amenities['upcoming_mrt_dist'].iloc[0]

    reg_val = {col: 1 if col == 'region_' + region else 0 for col in prefixed_regions}
    town_val = {col: 1 if col == 'town_' + town else 0 for col in prefixed_towns}
    row = {'flat_type': flat_types[flat_type]}
    row.update(reg_val)
    row.update(town_val)
    other_row = {'rent_approval_month': months[month], 'rent_approval_year': year, 'mrt_dist': mrt_dist,
        'school_dist': school_dist, 'mall_dist': mall_dist, 'upcoming_mrt_dist': upcoming_mrt_dist}
    row.update(other_row)
    dct = {k:[v] for k,v in row.items()}
    return pd.DataFrame(dct)


reqd_cols_st = ['flat_type']

reqd_cols_end = ['rent_approval_month', 'rent_approval_year', 'mrt_dist', 'school_dist', 'mall_dist', 'upcoming_mrt_dist']

regions_mapper = {'ANG MO KIO':'North East', 'BEDOK':'East', 'BISHAN':'Central', 'BUKIT BATOK':'West', 'BUKIT MERAH':'Central',
       'BUKIT PANJANG':'West', 'BUKIT TIMAH':'Central', 'CENTRAL': 'North', 'CHOA CHU KANG':'West',
       'CLEMENTI':'West', 'GEYLANG':'Central', 'HOUGANG':'North East', 'JURONG EAST':'West', 'JURONG WEST':'West',
       'KALLANG/WHAMPOA':'Central', 'MARINE PARADE':'Central', 'PASIR RIS':'East', 'PUNGGOL':'North East',
       'QUEENSTOWN':'Central', 'SEMBAWANG':'North', 'SENGKANG':'North East', 'SERANGOON':'North East', 'TAMPINES':'East',
       'TOA PAYOH':'Central', 'WOODLANDS':'North', 'YISHUN':'North'}

prefixed_regions = ['region_Central', 'region_East', 'region_North', 'region_North East', 'region_West']

months = {'January': 1, 'Febraury': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

flat_types = {'2-ROOM': 1, '3-ROOM': 2, '4-ROOM': 3, '5-ROOM': 4, 'EXECUTIVE': 5, 'MULTI-GENERATION': 6}

towns = list(regions_mapper.keys())

prefixed_towns = ['town_' + town for town in towns]

streets_amenities = pd.read_csv('auxillary/streets_towns_amenities.csv')

rf_pred, knn_pred, xgb_pred = load_ml_model('models/rental/rf_regressor.pkl'), load_ml_model('models/rental/grid_search_knn.pkl'), load_ml_model('models/rental/grid_search_xgb.pkl')

clx, cly, clz = st.columns([1.08,1.6,1])
with cly:
    st.title('Predict HDB rental prices')
        
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
    col1, col2, col3 = st.columns(3)

    with col2:
        flat_type = st.selectbox(key='flat_type', label='Select flat type', options=list(flat_types.keys()), index=None)

    col4, col5 = st.columns(2)
    with col4:
        year = st.selectbox(key='year', label='Year at which rental starts', options=[2024, 2023, 2022, 2021])
    with col5:
        month = st.selectbox(key='month', label='Month at which rental starts', options=list(months.keys()) if year < 2024 else ['January', 'Febraury'])

    st.divider()
    clmA, clmB = st.columns([0.05,1])
    with clmB:
        if all([street, flat_type, year, month]):
            df = create_df_for_prediction(town, year, street, flat_type, month )

            rf_pred_val = rf_pred.predict(df)
            knn_pred_val = knn_pred.predict(df)
            xgb_pred_val = xgb_pred.predict(df)

            col8, col9, col10 = st.columns([1,1,1])
            with col9:
                st.subheader("Predicted Rental Prices")
            
            clm1, clm2, clm3, clm4 = st.columns([0.1,1,1,1])
            with clm2:
                st.metric(label=f"Random Forest model predicted price: ", value='SGD ' + str(round(rf_pred_val[0])))
            with clm3:
                st.metric(label=f"Grid Search KNN model predicted price: ", value='SGD ' + str(round(knn_pred_val[0])))
            with clm4:
                st.metric(label=f"Grid Search XGBoost model predicted price: ", value='SGD ' + str(round(xgb_pred_val[0])))