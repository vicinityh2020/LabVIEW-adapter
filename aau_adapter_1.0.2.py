from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from urllib.parse import urlparse
import requests
import socket   
import json
import time
import threading

#define global vars default state
Global_state_emengency = b'Normal'

Global_state_parking_sensor_1 = b'F'
Global_state_parking_sensor_2 = b'F'
Global_state_parking_sensor_3 = b'F'

Global_state_freezer_refrigerator_door = b'C'
Global_state_freezer_freezer_door = b'C'

Global_state_oven_door = b'C'
Global_state_oven_device_status = b'I'

Global_Status_LoadScheduling = b'0'
Global_Status_LoadScheduling_last = b'0'

Global_Status_Alarm = b'Disable'

Gloal_alarmdetecttime = 60*15 # for 1min

stopflag = 0

#define global OID of devices
OID_Oven_7 = '9b4f2d11-addf-46b0-bec5-0773f5763612'
OID_Freezer_7 = 'ea0e3e81-56ce-4f8d-b843-2ff54c62a72f'
OID_Parking_Sensor_1 = '87bacf3e-ad0e-4120-938c-e01ce8014e16'
OID_Parking_Sensor_2 = 'f16b8c05-3bc0-4c81-b805-6dec543ba35b'
OID_Parking_Sensor_3 = 'f43c2e21-627c-44dd-b051-efd2ca4f29e3'

OID_Parking_Sensor_AUU = '8c9546ab-1385-499f-9524-6cd96187e37a'

#Alarm timer
def timerfun_alarm():
   global handle_timer_alarm
   global Global_Status_Alarm
   global Global_state_emengency
   
   Global_state_emengency = b'Alarm'
   
   handle_timer_alarm.cancel()
   Global_Status_Alarm = b'Disable'

   

#Enquire data and state from EMS
#Publish events to subscribers through VICINITY agnet
def timerfun_publishevent():
   global Global_state_parking_sensor_1
   global Global_state_parking_sensor_2
   global Global_state_parking_sensor_3
 
   global Global_Status_LoadScheduling
   global Global_Status_LoadScheduling_last 
   
   global handel_timer_publishevent
   global handel_TCPclient_interruptthread
   
   global Global_state_emengency
   
   global OID_Freezer_7
   global stopflag
   global Gloal_alarmdetecttime
   
   #Calculate number of free parking slot 
   FreeSlot= Global_state_parking_sensor_1 + Global_state_parking_sensor_2 + Global_state_parking_sensor_3 
   FreeSlot_string = str(FreeSlot, encoding = "utf-8")            
   FreeSlotNum = FreeSlot_string.count('F')     
   FreeSlotNum_byte = bytes(str(FreeSlotNum), encoding = "utf8")
    
   #Inquire state data from Labview for Charging price
   handel_TCPclient_interruptthread.send(b'Read_EMSstat_NNN') 
   responsestring = handel_TCPclient_interruptthread.recv(10) 

   
   #Rearrange received data from EMS
   chargeprice = responsestring[0:3]
   PV_perdicted = str(responsestring[4:7])
   PV_perdicted = PV_perdicted.strip()
   PV_perdicted = bytes(PV_perdicted, encoding = "utf8")
   Global_Status_LoadScheduling = responsestring[8:9]
   OverPowerComsumption = responsestring[9:10]


   #Derive System time
   ISOTIMEFORMAT = '%Y-%m-%d %X'        
   systemtime = time.strftime(ISOTIMEFORMAT,time.localtime())
   systemtime = str(systemtime)
   systemtime = bytes(systemtime, encoding = "utf8")
   
   #Publish the Charing and parking status event
   hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
   url = 'http://localhost:9997/agent/events/ParkingAndChargingStatus'  
   payload = b'{' + b'"value":"' + chargeprice + b'","free":"' +  FreeSlotNum_byte + b'","time":"'+ systemtime +b'"}'
   r=requests.request('PUT',url,headers=hd,data = payload)
   print(r.text)

   #Publish the perdicted PV power event
   hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
   url = 'http://localhost:9997/agent/events/PV_Perdiction'     
   payload = b'{' + b'"value":"' + PV_perdicted + b'","time":"'+ systemtime +b'"}'
   r=requests.request('PUT',url,headers=hd,data = payload)
   print(r.text)
   
   if (Global_state_emengency == b'Alarm'):
       
       #Set red alarm LED in EMS
       handel_TCPclient_interruptthread.send(b'USet_DoorAlr_1NN')     
       print('The emergency alarm should be published here!')     
   
       if(Global_state_parking_sensor_1 == b'R'):
           num_parking_resv = b'1'
       elif(Global_state_parking_sensor_2 == b'R'):
           num_parking_resv = b'2'
       elif(Global_state_parking_sensor_3 == b'R'):
           num_parking_resv = b'3'
       else:
           num_parking_resv = b'None'
    
       #Publish the alarm event
       hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
       url = 'http://localhost:9997/agent/events/EmergencyAlarm'     
       payload = b'{' + b'"state":"alarm",' + b'"parking slot reserved":"'+ num_parking_resv + b'","time":"'+ systemtime +b'"}'
       print(payload)
       r=requests.request('PUT',url,headers=hd,data = payload)
       print(r.text)
       
   else:
       num_parking_resv = b'None'
    
       #Publish the alarm event
       hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
       url = 'http://localhost:9997/agent/events/EmergencyAlarm'     
       payload = b'{' + b'"state":"Normal",' + b'"parking slot reserved":"'+ num_parking_resv + b'","time":"'+ systemtime +b'"}'
       print(payload)
       r=requests.request('PUT',url,headers=hd,data = payload)
       print(r.text)
       
   if (OverPowerComsumption == b'1'):
       
       #Read freezer 7  freezer_door properties  
       hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
       url = 'http://localhost:9997/agent/remote/objects/' + OID_Freezer_7 + '/properties/fastfreeze'
       r=requests.request('GET',url,headers=hd)
       print(r.text)
       
       print('The over power comsumption alarm should be published here!')  
       
       #Publish the Abnormal Energy Comsumption Alarm event
       hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
       url = 'http://localhost:9997/agent/events/AbnormalEnergyComsumptionAlarm'     
       payload = b'{' + b'"state":"alarm",' + b'"time":"'+ systemtime +b'"}'
       r=requests.request('PUT',url,headers=hd,data = payload)
       print(r.text)
     
   
