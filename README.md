
This documentation describes the adapter for LabVIEW software used in AAU.

# Infrastructure overview

A PV/ wind turbine/battery hybrid residential microgrid is emulated in AAU IoT-microgrid Lab. A GORENJE smart refrigerator and a GORENJE smart oven are included in the residential microgrid. The residential microgrid is assumed to supply power to EV chargers at three parking slots. Parking slot usage data, energy consumption data, operation status of the smart appliances, and room usage data are collected to the LabVIEW-based energy management system through VICINITY P2P network. The real-time charging price is calculated by considering the forecasts of the PV and wind turbine power generation, forecast of the load consumption, and state-of-charge of batteries. The parking slot usage, the real-time charging price, room usage date, microgrid operation status, abnormal situation alarm, and energy consumption abnormal alarm will be published to VICINITY Cloud. 
The adapter serves as the interface between VICINITY and the LabVIEW-based energy management system to enable the required interaction patterns. The adapter runs on Python 3.6.


![Image text](https://github.com/YajuanGuan/pics/blob/master/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20191113143259.png)


# Configuration and deployment

Adapter runs on Python 3.6.

# Functionality and API

## Publish parking status and charging price event to the subscribers.

### Endpoints
* PUT : /remote/objects/{oid}/events/{eid}

Publish the vacant parking slot number, EV charging price and current time. Users can receive the number of free parking slot and charging price automatically.

### Return
After subscribing the VAS successfully, the subscriber receives a response for instance:  
{  
"value": "3.15",  
"free": "2",  
"time": "2018-11-10 11:30:29"  
}  

## Publish emergency alarm event to the subscribers.

### Endpoints
* PUT : /remote/objects/{oid}/events/{eid}

Publish the emergency alarm, the reserved parking slot number (0/1) and current time.

### Return
After subscribing the VAS successfully, the subscriber receives a response for instance:  
{  
"state": "alarm",  
"parking slot reserved": "1",  
"time": "2018-11-10 11:30:29"  
}  

## Publish cleaning request event to the subscribers.

### Endpoints
* PUT : /remote/objects/{oid}/events/{eid}

Publish the cleaning request and current time.

### Return
After subscribing the VAS successfully, the subscriber receives a response for instance:  
{  
"clean": "required",  
"time": "2018-11-10 11:30:29"  
} 

## Read the energy consumption of microgrid.

### Endpoints
*  GET : /remote/device/{oid}/properties/{pid}

Read the energy consumption and current time.

### Return
After executing GET method, a response can be received, for instance:  
properties/Load_ActivePower:  
{  
"value": "1",  
"time": "2018-11-10 11:30:29"  
}  

properties/WT_ActivePower:  
{  
"value": "2",  
"time": "2018-11-10 11:30:29"  
}  

properties/BMS_SoC:  
{  
"value": "60%",  
"time": "2018-11-10 11:30:29"  
}  

properties/PV_ActivePower:  
{  
"value": "3",  
"time": "2018-11-10 11:30:29"  
}  

## Publish an abnormal energy consumption alarm event to the subscribers.

### Endpoints
* PUT : /remote/objects/{oid}/events/{eid}

Publish the alarm and current time.

### Return
After subscribing the VAS successfully, the subscriber receives a response for instance:  
{  
"state": "alarm",  
"time": "2018-11-10 11:30:29"  
}  


## PUT GORENJE refrigerator property

### Endpoint:  
* PUT : /remote/objects/{oid}/properties/{pid}

For PUT method request the following JSON is needed:  
{  
"fastfreeze": "ON"  
}  

## POST GORENJE oven baking parameters

### Endpoint:
* POST : /remote/objects/{oid}/actions/{aid}

For PUT method request the following JSON is needed:  
{  
"duration": "20",  
"temperature": "150",  
"heater_system": "hotair"  
}  

## Publish an PV forecast event to the subscribers

### Endpoint:
* PUT : /remote/objects/{oid}/events/{eid}

Publish the with solar irradiance forecast for next 15 mins.

### Return:
After subscribing the VAS successfully, the subscriber receives a response for instance:  
{  
"value": "843",  
"time": "2018-11-10 11:30:29"  
}  

