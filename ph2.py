import json
from time import sleep

import urllib3
# TODO: Enable SSL
urllib3.disable_warnings()

class DataNotReady(Exception):
    pass


class ParseHub(object):
    # TODO: not needed?
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
        """
        Initializes ParseHub objects

        :param api_key: your API key from either PH website or browser plugin
        :param proxy: if needed, in format http[s]://host:port
        """
        self.api_key = api_key
        if proxy:
            self.conn = urllib3.proxy_from_url(proxy)
        else:
            self.conn = urllib3.PoolManager()
        self.projects = [project for project in self.getprojects()]

    def __repr__(self):
        return '<ParseHub object API key: \'{}\'>'.format(self.api_key)

    def getprojects(self):
        """
        Returns all project of a user
        :return: array of PhProject objects
        """
        resp = self.conn.request('GET', self.URLS['allprojects'], dict(api_key=self.api_key))
        data = resp.data.decode('utf-8')
        jdata = json.loads(data)['projects']
        # Convert nested JSON documents
        for project_index in range(len(jdata)):
            for field in ('options_json', 'templates_json'):
                jdata[project_index][field] = json.loads(jdata[project_index][field])
        # Pass project details dictionaries to constructors, return array
        return [PhProject(self, project) for project in jdata]

    @staticmethod
    def pprint(obj):
        """
        Pretty prints all attributes and their respective values of and object.
        Callables are skipped.
        :param obj: Object to be printed
        :return:
        """
        for argname in sorted([x for x in dir(obj) if not x.startswith('__')]):
            # Skip callables
            if hasattr(getattr(obj, argname), '__call__'):
                continue
            print("{} : {}".format(argname, getattr(obj, argname)))


class PhProject(object):
    """
    Implements project datatype and its functionality
    https://www.parsehub.com/docs/ref/api/v2/?python#project

    Attributes:

    token 	        A globally unique id representing this project.
    title 	        The title give by the user when creating this project.
    templates_json 	The JSON-stringified representation of all the instructions for running this project. This
                    representation is not yet documented, but will eventually allow developers to create
                    plugins for ParseHub.
    main_template 	The name of the template with which ParseHub should start executing the project.
    main_site 	    The default URL at which ParseHub should start running the project.
    options_json 	An object containing several advanced options for the project.
    last_run 	    The run object of the most recently started run (orderd by start_time) for the project.
    last_ready_run 	The run object of the most recent ready run (ordered by start_time) for the project. A ready run
                    is one whose data_ready attribute is truthy. The last_run and last_ready_run for a project may
                    be the same.
    """
    def __init__(self, ph, arg_dict: dict):
        self.ph = ph
        self.runs = []
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
        """
        Gets all runs for a given project

        :param offset: Get all except n newest runs
        :return: Arrays of available runs
        """
        resp = self.ph.conn.request(
            'GET', self.ph.URLS['project'].format(self.token), dict(api_key=self.ph.api_key, offset=offset))
        data = resp.data.decode('utf-8')
        jdata = json.loads(data)['run_list']
        return [PhRun(self.ph, rundata) for rundata in jdata]

    def run(self, args: dict={}):
        """
        Start a new run from a given project

        :param args:    start_url               (Optional) 	The url to start running on. Defaults to
                            the project’s start_site.
                        start_value_override    (Optional) 	The starting global scope for this run. This can be used to
                            pass parameters to your run. For example, you can pass {"query": "San Francisco"} to use the
                            query somewhere in your run. Defaults to the project’s start_value.
                            send_email              (Optional) 	If set to anything other than 0, send an email when
                            the run either completes successfully or fails due to an error. Defaults to 0.
        :return: A PhRun object referencing the new run
        """
        params = dict(api_key=self.ph.api_key)
        if args:
            params.update(args)
        resp = self.ph.conn.request(
            'POST', self.ph.URLS['startrun'].format(self.token), params)
        data = resp.data.decode('utf-8')
        jdata = json.loads(data)
        return PhRun(self.ph, jdata)

    def delete_runs(self):
        """
        Delete all runs for a given project
        :return:
        """
        for run in self.get_runs():
            run.delete()

    def __repr__(self):
        return '<PhProject \'{}\' token \'{}\'>'.format(self.title, self.token)

    def pprint(self):
        """
        Prettyprint the project's attributes
        :return:
        """
        ParseHub.pprint(self)


class PhRun(object):
    """
    Implements the functionality of Run object
    https://www.parsehub.com/docs/ref/api/v2/?python#run

    Attributes:

    project_token 	A globally unique id representing the project that this run belongs to.
    run_token 	    A globally unique id representing this run.
    status 	        The status of the run. It can be one of initialized, running, cancelled, complete, or error.
    data_ready 	    Whether the data for this run is ready to download. If the status is complete, this will always be
                    truthy. If the status is cancelled or error, then this may be truthy or falsy, depending on whether
                    any data is available.
    start_time 	    The time that this run was started at, in UTC +0000.
    end_time 	    The time that this run was stopped. This field will be null if the run is either initialized or
                    running. Time is in UTC +0000.
    pages 	        The number of pages that have been traversed by this run so far.
    md5sum 	        The md5sum of the results. This can be used to check if result data has changed between two runs.
    start_url 	    The url that this run was started on.
    start_value 	The starting value of the global scope for this run.
    """
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
        # self.data = self.get_data()

    def __repr__(self):
        return '<PhRun object token:{}>'.format(self.run_token)

    def get_data(self, out_format: str='json'):
        """
        Get results for a given run. If the results were fetched before, returns it, otherwise fetch them from server.
        Throws DataNotReady exception if its not available
        :param out_format: 'json' or 'csv', csv not implemented yet
        :return: The fetched data
        """
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
        """
        Get results for a given run while blocking execution. If the results were fetched before, returns it, otherwise
        fetch them.
        :param out_format: 'json' or 'csv', csv not implemented yet
        :param chk_interval: interval to wait before checks, in seconds
        :param max_chks: maximum number of checks, if data is still not available DataNotReady exception is raised
        :return:
        """
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
        """
        Checks whether data is available for download for a given run
        :return:
        """
        resp = self.ph.conn.request(
            'GET', self.ph.URLS['project'].format(self.project_token), dict(api_key=self.ph.api_key))
        data = resp.data.decode('utf-8')
        return json.loads(data)['last_run']['data_ready']

    def cancel(self):
        """
        Cancel an in-progress run
        :return: run_token of the cancelled run
        """
        resp = self.ph.conn.request(
            'POST', self.ph.URLS['cancelrun'].format(self.run_token), dict(api_key=self.ph.api_key))
        data = resp.data.decode('utf-8')
        return json.loads(data)['run_token']

    def delete(self):
        """
        Deletes a run
        :return: run_token of the deleted run
        """
        resp = self.ph.conn.request(
            'DELETE', self.ph.URLS['deleterun'].format(self.run_token), dict(api_key=self.ph.api_key))
        data = resp.data.decode('utf-8')
        return json.loads(data)['run_token']

    def pprint(self):
        """
        Prettyprint the run's attributes
        :return:
        """
        ParseHub.pprint(self)

    def __eq__(self, other):
        if not isinstance(other, PhRun):
            raise TypeError("Cant compare PhRun to {}".format(type(other)))
        return self.md5sum == other.md5sum
