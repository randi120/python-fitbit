import fitbit
import datetime
import os
import ConfigParser


"""
Create a config file at ~/fitbit/.fitbit.conf with the following:

[fitbit]
user_id: XXXXX
uid: 123456
u: <long string>
dump_dir: ~/Dropbox/fitbit

This data comes from the cookies. 
To get this data, simply open chrome  and get to your fitbit dashboard then press "Control+Shift+I" to bring up console
Chrome: click "Resources" on the top bar and "Cookies" on the left bar to expand it, followed by "www.fitbit.com"
You should see the necessary fields

"""




CONFIG = ConfigParser.ConfigParser()
CONFIG.read(["fitbit.conf", os.path.expanduser("~/fitbit/.fitbit.conf")])


client = fitbit.Client(CONFIG.get('fitbit', 'user_id'), CONFIG.get('fitbit', 'uid'), CONFIG.get('fitbit', 'u'))


date = datetime.date(2014,5,21)


# example data
steps = client.intraday_steps(date)
floors = client.intraday_floors(date)
cal = client.intraday_calories_burned(date)
sleep = client.intraday_sleep(date)
dist = client.intraday_distance(date)


# data will be a list of tuples. example:
# [
#   (datetime.datetime(2010, 2, 21, 0, 0), 0),
#   (datetime.datetime(2010, 2, 21, 0, 5), 40),
#   ....
#   (datetime.datetime(2010, 2, 21, 23, 55), 64),
# ]

# The timestamp is the beginning of the 5 minute range the value is for

# Other API calls:
# data = client.intraday_calories_burned(datetime.date(2010, 2, 21))
# data = client.intraday_active_score(datetime.date(2010, 2, 21))

# Sleep data is a little different:
# data = client.intraday_sleep(datetime.date(2010, 2, 21))

# data will be a similar list of tuples, but spaced one minute apart
# [
#   (datetime.datetime(2010, 2, 20, 23, 59), 2),
#   (datetime.datetime(2010, 2, 21, 0, 0), 1),
#   (datetime.datetime(2010, 2, 21, 0, 1), 1),
#   ....
#   (datetime.datetime(2010, 2, 21, 8, 34), 1),
# ]

# The different values for sleep are:
#   0: no sleep data
#   1: asleep
#   2: awake
#   3: very awake
