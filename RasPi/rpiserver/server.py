from typing import Optional, List
from fastapi import FastAPI
from pydantic import BaseModel, Field

import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor
import time

GPIO.setmode(GPIO.BOARD)

IN1 = 16 #GPIO23 to IN1  pump direction 
IN2 = 18 #GPIO24 to IN2  pump direction

ENA = 12 #GPIO18 to ENA PWM SPEED 0 to 100

#initialize GPIO pins
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

#Initialize ENA pin PWM with 1000 frequency
pump = GPIO.PWM(ENA,1000)
pump.start(0)

sensor = W1ThermSensor()	


class Measure(BaseModel):
    measure_type: str = Field(..., title = "The measurement type", description = "The type of measurement to take", max_length = 30, example = " temperature")
    measure_time: List[str] = Field(["at_start","at_end"],title = "The moment of measurement", description = "The moment at which temperature is taken in the process", min_items = 1, max_items = 2)


class Pump_water(BaseModel):
    operation_type: str = Field(..., title = "The operation type", description = "The operation type to run",max_length = 30, example = "pump")
    pumping_time: int = Field(..., title = "The pumping time", description = "The pumping time in seconds", gt = 0, le=100,units = "s", example = 10)
    pumping_speed: int = Field(..., title = "The pump speed", description = "The pump speed as 8bit PWM values", ge = 0, le = 100, units = None, example = 150 )
    input_substance: List[str] = Field(["water"],title="The type of input substance to use", description = "The types of input substances to use in the operation", min_items = 1, max_items =5)
    measure: List[Measure]

    #Pump functions
    def run(self):
        GPIO.output(IN1,True)
        GPIO.output(IN2,False)
        print("IN1", True)
        print("IN2", False)

        #ChangeDutyCycle(speed) function changes the motor speed (accepts values from 0 to 100)
        pump.ChangeDutyCycle(self.pumping_speed)
        print("pump_speed", self.pumping_speed)

    def stop(self):
        GPIO.output(IN2,False)
        GPIO.output(IN1,False)
        print("IN1", False)
        print("IN2", False)
    

class Pump_water_data(BaseModel):
    meta_data: Pump_water
    data: List[float] = Field([], title = "The output data", description = "The data as a list of float values", min_items = 1, example = [0.1,0.5,1.6,2.4,3.9])


pump_app = FastAPI()


@pump_app.on_event("shutdown")
def cleanup_GPIO():
    GPIO.cleanup()

@pump_app.post("/pump_water",response_model=Pump_water_data)
def run_pump_water(operation: Pump_water):

    if len(operation.measure) > 0:
        tempData = []
    else:
        tempData = [-1]

    if len(operation.measure) > 0:
        for item in operation.measure:
            if ("at_start" in item.measure_time):
                tempData.append(sensor.get_temperature())
                print("Taking temp at start")


    operation.run()
    time.sleep(operation.pumping_time)
    operation.stop()

    
    if len(operation.measure) > 0:
        for item in operation.measure:
            if ("at_end" in item.measure_time):
                tempData.append(sensor.get_temperature())
                print("Taking temp at end")

    pump_data = Pump_water_data(meta_data=operation,data=tempData) #TODO: include one data entry per entry in measure list
    return pump_data



