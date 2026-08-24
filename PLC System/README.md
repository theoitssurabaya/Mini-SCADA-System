# PLC System

## System Overview
The PLC System utilizes a Node-RED SCADA Server that communicates with an Omron CP2E PLC over Ethernet. The Omron PLC acts as the central controller for the field instrumentation, processing inputs from push buttons, an emergency stop, and a PT100 temperature sensor, while driving NEMA 17 stepper motors via TB6600 motor drivers.
![System Overview](./overview.jpeg)

## System Topology
Node-RED SCADA Server -> Omron PLC -> (Transmitter, E-Stop Button, Safety Reset Button, Motor Drivers, Motor 1 Push Button, Motor 2 Push Button, Temperature Sensor, Stepper Motors)
![System Topology](./topology.png)

## Components Used
* AC Power Cable
* Mean Well PSU
* VCC Bus Bar
* GND Bus Bar
* Omron CP2E PLC
* XB7-EA31 Push Button (Green Motor 1, Green Motor 2, Red Safety Reset)
* XB2BS542C Emergency Button
* PT100 Transmitter
* CP1W-ADB21 Option Board
* TB6600 Driver (x2)
* PT100 Sensor Probe
* NEMA 17 Motor (x2)
* SCADA Server (PC)

## Wiring Table

### 1. Power
| SOURCE COMPONENT | SOURCE TERMINAL | DESTINATION COMPONENT | DESTINATION TERMINAL |
| :--- | :--- | :--- | :--- |
| AC Power Cable | Live (Brown or Black wire) | Mean Well PSU | L screw |
| AC Power Cable | Neutral (Blue wire) | Mean Well PSU | N screw |
| AC Power Cable | Ground (Yellow or Green wire) | Mean Well PSU | FG screw |
| Mean Well PSU | V+ Screw | VCC Bus Bar | Terminal Screw |
| Mean Well PSU | V- Screw | GND Bus Bar | Terminal Screw |
| VCC Bus Bar | Terminal | Omron CP2E PLC | L+ Screw |
| GND Bus Bar | Terminal | Omron CP2E PLC | M- Screw / COM |
| VCC Bus Bar | Terminal | All XB7-EA31 Push Button | C Output Terminal |
| VCC Bus Bar | Terminal | XB2BS542C Emergency Button | C Output Terminal |
| VCC Bus Bar | Terminal | PT100 Transmitter | V+ |
| GND Bus Bar | Terminal | PT100 Transmitter | V- |
| GND Bus Bar | Terminal | CP1W-ADB21 Board | COM 1 |
| VCC Bus Bar | Terminal | TB6600 Driver 1 | VCC |
| GND Bus Bar | Terminal | TB6600 Driver 1 | GND |
| VCC Bus Bar | Terminal | TB6600 Driver 2 | VCC |
| GND Bus Bar | Terminal | TB6600 Driver 2 | GND |
| VCC Bus Bar | Terminal | TB6600 Driver 1 | PUL+ & DIR+ |
| VCC Bus Bar | Terminal | TB6600 Driver 2 | PUL+ & DIR+ |

### 2. Signal & Communication
| SOURCE COMPONENT | SOURCE TERMINAL | DESTINATION COMPONENT | DESTINATION TERMINAL |
| :--- | :--- | :--- | :--- |
| Green Motor 1 XB7-EA31 Push Button | NO Output Terminal | Omron CP2E PLC | Input 0.00 |
| Green Motor 2 XB7-EA31 Push Button | NO Output Terminal | Omron CP2E PLC | Input 0.03 |
| Red Safety Reset XB7-EA31 Push Button | NO Output Terminal | Omron CP2E PLC | Input 0.02 |
| XB2BS542C Emergency Button | Terminal 12 (NC Output) | Omron CP2E PLC | Input 0.01 |
| PT100 Sensor Probe | 3-Wire Leads Blue-Blue, Red | PT100 Transmitter | RTD / PT100 Terminals |
| PT100 Transmitter | Bottom-left Terminal (Signal) | CP1W-ADB21 Option Board | Vin 1 |
| Omron CP2E PLC | Output 0.00 (Transistor PTO) | TB6600 Driver 1 | PUL- |
| Omron CP2E PLC | Output 0.02 (Transistor PTO) | TB6600 Driver 1 | DIR- |
| Omron CP2E PLC | Output 0.01 (Transistor PTO) | TB6600 Driver 2 | PUL- |
| Omron CP2E PLC | Output 0.03 (Transistor PTO) | TB6600 Driver 2 | DIR- |
| TB6600 Driver 1 | A+ / A- / B+ / B- | NEMA 17 Motor 1 | 4-Wire Leads |
| TB6600 Driver 2 | A+ / A- / B+ / B- | NEMA 17 Motor 2 | 4-Wire Leads |
| Omron CP2E PLC | COM (Output) | Omron CP2E PLC | 2x COM (Output) |
| SCADA Server (PC) | Ethernet Port (RJ45) | Omron CP2E PLC | Ethernet Port (RJ45) |

