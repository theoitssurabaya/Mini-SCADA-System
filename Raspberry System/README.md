# Raspberry System

## System Overview
The Raspberry System features a SCADA architecture where a laptop running Node-RED acts as the host server. It communicates over a network (Ethernet and Wi-Fi) with two Remote Terminal Units (RTUs): a Raspberry Pi 3 (RTU 1) and an ESP8266 (RTU 2). These RTUs directly interface with N20 micro DC motors via a TB6612FNG driver, a DS18B20 temperature sensor, and digital push buttons.
![System Overview](./overview.png)

## System Topology
Laptop SCADA Server (Node-RED) -> Ethernet Hub & Wi-Fi Extender -> RTU 1 (Raspberry Pi 3) & RTU 2 (ESP8266) -> Stepper Motors, Push Button, Temperature Sensor
![System Topology](./topology.png)

## Components Used
* 12V DC Adapter
* 5V DC Adapter
* LM2596 Buck Converter
* TB6612FNG Motor Driver
* Raspberry Pi 3
* ESP8266 Dev Module
* N20 Motor (x2)
* XB7 Push Button
* DS18B20 Temp Sensor

## IP Configuration

| Device | IP Address | Subnet Mask | Gateway | Connection Method | How to Configure |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SCADA Laptop (Host Server) | 192.168.2.200 | 255.255.254.0 | 192.168.2.1 | Wireless to Company Wifi | Win + R -> `ncpa.cpl` -> Wi-Fi IPv4 Configurations |
| SCADA Laptop (Ethernet) | 192.168.2.210 | 255.255.255.0 | 192.168.2.1 | Wired to Ethernet Switch | Win + R -> `ncpa.cpl` -> Ethernet IPv4 Configurations |
| Raspberry Pi (RTU 1) | 192.168.2.220 | 255.255.255.0 | 192.168.2.1 | Wired to Ethernet Switch | Terminal -> `sudo nmtui` -> Edit connection -> Set static IPv4 for eth0 |
| ESP8266 D1 Mini (RTU 2) | 192.168.2.230 | 255.255.255.0 | 192.168.2.1 | Wireless via Arduino Firmware Code | Arduino IDE -> Add `WiFi.config(ip, gateway, subnet)` inside `setup()` |
| TP-Link Wifi Extender | 192.168.2.240 | 255.255.254.0 | 192.168.2.1 | Wireless Repeater Mode | Browser -> tplinkrepeater.net (or Admin IP) -> Settings -> Network -> LAN -> Set Static IP |

## Wiring Table

### 1. Power
| SOURCE COMPONENT | SOURCE TERMINAL | DESTINATION COMPONENT | DESTINATION TERMINAL |
| :--- | :--- | :--- | :--- |
| 12V DC Adapter | Positive (+) | LM2596 Buck Converter | IN+ |
| 12V DC Adapter | Negative (-) / GND | LM2596 Buck Converter | IN- |
| 12V DC Adapter | Positive (+) | TB6612FNG Motor Driver | VM |
| LM2596 Converter | OUT+ (Set to 5.0V) | Raspberry Pi 3 | Pin 2 or 4 (5V) |
| LM2596 Converter | OUT- (GND) | Raspberry Pi 3 | Pin 6 (GND) |
| 5V DC Adapter | Positive (+) | ESP8266 Dev Module | VIN / 5V |
| 5V DC Adapter | Negative (-) / GND | ESP8266 Dev Module | GND |

### 2. RTU 1: Raspberry Pi 3 -> TB6612FNG Dual DC Motor Driver
| Raspberry Pi 3 Pin | TB6612FNG Pin |
| :--- | :--- |
| Pin 2 or 4 (5V) | VCC |
| Pin 6 (GND) | GND |
| GPIO 17 | PWMA |
| GPIO 18 | AIN1 |
| GPIO 27 | AIN2 |
| GPIO 22 | STBY |
| GPIO 23 | PWMB |
| GPIO 24 | BIN1 |
| GPIO 25 | BIN2 |

### 3. Motor Driver -> N20 Micro DC Motors Output
| TB6612FNG Terminal | Target Component | Wire Connection |
| :--- | :--- | :--- |
| A01 | N20 Motor 1 | Terminal 1 (Red) |
| A02 | N20 Motor 1 | Terminal 2 (Black) |
| B01 | N20 Motor 2 | Terminal 1 (Red) |
| B02 | N20 Motor 2 | Terminal 2 (Black) |

