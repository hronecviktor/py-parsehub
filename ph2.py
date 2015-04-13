import urllib3
import json


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
        # self.projects = {project.title: project for project in self.getprojects()}



if __name__ == '__main__':
    ph = ParseHub(api_key='tDYy17aCebNjQ47QM7J4aSku3SGthPGh')
