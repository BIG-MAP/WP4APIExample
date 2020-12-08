# Pump API
This is a minimal REST API implementation for controlling a dosing pump.

## Specification
The OpenAPI specification can be found here, the yaml can be found here.

## Implementation

### ESP8266
The API has been implemented using an ESP8266 NodeMCU V3.

### Source Code
The software implementation makes use of the ESPWebServer and the ArduinoJson libraries.
Most languages have similar tools and frameworks for handling requests and providing 
responses. Regardless of framework there are three main parts for the code:

* Routing: This part is in charge of matching the incoming request command and path, with the corresponding program routine,
sometimes called action.
* Action:The program routine that is executed when accepting a request, is in charge of interpreting the incoming body of the request.

### Hardware
The following hardware is connected to the ESP8266 device:
* L298N driver board
* 12V, 3W peristaltic dosing pump
* 12V and 5V power source

### Connections
* Pin D4 (GPIO 2) of the ESP8266 is connected to ENA in the L298N board.
* In1 and In2 in the L298N board are connected to 5V and Gnd respectively.
* Ground pins on the ESP8266 and the L298N board are connected.
* The L298N board is powered by 12V.
* The pump terminals is connected to OUT1 and OUT2 on the L298N board.


