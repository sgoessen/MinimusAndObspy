# -*- coding: utf-8 -*-
"""
Created on 9/12/2020
@author: sgoessen
"""


import socket
import xml.etree.ElementTree as ET
import threading
import time
from obspy import UTCDateTime
from colorama import Fore

capList = []


class CapMsg:
    def __init__(self,capAlert):
        ns = {'alert':'urn:oasis:names:tc:emergency:cap:1.2'}
        root = ET.fromstring(capAlert.decode('utf-8'))
        infoElement = root.find('alert:info',ns)
        locationElement = infoElement.find('alert:area',ns)

        self.time = UTCDateTime(root.find('alert:sent',ns).text) #Returns time of event in UTCDatetime unit
        self.sender = root.find('alert:sender',ns).text
        self.type = infoElement.find('alert:event',ns).text
        self.location = locationElement.find('alert:circle',ns).text
        self.magnitude = infoElement.find('alert:description',ns).text

####  Setup Network CAP monitoring   ####
UDP_IP = '0.0.0.0'         
UDP_PORT = 11789           
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT))
print('Monitoring Port {0} for any messages'.format(UDP_PORT))

while True:
    data, addr = sock.recvfrom(16384)

    capAlert = CapMsg(data)

    if capAlert.magnitude[:3] == "STA":
        print(Fore.GREEN, 'CAP Alert recevied from',addr[0])
        print(Fore.GREEN, 'TIME : ', capAlert.time)
        print(Fore.GREEN,'LOCATION : ', capAlert.location)
        print(Fore.GREEN,'Magnitude : ', capAlert.magnitude)
        print(Fore.GREEN,'')
    else:
        print(Fore.RED, 'CAP Alert recevied from', addr[0])
        print(Fore.RED, 'TIME : ', capAlert.time)
        print(Fore.RED, 'LOCATION : ', capAlert.location)
        print(Fore.RED, 'Magnitude : ', capAlert.magnitude)
        print(Fore.RED, '')