### 4. RTU 2: ESP8266 -> Field Inputs
| ESP8266 Pin | Connected Component | Terminal / Wire |
| :--- | :--- | :--- |
| GND | XB7 Push Button | Terminal 1 (NO) |
| GPIO 5 | XB7 Push Button | Terminal 2 (NO) |
| 3V3 | DS18B20 Temp Sensor | Red Wire (VCC) |
| GND | DS18B20 Temp Sensor | Black Wire (GND) |
| GPIO 4 | DS18B20 Temp Sensor | Yellow Wire (DATA) |

## Protocols & Data Mapping

### 1. Protocols & Ports
* **RTU 1 (Raspberry Pi)**: Modbus TCP Server (Port 502)
* **RTU 2 (ESP8266)**: Modbus TCP Server (Port 502)
* **Virtual PLC (OpenPLC)**: Modbus TCP Server (Port 502)
* **SCADA Server (Node-RED)**: HTTP Web Server (Port 1880)

### 2. Modbus Register Mapping

#### Field Devices (RTUs)
| RTU Node | Register Type | Address | Data Description | Data Range / Values |
| :--- | :--- | :--- | :--- | :--- |
| **Raspberry Pi (RTU 1)** | Holding Register (4x) | 200 | Motor 1 Speed (RPM) | -100 to 100 (Negative = Reverse) |
| **Raspberry Pi (RTU 1)** | Holding Register (4x) | 201 | Motor 2 Speed (RPM) | -100 to 100 (Negative = Reverse) |
| **ESP8266 (RTU 2)** | Holding Register (4x) | 100 | DS18B20 Temperature | °C Scaled by x100 |
| **ESP8266 (RTU 2)** | Discrete Input (1x) | 0 | XB7 Push Button State | 0 (Released), 1 (Pressed) |

#### Virtual PLC (OpenPLC) Central Logic
| Register Type | Address | Data Description |
| :--- | :--- | :--- |
| Coil (0x) | 1 | Node-RED Emergency Stop |
| Coil (0x) | 2 | Node-RED Safety Reset |
| Coil (0x) | 4 | Master Safety Lockout Latch Bit |
| Coil (0x) | 5 | Motor 1 LED Status |
| Coil (0x) | 6 | Motor 2 LED Status |
| Coil (0x) | 7 | Field Override Badge Status |
| Coil (0x) | 8 | Motor 1 Switch Enable |
| Coil (0x) | 9 | Motor 2 Switch Enable |
| Coil (0x) | 10 | Motor 1 Direction |
| Coil (0x) | 11 | Motor 2 Direction |
| Holding Register (4x) | 0 | HMI Temp |
| Holding Register (4x) | 1 | Node-RED Motor 1 Cmd |
| Holding Register (4x) | 2 | Node-RED Motor 2 Cmd |

## Software Setup & Execution Walkthrough

### 1. RTU 1: Raspberry Pi 3
1. **OS Setup**: Flash Raspberry Pi OS onto a microSD card and boot up the Pi. Connect it to the network. *(Note: You can access the Pi remotely via SSH using `ssh pi@192.168.2.220`)*.
2. **Install Dependencies**: Open the Pi's terminal (or your SSH session) and run:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   pip3 install pymodbus RPi.GPIO asyncio
   ```
3. **Transfer Code**: Copy `rtu_terminal.py` to the Raspberry Pi (e.g., `/home/pi/`).
4. **Run Script**: Execute the script via terminal: `python3 /home/pi/rtu_terminal.py`.

#### How to Setup Raspberry Program to Run on Boot
1. Create a new service file:
   ```bash
   sudo nano /etc/systemd/system/scada_rtu.service
   ```
2. Paste the following configuration:
   ```ini
   [Unit]
   Description=SCADA RTU Raspberry Pi Service
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=simple
   ExecStart=/usr/bin/python3 /home/pi/rtu_terminal.py
   WorkingDirectory=/home/pi
   Environment=PYTHONPATH=/home/pi/.local/lib/python3.13/site-packages
   StandardOutput=journal
   StandardError=journal
   Restart=always
   RestartSec=5
   User=root

   [Install]
   WantedBy=multi-user.target
   ```
3. Reload systemd, enable, and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable scada_rtu.service
   sudo systemctl start scada_rtu.service
   ```