#   when EMS start to limit applicane load
   if(Global_Status_LoadScheduling_last==b'0' and Global_Status_LoadScheduling==b'1'):
       
       # Set freezer 7 refrigerator_temperature properties to normal mode
       hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
       url = 'http://localhost:9997/agent/remote/objects/' + OID_Freezer_7 + '/properties/fastfreeze'
       payload = {'type': 'object','fastfreeze': 'OFF'}
       payload = json.dumps(payload) # transfer to JSON type data 
       r=requests.request('PUT',url,headers=hd,data = payload)
       print(r.text)
             
       
       #Set oven7 to stop (Action)        
       hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
       url = 'http://localhost:9997/agent/remote/objects/' + OID_Oven_7 + '/actions/stop'
       payload = {'type':'object','id':'1'}
       payload = json.dumps(payload) # transfer to JSON type data 
       r=requests.request('POST',url,headers=hd,data = payload)
       print(r.text)    
   
   #when EMS stop to limit applicane load       
   elif(Global_Status_LoadScheduling_last==b'1' and Global_Status_LoadScheduling==b'0'):

       # Set freezer 7 refrigerator_temperature properties to normal mode
       hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
       url = 'http://localhost:9997/agent/remote/objects/' + OID_Freezer_7 + '/properties/fastfreeze'
       payload = {'type': 'object','fastfreeze': 'ON'}
       payload = json.dumps(payload) # transfer to JSON type data 
       r=requests.request('PUT',url,headers=hd,data = payload)
       print(r.text)
       
   #Read freezer 7  freezer_door properties  
   hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
   url = 'http://localhost:9997/agent/remote/objects/' + OID_Freezer_7 + '/properties/fastfreeze'
   r=requests.request('GET',url,headers=hd)
   print(r.text)    
   
       #Set work parameter for oven7 action        
       hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
       url = 'http://localhost:9997/agent/remote/objects/'+ OID_Oven_7 +'/actions/baking'
       payload = {'type':'object','duration':'10','temperature':'150','heater_system':"hotair"}
       payload = json.dumps(payload) # transfer to JSON type data 
       r=requests.request('POST',url,headers=hd,data = payload)
       print(r.text)
   
   Global_Status_LoadScheduling_last = Global_Status_LoadScheduling;
   
   handel_timer_publishevent = threading.Timer(5,timerfun_publishevent,())         
   
   if stopflag==1:
        handel_timer_publishevent.cancel()
   else:
        handel_timer_publishevent.start()
   