## Protocols & Data Mapping

### 1. Protocols & Ports
* **Omron CP2E PLC**: Modbus TCP Server (Port 502)
* **SCADA Server (Node-RED)**: HTTP Web Server (Port 1880)

### 2. Modbus Register Mapping
| Register Type | Address | Data Description |
| :--- | :--- | :--- |
| Coil (0x) | 1 | E-Stop Command |
| Coil (0x) | 2 | Safety Reset Command |
| Coil (0x) | 3 | Physical Field E-Stop Status |
| Coil (0x) | 4 | Master Safety Latch Bit |
| Coil (0x) | 5 | Motor 1 Running Status |
| Coil (0x) | 6 | Motor 2 Running Status |
| Coil (0x) | 7 | Field Button Status |
| Coil (0x) | 16 | Motor 1 Enable Command |
| Coil (0x) | 17 | Motor 2 Enable Command |
| Coil (0x) | 18 | Motor 1 Direction Command |
| Coil (0x) | 19 | Motor 2 Direction Command |
| Holding Register (4x) | 100 | Motor 1 Speed Feedback (RPM) |
| Holding Register (4x) | 101 | Motor 2 Speed Feedback (RPM) |
| Holding Register (4x) | 1024 | Temperature Raw (x100 °C) |
| Holding Register (4x) | 1025 | Speed Control Setpoint |
| Holding Register (4x) | 1026 | Calculated Thermal Auto-Speed |

## Software Setup & Execution Walkthrough

### 1. Omron CP2E PLC Programming
1. **Install CX-Programmer**: Download and install OMRON CX-One, which includes CX-Programmer.
2. **Open the Project**: Launch CX-Programmer and open `OmronSCADA_CXProgrammer.cxp`.
3. **Configure Network**: Go to PLC settings and configure the PLC's IP address to match your network (e.g., `192.168.2.xxx`).
4. **Compile and Download**: 
   - Compile the program (Ctrl+F7).
   - Go online with the PLC (Ctrl+W).
   - Download the program to the PLC (Program > Transfer > To PLC).
5. **Run Mode**: Switch the PLC into Run/Monitor mode to start execution.

### 2. SCADA Server (Node-RED)
1. **Start Node-RED**: Open command prompt on your SCADA laptop and type `node-red`.
2. **Import Flow**: 
   - Open browser and go to `http://localhost:1880`.
   - Click the menu (hamburger icon) > Import.
   - Select `node-REDFlow.json` from the `PLC System` directory.
   - Click Import.
3. **Configure Nodes**: Update the Modbus nodes within the flow to point to the Omron PLC's IP address.
4. **Deploy**: Click the Deploy button to apply the changes and start the SCADA interface.

## System Operation Walkthrough

1. **Safety Lockout System (Reset)**: The PLC features a hardcoded Safety Lockout mechanism. Before any operation can begin, ensure the physical red XB2 E-Stop button is released (pulled out). You MUST press the physical Red Safety Reset XB7 button to clear the Master Safety Lockout Latch in the PLC. Motors will not spin while this latch is engaged.
2. **Access Dashboard**: Open a web browser on the SCADA Server and navigate to `http://localhost:1880/ui` to access the Node-RED HMI.
3. **Motor Control**: You can control the motors (Enable, Direction, Speed) directly from the HMI, or use the physical Green XB7 buttons in the field to toggle the motors on/off.
4. **Thermal Monitoring**: The PT100 sensor provides real-time temperature feedback. The SCADA system will log this data to IoTDB and can adjust Motor 2's speed if the thermal ramp triggers.
5. **Emergency Stop**: In case of an emergency, press the physical field E-Stop button or click the Emergency Stop button on the HMI dashboard to immediately halt all operations.

## System Power Up & Shutdown Procedures

### Power On Procedure
1. Boot the SCADA Server Laptop and start Node-RED.
2. Plug in the AC Power Cable to energize the Mean Well PSU. This will supply 24V DC to the VCC Bus Bar, powering the Omron CP2E PLC, PT100 Transmitter, TB6600 Drivers, and all Field Buttons.
3. Wait for the Omron PLC to finish booting and enter RUN/MONITOR mode.
4. Verify the Node-RED dashboard indicates active connection and telemetry.

### Power Off Procedure
1. Ensure the E-Stop is pressed or all motors are commanded to a full stop via the Node-RED dashboard.
2. Unplug the AC Power Cable to de-energize the Mean Well PSU, safely cutting power to the PLC, drivers, and sensors simultaneously.
3. Stop Node-RED on the SCADA Server.
