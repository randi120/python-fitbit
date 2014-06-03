import xml.etree.ElementTree as ET
import datetime
from datetime import datetime as localDateTime
import urllib, urllib2
import logging
import json


_log = logging.getLogger("fitbit")
_log.setLevel(logging.DEBUG)

#new graph data syntax
#https://www.fitbit.com/graph/getNewGraphData?userId=XXXX&type=intradayFloors&dateFrom=2014-05-23&dateTo=2014-05-23
#https://www.fitbit.com/graph/getNewGraphData?type=distance&dateFrom=2014-04-13&dateTo=2014-04-13

#original syntax
#https://www.fitbit.com/graph/getGraphData?userId=XXXX&type=intradaySteps&dateTo=2014-05-21&period=1d

class Client(object):
    """A simple API client for the www.fitbit.com website.
    see README for more details
    """
    
    #def __init__(self, user_id, sid, uid, uis, url_base="http://www.fitbit.com"):
    def __init__(self, user_id, uid, u, url_base="http://www.fitbit.com"):
        
        self.user_id = user_id
        self.uid = uid        
        self.url_base = url_base

        #origninal cookie info
        #self.sid = sid
        #self.uis = uis        
        #self._request_cookie = "sid=%s; uid=%s; uis=%s" % (sid, uid, uis)
        
        self.u = u

        self._request_cookie = "uid=%s; u=%s" % (self.uid, self.u)    

    def intraday_distance(self, date):	
        """Retrieve the floors burned every 5 minutes
        the format is: [(datetime.datetime, floors), ...]
        """
        return self._graphdata_intraday_request_new("distance", date,False)
    
    def intraday_floors(self, date):
        """Retrieve the floors burned every 5 minutes
        the format is: [(datetime.datetime, floors), ...]
        """
        return self._graphdata_intraday_request_new("intradayFloors", date)

    def intraday_calories_burned(self, date):
        """Retrieve the calories burned every 5 minutes
        the format is: [(datetime.datetime, calories_burned), ...]
        """
        return self._graphdata_intraday_request("intradayCaloriesBurned", date)
    
    def intraday_active_score(self, date):
        """Retrieve the active score for every 5 minutes
        the format is: [(datetime.datetime, active_score), ...]
        """
        return self._graphdata_intraday_request("intradayActiveScore", date)

    def intraday_steps(self, date):
        """Retrieve the steps for every 5 minutes
        the format is: [(datetime.datetime, steps), ...]
        """
        return self._graphdata_intraday_request("intradaySteps", date)
    
    def intraday_sleep(self, date):
        """Retrieve the sleep status for every 1 minute interval
        the format is: [(datetime.datetime, sleep_value), ...]
        The statuses are:
            0: no sleep data
            1: asleep
            2: awake
            3: very awake
        For days with multiple sleeps, you need to provide the sleep_id
        or you will just get the first sleep of the day
        """
        return self._graphdata_intraday_request("intradaySleep", date)
    
    def _request(self, path, parameters):
        # Throw out parameters where the value is not None
        parameters = dict([(k,v) for k,v in parameters.items() if v])
        
        query_str = urllib.urlencode(parameters)

        request = urllib2.Request("%s%s?%s" % (self.url_base, path, query_str), headers={"Cookie": self._request_cookie})
        _log.debug("requesting: %s", request.get_full_url())

        data = None
        try:
            response = urllib2.urlopen(request)
            data = response.read()
            response.close()
        except urllib2.HTTPError as httperror:
            data = httperror.read()
            httperror.close()

        _log.debug("response: %s", data)

        return data.strip()

    def _graphdata_intraday_xml_request(self, graph_type, date, data_version=2108, **kwargs):
        params = dict(
            userId=self.user_id,
            type=graph_type,
            #version="amchart",
            dataVersion=data_version,
            chart_Type="column2d",
            period="1d",
            dateTo=str(date)
        )
        
        if kwargs:
            params.update(kwargs)

        return ET.fromstring(self._request("/graph/getGraphData", params))

    def _graphdata_intraday_json_request(self, graph_type, date, data_version=2108, **kwargs):
        params = dict(
            userId=self.user_id,
            type=graph_type,
            #version="amchart",
            #dataVersion=data_version,
            #chart_Type="column2d",
            #period="1d",
            dateFrom=str(date),
            dateTo=str(date)
        )
        if kwargs:
            params.update(kwargs)
        
        
        return self._request("/graph/getNewGraphData", params)


    def _graphdata_intraday_request(self, graph_type, date):
        # This method used for the standard case for most intraday calls (data for each 5 minute range)
        xml = self._graphdata_intraday_xml_request(graph_type, date)
        
        base_time = datetime.datetime.combine(date, datetime.time())
        timestamps = [base_time + datetime.timedelta(minutes=m) for m in xrange(0, 288*5, 5)]
        #values = [int(float(v.text)) for v in xml.findall("data/chart/graphs/graph/value")]
        values = [int(float(v.attrib['value'])) for v in xml.findall("dataset/set")]
        
        return zip(timestamps, values)
        
    def _graphdata_intraday_request_new(self, graph_type, date, convert2integer=True):
        """This method used for the new graph data case for most intraday calls 
        (data for each 5 minute range OR given by the data)
        (this should work with intradayCaloriesBurned,intradaySteps,intradayFloors,intradaySleep)       
        """
        
        decoded = json.loads(self._graphdata_intraday_json_request(graph_type, date))

        #values = [int(float(v.text)) for v in xml.findall("data/chart/graphs/graph/value")]

        if decoded['graph']['dataSets']['activity'].has_key('dataPoints'):
            if len(decoded['graph']['dataSets']['activity']['dataPoints'])==288:
                #recods every 5 mins
                base_time = datetime.datetime.combine(date, datetime.time())
                timestamps = [base_time + datetime.timedelta(minutes=m) for m in xrange(0, 288*5, 5)]
    
                if convert2integer:        
                    values = [int(float(v['value'])) for v in decoded['graph']['dataSets']['activity']['dataPoints'] ]
                else:
                    values = [   (float(v['value'])) for v in decoded['graph']['dataSets']['activity']['dataPoints'] ]
                    
                return zip(timestamps, values)
            else:
                #arbitrary record length
                if convert2integer:        
                    tup = list([(localDateTime.strptime(v['dateTime'],"%Y-%m-%d %H:%M:%S"), int(float(v['value']))) for v in decoded['graph']['dataSets']['activity']['dataPoints'] ])
                else:
                    tup = list([(localDateTime.strptime(v['dateTime'],"%Y-%m-%d %H:%M:%S"),     float(v['value']))  for v in decoded['graph']['dataSets']['activity']['dataPoints'] ])
                return tup
    
            
        else: 
            return list()
        	
        	
        #NOT USING THIS 
    def _graphdata_intraday_sleep_request(self, graph_type, date, sleep_id=None):
        # Sleep data comes back a little differently
        xml = self._graphdata_intraday_xml_request(graph_type, date, data_version=2112, arg=sleep_id)
        
        
        elements = xml.findall("data/chart/graphs/graph/value")
        timestamps = [datetime.datetime.strptime(e.attrib['description'].split(' ')[-1], "%I:%M%p") for e in elements]
        
        # TODO: better way to figure this out?
        # Check if the timestamp cross two different days
        last_stamp = None
        datetimes = []
        base_date = date
        for timestamp in timestamps:
            if last_stamp and last_stamp > timestamp:
                base_date -= datetime.timedelta(days=1)
            last_stamp = timestamp
        
        last_stamp = None
        for timestamp in timestamps:
            if last_stamp and last_stamp > timestamp:
                base_date += datetime.timedelta(days=1)
            datetimes.append(datetime.datetime.combine(base_date, timestamp.time()))
            last_stamp = timestamp
        
        values = [int(float(v.text)) for v in xml.findall("data/chart/graphs/graph/value")]
        return zip(datetimes, values)