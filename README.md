# Protergo-SCADA-System

Welcome to the Protergo SCADA System repository. This project is divided into two main components:
- [PLC System](./PLC%20System/README.md)
- [Raspberry System](./Raspberry%20System/README.md)

Please refer to the respective directories for detailed documentation on wiring.

## SCADA HMI Overview
![SCADA HMI](./SCADA_HMI.png)

## Node-RED Setup Walkthrough
1. **Install Node.js**
   Download and install Node.js from the official website.
2. **Install Node-RED**
   Open command prompt and run: `npm install -g --unsafe-perm node-red`
3. **Start Node-RED**
   Run the command: `node-red`
4. **Access the Editor**
   Open your browser and navigate to `http://localhost:1880`.
5. **Install Required Nodes**
   Click the menu (hamburger icon) > Manage palette > Install. Search for and install nodes like `node-red-dashboard` or Modbus nodes as needed for the project.
6. **Create Flows**
   Drag and drop nodes from the palette on the left into the workspace to create your SCADA flow. Wire them together to define the logic, then click the **Deploy** button in the top right to make it active.

## Apache IoTDB Setup Walkthrough
1. **Prerequisites**
   Ensure Java 8+ is installed and the `JAVA_HOME` environment variable is set.
2. **Download Apache IoTDB**
   Download the latest binary from the official website and extract the archive (e.g., to `C:\iotdb`).
3. **Terminal 1: Start the ConfigNode**
   Open command prompt:
   `cd C:\iotdb\sbin\windows`
   `start-confignode.bat`
4. **Terminal 2: Start the DataNode**
   Open a new command prompt:
   `cd C:\iotdb\sbin\windows`
   `start-datanode.bat`
5. **Terminal 3: Log In via the Interactive CLI**
   Open a new command prompt:
   `cd C:\iotdb\sbin\windows`
   `start-cli.bat -h 127.0.0.1 -p 6667 -u root -pw root`
   You can now execute SQL-like commands to manage your time-series data.