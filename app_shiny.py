from shiny import App, render, ui
from shiny import reactive
import numpy as np
import pandas  as pd 
from shinywidgets import output_widget, register_widget

from functions.functions_data import get_global_daily, get_rolling, get_rolling_values
from functions.functions_graphics import plot_engagements_users, plot_metrics
from functions.functions_data import get_engagement_list_v2

#import the data
def load_data():
    #read the data
    path_to_csv = "data/data_20230606.csv"
    df = pd.read_csv(path_to_csv, parse_dates=['EventDateTime'], dtype={'CurrentPlatform': str,
                                                                        'CurrentType': str,
                                                                        'Platform': str,
                                                                        'Version': str})
    #change data type
    df['EventDateTime'] = pd.to_datetime(df['EventDateTime'])

    #Abreviaturas de los estados de USA
    df_states = pd.read_csv("data/abreviaturas_USA.csv")

    return df, df_states

#call the funcion load_data
df, df_states = load_data()

#quita nan
for col in df:
    #get dtype for column
    column_type = df[col].dtype 
    #check if it is a number
    if column_type == int or column_type == float:
        df[col] = df[col].fillna(0)
    else:
        df[col] = df[col].fillna("")

print(df.info())
#create a copy 
df_filter = df.copy()

#diccionario, abreviatura : state
#'Alabama' : 'AL'
df_states = df_states[df_states["Abreviatura"].isin(df.UserState.unique())]
diccionario_abreviaturas = pd.Series(df_states.Abreviatura.values,index=df_states.State).to_dict()

#gender list for the selectbox
gender_list = df[df.UserGender.notna()].UserGender.unique()

#UserMaritalStatus list for the selectbox
maritalstatus_list = df[df.UserMaritalStatus.notna()].UserMaritalStatus.unique()

#get max and min date of a dataframe 
max_date = pd.to_datetime(df.EventDateTime.max())
min_date = pd.to_datetime(df.EventDateTime.min())

app_ui = ui.page_fluid(

    ui.layout_sidebar(

      ui.panel_sidebar(
        ui.input_date("sd", "Start date"),
        ui.input_date("ed", "End date"),
        ui.input_numeric("rq", "Rolling Quantity", 7, step=1),
        ui.input_selectize("age", "Age Bins", ("All", "18-29", "30-39","40-49","50-59","60-69","70-79")),
        ui.input_selectize("platform", "Platform",("All", "iOS", "Android")),
        ui.input_selectize("state", "State" , ["All",]  + list(diccionario_abreviaturas.keys())),
        ui.input_selectize("gender", "Gender", ["All",]  + list(gender_list) ),
        ui.input_selectize("maritalstatus", "Marital status", ["All",]  + list(maritalstatus_list) ),
        ui.input_action_button("sumbit", "Sumbit" , class_="btn-primary"),
      ),

      ui.panel_main(
        ui.navset_tab(
          # elements ----
          ui.nav("Engagements users", 
                 "tab a content",
                 ui.output_table("result"),
                 output_widget("scatterplot"),
                 
                 ),
          ui.nav("Engagements Metrics", "tab b content"),
        )
      ),

    ),
)


def server(input, output, session):
    #this data is used in both plots
    engagement_list = get_engagement_list_v2(df = df_filter, start_date= min_date, end_data= max_date  )
    
     
    #data for the plot
    global_metrics = get_global_daily(engagement_list)
    
    rolled = get_rolling(global_metrics,int(7), engagement_list)
    
    #quita nan
    for col in rolled:
        #get dtype for column
        column_type = rolled[col].dtype 
        #check if it is a number
        if column_type == int or column_type == float:
            rolled[col] = rolled[col].fillna(0)
        else:
            rolled[col] = rolled[col].fillna("")
    #plot 
    fig = plot_engagements_users(rolled, str(7) +' days')
    
    register_widget("scatterplot", fig)
    


app = App(app_ui, server)