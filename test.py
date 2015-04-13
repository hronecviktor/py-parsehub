import urllib3
import zipfile
from io import BytesIO
import json

# Proxy
http = urllib3.proxy_from_url('http://websense.usk.egit.sk:3128')
# For unproxied connection
# http = urllib3.PoolManager()

### GET RUN_STATUS by run_token
###
# r = http.request('GET', 'http://www.parsehub.com/api/scrapejob/run_status',
#                  {'api_key':'tDYy17aCebNjQ47QM7J4aSku3SGthPGh', 'run_token' : 'tEgOgLwuAR2cKPnImZlQdYMe-kpLxIuO'})
# print(r.status)
# print(r.data.decode('utf-8'))


### GET RESULTS BY run_token
###
r = http.request('GET','https://www.parsehub.com/api/scrapejob/dl', {'api_key':'tDYy17aCebNjQ47QM7J4aSku3SGthPGh',
                                                                     'run_token':'tmAF7lirdViTxuhroK8w4FP4UE82H8S4'})
myzip = zipfile.ZipFile(BytesIO(r.data))

print('Status: {}'.format(r.status))

for info in myzip.infolist():
    print('Filename: {}'.format(info.filename))
    for line in myzip.open(info.filename).readlines():
        print(line.decode('utf-8'))
        print(json.dumps(line,indent=2,separators=(',', ': ')))

