The project aims to streamline and digitize parcel delivery management in apartment buildings or shared buildings. Through a combination of IoT sensors, Telegram bots and a scalable software infrastructure, it offers an intelligent system to improve communication between couriers, residents and building administrators.

The main goal is to ensure a secure, reliable and automated process for managing deliveries, reducing the risk of lost parcels, minimizing interaction time and providing a smooth experience for both residents and couriers.

What the project does:
Doorbell detection via sound sensors:

When a courier rings the doorbell, a sound sensor detects the sound and sends a notification via Telegram to the corresponding user.
The system uses a configurable sound threshold to distinguish the sound of the doorbell from other environmental noises.
Delivery code management:

The courier can enter a delivery code via a keypad associated with the sound sensor.
The code is forwarded directly to the correct user, allowing the user to verify and authorize the opening of the box or door.
Integration with Telegram:

Users can register for the system via a Telegram bot.
The bot allows users to:
Monitor the status of the boxes (occupied/vacant).
Check associated sensors (temperature, humidity, weight).
Receive real-time notifications regarding deliveries or any anomalies (e.g., box too hot or humid).
Open the door or an associated box remotely.
Box management:

Boxes are monitored by sensors that detect parameters such as temperature, humidity, and weight.
Users can choose which box to use based on availability and detected parameters.
If all boxes are occupied, the system alerts the user and administrator, suggesting possible improvements to system management.
Statistics and monitoring:
The system collects useful data for analysis, including:
Number of registered users per building.
Percentage of use of the boxes.
Events when all boxes are occupied.
Temperature/humidity trends and associated risk thresholds.
This data is used to improve the efficiency and scalability of the system.
Scalability and flexibility:

The platform supports the management of multiple buildings and allows users to change their registration parameters, such as buildingID, by contacting the manager.
The system is designed to be easily expandable, thanks to an architecture based on MQTT and REST API, as well as a centralized dashboard for administration.
Key Benefits.
Efficiency: Minimizes the interaction time between courier and recipient, making the delivery process faster and smoother.
Security: Ensures correct association of the delivery code with the recipient, preventing errors or theft.
Automation: Integration of sensors and Telegram bots eliminates the need for continuous human intervention.
Intelligent monitoring: Allows complete control of boxes and sensors, with proactive notifications in case of anomalies.
Scalability: Can be deployed in buildings of different sizes, with flexibility in adding new sensors or features.
