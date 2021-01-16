# Pump API
This is a minimal REST API specification and implementation for controlling a dosing pump.

## What is a REST API?
An API (Application Programming Interface) is a software computer interface that can accept requests and provide responses to these requests, REST is a way of communication in which computers interchange data using APIs.

<img src="https://github.com/rmorenoga/pump-api/blob/main/ReadmeImages/SimpleAPI.png" width="700">

Usually, REST APIs match HTTP commands (GET) and paths (/pump), also called URIs (Uniform resource identifiers), to program routines inside the server. Responses and requests can contain data in their body which can be stored in JSON format, a type of human readable data interchange format.

<img src="https://github.com/rmorenoga/pump-api/blob/main/ReadmeImages/HTTPAPI.png" width="700">

# Basic pump API

## Specification
The basic version of the pump API can receive 3 types of requests, with no parameters, all of them use the GET HTTP command so they can be sent from a web browser (Example: typing 190.157.46.49:81/pump prompts the browser to send a GET /pump request to the API server):

* GET /pump: Returns the pump data as a JSON document. Example response body: {“id”:1, “port”:2, “status”: 0}
* GET /pump/on: Turns the pump on and returns the pump data as a JSON document. Example response body: {“id”:1, “port”:2, “status”: 0}
* GET /pump/off: Turns the pump off and returns the pump data as a JSON document. Example response body: {“id”:1, “port”:2, “status”: 1}

## Implementation

