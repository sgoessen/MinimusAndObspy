# -*- coding: utf-8 -*-
"""
Created on Thu Mar 07 2019 10:40
@author: sgoessen
"""

import logging
import socket
import xml.etree.ElementTree as ET
from obspy import UTCDateTime, read
import threading
import time
import wget
import os
from selenium import webdriver
import winsound

######### Start of variable to set #############

tw = 1 # Number of seconds between CAP alerts for event to be declared
timeBefore = 5 # Number of seconds before event to retrieve
timeAfter = 5 # Number of seconds after event to retrieve
temp = os.environ["TEMP"]
########### End of variables to set ###########

capList = []
ip = []

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



def generateCAP(incoming):
      output = CapMsg(incoming)
      print('CAP Alert recevied....')
      print('SENDER : ', output.sender)
      print('TIME : ', output.time)
      print('TYPE : ', output.type)
      print('LOCATION : ', output.location)
      print('Magnitude : ', output.magnitude)

      return output

def thread_routine(aname):
    while True:
        #print('Caplist number of : ', len(capList))
        #print('Running Thread',aname)

        time.sleep(0.1)
        


####  Setup Network CAP monitoring   ####
UDP_IP = '0.0.0.0'         
UDP_PORT = 11789           
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT))
print('Monitoring Port {0} for any messages'.format(UDP_PORT))
x = threading.Thread(target=thread_routine, args=(1,))
x.start()



def clicksomebuttons(ip1,ip2,ip3):

    driver1 = webdriver.Chrome()
    driver2 = webdriver.Chrome()
    driver3 = webdriver.Chrome()

    time.sleep(1)

    driver1.get("http://{0}/tab9.html".format(ip1))
    driver2.get("http://{0}/tab9.html".format(ip2))
    driver3.get("http://{0}/tab9.html".format(ip3))
    button1 = driver1.find_element_by_id('hmmm')
    button2 = driver2.find_element_by_id('hmmm')
    button3 = driver3.find_element_by_id('hmmm')

    button1.click()
    button2.click()
    button3.click()


def createPDF(directory):

    st = read(rf'{directory}\*.mseed')
    st.plot()


def event(sen1,sen2,sen3,ip1,ip2,ip3):

    chan1 = sen1.sender[4:8]
    chan2 = sen2.sender[4:8]
    chan3 = sen3.sender[4:8]
    chan1 = ("DG.0{}.00.FNZ".format(chan1))
    chan2 = ("DG.0{}.00.FNZ".format(chan2))
    chan3 = ("DG.0{}.00.FNZ".format(chan3))

    clicksomebuttons(ip1,ip2,ip3)

    start = min([sen1.time,sen2.time,sen3.time]) - timeBefore
    end = max([sen1.time,sen2.time,sen3.time]) + timeAfter
    print(start)
    print(end)

    startUNIX = UTCDateTime(start).timestamp
    endUNIX = UTCDateTime(end).timestamp

    directory = (rf"c:\data\events\{start.year}-{start.month}-{start.day} {start.hour}.{start.minute}.{start.second}")

    os.mkdir(directory)
    print(rf"http://{ip1}/data?channel={chan1}&from={startUNIX}&to={endUNIX}", rf"{directory}\{chan1}.mseed")
    wget.download(rf"http://{ip1}/data?channel={chan1}&from={startUNIX}&to={endUNIX}", rf"{directory}\{chan1}.mseed")
    wget.download(rf"http://{ip2}/data?channel={chan2}&from={startUNIX}&to={endUNIX}", rf"{directory}\{chan2}.mseed")
    wget.download(rf"http://{ip3}/data?channel={chan3}&from={startUNIX}&to={endUNIX}", rf"{directory}\{chan3}.mseed")

    createPDF(directory)

while True:
    data, addr = sock.recvfrom(16384)
    capAlert = generateCAP(data)
    if capAlert.magnitude[:3] == "STA":
        capList.append(capAlert)
        ip.append(addr[0])

    if len(capList) >= 3:
        cap1 = capList[len(capList)-1]
        cap2 = capList[len(capList)-2]
        cap3 = capList[len(capList)-3]
        ip1 = ip[len(ip)-1]
        ip2 = ip[len(ip)-2]
        ip3 = ip[len(ip)-3]
        if cap1 != cap2 and cap1 != cap3 and cap2 != 3:
            if abs(cap1.time - cap2.time) <= tw and abs(cap1.time - cap3.time) <= tw and abs(cap2.time - cap3.time) <= tw:
                print("!!!!!!!!!!!  EVENT  !!!!!!!!!!!!!")
                winsound.Beep(1500,500)
                time.sleep(0.1)
                winsound.Beep(1500,700)
                event(cap1,cap2,cap3,ip1,ip2,ip3)

