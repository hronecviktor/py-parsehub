import json

import urllib3


class ParseHub(object):
    INITIALIZED = 'initialized'
    RUNNING = 'running'
    CANCELLED = 'cancelled'
    COMPLETE = 'complete'
    ERROR = 'error'
    URLS = dict(project='https://www.parsehub.com/api/v2/projects/{}',          # GET A PARTICULAR PROJECT
                startrun='https://www.parsehub.com/api/v2/projects/{}/run',     # RUN A PARTICULAR PROJECT
                allprojects='https://www.parsehub.com/api/v2/projects',         # GET PROJECT LIST
                getrun='https://www.parsehub.com/api/v2/runs/{}',               # GET A PARTICULAR RUN
                rundata='https://www.parsehub.com/api/v2/runs/{}/data',         # GET RUN DATA
                lastready='https://www.parsehub.com/api/v2/projects/{}/last_ready_run/data',  # LAST DATA FOR A PROJECT
                cancelrun='https://www.parsehub.com/api/v2/runs/{}/cancel',     # CANCEL A RUN
                deleterun='https://www.parsehub.com/api/v2/runs/{}',            # DELETE A RUN
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
        # print(resp.status)
        data = resp.data.decode('utf-8')

        # print(data)
        jdata = json.loads(data)['projects']
        # print(json.dumps(jdata, sort_keys=True, indent=2, separators=(',', ' : ')))
        # #Convert nested JSON documents
        for project_index in range(len(jdata)):
            for field in ('options_json', 'templates_json'):
                jdata[project_index][field] = json.loads(jdata[project_index][field])
        # for proj in jdata:
        #     print("*"*80)
        #     print(json.dumps(proj, indent=2, sort_keys=True))
        # Pass project details dictionaries to constructors, return array
        return [PhProject(self, project) for project in jdata]


class PhProject(object):
        def __init__(self, ph, arg_dict: dict):
            self.ph = ph
            self.runs = []
            self.last_run = arg_dict['last_run']
            self.last_ready_run = arg_dict['last_ready_run']
            self.main_site = arg_dict['main_site']
            self.main_template = arg_dict['main_template']
            self.options_json = arg_dict['options_json']
            self.output_type = arg_dict['output_type']
            self.syntax_version = arg_dict['syntax_version']
            self.templates_json = arg_dict['templates_json']
            self.title = arg_dict['title']
            self.token = arg_dict['token']
            self.webhook = arg_dict['webhook']

        def get_runs(self, offset: int=0):
            resp = self.ph.conn.request(
                'GET', self.ph.URLS['project'].format(self.token), dict(api_key=self.ph.api_key, offset=offset))
            data = resp.data.decode('utf-8')
            jdata = json.loads(data)['run_list']
            print('[GETRUNS]:', json.dumps(jdata, sort_keys=True, indent=2, separators=(',', ': ')))
            return jdata

        def __repr__(self):
            return '<PhProject \'{}\' token \'{}\'>'.format(self.title, self.token)


class PhRun(object):
    def __init__(self, ph, arg_dict: dict):
        self.ph = ph
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

    def __repr__(self):
        return '<PhRun object token:{}>'.format(self.run_token)


if __name__ == '__main__':
    urllib3.disable_warnings()
    parseh = ParseHub(api_key='tDYy17aCebNjQ47QM7J4aSku3SGthPGh')
    prjs = parseh.projects
    for prj in prjs:
        print("********")
        print(prj)
        print(prj.last_run)
        print(prj.get_runs())
