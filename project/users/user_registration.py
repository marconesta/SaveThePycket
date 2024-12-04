import json
import requests
import cherrypy
import time
import sys

class UserManager(): # create a user manager class that registers the user in the resource catalog 
    def __init__(self, user_settings, service_catalog_settings):
        self.user_settings = user_settings
        self.service_settings = service_catalog_settings
        
    def registration(self):
        with open(self.user_settings) as f:
            data = json.load(f)
            
        #request to the service catalog about the resource catalog
        with open(self.service_settings) as f: # get the settings of the building
            service_info = json.load(f)
            ip_service = service_info["ip_address"]
            service_port = service_info["ip_port"]
        info_request = "http://" + ip_service + ":" + str(service_port) + "/resource_catalog" # request of information to the service catalog about the resource catalog
        rc_info = requests.get(info_request) #get the ip address and port of resource catalog
        rc_info_dict = rc_info.json()
        ip_rc = rc_info_dict["ip_address"]
        port_rc = rc_info_dict["ip_port"]

        resource_request = "http://" + ip_rc + ":" + str(port_rc) + "/register_user"
        registration_req = requests.post(resource_request, data = json.dumps(data))
        #print(registration_req.status_code)

if __name__ == '__main__':
    user_manager = UserManager("user_settings.json", "service_catalog_settings.json")
    user_manager.registration()
    print("USER REGISTRATION")
    while True:
        #print("patate")
        time.sleep(300)
   


        
