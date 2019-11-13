
This documentation describes the adapter for LabVIEW software used in AAU.

# Infrastructure overview

A residential microgrid, which consists of PV, wind turbine and battery, is emulated in AAU IoT-microgrid Lab, and GORENJE smart refrigerator and oven are included in the residential microgrid. Parking slot usage data, the energy consumption data, and room usage data is collected through VICINITY by using parking sensors, microgrid EMS and Tinymesh door sensor to achieve residential microgrid monitoring function. The residential microgrid is assumed to supply power to EV chargers in the three parking slots. The real-time charging price is calculated by considering the simulated real-time utility electricity price, state-of-charge of batteries, and forecasts of the PV and wind turbine power generation.
The parking slot usage and the real-time charging price will be sent automatically to users after subscribing the Vacant parking slot and charging price notifications service VAS. A LabVIEW-based energy management system is developed to achieve optimized control for energy resources and local loads and to perform load-scheduling function. An energy cost alarm will be triggered by Energy consumption abnormal VAS if the energy consumption exceeds desired thresholds, for instance continuously baking. A cleaning notification VAS will report it if the usage of the room over the threshold.
The VAS identify abnormal situations for instance a GORENJE refrigerator’ door has been left open more than normal time and trigger notifications to care providers and reserve a free parking slot for an ambulance. The VAS also provide short-term prediction and reporting of solar irradiance for residences and utility who have PV panels to enhance the energy management system capability.


# Configuration and deployment

Adapter runs on Python 3.6.

# Functionality and API

## Endpoints
* PUT : /remote/objects/{oid}/events/{eid}

Publish the vacant parking slot number, EV charging price and current time. Users can receive the number of free parking slot and charging price automatically.

## Return
After subscribing the VAS successfully, the subscriber receives a response for instance:
{
"value": "3.15",
"free": "2",
"time": "2018-11-10 11:30:29"
}

## Endpoints
* PUT : /remote/objects/{oid}/events/{eid}

Publish the emergency alarm, the reserved parking slot number (0/1) and current time.

## Return
After subscribing the VAS successfully, the subscriber receives a response for instance:
{
"state": "alarm",
"parking slot reserved": "1",
"time": "2018-11-10 11:30:29"
}

## Endpoints
* PUT : /remote/objects/{oid}/events/{eid}

Publish the cleaning request and current time.

## Return
After subscribing the VAS successfully, the subscriber receives a response for instance:
{
"clean": "required",
"time": "2018-11-10 11:30:29"
}



