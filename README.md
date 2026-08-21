# Mini-SCADA-System

Welcome to the Mini SCADA System repository. This project is divided into two main components:
- [PLC System](./PLC%20System/README.md)
- [Raspberry System](./Raspberry%20System/README.md)

Please refer to the respective directories for detailed documentation on wiring.

## SCADA HMI Overview
![SCADA HMI](./SCADA_HMI.png)

## Setup Node-RED and IoTDB with Docker

1. **Install Docker**
   Make sure Docker and Docker Compose are installed on your machine.
2. **Run Docker Compose**
   Open command prompt in the root of this project and run:
   ```bash
   docker-compose up -d
   ```
3. **Access Node-RED Editor**
   Open your browser and navigate to `http://localhost:1880`.
4. **Access IoTDB**
   You can connect to IoTDB at `localhost:6667`.

To stop the services, run:
```bash
docker-compose down
```
