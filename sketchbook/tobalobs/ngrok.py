import requests
import time
import urllib

# list API
API_SAVE_TUNNEL = 'http://66.70.190.240:8000/api/save-tunnel'
API_GET_NGROK = 'http://localhost:4040/api/tunnels'

# check internet connection
while True: 
    try:
        urllib.urlopen("http://google.com")
        # get parameter penyimpangan 
        r = requests.get(url = API_GET_NGROK)
        data = r.json()
        if(len(data['tunnels']) == 0 ):
            continue;
        for tunnel in data['tunnels']:
            #print(tunnel)
            if (tunnel['name'] == 'tcp_ssh'):
                hostPort = tunnel['public_url'].split('//')
                splitHostPort = hostPort[1].split(':')
                host = splitHostPort[0]
                port = splitHostPort[1]
                id = 1
                dataHttp = {'id':id, 'ip':host,'port':port}
                r = requests.post( url = API_SAVE_TUNNEL, data = dataHttp)
            elif (tunnel['name'] == 'http_flask'):
                host = tunnel['public_url']
                port = 80
                id = 2
                dataHttp = {'id':id, 'ip':host,'port':port}
                r = requests.post( url = API_SAVE_TUNNEL, data = dataHttp)
    except:
        print('something error')
        time.sleep(1)
        continue;
    else:
        break;
 



