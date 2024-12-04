from Sensor_Manager import *
import random 
import sys 
import time

class SensorDoorbell(SensorManager):
    def __init__(self):
        SensorManager.__init__(self)
        self.doorbell_is_ringing = "False"


if __name__ == "__main__":
    print("Doorbell sensor")
    sensor = SensorDoorbell()
    
    sensor.registration("doorbell_settings.json","service_catalog_settings.json")
    
    if sensor.sensorID=='NOT FOUND' and sensor.topic=='NOT FOUND' and sensor.sensor_type =='NOT FOUND' and sensor.sensor_unit=='NOT FOUND'and sensor.sensor_location=='NOT FOUND' and sensor.broker=='NOT FOUND' and sensor.port=='NOT FOUND':
        print("Error: Service Catalog not found")
        exit()
    #sensor = SensorManager(sensorID, type, sensor_unit, sensor_location, buildingID, boxID, broker, port, topic) # create an instance of the sensor manager
    sensor.start() # start the sensor manager

    sound_ref = 70 # base temperature
    #print("topic: ", sensor.topic) #WE SHOULD CHANGE THE TOPIC OF EACH SENSOR WHEN REGISTERING (COMPLETE TOPIC)
    #sensor.mySubscribe("SaveThePycket/sensors/sensor_th_1") # subscribe to the topic of the sensor (just for debugging)
    
    while True:
        sound = random.uniform(sound_ref, sound_ref+20)
        print(sound)
        # adding a threshold
        if sound > 75:
            sensor.myPublish(sound, sensor.sensor_location, sensor.sensor_type, sensor.sensor_unit) # publish the sound
            print("Doorbell is ringing!!!!")
            #sensor.client.myOnMessageReceived
        time.sleep(60) 
