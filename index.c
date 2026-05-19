#include <PZEM004Tv30.h>
#include <WiFi.h>
#include <PubSubClient.h>

// ========== WiFi & MQTT Credentials ==========
const char* WIFI_SSID = "Air University";
const char* WIFI_PASSWORD = "Pak@12345";
const char* MQTT_BROKER = "td182d6f.ala.asia-southeast1.emqxsl.com";
const int MQTT_PORT = 8883;
const char* MQTT_USERNAME = "Hammad";
const char* MQTT_PASSWORD = "Hammad@123";
const char* MQTT_TOPIC = "sensors/smart-grid-unit-01";

// ========== MQTT Client ==========
WiFiClientSecure wifiClient;
PubSubClient mqttClient(wifiClient);

// ========== Timing ==========
unsigned long lastPublish = 0;
const long PUBLISH_INTERVAL = 5000;

// ========== YOUR EXISTING PINS ==========
#define RELAY1 4
#define RELAY2 5
#define RELAY3 9
#define RELAY4 10
#define BUZZER 8

float INPUT_MAX_VOLTAGE = 242.0;
float INPUT_MIN_VOLTAGE = 198.0;
float OUTPUT_MAX_VOLTAGE = 120.0;
float OUTPUT_MIN_VOLTAGE = 95.0;
float MAX_CURRENT = 5.0;

HardwareSerial SerialPZEM1(1);
HardwareSerial SerialPZEM2(2);

PZEM004Tv30 pzem1(SerialPZEM2, 19, 20, 0x01); // Input
PZEM004Tv30 pzem2(SerialPZEM2, 19, 20, 0x02); // Load 1
PZEM004Tv30 pzem3(SerialPZEM1, 15, 16, 0x03); // Load 2
PZEM004Tv30 pzem4(SerialPZEM1, 15, 16, 0x04); // Load 3

bool load1Fault = false, load2Fault = false, load3Fault = false;

// ========== Connection Functions ==========
void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
}

void connectMQTT() {
  wifiClient.setInsecure();
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  while (!mqttClient.connected()) {
    if (mqttClient.connect("ESP32", MQTT_USERNAME, MQTT_PASSWORD)) {
      Serial.println("MQTT connected!");
    } else {
      delay(5000);
    }
  }
}

// ========== PUBLISH ALL SENSOR DATA ==========
void publishData() {
  // Read all sensors
  float input_voltage = pzem1.voltage();
  float input_current = pzem1.current();
  float input_power = pzem1.power();
  float input_energy = pzem1.energy();
  float input_frequency = pzem1.frequency();
  
  float voltage_1 = pzem2.voltage();
  float current_1 = pzem2.current();
  float power_1 = pzem2.power();
  float energy_1 = pzem2.energy();
  float frequency_1 = pzem2.frequency();
  
  float voltage_2 = pzem3.voltage();
  float current_2 = pzem3.current();
  float power_2 = pzem3.power();
  float energy_2 = pzem3.energy();
  float frequency_2 = pzem3.frequency();
  
  float voltage_3 = pzem4.voltage();
  float current_3 = pzem4.current();
  float power_3 = pzem4.power();
  float energy_3 = pzem4.energy();
  float frequency_3 = pzem4.frequency();
  
  // Build JSON with ALL fields matching your InfluxDB schema
  String payload = "{";
  payload += "\"timestamp\":" + String(millis()) + ",";
  payload += "\"voltage_1\":" + String(input_voltage) + ",";
  payload += "\"current_1\":" + String(input_current) + ",";
  payload += "\"power_1\":" + String(input_power) + ",";
  payload += "\"energy_1\":" + String(input_energy, 3) + ",";
  payload += "\"frequency_1\":" + String(input_frequency) + ",";
  payload += "\"voltage_2\":" + String(voltage_1) + ",";
  payload += "\"current_2\":" + String(current_1) + ",";
  payload += "\"power_2\":" + String(power_1) + ",";
  payload += "\"energy_2\":" + String(energy_1, 3) + ",";
  payload += "\"frequency_2\":" + String(frequency_1) + ",";
  payload += "\"voltage_3\":" + String(voltage_2) + ",";
  payload += "\"current_3\":" + String(current_2) + ",";
  payload += "\"power_3\":" + String(power_2) + ",";
  payload += "\"energy_3\":" + String(energy_2, 3) + ",";
  payload += "\"frequency_3\":" + String(frequency_2) + ",";
  payload += "\"voltage_4\":" + String(voltage_3) + ",";
  payload += "\"current_4\":" + String(current_3) + ",";
  payload += "\"power_4\":" + String(power_3) + ",";
  payload += "\"energy_4\":" + String(energy_3, 3) + ",";
  payload += "\"frequency_4\":" + String(frequency_3);
  payload += "}";
  
  mqttClient.publish(MQTT_TOPIC, payload.c_str());
  Serial.println("All sensor data published");
}

