# py-parsehub
Python3 ParseHub module

---
### What is ParseHub?
**ParseHub** is a service providing automated webscraping. You design a template using their Mozilla plugin and then access it through a REST API. Results can be retrieved in both JSON and CSV (coming soon) format. The templates are pretty flexible and use machine-learning to grasp complex hierarchies.
> You can extract data from anywhere. ParseHub works with single-page apps, multi-page apps and just about any other modern web technology.
ParseHub can handle Javascript, AJAX, cookies, sessions and redirects. You can easily fill in forms, loop through dropdowns, login to websites, click on interactive maps and even deal with infinite scrolling.


see [ParseHub homepage](https://www.parsehub.com/)

---
###Prerequisities
* python3 (3.2.3 tested)
* [urllib3](https://pypi.python.org/pypi/urllib3) ($ pip3 install urllib3)

---
### Usage


Initialize
 
    >>> from ph2 import ParseHub  
    >>> ph = ParseHub('<redacted API-key>')  

Get all projects

    >>> print(ph.projects)
    [<PhProject 'Project1' token 'tCWOS3cB-ZM8qtShXw6j8tyOHZ84hLik'>, <PhProject 'Project2' token 'tfs9Gv10cixnCtrk0iz0-u62r7lSdNt8'>]

Run a given project

    >>> p1 = ph.projects[0]
    >>> r1 = p1.run()

Is data available for download?

    >>> r1.check_available()
    1

Get data if available

    >>> r1.get_data()
    [{'link': 'http://www.123greetings.com/', 'title': '123Greetings'}, {'link': 'https://webmail.123-reg.co.uk/', 'title': 'Welcome to 123-reg Webmail | Webmail log in | 123-reg'}.....]

A blocking request for data

    >>> r2 = p1.run()
    >>> r2.get_data_sync()
    [{'link': 'http://www.123greetings.com/', 'title': '123Greetings'}, {'link': 'https://webmail.123-reg.co.uk/', 'title': 'Welcome to 123-reg Webmail | Webmail log in | 123-reg'}.....]

Cancel a running job

    >>> r3 = p1.run()
    >>> r3.cancel()

Or delete it alltogether

    >>> r3.delete()

Get array of runs of a project

    >>> p1.get_runs()
    [<PhRun object token:tbcBSs9i7WHWtx3nqXW7vwp9>, ....]

You can specify offset to leave out the last `x` runs

    >>> p1.get_runs(5)
    [<PhRun object token:tbcBSs9i7WHWtx3nqXW7vwp9>, ....]

Projects hold reference to their last `complete`d run...

    >>> p1.last_ready_run
    <PhRun object token:tCNPbuLm7wd-Aqmb9WHHZMV0>

...and the last run no matter what its status is

    >>> p1.last_run.status
    'running'

Runs can be compared based on their `md5sum` to detect changes between runs

    >>> p1.get_runs()[0] == p1.get_runs()[1]
    True

Both runs and projects can have their attributes easily printed printed for debugging

    >>> p1.last_run.pprint()
    data : [...]
    data_ready : 1
    end_time : 2015-04-13T15:30:10
    md5sum : 51b246040a0ee389dd5eb6bb46e1b06b
    pages : 1
    ph : <ParseHub object API key:'<redacted>'>
    project_token : tCWOS3cB-ZM8qtShXw6j8tyOHZ84hLik
    run_token : tCNPbuLm7wd-Aqmb9WHHZMV0
    start_time : 2015-04-13T15:30:03
    start_url : https://www.google.com/search?q=...
    start_value : {}
    status : complete
----
###Todo
* package
* refactor
* SSL
* CSV

