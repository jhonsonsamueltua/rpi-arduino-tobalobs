import serial
import time
import os
import sys
import requests
from datetime import datetime
import urllib
import math

#get tambakID
tambakID = str(sys.argv[1])
# api monitor
API_MONITOR = 'http://66.70.190.240:8000/api/tambak/monitor'
API_MENYIMPANG = 'http://66.70.190.240:8000/api/tambak/monitor-menyimpang'
API_GET_KONDISI_MENYIMPANG = 'http://66.70.190.240:8000/api/penyimpangan-kondisi-tambak'
# ambang batas pengukuran / parameter 
phMin = 6
phMax = 8
suhuMin = 24
suhuMax = 30
doMin = 3
doMax = 100

# check internet connection
while True: 
    try:
        urllib.urlopen("http://google.com")
    except:
        print("Please check your connection")
        time.sleep(1)
        continue;
    else:
        break;
    
# get parameter penyimpangan 
r = requests.get(url = API_GET_KONDISI_MENYIMPANG)
data = r.json()
if (data['status'] == 'OK'):
    for kondisi in data['data']:
        if (kondisi['tipe'] == 'ph-min'):
            phMin = int(kondisi['nilai'])
        elif (kondisi['tipe'] == 'ph-max'):
            phMax = int(kondisi['nilai'])
        elif (kondisi['tipe'] == 'suhu-min'):
            suhuMin = int(kondisi['nilai'])
        elif (kondisi['tipe'] == 'suhu-max'):
            suhuMax = int(kondisi['nilai'])
        elif (kondisi['tipe'] == 'do-min'):
            doMin = int(kondisi['nilai'])
        elif (kondisi['tipe'] == 'do-max'):
            doMax = int(kondisi['nilai'])

# temp penyimpangan
phTemp = 0.0
suhuTemp = 0.0
doTemp = 0.0

if __name__ == '__main__':
    s = []
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.flush()
    while True:
        try:
            urllib.urlopen("http://google.com")
            
            # run code monitoring tambak 
            now = datetime.now()
            timeNow = now.strftime("%H:%M")
            cekSaveMonitor = False
            cekMenyimpang = False
            phKet = ''
            suhuKet = ''
            doKet = ''
            
            if ser.in_waiting > 0:
                try:
                    data = ser.readline().decode('utf-8').rstrip() #get data from arduino
                    listData = data.split(';')
                    pH = float(listData[0])
                    temp = float(listData[1])
                    do = float(listData[2])
                except:
                    print("error get data from arduino")
                    time.sleep(1)
                    continue;
                
                r = requests.get(url = API_GET_KONDISI_MENYIMPANG)
                data = r.json()
                if (data['status'] == 'OK'):
                    for kondisi in data['data']:
                        if (kondisi['tipe'] == 'ph-min'):
                            phMin = int(kondisi['nilai'])
                        elif (kondisi['tipe'] == 'ph-max'):
                            phMax = int(kondisi['nilai'])
                        elif (kondisi['tipe'] == 'suhu-min'):
                            suhuMin = int(kondisi['nilai'])
                        elif (kondisi['tipe'] == 'suhu-max'):
                            suhuMax = int(kondisi['nilai'])
                        elif (kondisi['tipe'] == 'do-min'):
                            doMin = int(kondisi['nilai'])
                        elif (kondisi['tipe'] == 'do-max'):
                            doMax = int(kondisi['nilai'])
                
                print(pH);
                print(temp);
                print(do);
                #continue;
                
                #cek pH
                if (pH < phMin or pH > phMax):
                    #set data
                    phKet = "pH " + str(pH) + " bermasalah (pH < " + str(phMin) + "):" if pH < phMin else "pH " + str(pH) + " bermasalah (pH > " + str(phMax) + "):"
                    penyimpanganKondisiTambakID = 1 if pH < phMin else 2
                    if (math.floor(phTemp) != math.floor(pH)):
                        phTemp = pH
                        #save notifikasi and push notifikasi
                        dataMenyimpang = {'tambakID':tambakID,'penyimpanganKondisiTambakID':penyimpanganKondisiTambakID, 'keterangan':phKet}
                        r = requests.post(url = API_MENYIMPANG, data = dataMenyimpang)
                        print("ph bermasalah")
                        cekMenyimpang = True
                else:
                    phTemp = 0.0
              
                #cek suhu
                if (temp < suhuMin or temp > suhuMax):
                    #set data
                    suhuKet = "Suhu " + str(temp) + "C bermasalah (suhu < " + str(suhuMin) + "):" if temp < suhuMin else "Suhu " + str(temp) + "C bermasalah (suhu > " + str(suhuMax) + "C):"
                    penyimpanganKondisiTambakID = 3 if temp < suhuMin else 4
                    if (math.floor(suhuTemp) != math.floor(temp)):
                        suhuTemp = temp
                        #save notifikasi and push notifikasi
                        dataMenyimpang = {'tambakID':tambakID,'penyimpanganKondisiTambakID':penyimpanganKondisiTambakID, 'keterangan':suhuKet}
                        r = requests.post(url = API_MENYIMPANG, data = dataMenyimpang)
                        print("suhu bermasalah")
                        cekMenyimpang = True
                else:
                    suhuTemp = 0.0 
                    
                #cek DO
                if (do < doMin or do > doMax):
                    #set data
                    doKet = "DO " + str(do) + " bermasalah (DO < " + str(doMin) + "):" if do < doMin else "DO " + str(do) + " bermasalah (DO > " + str(doMax) + "):"
                    penyimpanganKondisiTambakID = 5 if do < doMin else 6
                    if (math.floor(doTemp) != math.floor(do)):
                        doTemp = do
                        #save notifikasi and push notifikasi
                        dataMenyimpang = {'tambakID':tambakID,'penyimpanganKondisiTambakID':penyimpanganKondisiTambakID, 'keterangan':doKet}
                        r = requests.post(url = API_MENYIMPANG, data = dataMenyimpang)
                        print("DO bermasalah")
                        cekMenyimpang = True
                else:
                    doTemp = 0.0
                
                if(cekMenyimpang == True):
                    ket = phKet + '' + suhuKet + '' + doKet
                    data = {'tambakID':tambakID,'ph':pH,'suhu':temp,'do':do,'keterangan':ket}
                    r = requests.post(url = API_MONITOR, data = data)
                    cekSaveMonitor == True
                
                #kondisi normal
                if (cekSaveMonitor == False):
                    if (timeNow == "02:00" or timeNow == "06:00" or timeNow == "10:00" or timeNow == "14:00" or timeNow == "20:00" or timeNow == "14:37"):
                        ket = 'Kondisi tambak normal'
                        if (phTemp != 0.0 or suhuTemp != 0.0 or doTemp != 0.0):
                            ket = phKet + '' + suhuKet + '' + doKet
                        data = {'tambakID':tambakID,'ph':pH,'suhu':temp,'do':do,'keterangan':ket}
                        r = requests.post(url = API_MONITOR, data = data)
                        cekSaveMonitor = True
                        time.sleep(30) 

        except:
            print("Something error or check your connection ")
            time.sleep(1)
            continue;
        
        time.sleep(30)
    