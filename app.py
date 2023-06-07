import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
#from functions.functions_data import get_engagement_list, get_global_daily, get_rolling, get_daily_users_list, get_rolling_values
#from functions.functions_graphics import plot_engagements_users, plot_metrics, get_engagements_by_age
#from functions.functions_graphics import get_metrics_by_age
from functions.functions_data import get_engagement_list, get_global_daily, get_rolling, get_rolling_values
from functions.functions_graphics import plot_engagements_users, plot_metrics

#Set title, icon, and layout
st.set_page_config(
     page_title="FinHabits",
     page_icon="guitar",
     layout="wide")

#function to load data
@st.cache_data()
def load_data():
    #read the data
    path_to_csv = "data/data_20230606.csv"

    df = pd.read_csv(path_to_csv)
    #change data type
    df['EventDateTime'] = pd.to_datetime(df['EventDateTime'], infer_datetime_format=True, format='mixed')
    return df

#tabs
tab1, tab2 = st.tabs(["Engagements users", "Engagements Metrics"])

#bins of age
age_bins = {
   "18-29" : (18,29),
   "30-39" : (30,39),
   "40-49" : (40,49),
   "50-59" : (50,59),
   "60-69" : (60,69),
   "70-79" : (70,79)
}

#load data and create a copy
df = load_data()
df_filter = df.copy()

#En el primer tab
with tab1:
    #contenedor
    with st.container():
        #tres columnas
        col1, col2,col3 = st.columns((2, 2,2))
        with col1:
            #year-month-day
            start_date = st.date_input(label='From date', key="sd1")
        with col2:
            #lookback
            lookback = st.number_input(label='Lookback',step=1, value = 1358, key="lb1")
        with col3:
            #rolling quantity
            rolling_quantity = st.number_input(label='Rolling Quantity',step=1, value = 7, key="rq1")

    #filtros adicionales
    with st.container():
        st.text("Filter")
        filters_text = []
        #Filter to age
        by_age = st.checkbox('Age')
        if by_age:
            age_filter = st.selectbox( "Bins",("18-29", "30-39","40-49","50-59","60-69","70-79"))
            #filter df
            df_filter = df_filter[df_filter['Age'].between( age_bins[age_filter][0], age_bins[age_filter][1] )]
            filters_text.append("Age: " + age_filter )

        #Filter to platform
        by_platform = st.checkbox('Plataforma')
        if by_platform:
            platform_filter = st.selectbox( "Plataforma",("iOS", "Android"))
            #filter df
            df_filter = df[df['Mobile_Device'] == platform_filter]
            filters_text.append("Mobile_Device: " + platform_filter )


    #data for the plot
    engagement_list = get_engagement_list(df = df_filter, lookback = int(lookback), from_date=pd.Timestamp(str(start_date)))
    global_metrics = get_global_daily(engagement_list)
    rolled = get_rolling(global_metrics,int(rolling_quantity), engagement_list)
    #plot
    fig = plot_engagements_users(rolled, str(rolling_quantity) +' days')

    st.subheader("Engagement ")

    if filters_text:
        st.write("with filters")
        for f in filters_text:
            st.write(f)

    #plot in streamlit
    st.plotly_chart(
        fig,
        theme="streamlit",
    )


with tab2:
    #contenedor
    with st.container():
        col1, col2,col3 = st.columns((2, 2,2))
        with col1:
            #year-month-day
            start_date_metric = st.date_input(label='From date', key="sd2")
        with col2:
            #
            lookback_metric = st.number_input(label='Lookback',step=1, value = 1358, key="lb2")
        with col3:
            #
            rolling_quantity_metric = st.number_input(label='Rolling Quantity',step=1, value = 7, key="rq2")

    engagement_list = get_engagement_list(df = df, lookback = int(lookback_metric), from_date=pd.Timestamp(str(start_date_metric)))

    rolling_7 = get_rolling_values(engagement_list, rolling_quantity_metric)

    fig2 = plot_metrics(rolling_7,  str(rolling_quantity_metric) +' days')

    fig.update_layout(height=800)
    
    st.plotly_chart(
        fig2,
        theme="streamlit", height=800
    )

 
