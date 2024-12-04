# create a sensor manager class that registers the sensor in the catalog and publishes the sensor data with MQTT
import json
import requests
import cherrypy
import time
from MyMQTT import *
import random
import keyboard

class SensorManager(): # create a sensor manager class that registers the sensor in the catalog and publishes the sensor data with MQTT
    def __init__(self):
        self.sensorID = "" 
        self.sensor_name = ""
        self.sensor_type = ""
        self.sensor_unit = ""
        self.sensor_location = ""
        self.buildingID = ""
        self.boxID = ""
        self.topic = ""
        self.client = ""
        self.broker = ""
        self.port = ""
        self.__message = {
                                    'topic': self.topic, 
                                    'info_sensor': [
                                            {
                                                'type':self.sensor_type,
                                                'unit':self.sensor_unit,
                                                'timestamp':'',
                                                'value':'',
                                                'location':'',
                                                'buildingID':'',
                                                'boxID':'',
                                                'sensor_name':''
                                            }
                                        ]
                }
    def registration (self, settings, service_catalog_settings): # registration of a new sensor in the catalog
        with open(settings) as f: # get the settings of the sensor
            data = json.load(f)
            buildingID = data["buildingID"]
            sensorID = data["sensorID"]
            sensor_type = data["sensor_type"] 
            sensor_unit = data["sensor_unit"]
            sensor_location = data["sensor_location"] 
            topic = data["topic"]
            if "boxID" in data:
                boxID = data["boxID"]
                sensor_name = data["sensor_name"]
           
        with open(service_catalog_settings) as f: # get the settings of the service catalog
            data_service = json.load(f)
            ip_address = data_service["ip_address"]
            ip_port = data_service["ip_port"]
        
        #print("DATAAAA: ", type(data))
        info_request = "http://" + ip_address + ":" + str(ip_port) + "/resource_catalog" # request of information to the service catalog about the resource catalog
        rc = requests.get(info_request)
        #print("Get request from Sensor to Service", rc)
        rc_dict = rc.json()
        #print(rc_dict)
        mqtt_request = "http://" + ip_address + ":" + str(ip_port) + "/mqtt_connection" # request of information to the service catalog about the mqtt broker
        mqtt = requests.get(mqtt_request)
        #print("Get request from Sensor to Service", mqtt)
        mqtt_dict = mqtt.json()
        #print(mqtt_dict)
        if len(rc_dict) == 0 and len(mqtt_dict) == 0: # if there is no resource catalog
            return "NOT FOUND", "NOT FOUND", "NOT FOUND", "NOT FOUND", "NOT FOUND", "NOT FOUND", "NOT FOUND", "NOT FOUND", "NOT FOUND", "NOT FOUND"
        else:
            request = "http://" + rc_dict["ip_address"] + ":" + str(rc_dict["ip_port"]) + "/register_sensor" # request to the resource catalog to register a global sensor
            #print(request)
            #print(json.dumps(data))
            requests.post(request, data = json.dumps(data))
            
            self.sensorID = sensorID
            self.sensor_type = sensor_type
            self.sensor_unit = sensor_unit
            self.sensor_location = sensor_location
            self.buildingID = buildingID
            self.topic = topic
            if "boxID" in data:
                self.boxID = boxID
                self.sensor_name = sensor_name
            self.broker = mqtt_dict["broker"]
            self.port = mqtt_dict["broker_port"]

            # create an instance of the MQTT client
            self.client = MyMQTT(self.sensorID, self.broker, self.port, self)
    
    def start (self): # start the MQTT client
        self.client.start()
    
    def stop (self): # stop the MQTT client
        self.client.stop()

    def myPublish (self, value, location, type_meas, unit): # publish a message with a certain topic
        msg = self.__message
        msg['info_sensor'][0]['type'] = type_meas # update the type of measurement
        msg['info_sensor'][0]['unit'] = unit # update the unit of measure
        msg['info_sensor'][0]['value'] = value # update the value of the sensor
        msg['info_sensor'][0]['timestamp'] = str(time.time()) # update the timestamp of the sensor
        msg['info_sensor'][0]['location'] = location # update the location of the sensor
        msg['info_sensor'][0]['buildingID'] = self.buildingID # update the buildingID of the sensor
        if self.boxID != "": # if the sensor is in a box 
            msg['info_sensor'][0]['boxID'] = self.boxID # update the boxID of the sensor
            msg['info_sensor'][0]['sensor_name'] = self.sensor_name # update the sensor name
        # publish a message with a certain topic
        #print(f"publishing {msg} on topic {self.topic}")
        self.client.myPublish(self.topic, msg) 
    
    def mySubscribe (self, topic): # subscribe to a certain topic
        self.client.mySubscribe(topic)

    def notify(self, topic, msg): # notify the sensor manager that a message has been received
        jsonMsg=json.loads(msg)
        value=jsonMsg["info_sensor"][0]["value"]
        print("Value received: "+str(value))

    def reactToSound(self,topic,msg): #notify method of the keyboard
        topic_doorbell = topic.split("_") # split the topic of the doorbell in order to get the order userID  
        code = input("Postman, you must insert the order code!!!!") # the postman must insert the order number of the packet in order to open the door
        # now this code must be published on the topic of the keyboard in order to allow telegram to send this code to the user
        self.myPublish(code+"&"+topic_doorbell[-1], self.sensor_location, self.sensor_type, self.sensor_unit) 
        print(code+"&"+topic_doorbell[-1])
        '''password="ciao" #for debugging purposes
        if code==password:  
            print("Access granted")'''
        
    # def reactToWeight_box(self, topic, msg):
    #     print("TOPIC", topic)
    #     jsonMsg=json.loads(msg)
    #     print(jsonMsg['info_sensor'][0]['value'])
    #     print(type(jsonMsg['info_sensor'][0]['value']))
    #     msg_int= jsonMsg['info_sensor'][0]['value']
    #     if msg_int != 0 :
    #         print("REACT TO WEIGHT: True")
    #         led_is_on_msg="True"
    #     else:
    #         print("REACT TO WEIGHT: False")
    #         led_is_on_msg="False"
            
    #     self.myPublish(led_is_on_msg, self.sensor_location, self.sensor_type, self.sensor_unit)

    # def reactToTelegram(self, topic, msg): #aprire la porta e la box
    #     if topic.startswith('SaveThePycket/telegram/doors/'):
    #         if msg == "open":
    #             #relay door publishes that it is open
    #             self.myPublish("Open", self.sensor_location, self.sensor_type, self.sensor_unit)
            
    #     elif topic.startswith('SaveThePycket/telegram/boxes/'):
    #         if msg == "open":
    #             print("Opening box")
    #             box_is_open = "True"
    #             self.myPublish(box_is_open, self.sensor_location, self.sensor_type, self.sensor_unit) 
        

    # def reactToRelay_box(self, topic, msg):
    #     print("REACT TO RELAY BOX")
    #     self.myPublish(25, self.sensor_location, self.sensor_type, self.sensor_unit)
 



    # button = input("Premi il tasto w per simulare che la scatola sia occupata: \n ")

    #     if button == "w":
    #         weight = round(random.uniform(1, 5000), 2)
    #         print("weight:"+ str(weight))
    #         is_occupied = True

    #         while is_occupied:
    #             # Simulazione della pubblicazione del peso
    #             #print(f"IS OCCUPIED, publishing {weight} on {self.topic}")
    #             self.myPublish(weight, self.sensor_location, self.sensor_type, self.sensor_unit)
    #             time.sleep(5)
    #             # Verifica se si desidera terminare la simulazione premendo "w" nuovamente
    #             if keyboard.is_pressed("w"):
    #                 is_occupied = False
    #             if button == "f":
    #                 is_occupied = False

    

   