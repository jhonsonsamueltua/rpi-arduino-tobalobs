from flask import Flask, jsonify
import serial
import time
import requests

API_GET_KONDISI_MENYIMPANG = 'http://66.70.190.240:8000/api/penyimpangan-kondisi-tambak'

if __name__ == '__main__':
    app = Flask(__name__)
    
    @app.route('/get-monitor')
    def  monitor():
        s = []
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.flush()
        
        while True:
            pH = 0.0
            suhu = 0.0
            do = 0.0
            ket = ''
            phMin = 6
            phMax = 8
            suhuMin = 24
            suhuMax = 30
            doMin = 3
            doMax = 100
            cekMenyimpang = False
            
            try:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').rstrip() #get data from arduino
                    listData = data.split(';')
                    pH = float(listData[0])
                    suhu = float(listData[1])
                    do = float(listData[2])
                    
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
                                
                    if (pH < phMin or pH > phMax):
                        ket = "pH " + str(pH) + " bermasalah (pH < " + str(phMin) + "):" if pH < phMin else "pH " + str(pH) + " bermasalah (pH > " + str(phMax) + "):"
                        cekMenyimpang == True
                    if (suhu < suhuMin or suhu > suhuMax):
                        ket = ket + "Suhu " + str(suhu) + "C bermasalah (suhu < " + str(suhuMin) + "):" if suhu < suhuMin else "Suhu " + str(suhu) + "C bermasalah (suhu > " + str(suhuMax) + "C):"
                        cekMenyimpang = True
                    if (do < doMin or do > doMax):
                        ket = ket + "DO " + str(do) + " bermasalah (DO < " + str(doMin) + "):" if do < doMin else "DO " + str(do) + " bermasalah (DO > " + str(doMax) + "):"
                        cekMenyimpang = True
                    if (cekMenyimpang == False):
                        ket = 'Kondisi tambak normal'
                    
                    break;
            except:
                continue;
        
        return jsonify(
                ph = pH,
                suhu = suhu,
                do = do,
		keterangan = ket
            )

    app.run(debug=True, port=80, host='0.0.0.0')
