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

capList = []

class CapMsg:
    def __init__(self,capAlert):
        ns = {'alert':'urn:oasis:names:tc:emergency:cap:1.2'}
        root = ET.fromstring(capAlert.decode('utf-8'))
        infoElement = root.find('alert:info',ns)
        locationElement = infoElement.find('alert:area',ns)
        self.time = UTCDateTime(root.find('alert:sent',ns).text) #using obspy
        self.identifier = root.find('alert:identifier',ns).text
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
    print(data)
    capAlert = CapMsg(data)
    print('CAP Alert recevied from',addr[0])
    print('Identifier : ', capAlert.identifier[:8])
    print('TIME : ', capAlert.time)
    print('TYPE : ', capAlert.type)
    print('LOCATION : ', capAlert.location)
    print('Magnitude : ', capAlert.magnitude)
    print('')



