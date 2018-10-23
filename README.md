
This documentation describes the adapter for smart parking based energy management system (EMS) of Aalborg University (AAU).

# Infrastructure overview

Microgrid is emulated on the scaled-down experimental platform in AAU. Wind turbine (WT), PV, energy storage system (ESS) is simulated by three 3-phase inverters respectively, the load of electric vehicle (EV) charging is simulated by resistive loads, there are controlled by state of three parking sensors which are collected through Vicinity P2P Network automatically through adapter. EMS established in LabVIEW can monitor generated power, the state of charge (SoC) of ESS and the charging state for three parking slots in microgrid, and can calculate EVs charging prince according to SoC. End users can subscribe to EMS value added service to monitor parking slots state and EVs charging prince. 

![Image text](https://github.com/YajuanGuan/pics/blob/master/%E5%9B%BE%E7%89%871.png)

# Configuration and deployment

TBD .. Adapter is currently in design stage.

# Functionality and API

## Endpoints

* GET/PUT /objects/{oid}/properties/{pid}: read/set the property of remote object
* PUT /events/{eid}: publish the event

## Functions

Adapter will enable to pass incomming events from VICINITY into LAbVIEW software
