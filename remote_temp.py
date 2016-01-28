import nest
import numpy as np
import matplotlib.pyplot as plt
import curses
import os
from nest import utils as n_utils
import select
import socket
import time
#Nest username and password
username = 'user@gmail.com'
password = 'password'

nest_api = nest.Nest(username,password)
#TARGET TEMPERATURE
target_temp = 74
#States are 'COOLING','OFF'
current_state = 'ON'


server = '192.168.0.111'
port = 2000
addr = (server,port)
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.setblocking(0)
sock.settimeout(0)
sock.bind(addr)

def get_temp(nest_api):
    return n_utils.c_to_f(nest_api.devices[0].temperature)
def get_target(nest_api):
    return n_utils.c_to_f(nest_api.devices[0].target)

def set_temp(nest_api,temp):
    nest_api.devices[0].temperature = n_utils.f_to_c(temp)

def change_to_cool(nest_api):
    nest_api.structures[0].away = False
    print "CHANGED STATE TO COOLING"
    return 'COOLING'

def change_to_off(nest_api):
    nest_api.structures[0].away = True
    print "CHANGED STATE TO OFF"
    return 'OFF'
def get_away(nest_api):
    return nest_api.structures[0].away

#CALIBRATED BIAS
def get_remote_temp(self,sock):
        BIAS = 2
        data = ''
        try:
            data = sock.recv(1024)
        except:
            print 'Error'
            return self.sock_temp
        else:
            if(len(data)>0):
                print 'New Data'
                temp_f =float(data.strip('\x00'))-BIAS
                self.sock_temp = temp_f
                return temp_f
            else:
                return self.sock_temp
            
#SET DWELL TEMPERATURE
class controller(object):
    def __init__(self,nest_api,target_temp,addr):
        self.target_temp = target_temp
    	self.nest_api = nest_api
        self.addr = addr
	self.sock_temp = target_temp
        self.dwell = 3
        if(get_away(nest_api)):
            self.current_state = 'OFF'
        else:
            self.current_state = 'COOLING'
        self.saved_target = 0


    def controller(self):
        current_remote_temp = get_remote_temp(self,sock)
	print 'current remote temp:' + str(current_remote_temp)

        if(current_remote_temp > self.target_temp):
            if(self.current_state == 'COOLING'):
                print "Remote Temp:" + str(current_remote_temp) + ", Target Temp:" + str(self.target_temp)
            else:
                current_nest_temp = get_temp(self.nest_api)
                self.saved_target = get_target(self.nest_api)
                self.current_state = change_to_cool(self.nest_api)
                set_temp(self.nest_api,self.target_temp-self.dwell)

        if(current_remote_temp <= (self.target_temp - self.dwell)):
            if(self.current_state == 'COOLING'):
                self.current_state = change_to_off(self.nest_api)
        print "Remote Temp:" + str(current_remote_temp) + ", Target Temp:" + str(self.target_temp) + ' current state:' + self.current_state
        return current_remote_temp
simple = controller(nest_api,target_temp,addr)
temp_l = np.zeros(500).tolist()
while(True):
    print time.ctime()
    simple.controller()
    #temp_l.append(simple.controller())
    #temp_l.pop(0)
    #plt.plot(temp_l,'ko')
    #plt.show()
    time.sleep(.1)
    os.system('clear')
