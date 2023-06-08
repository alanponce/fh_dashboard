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

    #Abreviaturas de los estados de USA
    df_states = pd.read_csv("data/abreviaturas_USA.csv")

    return df, df_states

#load data and create a copy
df, df_states = load_data()
df_filter = df.copy()

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

#diccionario, abreviatura : state
#'Alabama' : 'AL'
df_states = df_states[df_states["Abreviatura"].isin(df.UserState.unique())]
diccionario_abreviaturas = pd.Series(df_states.Abreviatura.values,index=df_states.State).to_dict()

#gender list for the selectbox
gender_list = df[df.UserGender.notna()].UserGender.unique()

#UserMaritalStatus list for the selectbox
maritalstatus_list = df[df.UserMaritalStatus.notna()].UserMaritalStatus.unique()

#UserEmploymentStatus list for the selectbox
#employmentstatus_list = df[df.UserEmploymentStatus.notna()].UserEmploymentStatus.unique()

#contenedor
# Using "with" notation
with st.sidebar:
    #year-month-day
    start_date = st.date_input(label='From date', key="sd1")
    #lookback
    lookback = st.number_input(label='Lookback',step=1, value = 1358, key="lb1")
    #rolling quantity
    rolling_quantity = st.number_input(label='Rolling Quantity',step=1, value = 7, key="rq1")
    
    #filtros adicionales 
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
    by_platform = st.checkbox('Platform')
    if by_platform:
        platform_filter = st.selectbox( "Platform",("iOS", "Android"))
        #filter df
        df_filter = df_filter[df_filter['Mobile_Device'] == platform_filter]
        filters_text.append("Mobile_Device: " + platform_filter ) 

    #Filter to state     
    by_state = st.checkbox('State')
    if by_state:
        #Use the key of the diccionary, i mean, the name of the state
        state_filter = st.selectbox( "State", diccionario_abreviaturas.keys())
        #filter df
        df_filter = df_filter[df_filter['UserState'] == diccionario_abreviaturas[state_filter]]
        filters_text.append("State: " + state_filter) 

    #Filter to gender     
    by_gender = st.checkbox('Gender')
    if by_gender:
        gender_filter = st.selectbox( "Gender", gender_list)
        #filter df
        df_filter = df_filter[df_filter['UserGender'] == gender_filter]
        filters_text.append("Gender: " + gender_filter) 

    #Filter to marital status     
    by_maritalStatus = st.checkbox('Marital status')
    if by_maritalStatus:
        maritalStatus_filter = st.selectbox( "Marital status", maritalstatus_list)
        #filter df
        df_filter = df_filter[df_filter['UserMaritalStatus'] == maritalStatus_filter]
        filters_text.append("Marital Status: " + maritalStatus_filter) 

    #Filter to employmentStatus
    #by_employmentStatus = st.checkbox('Employment status')
    #if by_employmentStatus:
    #    employmentStatus_filter = st.selectbox( "Employment status", employmentstatus_list)
        #filter df
    #    df_filter = df_filter[df_filter['UserEmploymentStatus'] == employmentStatus_filter]
    #    filters_text.append("Employment status: " + employmentStatus_filter) 

    #this data is used in both plots
    engagement_list = get_engagement_list(df = df_filter, lookback = int(lookback), from_date=pd.Timestamp(str(start_date)))

    #En el primer tab, show the first plot
    with tab1:
        #data for the plot
        global_metrics = get_global_daily(engagement_list)
        rolled = get_rolling(global_metrics,int(rolling_quantity), engagement_list)
        #plot 
        fig = plot_engagements_users(rolled, str(rolling_quantity) +' days')

        #show acvite filters
        if filters_text:
            st.subheader("With filters")
            for f in filters_text:
                st.write(f)

        #plot in streamlit
        st.plotly_chart(
            fig, 
            theme="streamlit", use_container_width=True, height=800
        )
     
        st.table(engagement_list.head(15))
     
    #The second plot
    with tab2:
        #data for the plot
        rolling_7 = get_rolling_values(engagement_list, rolling_quantity)
        #plot 
        fig2 = plot_metrics(rolling_7,  str(rolling_quantity) +' days')

        #show active filters
        if filters_text:
            st.subheader("With filters")
            for f in filters_text:
                st.write(f)
               
        fig.update_layout(height=800)
        
        #plot in streamlit
        st.plotly_chart(
            fig2, 
            theme="streamlit", use_container_width=True, height=800
        )
