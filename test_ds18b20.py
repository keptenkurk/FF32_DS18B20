import ff32ds18b20

sensor=ff32ds18b20.DS18B20(("B", 2))
if sensor.init_success:
    while True:
        temperature=sensor.Read_Temp()
        print(temperature)