import matplotlib.pyplot as plt
import numpy as np

from shiny import *
from functions.functions_data import get_global_daily, get_rolling, get_rolling_values
from functions.functions_graphics import plot_engagements_users, plot_metrics
from functions.functions_data import get_engagement_list_v2
import pandas as pd 
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
def remove_nan(df_plot):
  for col in df_plot:
    #get dtype for column
    column_type = df_plot[col].dtype 
    #check if it is a number
    if column_type == int or column_type == float:
        df_plot[col] = df_plot[col].fillna(0)
    else:
        df_plot[col] = df_plot[col].fillna("")
    return df_plot
#create a copy 
df_filter = df.copy()

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

max_date = pd.to_datetime(df.EventDateTime.max())
min_date = pd.to_datetime(df.EventDateTime.min())


app_ui = ui.page_fluid(
    ui.layout_sidebar(

      ui.panel_sidebar(
        ui.input_date("sd", "Start date", value = min_date),
        ui.input_date("ed", "End date", value = max_date),
        ui.input_numeric("rq", "Rolling Quantity", 7, step=1),
        ui.input_selectize("age", "Age Bins", ("All", "18-29", "30-39","40-49","50-59","60-69","70-79")),
        ui.input_selectize("platform", "Platform",("All", "iOS", "Android")),
        ui.input_selectize("state", "State" , ["All",]  + list(diccionario_abreviaturas.keys())),
        ui.input_selectize("gender", "Gender", ["All",]  + list(gender_list) ),
        ui.input_selectize("maritalstatus", "Marital status", ["All",]  + list(maritalstatus_list) ),
        ui.input_action_button("go", "Submit", class_="btn-success"),
        ),
        ui.panel_main(
            ui.navset_tab(
                ui.nav("Engagements users", 
                    ui.output_plot("plot"),
                 ),
                ui.nav("Engagements Metrics", 
                   "t"
                ),
        )
        ))
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.plot(alt="A plot")
    @reactive.event(input.go, ignore_none=False)
    def plot():
        filters_text = []
        df_filter = df.copy()
        #filter df
        if input.age() != "All":
            df_filter = df_filter[df_filter['Age'].between( age_bins[input.age()][0], age_bins[input.age()][1] )]
            filters_text.append("Age: " + input.age()  ) 
        #filter df
        if input.platform() != "All":
            df_filter = df_filter[df_filter['Mobile_Device'] == input.platform()]
            filters_text.append("Mobile_Device: " + input.platform() ) 
        #filter df
        if input.state() != "All":
            df_filter = df_filter[df_filter['UserState'] == diccionario_abreviaturas[input.state()]]
            filters_text.append("State: " + input.state()) 
        #filter df
        if input.gender() != "All":
            df_filter = df_filter[df_filter['UserGender'] == input.gender()]
            filters_text.append("Gender: " + input.gender()) 
        #filter df
        if input.maritalstatus() != "All":
            df_filter = df_filter[df_filter['UserMaritalStatus'] == input.maritalstatus()]
            filters_text.append("Marital Status: " + input.maritalstatus() )

        #this data is used in both plots
        engagement_list = get_engagement_list_v2(df = df_filter, start_date= str(input.sd()), end_data= str(input.ed()))
        
        #data for the plot
        global_metrics = get_global_daily(engagement_list)
        rolled = get_rolling(global_metrics,int(input.rq()), engagement_list)
        #quita nan
        #rolled = remove_nan(rolled)

        fig = plt.plot(list(rolled.index), list(rolled.Engagements),  list(rolled.index), list(rolled.Unique_users))
        return fig


app = App(app_ui, server)