# Pump API
This is a minimal REST API specification and implementation for controlling a dosing pump.

## What is a REST API?
An API (Application Programming Interface) is a software computer interface that can accept requests and provide responses to these requests, REST is a way of communication in which computers interchange data using APIs.

Usually, REST APIs match HTTP commands (GET) and paths (/pump), also called URIs (Uniform resource identifiers), to program routines inside the server. Responses and requests can contain data in their body which can be stored in JSON format, a type of human readable data interchange format.

## Specification
The minimal pump API can receive 3 types of requests, with no parameters, all of them use the GET HTTP command so they can be sent from a web browser (Example: typing 190.157.46.49:81/pump prompts the browser to send a GET /pump request to the API server):

* GET /pump: Returns the pump data as a JSON document. Example response body: {“id”:1, “port”:2, “status”: 0}
* GET /pump/on: Turns the pump on and returns the pump data as a JSON document. Example response body: {“id”:1, “port”:2, “status”: 0}
* GET /pump/off: Turns the pump off and returns the pump data as a JSON document. Example response body: {“id”:1, “port”:2, “status”: 1}

## Implementation

The API can be implemented using different computer systems from the API specification. The example in this repository has been implemented using: 
* ESP8266 NodeMCU V3 Wifi [board](http://prometec.org/communications/nodemcu/arduino-ide/) and Arduino
* Raspberry Pi Model B and  the Fastapi Python framework


### ESP8266
For this device, the software implementation is built using the Arduino language and makes use of the ESP8266WebServer and ArduinoJson libraries. It is a very simple implementation and can run almost immediately with no configuration. An example using a modern framework (Fastapi) can be seen in the Raspberry pi section.
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

In this example the API runs in port 81, thus when sending a request from the browser is must have ":81" attached at the end (Example: 190.157.46.49:81/pump), the port can be configured in 

```java
#define HTTP_REST_PORT 81
```

#### Hardware and Connections
The following hardware is connected to the ESP8266 device:

* L298N motor driver [board](https://howtomechatronics.com/tutorials/arduino/arduino-dc-motor-control-tutorial-l298n-pwm-h-bridge/)
* 12V, 3W peristaltic dosing [pump](https://www.adafruit.com/product/1150)
* 12V and 5V power source

Connections:

* Pin D4 (GPIO 2) of the ESP8266 is connected to ENA in the L298N board.
* In1 and In2 in the L298N board are connected to 5V and Gnd respectively.
* Ground pins on the ESP8266 and the L298N board are connected together and to the main power source ground.
* The pump terminals are connected to OUT1 and OUT2 on the L298N board.

### Raspberry Pi
For this device, the implementation makes use of the Python language and the Fastapi framework. Fastapi is a modern API development framework in which programming is fairly straightforward but requires a few more configuration steps to run. Most languages have similar tools and frameworks for developing APIs.
As in the ESP8266 implemetation routing and actions are also present in a more compact form. Python decorators are used to specifiy request commands (GET), paths (/pump) and their corresponding actions (show_pump_info) inside the api (pump_app):

```python
pump_app = FastAPI()

@pump_app.get("/pump", response_model = Pump)
def show_pump_info():
    return pump
```

The parameter response_model helps the api validate the data sent as a response to the request, which is a JSON document by default, models are defined as python classes and use the python library pydantic for automatic validation.

```python
class Pump(BaseModel):
    id: str
    port : int
    status: bool = False
    
pump = Pump(id = 1, port=16).init()
```
Gpio pins in the Raspberry Pi are controller using the [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) library, which comes preinstalled

```python
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM) #Set the Raspberry pinout order

GPIO.setup(self.port, GPIO.OUT)

GPIO.output(self.port, GPIO.HIGH)
```

To test the example source code in the Raspberry Pi, open a terminal window and install fastapi and uvicorn, a simple web server tool, using pip (make sure the pip3 is used):

```shell
pip3 install fastapi uvicorn
```
Navigate to the folder where the server.py file is located in the Raspberry Pi using the cd command and run

```shell
uvicorn server:pump_app --reload --host 0.0.0.0 --port 8080
```

To access the api open a browser and use the Raspberry Pi ip address (Example: 192.168.0.27:8080/pump). To locate the api address of the raspberry just type in the terminal window

```shell
hostname -I
```

#### Hardware and Connections 
The same hardware is used as in the ESP8266 case, connections are as follows:

* Pin 36 (GPIO 16) of the Raspberry Pi is connected to ENA in the L298N board.
* In1 and In2 in the L298N board are connected to 5V and Gnd respectively.
* Ground pins on the ESP8266 and the L298N board are connected together and to the main power source ground.
* The pump terminals are connected to OUT1 and OUT2 on the L298N board.










