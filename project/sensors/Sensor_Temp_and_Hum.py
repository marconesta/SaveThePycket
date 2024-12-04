from Sensor_Manager import *
import random 
import sys 
import time

if __name__ == "__main__":
    print("Sensor Temp and Hum")
    #sys.argv[1] = "temp_and_hum_settings.json"
    sensor1 = SensorManager()
    
    sensor1.registration(sys.argv[1],"service_catalog_settings.json")
   
    
    if sensor1.sensorID=='NOT FOUND' and sensor1.topic=='NOT FOUND' and sensor1.sensor_type =='NOT FOUND' and sensor1.sensor_unit=='NOT FOUND'and sensor1.sensor_location=='NOT FOUND' and sensor1.broker=='NOT FOUND' and sensor1.port=='NOT FOUND':
        print("Error: Service Catalog not found")
        exit()
    #sensor = SensorManager(sensorID, type, sensor_unit, sensor_location, buildingID, boxID, broker, port, topic) # create an instance of the sensor manager
   
    sensor1.start() # start the sensor 1 manager

    temp_ref = 20 # base temperature
    hum_ref = 35 # base humidity
    #print("topic: ", sensor.topic) #WE SHOULD CHANGE THE TOPIC OF EACH SENSOR WHEN REGISTERING (COMPLETE TOPIC)
    #sensor.mySubscribe(sensor.topic) # subscribe to the topic of the sensor (just for debugging)

    #sensor.mySubscribe("SaveThePycket/sensors/sensor_Wg_1") # subscribe to the topic of the weight sensor

    while True:

        temp1 = random.uniform(temp_ref-0.5, temp_ref+0.5) #modificare distribuzione per avere outliers che modifichino la media 

        print("temp1: ", temp1)

        unit_temp = "Celsius"
        type_meas_temp = "temperature" # generate a random temperature around the base temperature 
        print(f"Publishing temperature: {temp1} on {sensor1.topic}")

        sensor1.myPublish(temp1, sensor1.sensor_location, type_meas_temp, unit_temp) # publish the temperature 1

        hum1 = random.uniform(hum_ref-5, hum_ref+5)
        print("hum1: ", hum1)
        unit_hum = "%"
        type_meas_hum = "humidity" # generate a random temperature around the base temperature 
        sensor1.myPublish(hum1, sensor1.sensor_location, type_meas_hum ,unit_hum) # publish the temperature

        #sensor.client.myOnMessageReceived
        time.sleep(10)