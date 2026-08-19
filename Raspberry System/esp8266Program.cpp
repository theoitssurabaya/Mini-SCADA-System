  #include <ESP8266WiFi.h>
  #include <OneWire.h>
  #include <DallasTemperature.h>
  #include <ModbusIP_ESP8266.h>

  // Network Credentials & Static IP
  const char* ssid     = "YOUR_WIFI_SSID";
  const char* password = "YOUR_WIFI_PASSWORD";
  IPAddress local_IP(192, 168, 2, 230);
  IPAddress gateway(192, 168, 2, 1);
  IPAddress subnet(255, 255, 255, 0);

  // Hardware Pins
  #define ONE_WIRE_BUS 4       // D2 (GPIO4)
  #define BUTTON_PIN   5       // D1 (GPIO5)

  OneWire oneWire(ONE_WIRE_BUS);
  DallasTemperature sensors(&oneWire);
  ModbusIP mb;

  // Modbus Register Mapping
  const int TEMP_REG   = 100;  
  const int BUTTON_IST = 0;    

  unsigned long lastUpdate = 0;
  bool lastButtonState = false; 

  void setup() {
    Serial.begin(115200);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    sensors.begin();

    Serial.println("   ESP8266 Modbus TCP Slave - Initializing   ");
    
    Serial.print("[WiFi] Connecting to: ");
    Serial.println(ssid);
    
    WiFi.config(local_IP, gateway, subnet);
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) { 
      delay(500); 
      Serial.print("."); 
    }
    
    Serial.println("\n[WiFi] Connected Successfully!");
    Serial.print("[WiFi] Assigned IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("[WiFi] Signal Strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");

    mb.server();
    mb.addHreg(TEMP_REG, 0);
    mb.addIsts(BUTTON_IST, 0);
    
    Serial.println("[Modbus] TCP Server listening on Port 502");
    Serial.println("[Modbus] Reg 100 (Holding) -> DS18B20 Temp");
    Serial.println("[Modbus] Ist 0 (Discrete)  -> Push Button");
  }

  void loop() {
    mb.task();

    // Digital Input Logic
    bool isPressed = (digitalRead(BUTTON_PIN) == LOW);
    mb.Ists(BUTTON_IST, isPressed);

    // Only print to Serial Monitor if the button state actually changed
    if (isPressed != lastButtonState) {
      lastButtonState = isPressed;
      Serial.print("[Digital Input] Button State Changed -> ");
      if (isPressed) {
        Serial.println("PRESSED (Modbus Discrete Input 0 = 1)");
      } else {
        Serial.println("RELEASED (Modbus Discrete Input 0 = 0)");
      }
    }

    // Analog Input Logic
    if (millis() - lastUpdate > 1000) {
      lastUpdate = millis();
      sensors.requestTemperatures();
      float tempC = sensors.getTempCByIndex(0);
      
      if (tempC != DEVICE_DISCONNECTED_C) {
        int16_t modbusTemp = (int16_t)(tempC * 100); 
        mb.Hreg(TEMP_REG, modbusTemp);
        
        // Print live telemetry to monitor
        Serial.print("[Analog Read] DS18B20: ");
        Serial.print(tempC);
        Serial.print(" °C | Scaled Modbus Val (Reg 100): ");
        Serial.println(modbusTemp);
      } else {
        Serial.println("[ERROR] DS18B20 Sensor Disconnected or Wiring Fault!");
      }
      
      // Warn if Wi-Fi drops mid-operation
      if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[WARNING] Wi-Fi Connection Lost! Attempting reconnect...");
      }
    }
  }