#Handle the http requests from VICINITY agent 
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
 
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
 
        querypath = urlparse(self.path)
        path = str(querypath.path)
        
        Name_startnum = path.find('properties/')##
        queryitemName = path[Name_startnum+10:];
        
        ISOTIMEFORMAT = '%Y-%m-%d %X'        
        systemtime = time.strftime(ISOTIMEFORMAT,time.localtime())
        systemtime = str(systemtime)
        systemtime = bytes(systemtime, encoding = "utf8")
        print(queryitemName)
        if (queryitemName=='/Load_ActivePower'):
           senddata = b'Read_Load_AP_NNN'  
           handel_TCPclient_mainthread.send(senddata) 
           data=handel_TCPclient_mainthread.recv(4)
          
           self.wfile.write(b'{')  
           
           self.wfile.write(b'"value":"')  
           self.wfile.write(data)
           self.wfile.write(b'"')    

           self.wfile.write(b',')  

           self.wfile.write(b'"time":"')  
           self.wfile.write(systemtime)
           self.wfile.write(b'"')  
           
           self.wfile.write(b'}')          
          
        elif (queryitemName=='/WT_ActivePower'):
           senddata = b'Read_WTPower_NNN'  
           handel_TCPclient_mainthread.send(senddata) 
           data=handel_TCPclient_mainthread.recv(4)
           
           self.wfile.write(b'{')  
           
           self.wfile.write(b'"value":"')  
           self.wfile.write(data)
           self.wfile.write(b'"')    

           self.wfile.write(b',')  

           self.wfile.write(b'"time":"')  
           self.wfile.write(systemtime)
           self.wfile.write(b'"')  
           
           self.wfile.write(b'}')     
            
        elif (queryitemName=='/BMS_SoC'):
           senddata = b'Read_BMS_SoC_NNN'  
           handel_TCPclient_mainthread.send(senddata) 
           data=handel_TCPclient_mainthread.recv(4)
           
           self.wfile.write(b'{')  
           
           self.wfile.write(b'"value":"')  
           self.wfile.write(data)
           self.wfile.write(b'"')    

           self.wfile.write(b',')  

           self.wfile.write(b'"time":"')  
           self.wfile.write(systemtime)
           self.wfile.write(b'"')  
           
           self.wfile.write(b'}')     

        elif (queryitemName=='/PV_ActivePower'):
           senddata = b'Read_PVPower_NNN'  
           handel_TCPclient_mainthread.send(senddata) 
           data=handel_TCPclient_mainthread.recv(4)
           
           self.wfile.write(b'{')  
           
           self.wfile.write(b'"value":"')  
           self.wfile.write(data)
           self.wfile.write(b'"')    

           self.wfile.write(b',')  

           self.wfile.write(b'"time":"')  
           self.wfile.write(systemtime)
           self.wfile.write(b'"')  
           
           self.wfile.write(b'}')     
            
        else:
            self.wfile.write(b'HTTP/1.1 406 Failed')             
 
    def do_POST(self):
        
        global stopflag
        
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        self.send_response(200)
        self.end_headers()
                  
        string = body.decode() #encode()
        string = json.loads(string)
        
        control_ID=string['control_ID']
        control_val=string['value']
        
        if (control_ID=='shutdown' and control_val=='1'):
            response = BytesIO()
            response.write(b'HTTP/1.1 200 OK/Server is shutdown successfully')
            self.wfile.write(response.getvalue())   
            httpd.shutdown
            httpd.socket.close()            
            print('AAU adapter is shutdown successfully!')
            stopflag = 1
    
        else:
            response = BytesIO()
            response.write(b'HTTP/1.1 406 Failed')
            self.wfile.write(response.getvalue())   
 
    def do_PUT(self):
        
        global Global_state_parking_sensor_1
        global Global_state_parking_sensor_2
        global Global_state_parking_sensor_3
        
        global Global_state_freezer_refrigerator_door
        global Global_state_freezer_freezer_door
        global Global_state_oven_door
        global Global_state_oven_device_status
        
        global Global_Status_Alarm
        global handle_timer_alarm
        
        global OID_Oven_7
        global OID_Freezer_7
        global Global_state_emengency
        global Gloal_alarmdetecttime
        
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        self.send_response(200)
        self.end_headers()
        
        if (self.path.count(OID_Freezer_7) == 1):  #Freezer
            
            string = body.decode() #encode()
            print(string)
            
            if (string.count('refrigerator_door') == 1 and  string.count('CLOSED') == 1):     
                Global_state_freezer_refrigerator_door = b'C'   
               
                if (Global_state_freezer_freezer_door == b'C' and Global_state_oven_door == b'C'):
                    handle_timer_alarm.cancel()
                    Global_Status_Alarm = b'Disable'
                    Global_state_emengency = b'Normal'
                   
                    Finalsenddata = b'USet_DoorAlr_' + b'0' + b'N' + b'N'   
                    handel_TCPclient_mainthread.send(Finalsenddata) 
                else:
                     #Stop alarm timer
                    handle_timer_alarm.cancel()
                    Global_Status_Alarm = b'Disable'
                    
                    #refersh alarm timer again
                    handle_timer_alarm=threading.Timer(Gloal_alarmdetecttime,timerfun_alarm,())  
                    handle_timer_alarm.start()
                    Global_Status_Alarm = b'Enable'
            
            elif (string.count('refrigerator_door') == 1 and string.count('OPENED') == 1):
                Global_state_freezer_refrigerator_door = b'O' 
              
                if (Global_Status_Alarm == b'Enable'):
                    #Stop alarm timer
                    handle_timer_alarm.cancel()
                    Global_Status_Alarm = b'Disable'
                    
                    #refersh alarm timer again
                    handle_timer_alarm=threading.Timer(Gloal_alarmdetecttime,timerfun_alarm,())  
                    handle_timer_alarm.start()
                    Global_Status_Alarm = b'Enable'
                else:
                    #start alarm timer again
                    handle_timer_alarm=threading.Timer(Gloal_alarmdetecttime,timerfun_alarm,())  
                    handle_timer_alarm.start()
                    Global_Status_Alarm = b'Enable'
                
            elif (string.count('freezer_door') == 1 and string.count('CLOSED') == 1):
                Global_state_freezer_freezer_door = b'C'  
                
                if (Global_state_freezer_refrigerator_door == b'C' and Global_state_oven_door == b'C'):
                    Global_state_emengency = b'Normal'
                    handle_timer_alarm.cancel()
                    Global_Status_Alarm = b'Disable'
                    Finalsenddata = b'USet_DoorAlr_' + b'0' + b'N' + b'N'   
                    handel_TCPclient_mainthread.send(Finalsenddata) 
                else:
                     #Stop alarm timer
                    handle_timer_alarm.cancel()
                    Global_Status_Alarm = b'Disable'
                    
                    #refersh alarm timer again
                    handle_timer_alarm=threading.Timer(Gloal_alarmdetecttime,timerfun_alarm,())  
                    handle_timer_alarm.start()
                    Global_Status_Alarm = b'Enable'
                
            elif (string.count('freezer_door') == 1 and string.count('OPENED') == 1):
                Global_state_freezer_freezer_door = b'O'  
                
                if (Global_Status_Alarm == b'Enable'):
                    #Stop alarm timer
                    handle_timer_alarm.cancel()
                    Global_Status_Alarm = b'Disable'
                    
                    #refersh alarm timer again
                    handle_timer_alarm=threading.Timer(Gloal_alarmdetecttime,timerfun_alarm,())  
                    handle_timer_alarm.start()
                    Global_Status_Alarm = b'Enable'
                else:
                    #start alarm timer again
                    handle_timer_alarm=threading.Timer(Gloal_alarmdetecttime,timerfun_alarm,())  
                    handle_timer_alarm.start()
                    Global_Status_Alarm = b'Enable'
                    
            else:
                response = BytesIO()
                response.write(b'HTTP/1.1 406 Failed')
                self.wfile.write(response.getvalue())           
            
            if (Global_state_freezer_refrigerator_door == b'C' and Global_state_freezer_freezer_door == b'C'):
                doorstate = b'0'
            elif (Global_state_freezer_refrigerator_door == b'O' and Global_state_freezer_freezer_door == b'C'):
                doorstate = b'1'
            elif (Global_state_freezer_refrigerator_door == b'C' and Global_state_freezer_freezer_door == b'O'):
                doorstate = b'2'
            else:
                doorstate = b'3'  
                   
            Finalsenddata = b'USet_Freezer_' + doorstate + b'N' + b'N'   
            handel_TCPclient_mainthread.send(Finalsenddata)       
           
                    
        elif (self.path.count(OID_Oven_7) == 1):  #Oven   
            string = body.decode() #encode()
         
            if (string.count('door') == 1 and  string.count('CLOSED') == 1):     
                Global_state_oven_door = b'C'   
                
                if (Global_state_freezer_freezer_door == b'C' and Global_state_freezer_refrigerator_door == b'C'):
                    Global_state_emengency = b'Normal'
                    handle_timer_alarm.cancel()
                    Global_Status_Alarm = b'Disable'
                    Finalsenddata = b'USet_DoorAlr_' + b'0' + b'N' + b'N'   
                    handel_TCPclient_mainthread.send(Finalsenddata) 
                else:
                     #Stop alarm timer
                    handle_timer_alarm.cancel()
                    Global_Status_Alarm = b'Disable'
                    
                    #refersh alarm timer again
                    handle_timer_alarm=threading.Timer(Gloal_alarmdetecttime,timerfun_alarm,())  
                    handle_timer_alarm.start()
                    Global_Status_Alarm = b'Enable'
                    
            elif (string.count('door') == 1 and string.count('OPENED') == 1):
                Global_state_oven_door = b'O'  
                
                if (Global_Status_Alarm == b'Enable'):
                    #Stop alarm timer
                    handle_timer_alarm.cancel()
                    Global_Status_Alarm = b'Disable'
                    
                    #refersh alarm timer again
                    handle_timer_alarm=threading.Timer(Gloal_alarmdetecttime,timerfun_alarm,())  
                    handle_timer_alarm.start()
                    Global_Status_Alarm = b'Enable'
                else:
                    #start alarm timer again
                    handle_timer_alarm=threading.Timer(Gloal_alarmdetecttime,timerfun_alarm,())  
                    handle_timer_alarm.start()
                    Global_Status_Alarm = b'Enable'                
                
                
            elif (string.count('device_status') == 1 and string.count('RUNNING') == 1):
                Global_state_oven_device_status = b'R'  
                
            elif (string.count('device_status') == 1 and string.count('PAUSE') == 1):
                Global_state_oven_device_status = b'I'  
                
            elif (string.count('device_status') == 1 and string.count('IDLE') == 1):
                Global_state_oven_device_status = b'I'  
          
            else:
                response = BytesIO()
                response.write(b'HTTP/1.1 406 Failed')
                self.wfile.write(response.getvalue())                       
                   
            Finalsenddata = b'USet_OvenSta_' + Global_state_oven_door + Global_state_oven_device_status + b'N'   
            handel_TCPclient_mainthread.send(Finalsenddata)        
            
        else:   #Parking sensor
            
            string = body.decode() #encode()
            string = json.loads(string)
        
            Sensor_ID=string['sensorID']
            Sensor_State=string['status']
        
            if (Sensor_ID=='008000000400882f'):
                if(Sensor_State=='Occupied'):
                    Global_state_parking_sensor_1 = b'O'
                else:
                    Global_state_parking_sensor_1 = b'F'

            elif (Sensor_ID=='0080000004008835'):   
               if(Sensor_State=='Occupied'):
                   Global_state_parking_sensor_2 = b'O'
               else:
                   Global_state_parking_sensor_2 = b'F'
         
            elif (Sensor_ID=='008000000400884a'):
                if(Sensor_State=='Occupied'):
                    Global_state_parking_sensor_3 = b'O'
                else:
                    Global_state_parking_sensor_3 = b'F'
          
            else:
                response = BytesIO()
                response.write(b'HTTP/1.1 406 Failed')
                self.wfile.write(response.getvalue())  
                
            if (Global_state_emengency == b'Alarm' and Global_state_parking_sensor_1 != b'R' and Global_state_parking_sensor_2 != b'R' and Global_state_parking_sensor_3 != b'R'):
                if (Global_state_parking_sensor_1 == b'F'):
                    Global_state_parking_sensor_1 = b'R'
                
                elif (Global_state_parking_sensor_2 == b'F'):
                    Global_state_parking_sensor_2 = b'R'
               
                elif (Global_state_parking_sensor_3 == b'F'):
                    Global_state_parking_sensor_3 = b'R'      
                    
            Finalsenddata = b'USet_ParkSen_' + Global_state_parking_sensor_1 + Global_state_parking_sensor_2 + Global_state_parking_sensor_3                     
            handel_TCPclient_mainthread.send(Finalsenddata)  
            print(Finalsenddata)
      

