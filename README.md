# Waterloop-Command-Control-State-Machine
In development. Waterloop's Hyperloop Pod is controlled by distributed flight computer hosted on a Raspberry Pi. This is the host application's command control state machine, which parses commands between the Dashboard and the motor controller.

## Cloning Instructions for Windows
Before cloning the repo, ensure you:
- Install grpc for Python
```
pip install grpcio
```
- Install CAN
```
pip install python-can
```
## Sending a test message to the server
Open a terminal and run:
```
python grpc_testserver.py
```
Open a second terminal and run:
```
python CommandControlSM.py
```
You should receive a test message from the server with:
```
Message: Battery voltage data
Battery Voltage: 48.5
Battery Current: 0.0
Speed: 0
```