4. **Check Service Status**: To verify the service is running, use:
   ```bash
   sudo systemctl status scada_rtu.service
   ```

### 2. RTU 2: ESP8266
1. **Install VSCode & PlatformIO**: Download and install Visual Studio Code, then install the PlatformIO IDE extension.
2. **Create Project**: Open PlatformIO, create a new project, and select your ESP8266 board (e.g., NodeMCU 1.0 or D1 Mini) with the Arduino framework.
3. **Install Libraries**: Open `platformio.ini` and add the following dependencies under `lib_deps`:
   ```ini
   lib_deps =
     paulstoffregen/OneWire
     milesburton/DallasTemperature
     emelianov/modbus-esp8266
   ```
4. **Flash Firmware**: Copy `esp8266Program.cpp` into the `src/` folder (rename to `main.cpp`), adjust the WiFi credentials, and click the PlatformIO **Upload** button to build and flash the board.

### 3. Virtual PLC: OpenPLC
1. **Install Software**: Download and install both OpenPLC Editor and OpenPLC Runtime on your laptop.
2. **Start Runtime**: Open the OpenPLC Runtime and let it run in the background.
3. **Extract Project**: Unzip the `OpenPLC.zip` file containing the project.
4. **Open in Editor**: Open the OpenPLC Editor, then open the unzipped `OpenPLC` folder.
5. **Connect to Runtime**: In the OpenPLC Editor, look at the left panel under "Configuration", open it, and then click **Connect**.
6. **Login**: Use `openplc` for both the username and password. The OpenPLC is now ready.

### 4. SCADA Server (Node-RED)
1. **Start Node-RED**: Run `node-red` on your SCADA laptop.
2. **Import Flow**: 
   - Go to `http://localhost:1880`.
   - Menu > Import, then select `node-REDFlow.json` from the `Raspberry System` directory.
3. **Configure Network**: 
   - Ensure OpenPLC runtime matches the static IPs of the Raspberry Pi (`192.168.2.220`) and ESP8266 (`192.168.2.230`).
   - The Node-RED setup needs to follow the OpenPLC IP, which in this case is the local computer (`127.0.0.1`).
4. **Deploy**: Click the Deploy button.

## System Operation Walkthrough

1. **Access Dashboard**: Open a web browser on the SCADA Server and navigate to `http://localhost:1880/ui` to access the Node-RED HMI.
2. **Safety Reset**: The system features a Safety Lockout mechanism. Before motors can run, ensure the Emergency Stop is disengaged, then click the **Safety Reset** button on the Node-RED dashboard to clear the safety lock latch in the Virtual PLC.
3. **Motor Control**: Use the HMI switches to enable Motor 1 and Motor 2. You can set their rotational direction (FWD/REV) and adjust their speed via the slider.
4. **Thermal Monitoring**: The DS18B20 Temp sensor feeds live data to the dashboard. If the temperature exceeds safe thresholds, the system's thermal logic will trigger warnings or automatically ramp up Motor 2's speed for cooling.
5. **Field Override**: Pressing the physical XB7 Push Button in the field will trigger a physical override status visible on the SCADA dashboard.
6. **Emergency Stop**: Click the Emergency Stop button on the HMI dashboard to immediately halt all operations and engage the Safety Lockout.

## System Power Up & Shutdown Procedures

### Power On Procedure
1. Power up the Network Infrastructure (Wi-Fi Extender & Ethernet Hub).
2. Boot the SCADA Server Laptop and start the OpenPLC Runtime and Node-RED.
3. Plug in the 5V DC Adapter to power on RTU 2 (ESP8266).
4. Plug in the 12V DC Adapter to power on RTU 1 (Raspberry Pi 3) via the LM2596 Buck Converter and TB6612FNG Motor Driver.
5. Wait for the RTUs to connect to the network. The Node-RED dashboard will display live telemetry.

### Power Off Procedure
1. Stop all active motor commands from the Node-RED dashboard to ensure safe states.
2. Shutdown the Raspberry Pi gracefully via SSH (`sudo shutdown -h now`) or Node-RED command if available. Wait for the green ACT LED to stop blinking.
3. Unplug the 12V DC Adapter (Raspberry Pi & Motor Driver power).
4. Unplug the 5V DC Adapter (ESP8266 power).
5. Stop Node-RED and OpenPLC Runtime on the SCADA Server.