if __name__ == '__main__':
     #Create handel for TCP client to connect to Labview (main)  
     address = ('17486633in.iask.in', 31127)  
     handel_TCPclient_mainthread = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
     handel_TCPclient_mainthread.connect(address) 

     #Create handel for TCP client to connect to Labview (interrupt)
     address = ('17486633in.iask.in', 36539 )  
     handel_TCPclient_interruptthread = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
     handel_TCPclient_interruptthread.connect(address)    
     
     #Open the channel for publishing the Charing and parking status event of AAU
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/events/ParkingAndChargingStatus'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
     
     #Open the channel for publishing the PV_Perdiction event of AAU
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/events/PV_Perdiction'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
     
     #Open the channel for publishing the Abnormal Energy Comsumption Alarm event of AAU
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/events/AbnormalEnergyComsumptionAlarm'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
     
     #Open the channel for publishing the Emergency Alarm event of AAU
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/events/EmergencyAlarm'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
    
     #Open the channel for publishing the Clearing Requirment event of AAU
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/events/ClearingRequirment'
     r=requests.request('POST',url,headers=hd)
     print(r.text)

     #subscribe to the event of door sensor1    
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/objects/72b0aa10-249f-406c-a5eb-548ec339f190/events/door_activity_b0654854-a9ff-4ad7-99ca-9d71f94c4f53'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
  
     #subscribe to the event of freezer 7 (freezer door)            
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/objects/' + OID_Freezer_7 + '/events/freezer_door'
     r=requests.request('POST',url,headers=hd)
     print(r.text)

     #subscribe to the event of freezer 7 (refrigerator_door)            
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/objects/' + OID_Freezer_7 + '/events/refrigerator_door'
     r=requests.request('POST',url,headers=hd)
     print(r.text)

     #subscribe to the event of oven 7 (door)            
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/objects/' + OID_Oven_7 + '/events/door'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
     
     #subscribe to the event of oven 7 (device statusr)            
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/objects/' + OID_Oven_7 + '/events/device_status'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
     
     #subscribe to the event of parking sensor 1(sensor_id:008000000400882f)           
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/objects/' + OID_Parking_Sensor_AUU + '/events/008000000400882f'
     r=requests.request('POST',url,headers=hd)
     print(r.text)

     #subscribe to the event of parking sensor 2(sensor_id:0080000004008835)           
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/objects/' + OID_Parking_Sensor_AUU + '/events/008000000400884a'
     r=requests.request('POST',url,headers=hd)
     print(r.text)

     #subscribe to the event of parking sensor 3(sensor_id:008000000400884a)           
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_RMEMS'}
     url = 'http://localhost:9997/agent/objects/' + OID_Parking_Sensor_AUU + '/events/0080000004008835'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
     
     #start thread for publish event
     handel_timer_publishevent = threading.Timer(5,timerfun_publishevent,())  
     handel_timer_publishevent.start()

     #start main http server
     print('AAU Server is working!')
     httpd = HTTPServer(('localhost', 9995), SimpleHTTPRequestHandler)
     httpd.serve_forever()
    
