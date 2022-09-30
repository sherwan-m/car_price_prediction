#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 14:09:23 2022
@author: ilkayisik
Streamlit app for user based movie recommendations
Changes to the first version:
1. put all the widgets to the sidebar
2. add the time period option in the user id based recommendation
"""
# imports
from email.policy import default
from multiprocessing.sharedctypes import Value
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
from datetime import datetime, date
import os
from joblib import dump, load
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)



dataset = pd.read_csv('data_for_app.csv')
rf_model = load('rf_model_v0.joblib') 


# def other_to_0(input):
#     if input == 'other': 
#         return '0 cylinders'
#     return input


def predict(year, brand, model, condition, cylinders,fuel, odometer, title_status,transmission, drive, size, type, paint_color):
    target_columns= ['year', 'manufacturer', 'model', 'condition', 'cylinders', 'fuel',
       'odometer', 'title_status', 'transmission', 'drive', 'size', 'type',
       'posting_date', 'paint_color']
    if cylinders == 'other' :
        cylinders = '0 cylinders'
    cylinders = int(cylinders.replace(' cylinders', '') ) 
    target_values = [float(year), brand, model, condition, cylinders, fuel, float(odometer),title_status,transmission, drive, size, type,int( date.today().strftime("%Y%m%d")) , paint_color ]
    target = pd.DataFrame(data=np.array(target_values).reshape(-1, 1).T, columns= target_columns) # 

    # target[target_columns] = target_values
    return rf_model.predict(target)

def details_lists_generator(data):
    details_lists = dict()
    details_lists['manufacturer'] = data.manufacturer.sort_values().unique()
    details_lists['cylinders'] = data.cylinders.sort_values().unique()
    details_lists['fuel'] = data.fuel.sort_values().unique()
    details_lists['transmission'] = data.transmission.sort_values().unique()
    details_lists['drive'] = data.drive.sort_values().unique()
    details_lists['size'] = data['size'].sort_values().unique()
    details_lists['type'] = data.type.sort_values().unique()
    return details_lists

def model_list_generator(data, manufacturer):
    model_list = data.loc[lambda df_ : df_['manufacturer'] == manufacturer]['model'].sort_values().unique()
    return model_list
    
def default_detail_generator(data, model):
    target= datamodel_list = data.loc[lambda df_ : df_['model'] == model]
    return target

# to make the the dataframe look nicer
def make_pretty(styler):
    styler.set_caption("Top movie recommendations for you")
    # styler.background_gradient(cmap="YlGnBu")
    return styler
year_list = list(range(2022, 1900, -1))
condition_list = ['salvage', 'fair', 'good', 'excellent', 'like new', 'new']
title_status_list = ['salvage', 'missing', 'parts only', 'rebuilt', 'lien', 'clean']
paint_color_list = ['white', 'blue', 'red', 'black', 'silver', 'grey', 'none', 'brown',
                   'yellow', 'orange', 'green', 'custom', 'purple']
details_list_dict = details_lists_generator(dataset)

def update_model_list():
        st.session_state['model_list'] = model_list_generator(dataset , brand)

if 'model_list' not in st.session_state:
        st.session_state.model_list = []
        
def update_default_details():
     st.session_state.defautl_details = default_detail_generator(dataset, model).reset_index(drop=True)
     
# columns_details = ['cylinders', 'fuel', 'transmission', 'drive',
#        'size', 'type']
# default_valuse = [details_list_dict['cylinders'][0],details_list_dict['fuel'][0],details_list_dict['transmission'][0],
#                   details_list_dict['drive'], details_list_dict['size'][0], details_list_dict['type'][0]]

if 'defautl_details' not in st.session_state:
        st.session_state.defautl_details = pd.DataFrame()
        st.session_state.defautl_details['cylinders'] = [details_list_dict['cylinders'][0]]
        st.session_state.defautl_details['fuel'] = [details_list_dict['fuel'][0]]
        st.session_state.defautl_details['transmission'] = [details_list_dict['transmission'][0]]
        st.session_state.defautl_details['drive'] = [details_list_dict['drive'][0]]
        st.session_state.defautl_details['size'] = [details_list_dict['size'][0]]
        st.session_state.defautl_details['type'] = [details_list_dict['type'][0]]

# %% STREAMLIT
# Set configuration
st.set_page_config(page_title="Car Price Prediction System",
                   page_icon="🎬",
                   initial_sidebar_state="expanded",
                   layout="wide"
                   )

# set colors: These has to be set on the setting menu online
    # primary color: #FF4B4B, background color:#0E1117
    # text color: #FAFAFA, secondary background color: #E50914

# Set the logo of app
st.sidebar.image("https://cdn.pixabay.com/photo/2018/09/06/10/02/car-icon-3657902_960_720.png",
                 width=300, clamp=True)
# welcome_img = Image.open('race-car-309123_960_720.png')
st.image('https://cdn.pixabay.com/photo/2014/04/03/00/41/race-car-309123_960_720.png' , width = 300)
st.sidebar.markdown("""
# Welcome to the car price prediction and recommendation app
""")

# %% APP WORKFLOW
st.sidebar.markdown("""
### How may we help you?
"""
)
# Popularity based recommender system
brand_default = None
main_menu = st.sidebar.radio("I want to :",
                            ('Predict Price', 'Buy a car', 'Sell a car'),
                            help="Just simple choose :)")
if main_menu == 'Predict Price':
    st.write('You selected Know the price of a car.')
elif main_menu == 'Buy a car':
    st.write("You selected Buy a car.")
else:
    st.write("You selected Sell a car")

# Initialization



if main_menu:
    st.markdown("### Please fill the inputs")
    with st.form(key="price_pridector"):
        col1, col2, col3= st.columns([1,1,1])
        with col1 : 
                # update_model_list('acura')
                brand = st.selectbox(
                    "Brand",
                    options=details_list_dict['manufacturer'],
                    # brand_default,
                    help="Select the Brand and pres the Show Models button",
                    # on_change= update_model_list
                    )
                if st.form_submit_button('Show Models'):
                    update_model_list()
                
        with col2 : 
                
                model = st.selectbox(
                    "Model",
                    options=st.session_state.model_list,
                    # brand_default,
                    help="Select the model and pres the Show fill default values",)
                if st.form_submit_button('Fill Defdaults'):
                    update_default_details()
                
        with st.container():
            detail_1, detail_2, detail_3, detail_4= st.columns([1,1,1,1])
            with detail_1 :
                    fuel = st.selectbox(
                        "Fuel",
                        options=details_list_dict['fuel'],
                        index = details_list_dict['fuel'].tolist().index(st.session_state.defautl_details['fuel'][0]),
                        help="Select the fuel type of the car you would like to predict the price",)
                    type = st.selectbox(
                        "type",
                        options=details_list_dict['type'],
                        index = details_list_dict['type'].tolist().index(st.session_state.defautl_details['type'][0]),
                        help="Select the type of the car you would like to predict the price",)
                    condition = st.selectbox(
                        "condition",
                        options=condition_list,
                        # index =,
                        help="Select the condition of the car you would like to predict the price",)
            with detail_2 :
                    cylinders = st.selectbox(
                        "cylinders",
                        options=details_list_dict['cylinders'],
                        index = details_list_dict['cylinders'].tolist().index(st.session_state.defautl_details['cylinders'][0]),
                        help="Select the cylinders of the car you would like to predict the price",)
                    size = st.selectbox(
                        "size",
                        options=details_list_dict['size'],
                        index = details_list_dict['size'].tolist().index(st.session_state.defautl_details['size'][0]),
                        help="Select the size of the car you would like to predict the price",)
                    description = st.text_input(
                        "description",
                        placeholder="Short Description",
                        help="Write a short description of the car you would like to predict the price",)
                    
            with detail_3 :
                    transmission = st.selectbox(
                        "transmission",
                        options=details_list_dict['transmission'],
                        index = details_list_dict['transmission'].tolist().index(st.session_state.defautl_details['transmission'][0]),
                        help="Select the transmission type of the car you would like to predict the price",)
                    paint_color = st.selectbox(
                        "paint_color",
                        options=paint_color_list,
                        # index =,
                        help="Select the paint_color of the car you would like to predict the price",)
                    year = st.selectbox(
                        "year",
                        options=year_list,
                        # index =,
                        help="Select the paint_color of the car you would like to predict the price",)
            with detail_4 :
                    drive = st.selectbox(
                    "drive",
                    options=details_list_dict['drive'],
                    index = details_list_dict['drive'].tolist().index(st.session_state.defautl_details['drive'][0]),
                    help="Select the drive type of the car you would like to predict the price",)
                    title_status = st.selectbox(
                        "title_status",
                        options=title_status_list,
                        # index =,
                        help="Select the title_status of the car you would like to predict the price",)
                    odometer = st.selectbox(
                        "odometer",
                        options=list(range(20000)),
                        # index =,
                        help="Select the odometer of the car you would like to predict the price",)


        submit_button_pop = st.form_submit_button(label="Predit Price")


    if submit_button_pop:
        st.write("The Predicted price is:")
        st.write(
            predict(year, brand, model, condition, cylinders,fuel, odometer, title_status,transmission, drive, size, type, paint_color)[0]  
        )
        st.write("The min price is:        The mean price is:         The max price is:")
        st.write(st.session_state.defautl_details['min_price'][0], st.session_state.defautl_details['avg_price'][0], st.session_state.defautl_details['max_price'][0])
# to put some space in between options
st.write("")
st.write("")
st.write("")
