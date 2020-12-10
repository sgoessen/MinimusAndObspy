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

### Variables
tw = 1 # Number of seconds between CAP alerts for event to be declared
timeBefore = 5 # Number of seconds before event to retrieve
timeAfter = 5 # Number of seconds after event to retrieve

temp = os.environ["TEMP"]

capList = []
magList = []
ip = []

class CapMsg:
    def __init__(self,capAlert):
        ns = {'alert':'urn:oasis:names:tc:emergency:cap:1.2'}
        root = ET.fromstring(capAlert.decode('utf-8'))
        infoElement = root.find('alert:info',ns)
        locationElement = infoElement.find('alert:area',ns)
        self.time = UTCDateTime(root.find('alert:sent',ns).text) #Returns time of event in UTCDatetime unit
        self.identifier = root.find('alert:identifier',ns).text
        self.sender = root.find('alert:sender',ns).text
        self.type = infoElement.find('alert:event',ns).text
        self.location = locationElement.find('alert:circle',ns).text
        self.magnitude = infoElement.find('alert:description',ns).text



def generateCAP(incoming):
      output = CapMsg(incoming)
      #print('CAP Alert recevied....')
      #print('SENDER : ', output.sender)
      #print('TIME : ', output.time)
      #print('TYPE : ', output.type)
      #print('LOCATION : ', output.location)
      #print('Magnitude : ', output.magnitude)

      return output



####  Setup Network CAP monitoring   ####
UDP_IP = '0.0.0.0'         
UDP_PORT = 11789           
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT))
print('Monitoring Port {0} for any messages'.format(UDP_PORT))


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


def createPDF(directory,eventTime):

    st = read(r'{}\*.mseed'.format(directory))
    st.plot(outfile=r'{}\plot.PNG'.format(directory),size=(800, 300))
    st1 = read(r'{}\*.mseed'.format(directory), starttime=eventTime-1, endtime=eventTime+1)
    st1.plot(outfile=r'{}\plot1.PNG'.format(directory), size=(800, 300))



def thread_event(directory, sen1,sen2,sen3,ip1,ip2,ip3):

    os.mkdir(directory)
    chan1 = sen1.sender[4:8]
    chan2 = sen2.sender[4:8]
    chan3 = sen3.sender[4:8]
    chan1 = ("DG.0{}.00.FNZ".format(chan1))
    chan2 = ("DG.0{}.00.FNZ".format(chan2))
    chan3 = ("DG.0{}.00.FNZ".format(chan3))
    clicksomebuttons(ip1,ip2,ip3)

    start = min([sen1.time,sen2.time,sen3.time]) - timeBefore
    end = max([sen1.time,sen2.time,sen3.time]) + timeAfter

    startUNIX = UTCDateTime(start).timestamp
    endUNIX = UTCDateTime(end).timestamp

    #print(r"http://{0}/data?channel={1}&from={2}&to={3}".format(ip1, channel1, startUNIX, endUNIX))
    #print(r"http://{0}/data?channel={1}&from={2}&to={3}".format(ip2, channel2, startUNIX, endUNIX))
    #print(r"http://{0}/data?channel={1}&from={2}&to={3}".format(ip3, channel3, startUNIX, endUNIX))
    time.sleep(1)

    wget.download(rf"http://{ip1}/data?channel={chan1}&from={startUNIX}&to={endUNIX}", rf"{directory}\{chan1}.mseed")
    wget.download(rf"http://{ip2}/data?channel={chan2}&from={startUNIX}&to={endUNIX}", rf"{directory}\{chan2}.mseed")
    wget.download(rf"http://{ip3}/data?channel={chan3}&from={startUNIX}&to={endUNIX}", rf"{directory}\{chan3}.mseed")

    createPDF(directory, min([sen1.time,sen2.time,sen3.time]))

def thread_recordMag(directory,m1,m2,m3):

    f= open(rf"{directory}\magDetails.txt","w+")
    f.write(f"{m1.sender}  ")
    f.write(f"{m1.location}  ")
    f.write(f"{m1.magnitude}\r\n")
    f.write(f"{m2.sender}  ")
    f.write(f"{m2.location}  ")
    f.write(f"{m2.magnitude}\r\n")
    f.write(f"{m3.sender}  ")
    f.write(f"{m3.location}  ")
    f.write(f"{m3.magnitude} %d\r\n")
    f.close()

directory = temp

while True:
    data, addr = sock.recvfrom(16384)
    capAlert = generateCAP(data)

    if capAlert.magnitude[:3] == "STA":
        capList.append(capAlert)
        ip.append(addr[0])
    else:
        magList.append(capAlert)




    if len(capList) >= 3:
        cap1 = capList[len(capList)-1]
        cap2 = capList[len(capList)-2]
        cap3 = capList[len(capList)-3]
        ip1 = ip[len(ip)-1]
        ip2 = ip[len(ip)-2]
        ip3 = ip[len(ip)-3]
        if cap1 != cap2 and cap1 != cap3 and cap2 != cap3:
            if abs(cap1.time - cap2.time) <= tw and abs(cap1.time - cap3.time) <= tw and abs(cap2.time - cap3.time) <= tw:
                print ("!!!!!!  Detected Event  !!!!!!")
                winsound.Beep(2000,200)
                #winsound.Beep(2000, 200)
                #winsound.Beep(2000, 200)
                sdir = min([cap1.time, cap2.time, cap3.time])
                directory = (rf"c:\data\events\{sdir.year}-{sdir.month}-{sdir.day} {sdir.hour}.{sdir.minute}.{sdir.second}")
                x = threading.Thread(target=thread_event, args=(directory,cap1,cap2,cap3,ip1,ip2,ip3))
                x.start()
                capList = []
                ip=[]

    if len(magList) >=3:
        mag1 = magList[len(magList) - 1]
        mag2 = magList[len(magList) - 2]
        mag3 = magList[len(magList) - 3]
        if mag1 != mag2 and mag1 != mag3 and mag2 != mag3:
            if abs(mag1.time - mag2.time) <= tw and abs(mag1.time - mag3.time) <= tw and abs(mag2.time - mag3.time) <= tw:
                print(rf"   {mag1.identifier[:8]}  {mag1.magnitude}")
                print(rf"   {mag2.identifier[:8]}  {mag2.magnitude}")
                print(rf"   {mag3.identifier[:8]}  {mag3.magnitude}")
                y = threading.Thread(target=thread_recordMag, args=(directory, mag1, mag2, mag3))
                y.start()
            magList = []


