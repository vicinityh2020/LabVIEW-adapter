from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from urllib.parse import urlparse
import requests
import socket   
import json
import time
import threading

#define global vars
senddata1 = b'F'
senddata2 = b'F'
senddata3 = b'F'
stopflag = 0

#Enquire Parking price and free number from EMS
#Publish events to subscribers through VICINITY agnet
def Timerfun():
   global senddata1
   global senddata2
   global senddata3
 
   #Calculate number of free parking slot 
   FreeSlot= senddata1 + senddata2 + senddata3 
   FreeSlot_string = str(FreeSlot, encoding = "utf-8")            
   FreeSlotNum = FreeSlot_string.count('O')     
   FreeSlotNum_byte = bytes(str(FreeSlotNum), encoding = "utf8")
    
   #Inquire from Labview for Charging price
   DataToSimulink.send(b'Read_ParkPri_NNN') 
   Price=DataToSimulink.recv(4) 
      
   #Derive System time
   ISOTIMEFORMAT = '%Y-%m-%d %X'        
   systemtime = time.strftime(ISOTIMEFORMAT,time.localtime())
   systemtime = str(systemtime)
   systemtime = bytes(systemtime, encoding = "utf8")
        
   #Publish the Charing and parking status event
   hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'RMEMS'}
   url = 'http://localhost:9997/agent/events/ParkingAndChargingStatus'

   payload = b'{' + b'"value":"' + Price + b'","free":"' +  FreeSlotNum_byte + b'","time":"'+ systemtime +b'"}'
   r=requests.request('PUT',url,headers=hd,data = payload)
   
   t=threading.Timer(5,Timerfun,())   
   
   if stopflag==1:
        t.cancel()
   else:
        t.start()


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
        
        if (queryitemName=='/Load_ActivePower'):
           senddata = b'Read_Load_AP_NNN'  
           DataToSimulink.send(senddata) 
           data=DataToSimulink.recv(4)
          
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
           DataToSimulink.send(senddata) 
           data=DataToSimulink.recv(4)
           
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
           DataToSimulink.send(senddata) 
           data=DataToSimulink.recv(4)
           
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
           DataToSimulink.send(senddata) 
           data=DataToSimulink.recv(4)
           
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
        
        global senddata1
        global senddata2
        global senddata3
        
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        self.send_response(200)
        self.end_headers()
        
        string = body.decode() #encode()
        string = json.loads(string)
        print(string)
        Sensor_ID=string['sensor_id']
        Sensor_State=string['value']
        
        if (Sensor_ID=='008000000400882f'):
            if(Sensor_State=='Occupied'):
                senddata1 = b'O'
            else:
                senddata1 = b'F'

        elif (Sensor_ID=='0080000004008835'):   
            if(Sensor_State=='Occupied'):
                senddata2 = b'O'
            else:
                senddata2 = b'F'
         
        elif (Sensor_ID=='008000000400884a'):
            if(Sensor_State=='Occupied'):
                senddata3 = b'O'
            else:
                senddata3 = b'F'
          
        else:
            response = BytesIO()
            response.write(b'HTTP/1.1 406 Failed')
            self.wfile.write(response.getvalue())           

        Finalsenddata = b'USet_ParkSen_' + senddata1 + senddata2 + senddata3     
        DataToSimulink.send(Finalsenddata)  

if __name__ == '__main__':
    #Create TCP client to connect to Labview            
    address = ('localhost',10005)   
    DataToSimulink = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    DataToSimulink.connect(address) 

    #Open the channel for publishing the Charing and parking status event of AAU
    hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'RMEMS'}
    url = 'http://localhost:9997/agent/events/ParkingAndChargingStatus'
    r=requests.request('POST',url,headers=hd)
    print(r.text)

    #subscribe to the event of parking sensor 1(sensor_id:008000000400882f)           
    hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'RMEMS'}
    url = 'http://localhost:9997/agent/objects/aa9a9d7a-cf7d-452f-9165-cf038eccb96b/events/sensor-b4be8848-35bd-4720-9158-305d7e5c8c2b'
    r=requests.request('POST',url,headers=hd)
    print(r.text)

    #subscribe to the event of parking sensor 2(sensor_id:0080000004008835)           
    hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'RMEMS'}
    url = 'http://localhost:9997/agent/objects/22bc0d05-5c35-4042-82bc-9be958929bb4/events/sensor-849da2b0-8ed1-4d3b-bcac-46572b390acf'
    r=requests.request('POST',url,headers=hd)
    print(r.text)

    #subscribe to the event of parking sensor 3(sensor_id:008000000400884a)           
    hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'RMEMS'}
    url = 'http://localhost:9997/agent/objects/689e8e09-56e2-4a19-8d97-81286f0bedd3/events/sensor-64f41424-93ee-4130-8519-66a250f5bfe3'
    r=requests.request('POST',url,headers=hd)
    print(r.text)

    #start thread for publish parking event
    t=threading.Timer(5,Timerfun,()) 
    t.start()

    #Start AAU adapter 
    print('AAU adapter start working!')         
    httpd = HTTPServer(('localhost', 9995), SimpleHTTPRequestHandler)
    httpd.serve_forever()
