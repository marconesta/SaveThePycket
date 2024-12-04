start cmd.exe /c python.exe Sensor_Temp_and_Hum.py temp_and_hum_setting.json
@REM start cmd.exe /c python.exe Sensor_Temp_and_Hum.py temp_and_hum_setting_2.json
start cmd.exe /c python.exe Sensor_keyboard.py 
start cmd.exe /c python.exe Sensor_weight.py weight_settings.json
@REM start cmd.exe /c python.exe Sensor_weight.py weight_settings_2.json
start cmd.exe /c python.exe Sensor_led.py led_settings.json
@REM start cmd.exe /c python.exe Sensor_led.py led_settings_2.json
start cmd.exe /c python.exe Sensor_Relaydoor.py
start cmd.exe /c python.exe Sensor_Relaybox.py relay_box_settings.json
@REM start cmd.exe /c python.exe Sensor_Relaybox.py relay_box_settings_2.json
@REM start cmd.exe /c python.exe postman_simulator.py
start cmd.exe /c python.exe Sensor_doorbell.py

