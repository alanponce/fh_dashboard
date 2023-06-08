import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import base64
import math

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

@st.cache_data()
def convert_df(df):
    return df.to_csv().encode('utf-8')


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

#paginacion del df
def paginate_dataframe(dataframe, page_size = 10, page_num = 1):
    #cuantos resultados por pagina 
    page_size = page_size

    offset = page_size*(page_num-1)

    return dataframe[offset:offset + page_size]

#contenedor
# Using "with" notation
with st.sidebar:
    with st.form("form"):
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

        age_filter = st.selectbox( "Age Bins", ("All", "18-29", "30-39","40-49","50-59","60-69","70-79"))
        #filter df
        if age_filter != "All":
            df_filter = df_filter[df_filter['Age'].between( age_bins[age_filter][0], age_bins[age_filter][1] )]
            filters_text.append("Age: " + age_filter ) 
        #Filter to platform     

        platform_filter = st.selectbox( "Platform",("All", "iOS", "Android"))
        #filter df
        if platform_filter != "All":
            df_filter = df_filter[df_filter['Mobile_Device'] == platform_filter]
            filters_text.append("Mobile_Device: " + platform_filter ) 

        #Filter to state     

        #Use the key of the diccionary, i mean, the name of the state
        state_filter = st.selectbox( "State",["All",]  + list(diccionario_abreviaturas.keys()))
        #filter df
        if state_filter != "All":
            df_filter = df_filter[df_filter['UserState'] == diccionario_abreviaturas[state_filter]]
            filters_text.append("State: " + state_filter) 

        #Filter to gender     

        gender_filter = st.selectbox( "Gender", ["All"]  + list(gender_list))
        #filter df
        if gender_filter != "All":
            df_filter = df_filter[df_filter['UserGender'] == gender_filter]
            filters_text.append("Gender: " + gender_filter) 

        #Filter to marital status     

        maritalStatus_filter = st.selectbox( "Marital status", ["All"]  + list(maritalstatus_list) )
        if gender_filter != "All":
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
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")


    #this data is used in both plots
    engagement_list = get_engagement_list(df = df_filter, lookback = int(lookback), from_date=pd.Timestamp(str(start_date)))
    

    #En el primer tab, show the first plot
    with tab1:
        #data for the plot
        global_metrics = get_global_daily(engagement_list)
        rolled = get_rolling(global_metrics,int(rolling_quantity), engagement_list)
        #plot 
        fig = plot_engagements_users(rolled, str(rolling_quantity) +' days')

        #show active filters
        if filters_text:
            st.subheader("With filters")
            for f in filters_text:
                st.write(f)

        #plot in streamlit
        st.plotly_chart(
            fig, 
            theme="streamlit", use_container_width=True, height=800
        )
          
        # Show the first 10 records of the filtered DataFrame
        #st.subheader("Filtered Data")
        #st.dataframe(df_filter.head(10))
     
        number = st.number_input('Pagina', value=1,min_value=1, max_value=math.ceil(len(df_filter.index) / 10), step=1)

        st.table(paginate_dataframe(df_filter[['UserId', 'EventDateTime', 'Language', 
                                 'Age', 'UserState', 'Mobile_Device',
                                'UserGender', 'UserMaritalStatus']], 10, number))
 
        csv = convert_df(df_filter)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='df_filter.csv',
            mime='text/csv',
        )
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
          
        #st.table(engagement_list.head(10))
        
        st.subheader("Filtered Data")
        number = st.number_input('Pagina', value=1,min_value=1, max_value=math.ceil(len(df_filter.index) / 10), step=1, key = "paginacion_em")

        st.table(paginate_dataframe(df_filter[['UserId', 'EventDateTime', 'Language', 
                                 'Age', 'UserState', 'Mobile_Device',
                                'UserGender', 'UserMaritalStatus']], 10, number))
 