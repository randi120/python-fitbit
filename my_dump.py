#!/usr/bin/env python
"""
This is an example script to dump the fitbit data for a range of days.

Create a config file as specified in test.py
"""
import time
import os
import ConfigParser

import fitbit

CONFIG = ConfigParser.ConfigParser()
CONFIG.read(["fitbit.conf", os.path.expanduser("~/fitbit/.fitbit.conf")])

DUMP_DIR=os.path.expanduser(CONFIG.get('fitbit', 'dump_dir'))

def client():
    return fitbit.Client(CONFIG.get('fitbit', 'user_id'), CONFIG.get('fitbit', 'uid'), CONFIG.get('fitbit', 'u'))

def dump_to_str(data):
    return "\n".join(["%s,%s" % (str(ts), v) for ts, v in data])

def dump_to_file(data_type, date, data):
    directory = "%s/%s" % (DUMP_DIR, data_type)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    with open("%s/%s.csv" % (directory, str(date)), "w") as f:
        f.write(dump_to_str(data))

def dump_day(date):
    c = client()
    n = 1

    dump_to_file("steps", date, c.intraday_steps(date))
    time.sleep(n)    
    dump_to_file("calories", date, c.intraday_calories_burned(date))
    time.sleep(n)
    #dump_to_file("active_score", date, c.intraday_active_score(date))
    dump_to_file("floors", date, c.intraday_floors(date))
    time.sleep(n)
    dump_to_file("sleep", date, c.intraday_sleep(date))
    time.sleep(n)
    dump_to_file("distance", date, c.intraday_distance(date))
    time.sleep(n)


if __name__ == '__main__':
    #import logging
    #logging.basicConfig(level=logging.DEBUG)
   
    from datetime import date
    from dateutil.rrule import rrule, DAILY
    
    startDate = date(2014, 1, 25)
    endDate = date(2014, 5, 26)
    
    for dt in rrule(DAILY, dtstart=startDate, until=endDate):
        print dt.date()
        dump_day(dt.date())
    

 
    
    #dump_day((datetime.datetime.now().date() - datetime.timedelta(days=1)))
