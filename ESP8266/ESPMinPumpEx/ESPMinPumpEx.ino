//This code is based on https://gist.github.com/mancusoa74/9450227d1251e0a527965e858cf6eebd  

#include <stdio.h>
#include <ESP8266WebServer.h> //Web server tool
#include <ArduinoJson.h> //JSON encoding/decoding tool

#define HTTP_REST_PORT 81
#define WIFI_RETRY_DELAY 500
#define MAX_WIFI_INIT_RETRY 50


const char* wifi_ssid = "SSID";
const char* wifi_passwd = "psswd";

struct Pump { //Small resource "database"
    byte id;
    byte port;
    byte status;
} pump_resource;

const size_t capacity = JSON_OBJECT_SIZE(3); //Used to calculate JSON capacity in memory

ESP8266WebServer http_rest_server(HTTP_REST_PORT);


void init_pump_resource() //Database initialization
{
    pump_resource.id = 1; //Identifier
    pump_resource.port = 2; //GPIO 2 in the hardware board
    pump_resource.status = HIGH; //Status: LOW for on, HIGH for off
    
    pinMode(pump_resource.port, OUTPUT); //Configure port as output
    digitalWrite(pump_resource.port, pump_resource.status); //Initial state
}

int init_wifi() {
    int retries = 0;

    Serial.println("Connecting to WiFi AP..........");

    WiFi.mode(WIFI_STA);
    WiFi.begin(wifi_ssid, wifi_passwd);
    // check the status of WiFi connection to be WL_CONNECTED
    while ((WiFi.status() != WL_CONNECTED) && (retries < MAX_WIFI_INIT_RETRY)) {
        retries++;
        delay(WIFI_RETRY_DELAY);
        Serial.print("#");
    }
    return WiFi.status(); // return the WiFi connection status
}

void get_pump() { //GET /pump action
        DynamicJsonDocument  doc(capacity); //Create document for encoding JSON later
        doc["id"] = pump_resource.id; //Populate JSON object with resource info
        doc["port"] = pump_resource.port;
        doc["status"] = pump_resource.status;
        String buf;
        serializeJson(doc, buf); //Encode JSON string
        http_rest_server.send(200, F("application/json"), buf); //Send JSON response with code 200
}

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

void get_pump_off(){ //GET /pump/off action
   pump_resource.status = HIGH;
   digitalWrite(pump_resource.port, pump_resource.status);
   
   DynamicJsonDocument  doc(capacity);
   doc["id"] = pump_resource.id;
   doc["port"] = pump_resource.port;
   doc["status"] = pump_resource.status;
   String buf;
   serializeJson(doc, buf);
   http_rest_server.send(200, F("application/json"), buf);
}

void config_rest_server_routing() { //Routing function: Set actions for incoming commands and locations
    http_rest_server.on("/", HTTP_GET, []() {
        http_rest_server.send(200, "text/html",
            "Welcome to Minimal REST Server Example");//Welcome page
    });
    http_rest_server.on("/pump", HTTP_GET, get_pump); //Return pump info
    http_rest_server.on("/pump/on", HTTP_GET, get_pump_on); //Turn pump on and return status
    http_rest_server.on("/pump/off", HTTP_GET, get_pump_off);//Turn pump off and return status
}

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
