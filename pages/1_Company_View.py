#Import Libraries
from haversine import haversine
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium as fl
import numpy as np

st.set_page_config(page_title = 'Company view', page_icon = '🎯', layout = 'wide')

#===========================================================================================#
#                                       Functions                                           #
#===========================================================================================#

def country_map(df):
    """This function generates a map visualization to display delivery locations based on city and 
       road traffic density.

       Input: Dataframe
       Output: None
    """
    df_aux = (df.loc[:, ["City","Road_traffic_density", "Delivery_location_latitude", "Delivery_location_longitude"]]
                .groupby(["City","Road_traffic_density"])
                .median()
                .reset_index())
    map = fl.Map()
    for index,info_location in df_aux.iterrows():
        fl.Marker([info_location['Delivery_location_latitude'],
                   info_location["Delivery_location_longitude"]]).add_to(map)
    folium_static(map,width = 1024,height=600)
    return 

def order_share_by_week(df):
    """This function generates a line chart visualization to display the share of orders per delivery
        person over weeks.

    Input: DataFrame
    Output: Line chart

    """
    df_aux01 = df.loc[:,["ID","Week_of_Year"]].groupby("Week_of_Year").count().reset_index()
    df_aux02 = df.loc[:,["Delivery_person_ID","Week_of_Year"]].groupby("Week_of_Year").nunique().reset_index()
    df_aux = pd.merge(df_aux01,df_aux02, how = 'inner')
    df_aux['Order_by_Delivery'] = df_aux["ID"] / df_aux["Delivery_person_ID"]
    fig = px.line(df_aux, x = "Week_of_Year",y = "Order_by_Delivery")
    return fig
    
def order_by_week(df):
    """ This function generates a line chart visualization to display the trend of orders over weeks
        in a year.

        Input: DataFrame
        Output: Line chart 
    """
    df['Week_of_Year'] = df['Order_Date'].dt.strftime("%U")
    cols = ["ID", "Week_of_Year"]
    df_aux = df.loc[:,cols].groupby("Week_of_Year").count().reset_index()
    fig = px.line(df_aux, x = 'Week_of_Year', y = 'ID')
    return fig

def traffic_order_city(df):
    """ This function generates a scatter plot visualization to display the relationship between
        city, road traffic density, and the count of orders.

        Input: DataFrame
        Output: Scatter plot

    """
    cols = ["ID", "City","Road_traffic_density"]
    df_aux = df.loc[:,cols].groupby(["City","Road_traffic_density"]).count().reset_index()
    fig = px.scatter(df_aux, x = "City", y = "Road_traffic_density", size = "ID",color = "City")
    return fig
    
def traffic_order_share(df):
    """ This function generates a pie chart visualization to display the share of orders
        across different levels of road traffic density.
        
        Input: Dataframe
        Output: Pie chart
    """
    cols = ["ID","Road_traffic_density"]
    df_aux = df.loc[:,cols].groupby("Road_traffic_density").count().reset_index()
    df_aux['Entregas_percent'] = df_aux["ID"] /df_aux["ID"].sum()
    fig = px.pie(df_aux,values = "Entregas_percent", names = "Road_traffic_density")
    return fig

def order_metric(df):
    """ This function generates a bar chart visualization to display order metrics over day.
    
        Input: Dataframe
        Output: Bar chart
    """
    cols = ["ID", "Order_Date"]
    df_aux = df.loc[:,cols].groupby("Order_Date").count().reset_index()
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
    return fig

def clean_dataframe(df):
    """ This function clean the dataframe
    
        Types of cleaning
        1. Remove all lines with "NaN"
        2. Changing the data column type
        3. Removing spaces from text columns
        4. Date column formatting
        5. Removing text from the numeric variable(Column taken_time(min))
        6. Text removed for simplification(Column Weatherconditions)
        
        Input: Dataframe
        Output: Dataframe
    """
    
    #1. Revome all lines with "NaN"
    df = df.loc[df['Delivery_person_Age'] != 'NaN ', :]
    df = df.loc[df['Time_Orderd'] != 'NaN ', :]
    df = df.loc[df['multiple_deliveries'] != 'NaN ', :]
    df = df.loc[df['Festival'] != 'NaN ', :]
    df = df.loc[df['City'] != 'NaN ', :]

    #2. Changing the data column type
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

    #3. Removing spaces from text columns
    df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
    df.loc[:,'Delivery_person_ID'] = df.loc[:,'Delivery_person_ID'].str.strip()
    df.loc[:,'Weatherconditions'] = df.loc[:,'Weatherconditions'].str.strip()
    df.loc[:,'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
    df.loc[:,'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()    
    df.loc[:,'Type_of_vehicle'] = df.loc[:,'Type_of_vehicle'].str.strip()
    df.loc[:,'Festival'] = df.loc[:,'Festival'].str.strip()
    df.loc[:,'City'] = df.loc[:,'City'].str.strip()
    
    #4. Date column formatting
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )
    
    #5. Removing text from the numeric variable(Column taken_time(min))
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    #6. Text removed for simplification(Column Weatherconditions)
    df['Weatherconditions'] = df['Weatherconditions'].apply(lambda x: x.split('conditions ')[1])

    
    return df

#================================================================================================================================#
#                                           Beginning of the logical structure of the code                                       #
#================================================================================================================================#

#Import dataframe
df = pd.read_csv("dataset/train.csv")

#Cleaning dataframe
df1 = clean_dataframe(df)




#===========================================================================================#
#                                  Sidebar Streamlit                                        #
#===========================================================================================#
#Image_path = 'C:\\Users\\User\\Documents\\repos\\ftc_python\\logo.png'
logo = Image.open('logo.png')

st.sidebar.image(logo, width = 100)
st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown(' ## Fastest and Best Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown(' ## Select a deadline')
data_slider = st.sidebar.slider('Until what date to analyze?', 
                                value = datetime(2022, 4, 13 ),
                                min_value= datetime(2022, 2, 11),
                                max_value= datetime(2022, 4, 6),
                                format ='DD-MM-YYYY')
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect("Under what traffic conditions?",['Low','Medium','High','Jam'],default = ['Low','Medium','High','Jam'])
st.sidebar.markdown("""---""")

st.sidebar.markdown(" ### Powered by Paulo R. O. Ferreira")


#Date filter
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas,:]

#Date traffic
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

#===========================================================================================#
#                                Layout Streamlit                                           #
#===========================================================================================#
tab1, tab2, tab3 = st.tabs(['Managerial Vision', 'Tactical Vision','Geographic Vision'])

with tab1:
    with st.container():
        st.markdown('# Orders by day')
        fig = order_metric(df1)
        st.plotly_chart(fig,use_container_width = True)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('## Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig,use_container_width = True)
        with col2:
            st.markdown('## Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig,use_container_width = True)

with tab2:
    with st.container():
        st.markdown('# Orders by week')
        fig = order_by_week(df1)
        st.plotly_chart(fig,use_container_width = True)
    with st.container():
        st.markdown('# Orders Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig,use_container_width = True)
with tab3:
    st.markdown('# Country Maps')
    country_map(df1)
   
  




