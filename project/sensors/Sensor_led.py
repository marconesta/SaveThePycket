from Sensor_Manager import *
import random 
import sys 
import random 
import time
import json
import requests

class SensorLed(SensorManager):
    def __init__(self):
        SensorManager.__init__(self)
        self.service_settings = "service_catalog_settings.json"
     
    def notify(self, topic, msg):
        #print("TOPIC", topic)
        jsonMsg=json.loads(msg)
        #print(jsonMsg['info_sensor'][0]['value'])
        #print(type(jsonMsg['info_sensor'][0]['value']))
        msg_int= jsonMsg['info_sensor'][0]['value']
        print("Peso ricevuto dal weight: ", msg_int)
        if msg_int != 0 :
            print("REACT TO WEIGHT: True")
            led_is_on_msg="True"
        else:
            print("REACT TO WEIGHT: False")
            led_is_on_msg="False"
            
        #get request to the rc to know the last status of the box
        with open(self.service_settings) as f: # get the settings of the building
            service_info = json.load(f)
            ip_service = service_info["ip_address"]
            service_port = service_info["ip_port"]
        info_request = "http://" + ip_service + ":" + str(service_port) + "/resource_catalog" # request of information to the service catalog about the resource catalog
        rc = requests.get(info_request)
        rc_dict = rc.json()

        last_status_request = "http://" + str(rc_dict["ip_address"]) + ":" + str(rc_dict["ip_port"]) + "/box_status?boxID="+str(self.boxID)+"&buildingID="+str(self.buildingID) # request of information to the service catalog about the resource catalog
        last_status = requests.get(last_status_request) 
        print("last status request result: ", last_status)
        print("last status request result text: ", last_status.text)
        last_status_json = json.loads(last_status.text)

        if last_status_json['status'] != led_is_on_msg:
            print("The status of the box has changed", led_is_on_msg)
            print("The status of the box was", last_status_json['status'])
            #put request to the resource catalog to change the status of the box
            modify_status_request = "http://" + str(rc_dict["ip_address"]) + ":" + str(rc_dict["ip_port"]) + "/change_box_status?boxID="+str(self.boxID)+"&buildingID="+str(self.buildingID)
            modify_status_req = requests.put(modify_status_request, data = json.dumps(led_is_on_msg))
            print("Result of changing the status of box:", modify_status_req.status_code)

        self.myPublish(led_is_on_msg, self.sensor_location, self.sensor_type, self.sensor_unit)

if __name__ == "__main__":
    print("STARTING LED SENSOR")
    sensor = SensorLed()
    #sys.argv[1] = "led_settings.json"
    sensor.registration(sys.argv[1],"service_catalog_settings.json")
    
    if sensor.sensorID=='NOT FOUND' and sensor.topic=='NOT FOUND' and sensor.sensor_type =='NOT FOUND' and sensor.sensor_unit=='NOT FOUND'and sensor.sensor_location=='NOT FOUND' and sensor.broker=='NOT FOUND' and sensor.port=='NOT FOUND':
        print("Error: Service Catalog not found")
        exit()

    sensor.start() # start the sensor manager
    
    box_topic = "sensor_Wg_"+str(sensor.buildingID) + "_" + str(sensor.boxID)
    print("The topic to subscribe is SaveThePycket/sensors/"+box_topic)
    sensor.mySubscribe("SaveThePycket/sensors/"+box_topic) # subscribe to the topic of the weight sensor

    #FOR DEBUGGINF PURPOSES
    # topic_to_subscribe = "SaveThePycket/sensors/sensor_Wg_1"
    # sensor.mySubscribe(topic_to_subscribe) # subscribe to the topic of the weight sensor
    
    #print("topic: ", sensor.topic) #WE SHOULD CHANGE THE TOPIC OF EACH SENSOR WHEN REGISTERING (COMPLETE TOPIC)
    #sensor.notify = sensor.reactToWeight_box
    led_is_on_msg="False"

    while True:
        #print("SONO NEL WHILE DEL LED")
        
        #sensor.myPublish(led_is_on_msg, sensor.sensor_location, sensor.sensor_type, sensor.sensor_unit) # publish the temperature
        time.sleep(1)
        