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

st.set_page_config(page_title = 'Delivery view', page_icon = '🏍️', layout = 'wide')
#===========================================================================================#
#                                       Functions                                           #
#===========================================================================================#

def bot_delivers(df):
    """ This function calculates the bottom delivery drivers in each city based on the maximum delivery time.

        Imput: Dataframe
        Output: Dataframe
    """
    
    dfmedia_entregador = (df.loc[:,['Time_taken(min)','City','Delivery_person_ID']]
                                .groupby(['City','Delivery_person_ID'])
                                .max().sort_values(['City','Time_taken(min)'],ascending=False)
                                .reset_index())
    df_aux1 = dfmedia_entregador.loc[dfmedia_entregador['City'] == 'Metropolitian',:].head(10)
    df_aux2 = dfmedia_entregador.loc[dfmedia_entregador['City'] == 'Semi-Urban',:].head(10)
    df_aux3 = dfmedia_entregador.loc[dfmedia_entregador['City'] == 'Urban',:].head(10)
    df_lentos = pd.concat([df_aux1,df_aux2,df_aux3]).reset_index(drop = True)
    return df_lentos

def top_delivers(df):
    """This function calculates the top delivery drivers in each city based on the minimum delivery time.

        Input: Dataframe
        Output: Dataframe
    """
    dfmedia_entregador = (df.loc[:,['Time_taken(min)','City','Delivery_person_ID']]
                            .groupby(['City','Delivery_person_ID'])
                            .min().sort_values(['City','Time_taken(min)'],ascending=True)
                            .reset_index())
    df_aux1 = dfmedia_entregador.loc[dfmedia_entregador['City'] == 'Metropolitian',:].head(10)
    df_aux2 = dfmedia_entregador.loc[dfmedia_entregador['City'] == 'Semi-Urban',:].head(10)
    df_aux3 = dfmedia_entregador.loc[dfmedia_entregador['City'] == 'Urban',:].head(10)
    df_rapidos = pd.concat([df_aux1,df_aux2,df_aux3]).reset_index(drop = True)
    return df_rapidos

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


#Data filter
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas,:]
#Traffic filter
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]
#Climate filter
linhas_selecionadas = df1['Weatherconditions'].isin(climate_options)
df1 = df1.loc[linhas_selecionadas,:]
#===========================================================================================#
#                                Layout Streamlit                                           #
#===========================================================================================#

with st.container():
    st.title('Overall Metrics')
    col1,col2,col3,col4 = st.columns(4, gap ='Large')
    with col1:
        maior_idade = df1['Delivery_person_Age'].max()
        col1.metric('Oldest age', maior_idade)
    with col2:
        menor_idade = df1['Delivery_person_Age'].min()
        col2.metric('Youngest age', menor_idade)
    with col3:
        melhor_condicao = df['Vehicle_condition'].max()
        col3.metric('Best condition', melhor_condicao)
    with col4:
         pior_condicao = df['Vehicle_condition'].min()
         col4.metric('Worst condition', pior_condicao)

with st.container():
    st.markdown("""---""")
    st.markdown('# Ratings')
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('###### Average ratings per delivery person')
        dfmedia_entregador = (df1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
                                .groupby('Delivery_person_ID')
                                .mean()
                                .reset_index())
        st.dataframe(dfmedia_entregador)
    with col2:
        st.markdown('###### Average ratings per traffic density')
        dfmedia = (df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                           .groupby('Road_traffic_density')
                           .agg( {'Delivery_person_Ratings' : ['mean' , 'std']} ))
        dfmedia.columns = ['Delivery_mean','Delivery_std']
        dfmedia.reset_index()
        st.dataframe(dfmedia)
        st.markdown('###### Average ratings per Weather conditions')
        dfmedia = (df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                    .groupby('Weatherconditions')
                    .agg( {'Delivery_person_Ratings' : ['mean' , 'std']} ))
        dfmedia.columns = ['Delivery_mean','Delivery_std']
        dfmedia.reset_index()
        st.dataframe(dfmedia)
with st.container():
    st.markdown("""---""")
    st.markdown('# Delivery speed')
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('#### Fastest delivery drivers')
        df_rapidos = top_delivers(df1)
        st.dataframe(df_rapidos)
    with col2:
        st.markdown('#### Slowest delivery drivers')
        df_lentos = bot_delivers(df1)
        st.dataframe(df_lentos)
            
























