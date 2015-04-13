import json
from time import sleep

import urllib3


class DataNotReady(Exception):
    pass


class ParseHub(object):
    INITIALIZED = 'initialized'
    RUNNING = 'running'
    CANCELLED = 'cancelled'
    COMPLETE = 'complete'
    ERROR = 'error'
    URLS = dict(project='https://www.parsehub.com/api/v2/projects/{}',  # GET A PARTICULAR PROJECT
                startrun='https://www.parsehub.com/api/v2/projects/{}/run',  # RUN A PARTICULAR PROJECT
                allprojects='https://www.parsehub.com/api/v2/projects',  # GET PROJECT LIST
                getrun='https://www.parsehub.com/api/v2/runs/{}',  # GET A PARTICULAR RUN
                getdata='https://www.parsehub.com/api/v2/runs/{}/data',  # GET RUN DATA
                lastready='https://www.parsehub.com/api/v2/projects/{}/last_ready_run/data',  # LAST DATA FOR A PROJECT
                cancelrun='https://www.parsehub.com/api/v2/runs/{}/cancel',  # CANCEL A RUN
                deleterun='https://www.parsehub.com/api/v2/runs/{}',  # DELETE A RUN
                )

    def __init__(self, api_key: str, proxy: str=None):
        self.api_key = api_key
        if proxy:
            self.conn = urllib3.proxy_from_url(proxy)
        else:
            self.conn = urllib3.PoolManager()
        self.projects = [project for project in self.getprojects()]

    def __repr__(self):
        return '<ParseHub object API key: \'{}\'>'.format(self.api_key)

    def getprojects(self):
        resp = self.conn.request('GET', self.URLS['allprojects'], dict(api_key=self.api_key))
        data = resp.data.decode('utf-8')
        jdata = json.loads(data)['projects']
        # #Convert nested JSON documents
        for project_index in range(len(jdata)):
            for field in ('options_json', 'templates_json'):
                jdata[project_index][field] = json.loads(jdata[project_index][field])
        # Pass project details dictionaries to constructors, return array
        return [PhProject(self, project) for project in jdata]

    @staticmethod
    def pprint(obj):
        for argname in sorted([x for x in dir(obj) if not x.startswith('__')]):
            # Skip callables
            if hasattr(getattr(obj, argname), '__call__'):
                continue
            print("{} : {}".format(argname, getattr(obj, argname)))


class PhProject(object):
    def __init__(self, ph, arg_dict: dict):
        self.ph = ph
        # self.runs = []
        self.main_site = arg_dict['main_site']
        self.main_template = arg_dict['main_template']
        self.options_json = arg_dict['options_json']
        self.output_type = arg_dict['output_type']
        self.syntax_version = arg_dict['syntax_version']
        self.templates_json = arg_dict['templates_json']
        self.title = arg_dict['title']
        self.token = arg_dict['token']
        self.webhook = arg_dict['webhook']
        self.runs = self.get_runs(offset=0)
        self.last_run = PhRun(self.ph, arg_dict['last_run']) if arg_dict['last_run'] else None
        self.last_ready_run = PhRun(self.ph, arg_dict['last_ready_run']) if arg_dict['last_ready_run'] else None

    def get_runs(self, offset: int=0):
        resp = self.ph.conn.request(
            'GET', self.ph.URLS['project'].format(self.token), dict(api_key=self.ph.api_key, offset=offset))
        data = resp.data.decode('utf-8')
        jdata = json.loads(data)['run_list']
        return [PhRun(self.ph, rundata) for rundata in jdata]

    def run(self, args: dict={}):
        params = dict(api_key=self.ph.api_key)
        if args:
            params.update(args)
        resp = self.ph.conn.request(
            'POST', self.ph.URLS['startrun'].format(self.token), params)
        data = resp.data.decode('utf-8')
        jdata = json.loads(data)
        # TODO: Remove
        print("RUNNING: ", jdata)
        return PhRun(self.ph, jdata)

    def __repr__(self):
        return '<PhProject \'{}\' token \'{}\'>'.format(self.title, self.token)

    def pprint(self):
        ParseHub.pprint(self)


class PhRun(object):
    def __init__(self, ph, arg_dict: dict):
        self.ph = ph
        self.data = None
        self.data_ready = arg_dict['data_ready']
        self.end_time = arg_dict['end_time']
        self.md5sum = arg_dict['md5sum']
        self.pages = arg_dict['pages']
        self.project_token = arg_dict['project_token']
        self.run_token = arg_dict['run_token']
        self.start_time = arg_dict['start_time']
        self.start_url = arg_dict['start_url']
        self.start_value = arg_dict['start_value']
        self.status = arg_dict['status']
        # Uncomment to fetch data for each run at initialization
        # if self.data_ready:
        #     self.data = self.get_data()

    def __repr__(self):
        return '<PhRun object token:{}>'.format(self.run_token)

    def get_data(self, out_format: str='json'):
        if self.data:
            return self.data
        self.data_ready = self.check_available()
        if not self.data_ready:
            raise DataNotReady("The run {} has not yet finished, data not available yet.".format(self))
        resp = self.ph.conn.request(
            'GET', self.ph.URLS['getdata'].format(self.run_token), dict(api_key=self.ph.api_key, format=out_format))
        data = resp.data.decode('utf-8')
        jdata = json.loads(data)['results']
        self.data = jdata
        return jdata

    def get_data_sync(self, out_format: str='json', chk_interval=0.25, max_chks=65535):
        if self.data:
            return self.data
        check_cnt = 0
        while True:
            if check_cnt >= max_chks:
                break
            self.data_ready = self.check_available()
            if self.data_ready:
                break
            else:
                check_cnt += 1
                sleep(chk_interval)
        if not self.data_ready:
            raise DataNotReady("The run {} has not yet finished, data not available yet.".format(self))
        resp = self.ph.conn.request(
            'GET', self.ph.URLS['getdata'].format(self.run_token), dict(api_key=self.ph.api_key, format=out_format))
        data = resp.data.decode('utf-8')
        jdata = json.loads(data)['results']
        self.data = jdata
        return jdata

    def check_available(self):
        resp = self.ph.conn.request(
            'GET', self.ph.URLS['project'].format(self.project_token), dict(api_key=self.ph.api_key))
        data = resp.data.decode('utf-8')
        return json.loads(data)['last_run']['data_ready']

    def pprint(self):
        ParseHub.pprint(self)

    def __eq__(self, other):
        if not isinstance(other, PhRun):
            raise TypeError("Cant compare PhRun to {}".format(type(other)))
        return self.md5sum == other.md5sum


if __name__ == '__main__':
    urllib3.disable_warnings()
    parseh = ParseHub(api_key='tDYy17aCebNjQ47QM7J4aSku3SGthPGh')
    gpr = parseh.projects[0]
    # print(gpr)
    # glast = gpr.last_ready_run
    # print(glast)
    # glast.pprint()
    for p in parseh.projects:
        print("PROJECT: {}".format(p.title))
        print("LAST: {}".format(p.last_run))
        if p.last_run:
            p.last_run.pprint()
            p.last_ready_run.get_data()
        print("LAST READY: {}".format(p.last_ready_run))
        if p.last_ready_run:
            p.last_ready_run.pprint()
    newrun = parseh.projects[0].run()
    newrun.pprint()
    for _ in range(15):
        try:
            print(newrun.get_data_sync())
            break
        except DataNotReady as E:
            print("waiting")
            sleep(1)
    print(newrun.get_data())
