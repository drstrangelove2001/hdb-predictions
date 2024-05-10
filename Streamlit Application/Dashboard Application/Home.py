import streamlit as st

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

st.title('HDB Rentals and Resales - A Brief Picture')

# st.markdown('#### Navigate to different sections on the tab to the left to find out more')

st.divider()

st.markdown('##### ****HDB Rentals****')
st.markdown('Visualize the rental trends of HDBs in the years 2021-2023 based on parameters like flat types, rental prices, time and more.')

st.markdown('##### ****HDB Resales****')
st.markdown('Visualize the resale trends of HDBs in the years 1990-2024 based on parameters like flat types, rental prices, time and more.')

st.markdown('##### ****HDB Compare****')
st.markdown('A feature to compare and visualize HDBs across any two towns in Singapore (both rental and resale trends) and analyze which town is better suited for you!')

st.markdown('##### ****HDB Predict****')
st.markdown('Predict the resale price of a HDB in Singapore with your own preferences!')

st.sidebar.markdown('''
Data taken from https://beta.data.gov.sg/. 
''')