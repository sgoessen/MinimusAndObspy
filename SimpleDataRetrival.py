# -*- coding: utf-8 -*-
"""
Created on 9/12/2020
@author: sgoessen
"""

import os
import wget
from obspy import read, UTCDateTime


######### Start of variable to set #############
temp = os.environ["TEMP"]
ip = "192.168.78.1"
channel = "DG.0185E.00.FNZ"
start = UTCDateTime("2020-12-10T00:00:00.0")
end = UTCDateTime("2020-12-10T01:00:00.0")
########### End of variables to set ###########

startUNIX = UTCDateTime(start).timestamp
endUNIX = UTCDateTime(end).timestamp

if os.path.exists(rf"{temp}\tt.mseed"):  # See if temp file exists, if so delete.
  os.remove(rf"{temp}\tt.mseed")

print(rf"http://{ip}/data?channel={channel}&from={startUNIX}&to={endUNIX}")
wget.download((rf"http://{ip}/data?channel={channel}&from={startUNIX}&to={endUNIX}"), rf"{temp}\tt.mseed")

st = read(rf"{temp}\tt.mseed", starttime=start, endtime=end, format='MSEED')
print(st)
st.plot()
