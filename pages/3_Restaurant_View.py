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

st.set_page_config(page_title = 'Restaurant view', page_icon = '🥧', layout = 'wide')
#===========================================================================================#
#                                       Functions                                           #
#===========================================================================================#

def avg_std_time_on_traffic(df):
    """ This function calculates the average delivery time and its standard deviation per city and road traffic density
        and visualizes it using a sunburst chart.

    Input: Dataframe
    Output: Sunburst chart
    """

    df_aux = df.loc[:,['City','Time_taken(min)','Road_traffic_density']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']} )
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = (px.sunburst(df_aux,path =['City','Road_traffic_density'],
                       values='avg_time',
                       color ='std_time',
                       color_continuous_scale = 'RdBu', 
                       color_continuous_midpoint = np.average(df_aux['std_time'])))
    return fig

def avg_std_graph(df):
    """This function calculates the average delivery time and its standard deviation per city and visualizes it using a grouped bar chart.

       Input: Dataframe
       Output: Bar graph
    """
    df_aux = df.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']} )
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar(name = 'Control',x = df_aux['City'],y = df_aux['avg_time'], error_y = dict(type = 'data', array = df_aux['std_time'])))
    fig.update_layout(barmode = 'group')
    return fig

def calc_distance(df,fig):
    """This function calculates the distance between the restaurant and delivery location using Haversine formula.
    
    Input: Dataframe and Boolean var
    Output: If boolean var =  False: float, else: Pie graph 
    """
    col = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df['Distance'] = df.loc[:, col].apply(lambda x: 
                                            haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                            (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis =1)
    if fig == False:
        media_distancia = np.round(df['Distance'].mean(),2)
        return media_distancia
    else:
        media_distancia = df1.loc[:,['City','Distance']].groupby('City').mean().reset_index()
        fig = go.Figure( data =[go.Pie(labels=media_distancia['City'],values=media_distancia['Distance'],pull = [0,0.1,0])])
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

climate_options = st.sidebar.multiselect("Under what climate conditions?",['Cloudy','Fog','Sandstorms','Stormy','Sunny','Windy'],default = ['Cloudy','Fog','Sandstorms','Stormy','Sunny','Windy'])
st.sidebar.markdown("""---""")

st.sidebar.markdown(" ### Powered by Paulo R. O. Ferreira")


#Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas,:]
#Filtro de tráfego
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]
#Filtro de climas
linhas_selecionadas = df1['Weatherconditions'].isin(climate_options)
df1 = df1.loc[linhas_selecionadas,:]
#===========================================================================================#
#                                Layout Streamlit                                           #
#===========================================================================================#
with st.container():
    st.markdown('# Overall Metrics')
    col1,col2,col3,col4,col5,col6 = st.columns(6)
    with col1:
      
        entregadores_unicos = len(df1['Delivery_person_ID'].unique())
        col1.metric("Delivers", entregadores_unicos)
    with col2:
        media_distancia = calc_distance(df1,False)
        col2.metric("Average distance",media_distancia)
        
    with col3:
       
        dfmedia = np.round(df1.loc[df1['Festival'] == 'Yes','Time_taken(min)'].mean(),2)
        col3.metric("Average time",dfmedia)
    with col4:
        
        dfdesvio = np.round(df1.loc[df1['Festival'] == 'Yes','Time_taken(min)'].std(),2)
        col4.metric("Standard deviation",dfdesvio)
    with col5:
        
        dfmedia = np.round(df1.loc[df1['Festival'] == 'No','Time_taken(min)'].mean(),2)
        col5.metric("Average time ",dfmedia)
    with col6:
        dfdesvio = np.round(df1.loc[df1['Festival'] == 'No','Time_taken(min)'].std(),2)
        col6.metric("Average distance ",dfdesvio)
    st.markdown("""---""")

with st.container():
    st.markdown('## Average delivery time per city')
    col1, col2 = st.columns(2)
    with col1:
        fig = avg_std_graph(df1)
        st.plotly_chart(fig)
    with col2:
        dfmedia = df1.loc[:,['Time_taken(min)','City','Type_of_order']].groupby(['City','Type_of_order']).agg( {'Time_taken(min)' : ['mean' , 'std']} )
        dfmedia.columns = ['Time_mean','Time_std']
        dfmedia.reset_index()
        st.dataframe(dfmedia)
   
with st.container():
    st.markdown("""---""")
    st.markdown('# Time distribution')
    col1,col2 = st.columns(2)
    with col1:
        fig = calc_distance(df1,True)
        st.plotly_chart(fig)
    with col2:
        fig = avg_std_time_on_traffic(df1)
        st.plotly_chart(fig)










  