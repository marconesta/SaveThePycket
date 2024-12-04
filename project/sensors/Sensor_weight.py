from Sensor_Manager import *
import random 
import sys 
import random 
import time
import json

class SensorWeight(SensorManager):
    def __init__(self):
        SensorManager.__init__(self)
        self.is_relay_open = False
        self.weight = 0.0

    def notify(self, topic, msg):
        print("msg: ", msg)
        jsonMsg=json.loads(msg)
    
        value=jsonMsg["info_sensor"][0]["value"] 
        if value == "True": # if the relay has opened from the postman
            self.weight = random.uniform(weight_ref+5, weight_ref+50)
            self.is_relay_open = True

        else: # if the relay has opened from the user
            self.is_relay_open = False
            self.weight = 0.0

if __name__ == "__main__":
    print("Starting weight sensor")
    sensor = SensorWeight()
    #sys.argv[1] = "weight_settings.json"
    sensor.registration(sys.argv[1],"service_catalog_settings.json")
    
    if sensor.sensorID=='NOT FOUND' and sensor.topic=='NOT FOUND' and sensor.sensor_type =='NOT FOUND' and sensor.sensor_unit=='NOT FOUND'and sensor.sensor_location=='NOT FOUND' and sensor.broker=='NOT FOUND' and sensor.port=='NOT FOUND':
        print("Error: Service Catalog not found")
        exit()
    sensor.start() # start the sensor manager
    weight_ref = 0
    #box_topic = "sensor_Relbox_"+str(sensor.boxID)
    #sensor.mySubscribe("SaveThePycket/sensors/"+box_topic) # subscribe to the topic of the relay of the box
    #print("topic: ", sensor.topic) #WE SHOULD CHANGE THE TOPIC OF EACH SENSOR WHEN REGISTERING (COMPLETE TOPIC)
    #sensor.mySubscribe("SaveThePycket/sensors/doorbells/sensor_dB_1")
    box_topic = sensor.boxID 
    building_topic = sensor.buildingID
    sensor.mySubscribe("SaveThePycket/sensors/sensor_Relbox_"+str(building_topic)+"_"+str(box_topic))

    #sensor.notify = sensor.reactToRelay_box
        #weight=0
        #sensor.myPublish(weight, sensor.sensor_location, sensor.sensor_type, sensor.sensor_unit) # publish the temperature
    while True:

        if sensor.is_relay_open:
            print("Publishing weight: ", sensor.weight)
            # f = open("weight.txt", "r")
            # weight = float(f.readline().strip())
            # f.close()
            # print("Publishing weight: ", weight)
            sensor.myPublish(sensor.weight, sensor.sensor_location, sensor.sensor_type, sensor.sensor_unit)
            time.sleep(5)
        else:
            # f = open("weight.txt", "w")
            # f.write(str(weight))
            # f.close()
            print("Publishing weight: ", sensor.weight)
            sensor.myPublish(sensor.weight, sensor.sensor_location, sensor.sensor_type, sensor.sensor_unit)
            time.sleep(5)

