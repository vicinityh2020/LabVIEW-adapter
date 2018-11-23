
This documentation describes the adapter for smart parking based energy management system (EMS) of Aalborg University (AAU).

# Infrastructure overview

Microgrid is emulated on the scaled-down experimental platform in AAU. Wind turbine (WT), PV and energy storage system (ESS) is simulated by three 3-phase inverters respectively. The load of electric vehicle (EV) charging is simulated by resistive loads which are controlled by state of three parking sensors, the states of parking sensors are collected through Vicinity P2P Network automatically through adapter established on Python. EMS established in LabVIEW monitors generated power of PV/WT, the state of charge (SoC) of ESS and the charging state of three parking slots in microgrid, and also, it calculates EVs charging prince according to SoC. End users could subscribe to EMS value added service to receive parking slots state and EVs charging price automatically. 

![Image text](https://github.com/YajuanGuan/pics/blob/master/%E5%9B%BE%E7%89%871.png)

# Configuration and deployment

Adapter run on python 3.6

# Adapter changelog by version
Adapter releases are as aau_adapter_x.y.z.py

## 1.0.0
Start version, it works with agent-service-full-0.6.0.jar, and it receives three parking slots states and publishes charging price.

# Functionality and API

## Read microgrid state
### Endpoint:
            GET /remote/objects/{oid}/properties/{pid}
Returns last known value and time received by EMS. “oid” is UUID of EMS and “pid” is a property identifier. User can read generated active power of PV and WT, the SoC of ESS, active power load of microgrid.

## Subscribe to event channel
### Endpoint:
            POST /objects/{oid}/events/{eid}
Returns last charing price value and time received by EMS. “oid” is UUID of EMS and “eid” is a event identifier. User can read the number of free parking slot and charing price automatically.