// ========== SETUP ==========
void setup() {
  Serial.begin(115200);
  
  SerialPZEM2.begin(9600, SERIAL_8N1, 19, 20);
  SerialPZEM1.begin(9600, SERIAL_8N1, 15, 16);
  
  pinMode(RELAY1, OUTPUT);
  pinMode(RELAY2, OUTPUT);
  pinMode(RELAY3, OUTPUT);
  pinMode(RELAY4, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  
  digitalWrite(RELAY1, HIGH);
  digitalWrite(RELAY2, HIGH);
  digitalWrite(RELAY3, HIGH);
  digitalWrite(RELAY4, HIGH);
  digitalWrite(BUZZER, LOW);
  
  connectWiFi();
  connectMQTT();
  
  delay(3000);
  
  digitalWrite(RELAY1, LOW);
  digitalWrite(RELAY2, LOW);
  digitalWrite(RELAY3, LOW);
  digitalWrite(RELAY4, LOW);
  
  Serial.println("System Ready");
}

// ========== LOOP ==========
void loop() {
  mqttClient.loop();
  
  checkMainInput();
  checkLoad(pzem2, RELAY2, "LOAD 1", load1Fault);
  checkLoad(pzem3, RELAY3, "LOAD 2", load2Fault);
  checkLoad(pzem4, RELAY4, "LOAD 3", load3Fault);
  
  if (millis() - lastPublish > PUBLISH_INTERVAL) {
    publishData();
    lastPublish = millis();
  }
  
  delay(2000);
}

// ========== YOUR EXISTING FUNCTIONS ==========
void checkMainInput() {
  float voltage = pzem1.voltage();
  float current = pzem1.current();
  
  if(isnan(voltage)) return;
  
  Serial.print("Input: "); Serial.print(voltage); Serial.print("V, ");
  Serial.print(current); Serial.println("A");
  
  if(voltage > INPUT_MAX_VOLTAGE || voltage < INPUT_MIN_VOLTAGE || current > MAX_CURRENT) {
    shutdownMainSystem();
  }
}

void checkLoad(PZEM004Tv30 &pzem, int relayPin, String loadName, bool &faultStatus) {
  float voltage = pzem.voltage();
  float current = pzem.current();
  
  if(isnan(voltage)) return;
  
  if(voltage > OUTPUT_MAX_VOLTAGE || voltage < OUTPUT_MIN_VOLTAGE || current > MAX_CURRENT) {
    digitalWrite(relayPin, HIGH);
    faultStatus = true;
    digitalWrite(BUZZER, HIGH);
  } else if(!faultStatus) {
    digitalWrite(relayPin, LOW);
    digitalWrite(BUZZER, LOW);
  }
}

void shutdownMainSystem() {
  digitalWrite(RELAY1, HIGH);
  digitalWrite(RELAY2, HIGH);
  digitalWrite(RELAY3, HIGH);
  digitalWrite(RELAY4, HIGH);
  digitalWrite(BUZZER, HIGH);
  while(1);
}