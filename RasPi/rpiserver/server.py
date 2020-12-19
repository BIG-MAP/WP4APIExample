from fastapi import FastAPI
from pydantic import BaseModel

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Pump(BaseModel):
    id: str
    port : int
    status: bool = False

    def init(self):
        GPIO.setup(self.port, GPIO.OUT)
        return self

    def turn_on(self):
        GPIO.output(self.port, GPIO.HIGH)
        self.status = True

    def turn_off(self):
        GPIO.output(self.port GPIO.LOW)
        self.status = False   

pump = Pump(id = 1, port=16).init()

pump_app = FastAPI()

@pump_app.on_event("shutdown")
def turn_off_pumps():
    pump.turn_off()

@pump_app.get("/pump", response_model = Pump)
def show_pump_info():
    return pump
    
@pump_app.get("/pump/on", response_model = Pump)
def turn_on_pump():
    pump.turn_on()
    return pump

@pump_app.get("/pump/off", response_model = Pump)
def turn_off_pump():
    pump.turn_off()
    return pump