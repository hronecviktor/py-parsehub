import urllib3
import json
from time import sleep


class PyrseHub(object):
    INITIALIZED = 'initialized'
    RUNNING = 'running'
    CANCELLED = 'cancelled'
    COMPLETE = 'complete'
    ERROR = 'error'
    def __init__(self, api_key: str, proxy: str=None, include_last_run: int=1):
        self.api_key = api_key
        self.urls = urls = dict(projects='https://www.parsehub.com/api/v2/projects',
                                delete='https://www.parsehub.com/api/scrapejob/delete',
                                run='https://www.parsehub.com/api/scrapejob/run',
                                run_status='https://www.parsehub.com/api/scrapejob/run_status',
                                status='https://www.parsehub.com/api/scrapejob/status',
                                cancel='https://www.parsehub.com/api/scrapejob/cancel',
                                download='https://www.parsehub.com/api/scrapejob/dl')
        if proxy:
            self.conn = urllib3.proxy_from_url(proxy)
        else:
            self.conn = urllib3.PoolManager()
        self.projects = {project.title: project for project in self.getprojects(include_last_run)}

    def getprojects(self, include_last_run: int):
        resp = self.conn.request('GET', self.urls['projects'], dict(api_key=self.api_key))
        # print(resp.status)
        data = resp.data.decode('utf-8')

        print(data)
        jdata = json.loads(data)['projects']
        print(json.dumps(jdata, sort_keys=True, indent=2, separators=(',', ' : ')))
        # #Convert nested JSON documents
        # for project_index in range(len(jdata)):
        #     for field in ('options_json','templates_json'):
        #         jdata[project_index][field] = json.loads(jdata[project_index][field])
        # print(json.dumps(jdata, sort_keys=True, indent=2, separators=(',', ' : ')))
        #
        # # Pass project details dictionaries to constructors, return array
        # return [phProject(self, project) for project in jdata]


class phProject(object):
        def __init__(self, ph, arg_dict: dict):
            self.ph = ph
            self.runs = []
            self.last_run = None
            for key in arg_dict.keys():
                if key != 'last_run':
                    setattr(self, key, arg_dict[key])
                else:
                    self.runs.append(phRun(self.ph, arg_dict[key]))

        def __repr__(self):
            return 'phProject<{}:{}>'.format(self.title, self.token)

        def getruns(self):
            resp = self.ph.conn.request('GET', self.ph.urls['status'], dict(api_key=self.ph.api_key, token=self.token))
            data = resp.data.decode('utf-8')
            # print(data)
            jdata = json.loads(data)['runList']
            print('[GETRUNS]:',json.dumps(jdata, sort_keys=True, indent=2, separators=(',', ': ')))

            self.runs = {run.run_token: run for run in [phRun(self.ph, rundict) for rundict in jdata]}
            # print(self.runs)

        def delete_project(self):
            resp = self.ph.conn.request('POST', self.ph.urls['delete'], dict(api_key=self.ph.api_key, token=self.token))
            return resp.data.decode('utf-8')

        def run(self, start_url=None, start_value_override=None, block: bool = False):
            options = {}
            if start_url:
                options['start_url'] = start_url
            if start_value_override:
                options['start_value_override'] = start_value_override
            resp = self.ph.conn.request('POST', self.ph.urls['run'], dict(options, api_key=self.ph.api_key, token=self.token))
            jdata = json.loads(resp.data.decode('utf-8'))
            print("=============IN RUN: ", dict(jdata,status='NOTSTARTED'))
            newrun = phRun(self.ph, dict(jdata))
            if block:
                while True:
                    newrun.refresh(block=True)
                    if newrun.status == 'complete':
                        break
            self.last_run = newrun
            return newrun

class phRun(object):
    def __init__(self, ph, arg_dict: dict):
        self.ph = ph
        self.status = 'NOT_STARTED'
        for key in arg_dict.keys():
            setattr(self, key, arg_dict[key])

    def __repr__(self):
        return 'phRun<token:{}>'.format(self.run_token)

    def refresh(self, block:bool=False):
        while True:
            # Break if job is already complete
            if self.status == 'complete':
                return self.status
            # Get new data for the job
            resp = self.ph.conn.request('GET', self.ph.urls['run_status'], dict(api_key=self.ph.api_key, run_token=self.run_token))
            data = resp.data.decode('utf-8')
            jdata = json.loads(data)
            print('[JDATA]:',jdata)
            # If status changed
            if jdata['status'] != self.status:
                print('==============STATUS CHANGED, UPDATING ALL====================')
                # Refresh the attributes with new data
                for key in jdata.keys():
                    setattr(self, key, jdata[key])
                return self.status
            # Status did not change and blocking is on
            elif block:
                print('NOT CHANGED, SLEEPING 250ms')
                sleep(250/1000)
        # print(json.dumps(jdata, sort_keys=True, indent=2, separators=(',', ': ')))

    def __cmp__(self, other):
        return self.md5sum == other.md5sum



urllib3.disable_warnings()
p = PyrseHub(api_key='tDYy17aCebNjQ47QM7J4aSku3SGthPGh')

# projs = p.projects
# # runs = projs['www.google.com Project'].getruns()
# gpro = projs['www.google.com Project']
# lastjob = gpro.runs[0]
# if lastjob.status == PyrseHub.COMPLETE:
#     print('***LASTJOB STATUS***',lastjob.status)
# gpro.getruns()
# allruns = gpro.runs
# print(len(allruns), allruns)
# print('RUNNING THE JOB')
# run = gpro.run(block=True)
# # print('RUN COMPLETE')
# print('=============RUN', run)
# run.refresh()
# print('=============AFTER REFRESH', run.status)
# gpro.getruns()
# allruns = gpro.runs
# print(allruns)
#
#
