from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import calendar
from datetime import datetime, timedelta
import numpy as np
from matplotlib import dates as mpl_dates
import matplotlib.ticker as plticker
import streamlit as st
from MyMQTT import *
import time
import json
import requests
#libraries to authentification
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import json
from streamlit_option_menu import option_menu
import os
#vedi anche st.set_page_config(layout="wide")
# AUTHENTICATION
# Parsa la stringa JSON in un dizionario Python
st.title("SaveThePycket")

def info_resource_cat(service_settings):
    with open(service_settings) as f: # get the settings of the service catalog
            data_service = json.load(f)
            ip_address = data_service["ip_address"]
            ip_port = data_service["ip_port"]  
    info_request = "http://" + ip_address + ":" + str(ip_port) + "/resource_catalog" # request of information to the service catalog about the resource catalog
    rc_info = requests.get(info_request) #get the ip address and port of resource catalog
    rc_info_dict = rc_info.json()
    ip_rc = rc_info_dict["ip_address"]
    port_rc = rc_info_dict["ip_port"]
    return ip_rc, port_rc


if __name__=="__main__":
    # take the actual folder
    actual_folder = os.path.dirname(os.path.abspath("service_catalog_settings.json"))
    print(actual_folder)
    service_settings = "service_catalog_settings.json"
    ip_rc, port_rc = info_resource_cat(service_settings)
    resource_request = "http://" + ip_rc + ":" + str(port_rc) + "/" + "resources"
    resources = requests.get(resource_request)
    data = resources.json()



    # take data from resource catalog of admin
    dict_data_admin = []
    for admin in data["admins"]:
        address_roads = []
        address_numbers=[]
        for building_id in admin["buildingID"]:
            for building in data["buildings"]:
                if building["buildingID"] == building_id:
                    address_roads.append(building["address_road"])
                    address_numbers.append(building["address_number"])
        admin_data = {
            "adminname": admin["admin_name"],
            "buildingID": admin["buildingID"],
            "address_road": address_roads,
            "address_number": address_numbers
        }
        dict_data_admin.append(admin_data)
    adminname=[admin_data["adminname"] for admin_data in dict_data_admin]

    file_path= Path(__file__).parent / "hashed_admin_pw.pickle"

    with file_path.open("rb") as file:
        hashed_admin_password= pickle.load(file)



    # take data from resource catalog of users
    dict_data_users = []
    for user in data["users"]:
        for building in data["buildings"]:
            if user["buildingID"] == building["buildingID"]:
                user_data = {
                    "username": user["user_name"],
                    "buildingID": user["buildingID"],
                    
                }
                dict_data_users.append(user_data)  # Aggiungi l'oggetto user_data alla lista

    usernames = [user_data["username"] for user_data in dict_data_users]

    file_path= Path(__file__).parent / "hashed_user_pw.pickle"

    with file_path.open("rb") as file:
        hashed_user_password= pickle.load(file)

    #append dei due file hasher_user_pw e hashed_admin_pw
    hashed_password = hashed_admin_password + hashed_user_password
    username_total = adminname + usernames

    authenticator= stauth.Authenticate( username_total, username_total , hashed_password, "SaveThePycket", "abcdef", cookie_expiry_days=30)
    name, authentication_status, username = authenticator.login("Login", "main")

    #CONNECTION TO MONGODB
    uri = "mongodb+srv://savethepycketusername:savethepycketpassword@savethepycketdb.n4krejr.mongodb.net/?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client["SaveThePycketDb"]

    def query(coll):
        result = db[coll].aggregate([ {
                "$project":
                    {
                    "_id":0,
                    "info_sensor.type":1,
                    "info_sensor.value":1,
                    "info_sensor.timestamp":1,
                    "info_sensor.buildingID":1,
                    "info_sensor.boxID":1
            }
            },
        ])
        return pd.DataFrame(list(result))

    if authentication_status == False:
        st.error("User/password not valid. Please try again.")
    if authentication_status == None:
        st.warning("Please login to access the app.")
    if authentication_status == True:
        authenticator.logout("Logout", "sidebar")
        if username in adminname:
            st.sidebar.title(f"WELCOME {name.upper()}!")
            def query_all_collections(db):
                #prendi tutti i Building ID relativi a username
                building_id = None
                dict_data_admin_current={}
                collection_names =[]
                for admin_data in dict_data_admin:
                    if admin_data["adminname"] == username:
                        building_id = admin_data["buildingID"]
                        collection_names = ["Building"+str(num) for num in building_id]
                        break
                results = []

                for coll in collection_names:
                    result = query(coll)
                    results.append(result)

                combined_df = pd.concat(results, ignore_index=True)
                return combined_df
            admindf=query_all_collections(db)
            admindf=pd.json_normalize(admindf["info_sensor"])
            # normalizza i dati JSON in nuove colonne
            admindf_normalize = pd.json_normalize(admindf[0])

            # concatena i dati normalizzati al DataFrame originale
            dfadmin = pd.concat([admindf, admindf_normalize], axis=1)

            # rimuovi la colonna originale
            dfadmin = dfadmin.drop(0, axis=1)

            dfadmin["timestamp"] = dfadmin["timestamp"].astype(float).apply(datetime.fromtimestamp) # converte i timestamp in datetime
            dfadmin['timestamp'] = pd.to_datetime(dfadmin['timestamp'])

            # estrae la data e l'ora in due colonne separate
            dfadmin['data'] = dfadmin['timestamp'].dt.date
            dfadmin['ora'] = dfadmin['timestamp'].dt.time 
            dfadmin['ora'] = dfadmin['ora'].astype(str).str.split('.').str[0] # rimuove i millisecondi
            # rimuove la colonna "timestamp"
            dfadmin = dfadmin.drop('timestamp', axis=1)

            #visualize the building 
            st.title("Building Info")
            st.write("Here you can see the information about the buildings you are responsible for:")
            #per ogni buildingID del mio username, prendi l'indirizzo e mettilo in un menu a tendina
            admin_address = []
            for admin_data in dict_data_admin:
                    if admin_data["adminname"] == username:
                        for i in range(len(admin_data['buildingID'])):
                            building_id = admin_data['buildingID'][i]
                            address_roads = admin_data['address_road'][i]
                            address_numbers = admin_data['address_number'][i]
                            #st.write("The buildingID {} corresponds to the address {} number {}".format(building_id, address_roads, address_numbers)
                            admin_address.append(address_roads+ " "+str(address_numbers))
            
            admin_address.append("All")

            print(admin_address)

            selected = option_menu(
                menu_title= "Select the building you want to visualize",
                options= admin_address,    
                default_index=0,
                orientation="horizontal")
            
            if selected == "All":
                st.write("You have selected to visualize all the buildings.")
                st.write("Here you can see the information about the buildings you are responsible for:")
                st.write(admindf)
            elif selected != "All":
                st.write("You have selected to visualize the building: {}".format(selected))
                #prendi il buildingID corrispondente all'indirizzo selezionato
                for admin_data in dict_data_admin:
                    if admin_data["adminname"] == username:
                        for i in range(len(admin_data['buildingID'])):
                            building_id = admin_data['buildingID'][i]
                            address_roads = admin_data['address_road'][i]
                            address_numbers = admin_data['address_number'][i]
                            if address_roads+ " "+str(address_numbers) == selected:
                                selected_building_id = building_id
                                break
                st.write("The buildingID {} corresponds to the address {} number {}".format(selected_building_id, address_roads, address_numbers))
                #seleziona solo i dati relativi al buildingID selezionato
                st.write("Here you can see the information about the building you have selected:")
                dfadmin = dfadmin[dfadmin['buildingID'] == selected_building_id]
                st.write(dfadmin)
                #visualizzo solo i dati relativi a led
                dfadmin_led = dfadmin[dfadmin['type'] == "led"]
                st.write(dfadmin_led)
            
            
        elif username in usernames:
            st.sidebar.title(f"WELCOME {name.upper()}!")

            #DEFINITION OF THE QUERY
            building_id = None
            for user_data in dict_data_users:
                if user_data["username"] == username:
                    building_id = user_data["buildingID"]
                    break
            num_building=building_id  #LO USERNAME DEVE ESSERE UGUALE AL NOME DELLA COLLECTION


            res_building="Building"+str(num_building)
            res=query(res_building)
        

            # CREAZIONE DEL DATAFRAME
            res=pd.json_normalize(res["info_sensor"])
            # normalizza i dati JSON in nuove colonne
            res_normalized = pd.json_normalize(res[0])

            # concatena i dati normalizzati al DataFrame originale
            df = pd.concat([res, res_normalized], axis=1)

            # rimuovi la colonna originale
            df = df.drop(0, axis=1)

            df["timestamp"] = df["timestamp"].astype(float).apply(datetime.fromtimestamp) # converte i timestamp in datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            # estrae la data e l'ora in due colonne separate
            df['data'] = df['timestamp'].dt.date
            df['ora'] = df['timestamp'].dt.time 
            df['ora'] = df['ora'].astype(str).str.split('.').str[0] # rimuove i millisecondi
            # rimuove la colonna "timestamp"
            df = df.drop('timestamp', axis=1)

            #WORKING WITH STREAMLIT
            current_building=int(df["buildingID"][0])
            #TEMPERATURE
            #prendo il numero delle boxes dal numero massimo di boxID
            df = df[df['boxID'] != '']
            df['boxID'] = df['boxID'].astype(int)

            boxes=int(df["boxID"].max())
            #crea un array da 1 al numero di boxes
            boxes=np.arange(1,boxes+1)
            #boxes=[1,2,3,4,5] # number of the boxes

            #st.subheader("BUILDINGS: ")
            #state_building= st.radio("Number of the building",boxes,key=1)
            st.write("You are visualizing the building number:", current_building)
            state_box= st.selectbox("Number of the box",boxes,key=2)
            st.write("You selected the box number:",state_box)
            
            list_sensor=["temperature","humidity","weight", "status of the box"]
            
            for i in range(len(boxes)):
                if state_box==boxes[i]:
                    state_box= st.radio("Choose the sensor you want to visualize",list_sensor,key=3)

                    #''''''''''''''''''''''''temperature''''''''''''''''''''''''''''  
                    if state_box=="temperature":            
                    #state_box= st.radio("Temperature", key=3)
                        st.header("TEMPERATURE")
                        st.subheader("Temperature in the current box:")
                        fig, ax = plt.subplots()
                        current_box=boxes[i]
                        x1 = df["ora"].loc[(df['boxID'] == current_box) & (df['type'] == 'temperature')&(df['buildingID'] == current_building)]
                        y1 = df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'temperature')&(df['buildingID'] == current_building)]
                        ax.plot(x1,y1,label='Temperature in the box '+str(current_box)+' of the building '+str(current_building))
                        ax.legend()
                        loc = plticker.MultipleLocator(base=5) # this locator puts ticks at regular intervals
                        ax.xaxis.set_major_locator(loc)
                        plt.grid()
                        plt.legend()
                        plt.xlabel("Time (s)")
                        plt.ylabel("Temperature (°C)")
                        plt.xticks(rotation=45)
                        plt.title("Temperature in the box "+str(current_box))
                        st.pyplot(fig)

                        mean_temp=round(df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'temperature')&(df['buildingID'] == current_building)].mean(),2)
                        st.write("The mean temperature of the box "+str(current_box)+ " of the building " + str(current_building) + " is: "+ str(mean_temp))
                

                    #''''''''''''''''''''''''humidity''''''''''''''''''''''''''''  
                    if state_box=="humidity":            
                    #state_box= st.radio("Temperature", key=3)
                        st.header("HUMIDITY")
                        st.subheader("Humidity in the Boxes:")
                        fig, ax = plt.subplots()
                        current_box=boxes[i]
                        x1 = df["ora"].loc[(df['boxID'] == current_box) & (df['type'] == 'humidity')&(df['buildingID'] == current_building)]
                        y1 = df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'humidity')&(df['buildingID'] == current_building)]
                        ax.plot(x1,y1,label='Humidity in the box '+str(current_box)+' of the building '+str(current_building))
                        ax.legend()
                        loc = plticker.MultipleLocator(base=5) # this locator puts ticks at regular intervals
                        ax.xaxis.set_major_locator(loc)
                        plt.grid()
                        plt.legend()
                        plt.xlabel("Time (s)")
                        plt.ylabel("Humidity (%)")
                        plt.xticks(rotation=45)
                        plt.title("Humidity in the box "+str(current_box))
                        st.pyplot(fig)

                        mean_hum=round(df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'humidity')&(df['buildingID'] == current_building)].mean(),2)
                        st.write("The mean humidity of the box "+str(current_box)+ " of the building " + str(current_building) + " is: "+ str(mean_hum))


                    #''''''''''''''''''''''''weight''''''''''''''''''''''''''''  
                    if state_box=="weight":
                        st.header("WEIGHT")
                        st.subheader("Weight in the Box:")
                        fig, ax = plt.subplots()
                        current_box=boxes[i]
                        x1 = df["ora"].loc[(df['boxID'] == current_box) & (df['type'] == 'weight')&(df['buildingID'] == current_building)]
                        y1 = df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'weight')&(df['buildingID'] == current_building)]
                        ax.plot(x1,y1,label='weight in the box '+str(current_box)+' of the building '+str(current_building))
                        ax.legend()
                        loc = plticker.MultipleLocator(base=5) # this locator puts ticks at regular intervals
                        ax.xaxis.set_major_locator(loc)
                        plt.grid()
                        plt.legend()
                        plt.xlabel("Time (s)")
                        plt.ylabel("Weight (kg)")
                        plt.xticks(rotation=45)
                        plt.title("Weight in the box "+str(current_box))
                        st.pyplot(fig)

                        mean_weight=round(df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'weight')&(df['buildingID'] == current_building)].mean(),2)
                        st.write("The mean weight of the box "+str(current_box)+ " of the building " + str(current_building) + " is: "+ str(mean_weight))

                        last_value=df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'weight')&(df['buildingID'] == current_building)].iloc[-1]
                        if last_value==0:
                                st.error("The box is empty")
                        else:
                                st.success("The weight of the box is: "+str(last_value)+" kg")

                        #''''''''''''''''''''''''led''''''''''''''''''''''''''''      
                        if state_box=="status of the box":
                            st.header("STATUS OF THE BOX")
                            #st.subheader("State of the box:")
                            fig, ax = plt.subplots()
                            current_box=boxes[i]
                            x1 = df["ora"].loc[(df['boxID'] == current_box) & (df['type'] == 'led')&(df['buildingID'] == current_building)]
                            y1 = df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'led')&(df['buildingID'] == current_building)]
                            ax.plot(x1,y1,label='Status of the box '+str(current_box)+' of the building '+str(current_building))
                            ax.legend()
                            loc = plticker.MultipleLocator(base=5) # this locator puts ticks at regular intervals
                            ax.xaxis.set_major_locator(loc)
                            plt.grid()
                            plt.legend()
                            plt.xlabel("Time (s)")
                            plt.ylabel("Status")
                            plt.xticks(rotation=45)
                            plt.title("Status of the box "+str(current_box))
                            st.pyplot(fig)

                            #prendo l'ultimoo valore della colonna value
                            last_value=df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'led')&(df['buildingID'] == current_building)].iloc[-1]
                            if last_value==0:
                                st.success("The box is free")
                            else:
                                st.error("The box is occupied")
                            #calcolo della percentuale di occupazione rispetto al tempo totale
                            percentuale=round((df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'led')&(df['buildingID'] == current_building)].sum()/len(df["value"].loc[(df['boxID'] == current_box) & (df['type'] == 'led')&(df['buildingID'] == current_building)]))*100,2)
                            st.write("The box has been occupied for "+str(percentuale)+ " % of the time")