
This documentation describes the adapter for smart parking based energy management system (EMS) of Aalborg University (AAU).

# Infrastructure overview

Microgrid is emulated on the scaled-down experimental platform in AAU. Wind turbine (WT), PV and energy storage system (ESS) is simulated by three 3-phase inverters respectively. The load of electric vehicle (EV) charging is simulated by resistive loads which are controlled by state of three parking sensors, the states of parking sensors are collected through Vicinity P2P Network automatically through adapter established on Python. EMS established in LabVIEW monitors generated power of PV/WT, the state of charge (SoC) of ESS and the charging state of three parking slots in microgrid, and also, it calculates EVs charging prince according to SoC. End users could subscribe to EMS value added service to receive parking slots state and EVs charging price automatically. 

![Image text](https://github.com/YajuanGuan/pics/blob/master/%E5%9B%BE%E7%89%871.png)

# Configuration and deployment

TBD .. Adapter is currently in design stage.

# Functionality and API

## Endpoints

* GET/PUT /objects/{oid}/properties/{pid}: read/set the property of remote object
* PUT /events/{eid}: publish the event

## Functions

Adapter will enable to pass incomming events from VICINITY into LAbVIEW software