The API can be implemented using different computer systems from the API specification. The example in this repository has been implemented using:
* Raspberry Pi Model B and  the Fastapi Python framework
* ESP8266 NodeMCU V3 Wifi [board](http://prometec.org/communications/nodemcu/arduino-ide/) and Arduino

### Raspberry Pi
For this device, the implementation makes use of the Python language and the Fastapi framework. Fastapi can be run in any computer system with a python interpreter. Most programming languages have similar tools and frameworks for developing APIs.
There are two main parts on the source [code](/RasPi/rpiserver/server.py):

* Routing: This part is in charge of matching the incoming request commands (GET), paths (/pump) and their corresponding actions (show_pump_info) inside the api (pump_app)
* Action: The program routine that is executed when handling a request, which is converted to a JSON document by default.

```python
pump_app = FastAPI()

@pump_app.get("/pump", response_model = Pump)
def show_pump_info():
    return pump
```

 The response_model parameter helps the api validate the data that will be sent as a response to the request, models are defined as python classes and use the pydantic python library for automatic validation.

```python
class Pump(BaseModel):
    id: str
    port : int
    status: bool = False
    
pump = Pump(id = 1, port=16).init()
```
Gpio pins in the Raspberry Pi are controller using the [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) package, which comes preinstalled.

```python
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM) #Set the Raspberry pinout order

GPIO.setup(self.port, GPIO.OUT) #Configure a gpio pin as output

GPIO.output(self.port, GPIO.HIGH) #Set a pin high
```

To test the example source code in the Raspberry Pi, copy the file [server.py](/RasPi/rpiserver/server.py) to the Raspberry Pi or clone this repository using git, open a terminal window and install the fastapi and uvicorn packages using pip (make sure the pip3 command is used):

```shell
pip3 install fastapi uvicorn
```

Navigate to the folder where the server.py file is located in the Raspberry Pi, using the cd command, and run

```shell
uvicorn server:pump_app --reload --host 0.0.0.0 --port 8080
```

To access the api open a browser and type the Raspberry Pi ip address with port 8080 at the end (Example: 192.168.0.27:8080/pump). To locate the api address of the raspberry just type in the terminal window.

```shell
hostname -I
```

#### Hardware and Connections 
The following hardware is connected to the Raspberry Pi:

* L298N motor driver [board](https://howtomechatronics.com/tutorials/arduino/arduino-dc-motor-control-tutorial-l298n-pwm-h-bridge/)
* 12V, 3W peristaltic dosing [pump](https://www.adafruit.com/product/1150)
* 12V and 5V power source

Connections:

* Pin 36 (GPIO 16) of the Raspberry Pi is connected to ENA in the L298N board.
* In1 and In2 in the L298N board are connected to 5V and Gnd respectively.
* Ground pins on the Raspberry Pi and the L298N board are connected together and to the main power source ground.
* 12V from the power source is connected to the 12V pin on the L298N board.
* The pump terminals are connected to OUT1 and OUT2 on the L298N board.


### ESP8266
For this device, the software [implementation](/ESP8266/ESPMinPumpEx/ESPMinPumpEx.ino) uses the Arduino language and the ESP8266WebServer and ArduinoJson libraries. It is a very simple implementation but shows the inner workings of an api.
There are two important parts in the code:

* Routing: This part is in charge of matching the incoming request command (i.e GET) and path (i.e. /pump), with the corresponding program routine or action (get_pump function).

```java
void config_rest_server_routing() { //Routing function: Set actions for incoming commands and locations
    http_rest_server.on("/", HTTP_GET, []() {
        http_rest_server.send(200, "text/html",
            "Welcome to Minimal REST Server Example");//Welcome page
    });
    http_rest_server.on("/pump", HTTP_GET, get_pump); //Return pump info
    http_rest_server.on("/pump/on", HTTP_GET, get_pump_on); //Turn pump on and return status
    http_rest_server.on("/pump/off", HTTP_GET, get_pump_off);//Turn pump off and return status
}
```
* Action: The program routine that is executed when handling a request, it is in charge of interpreting the incoming body of the request, building the JSON response (serialization) and sending it through the server.

```java
void get_pump_on(){//GET /pump/on action
   pump_resource.status = LOW; //Change resource status
   digitalWrite(pump_resource.port, pump_resource.status);//Change external pin status
   
   DynamicJsonDocument  doc(capacity);
   doc["id"] = pump_resource.id;
   doc["port"] = pump_resource.port;
   doc["status"] = pump_resource.status;
   String buf;
   serializeJson(doc, buf);
   http_rest_server.send(200, F("application/json"), buf);
}
```
The JSON document is populated using information from a  struct "database".
```java
struct Pump { //Resource "database"
    byte id;
    byte port;
    byte status;
} pump_resource;
```

The web server is initialized by the setup function, which also attempts to connect to the wifi network. The main program loop waits for and handles incoming requests.

```java
void setup() {
  Serial.begin(115200);

    init_pump_resource();
    
    if (init_wifi() == WL_CONNECTED) { //Connect to Wifi
        Serial.print("Connected to ");
        Serial.print(wifi_ssid);
        Serial.print("--- IP: ");
        Serial.println(WiFi.localIP());
    }
    else {
        Serial.print("Error connecting to: ");
        Serial.println(wifi_ssid);
    }

    config_rest_server_routing(); //Configure routing

    http_rest_server.begin();//Start web server
    
    Serial.println("HTTP REST Server Started");
}

void loop() {
  http_rest_server.handleClient();//Handle incoming requests
}
```

In this example the API runs in port 81 (Example: 190.157.46.49:81/pump). The port number can be configured in 

```java
#define HTTP_REST_PORT 81
```
A Wifi network ssid and password must be configured in

```java
const char* wifi_ssid = "SSID";
const char* wifi_passwd = "psswd";
```

To run the example server source code, upload the program to the board using the Arduino [IDE](https://www.arduino.cc/en/software), open the serial monitor tool and reset the board, the ip address of the board will be displayed when connected to the wifi network. For more information on setting up the Arduino IDE to work with the ESP8266 device look [here](https://randomnerdtutorials.com/how-to-install-esp8266-board-arduino-ide/)

#### Hardware and Connections
The same hardware can be connected to the ESP8266 device as with the Raspberry Pi, connection information is as follows:

* Pin D4 (GPIO 2) of the ESP8266 is connected to ENA in the L298N board.
* In1 and In2 in the L298N board are connected to 5V and Gnd respectively.
* Ground pins on the ESP8266 and the L298N board are connected together and to the main power source ground.
* 12V from the power source is connected to the 12V pin on the L298N board.
* The pump terminals are connected to OUT1 and OUT2 on the L298N board.

# Pump API

This more elaborated version of the API adds more functionality, including the posibility of turning the pump on for an specified amount of time and also to take measurements of temperature using a temperature probe of the water. This version also organizes the data to be validated in the JSON request and the data to be sent as a JSON response using models (Specifications of fields and their values). The next diagram shows the main hardware components that are coupled to the API.

<img src="https://github.com/rmorenoga/pump-api/blob/devel/ReadmeImages/PumpSensorTank.jpg" width="700">

## Specification


## Implementation


## Hardware












