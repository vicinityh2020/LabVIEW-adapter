
This documentation describes the adapter for LabVIEW software used in AAU.

# Infrastructure overview

LabVIEW is systems engineering software for applications that require test, measurement, and control with rapid access to hardware and data insights. 
It offers a graphical programming approach that helps you visualize every aspect of the application, including hardware configuration, 
measurement data, and debugging.


![Image text](https://github.com/YajuanGuan/pics/blob/master/%E5%9B%BE%E7%89%871.png)

In LabVIEW simulations, it was necessary to listen to the data and events from the other VICINITY client nodes. 
Adapter serves as the interface between VICINITY and LabVIEW enabling to use all required interaction patterns.


# Configuration and deployment

TBD .. Adapter is currently in design stage.

# Functionality and API

## Endpoints

* GET/PUT /objects/{oid}/properties/{pid}: read/set the property of remote object
* PUT /events/{eid}: publish the event

## Functions

Adapter will enable to pass incomming events from VICINITY into LAbVIEW software
