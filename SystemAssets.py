# Author:   Gregory Ewing
# Contact:  gregjewi@umich.edu
# Date:     January 2019

# About:    Support Module for real-time recommendations for sewer assets.
#           Specifically written to interface with InfluxDB and GLWA systems.


import numpy as np
import datetime as dt
import pytz
from collections import OrderedDict
import influxdb

def get_asset_fields(filename):
    # Get asset fields from csv file. 
    # Return in dict['MEASURE'] = [fields]
    # Assets fields detail what fields and measured can be queried.
    # See './csv/GLWA_infdb_data_structures.csv' for example.
    asset_fields = {}
    with open(filename) as f:
        for l in f.readlines()[1:]:
            l = l.rstrip().split(',')
            asset_fields[l[0]] = []
            for i in l[1:]:
                if len(i) > 1 and i != 'SITE':
                    asset_fields[l[0]].append(i.rstrip())
                    
    return asset_fields

def connection(connection_file):
    # Make and return influxDB client object
    # Define connection details in './csv/Influx_Connect_File.csv'
    d = {}

    with open(connection_file) as f:
        for l in f:
            a = l.rstrip().split(',')
            d[a[0]] = a[1]


    influx_connection = influxdb.InfluxDBClient(
        host=d['host'],
        port=int(d['port']),
        database=d['database'],
        username=d['username'],
        password=d['password']
    )

    return influx_connection 

def time_return(*args):
    # ---- About ----
    # Convert datetime type in utc and convert to nanosecond since epoch.
    # Return tuple of nanoseconds and string of time
    
    t = dt.datetime.utcnow()

    # if given an argument, use it as the time.
    # *Assume* argument is type datetime
    for arg in args:
        t = arg
    
    t = t.replace(tzinfo = pytz.UTC)
    epoch0 = dt.datetime(1970,1,1)
    epoch0 = epoch0.replace(tzinfo = pytz.UTC)
    nano = str(int((t - epoch0).total_seconds()*1000000000))
    
    # Make datetime string
    t_simple_string = t.strftime("%m-%d %H:%M") + " UTC"
    
    # return time tuple
    return (nano, t_simple_string)

def calc_avail(v,pump,t):
    # ---- About ----
    # Used iteratively to determine the amount of time to recommend for each
    # pump within a pumpstation. calc_avail is called iteratively, accounting
    # previous pump(s) output to achieve the volume recommendation for
    # subsequent pumps at a pumpstation.
    
    # Maximum possible outflow from pump
    V_max = pump.flowrate * t

    if V_max > v:
        pump.rec = v / pump.flowrate # [seconds]
        return 0 # no more available volume for other pumps
    else:
        pump.rec = t # [seconds]
        return v - V_max # 


class asset():
    # ---- About ----
    # Super class for pumpstation, sewer meter, cso basin, and valve.
    # Write and query from/to influxDB capabilities fundamental purpose
    # of class.
    
    def __str__(self):
        return self.name
    
    def __init__(self, name, measure, fields):
        self.name = name            # Should be equivalent to the "site" tag in influx.
        self.measure = measure      # CSO_BASIN, ISD, CSO, VALVE, etc.
        self.fields = {}            # Type: LIST. Available infdb fields for given measure 
        self.add_fields(fields)     # Add to dict, for querying later
    
    def add_fields(self,fields):
        for f in fields:
            self.fields[f] = ''
        
    def query_measures(self,client):
        # ----- About ---- 
        # Given fields, query last value.
        # Store in dictionary
        
        for f in self.fields:
            query_str = "SELECT last({0}) FROM {1} WHERE SITE='{2}'".format(f,self.measure,self.name)
            # print(query_str)
            query_return = client.query(query_str)
            # print(query_return)
            series = query_return.raw['series'][0]
            self.fields[f] = series['values'][0]  
            
    def write_rec(self,client, *extra): 
        # ---- About ---- 
        # Not quite depricated, but used sparingly in new applications
        # Recommendations are only numeric (flow, volume)
        # More comprehensive recommendation push via write_goals() below.
        t = time_return(self.rec['DT_UTC'])
        
        self.write_str = '{0},SITE={1},GROUP={2},TYPE={3}'.format(self.measure,self.name,str(self.rec['GROUP']),self.rec['TYPE'])
        for arg in extra:
            for key in arg:
                self.write_str = self.write_str + ',{0}={1}'.format(key,self.rec[key])
        self.write_str = self.write_str + ' REC={0},REC_DT_UTC=\"{1}\" {2}'.format(str(self.rec['REC']),t[1],t[0])
        
        try:
            return(client.write_points([self.write_str],protocol='line'))
            # return [True]
        except:
            return [False, self.write_str]
        
    def write_goals(self,client,field,*extra):
        # ---- About ----
        # Write range of goals stored in the dictionaries self.q_goal or self.v_goal
        # Return a list of lines that failed to write to influxDB, [] empty if none
        
        fails = []
        
        # Trying to avoid tracebacks during the write to DB.
        go = False
        if field == "FLOW_REC":
            to_write = self.q_goal
            go = True
        elif field == "VOLUME_REC":
            to_write = self.v_goal
            go = True
        else:
            fails.append("{0} field value not recognized. Line not written.".format(field))
            
        if go:
            # q_goal and v_goal are type dict
            for key in to_write:
                a  = to_write[key][0].replace('T',' ').replace('Z','')
                a = dt.datetime.strptime(a,"%Y-%m-%d %H:%M:%S")
                t = time_return(a)
                line_str = '{0},SITE={1},GROUP={2},LOCATION={3}'.format(self.measure,self.name,to_write[key][2], key)
                for arg in extra:
                    for key in arg:
                        line_str = line_str + ',{0}={1}'.format(key,extra[key])
                        
                line_str = line_str + ' {0}={1},DT_UTC=\"{2}\" {3}'.format(field,str(to_write[key][1]),t[1],t[0])
                
                # Write to influxDB
                try:
                    client.write_points([line_str],protocol='line')
                except:
                    # if traceback during write
                    fails.append(line_str)
        return fails
            
class pumpstation(asset):
    # ---- About ----
    # Subclass to the asset class. Used with GLWA pumpstations
    # In some instances, gates are associated with a pumpstation
    # asset.
    
    def __str__(self):
        return "PUMPSTATION: " + super().__str__()
    
    def __init__(self, name, measure, fields, *args, **kwargs):
        super().__init__(name,measure,fields)
        
        self.rec = []
        
        self.kwargs = kwargs
        kw = self.kwargs.keys()
        if 'depth_max' in kw:
            self.depth_max[0] = self.kwargs['depth_max']
        if 'vol_max' in kw:
            self.vol_max = self.kwargs['vol_max']
    
    
    # ---- Pumps and Wet Wells Functions ----        
    def pump_dict(self):
        # self.pumps is a container for Pump objects of the pumps in the pumpstation
        # see Pump class for more on pump objects.
        self.pumps = OrderedDict()
            
        with open('/home/ubuntu/RT_Recs/csv/{0}_PUMP_FLOWS.csv'.format(self.measure),'r') as f:
            for l in f:
                s = l.strip().split(',')
                self.pumps[s[0]] = Pump(s)
                
    def pumps_running(self):
        # Count how many pumps are currently running for
        # 'ST' == Storm Pumps
        # 'SN' == Sanitary Pumps
        running = {'ST':0,'SN':0}
        for p in self.pumps:
            running[p[:2]] = running[p[:2]] + self.fields[p][1]
            # print(p, self.fields[p][1])
        self.running = running
        
    def pumps_recommended(self,client):
        # Used with building the 'recommended.svg' layer.
        # Query and counts the number of pumps to be used.
        # Must already have called self.pump_dict() method
        self.recommended = {'ST':0,'SN':0}
        
        for p in self.pumps:
            q_str  = "SELECT last(REC_BOOL) FROM {0} WHERE PUMP='{1}'".format(self.measure,p)
            query_return = client.query(q_str)

            # if query_return is empty 
            if not query_return.keys():
                pass
            else:
                series = query_return.raw['series'][0]
                self.pumps[p].status = series['values'][0]            
                self.recommended[p[:2]] = self.recommended[p[:2]] + self.pumps[p].status[1]
    
    def write_pump_recs(self, client, *extra):
        # Write recommendations associated with pumps at station to DB
        # Return a list of lines that failed to write to influxDB, [] empty if none failed

        fails = []
        t = time_return()
        
        for p in self.pumps:            
            if isinstance(self.pumps[p].rec,str):
                pass
            
            else:
                # Make line write for each pump recommendation
                self.write_str = '{0},SITE={1},PUMP={2}'.format(self.measure,self.name,p)
                for arg in extra:
                    for key in arg:
                        self.write_str = self.write_str + ',{0}={1}'.format(key,self.rec[key])

                # Single line contains many fields associated with the pumpstation measure
                self.write_str = self.write_str + ' REC_SECONDS={0},'.format(self.pumps[p].rec['REC_SECONDS'])
                self.write_str = self.write_str + 'REC_STR=\"{0}\",'.format(self.pumps[p].rec['REC_STR'])
                self.write_str = self.write_str + 'REC_BOOL={0},'.format(self.pumps[p].rec['REC_BOOL'])
                self.write_str = self.write_str + 'DT_UTC=\"{0}\" {1}'.format(t[1],t[0])
                
                try:
                    client.write_points([self.write_str],protocol='line')
                except:
                    fails.append(self.write_str)
                    
        return fails
    
    # ---- Gates Functions ----
    def gates_open(self, name_str, num_gates):
        # Counts number of gates open at latest time.
        self.open_gates = 0
        for i in range(0,num_gates):
            self.open_gates = self.open_gates + self.fields[name_str+str(i+1)][1]
            
    def gates_recommended(self,client):
        # Used with building the 'recommended.svg' layer.
        # Query and counts the number of gates to be used.
        self.recommended['SWR_GATE'] = 0
        
        for gate in [key for key in self.fields if 'GATE' in key]:
            q_str = "SELECT last(REC_BOOL) FROM {0} WHERE GATE='{1}'".format(self.measure,gate)
            query_return = client.query(q_str)
            
            # if query_return is empty 
            if not query_return.keys():
                pass
            else:
                series = query_return.raw['series'][0]
                self.recommended['SWR_GATE'] = self.recommended['SWR_GATE'] + series['values'][0][1]      
    
    # ---- Both ----
    def calc_dcost(self,*args):
        # Accepts one extra argument that will change the field that the cost is calculated with
        # eg., 'WET_WELL_2'
        field = 'WET_WELL_1'
        for arg in args:
            field = arg
        
        self.d_cost = [self.fields[field][0]]
        d = ( self.fields[field][2] - self.set_point[0] ) * self.d_param[0]
        self.d_cost.append(d)
        
    def normalized_depth(self):
        # Converts elevation or wet well level from ft. to unitless number
        # Order of ~0-1.0...
        to_normalize = ['WET_WELL_1']
        if self.wet_wells[0] > 1:
            to_normalize.append('WET_WELL_2')
        
        for field,invert,dmax in zip(to_normalize,self.invert,self.depth_max):
            d = ( self.fields[field][1] - invert ) / dmax
            self.fields[field].append(d)
        
        
class Pump():
    # Pump class. Use with Class Pumpstation
    def __init__(self,name_flow):
        self.name = name_flow[0]
        self.flowrate = float(name_flow[1])
        self.group = int(name_flow[2])
        self.rec = ''
        
class Gate():
    # Gate Class. Use with Class Asset or sub.
    def __init__(self):
        self.name = 'SWR_GATE_'
        self.location = 'UNKNOWN'
        
class sewer_meter(asset):
    # Asset subclass. Used with GLWA Sewer Meters assets.
    def __str__(self):
        return "METER: " + super().__str__()
    
    def __init__(self, name, measure, fields, *args, **kwargs):
        super().__init__(name,measure,fields)
        
    def every_timestep(self,client):
        # Perform query and calculations altogether.
        super().query_measures(client)
        self.normalized_depth()
        self.calc_area_max()
        self.calc_percent_area()
        
    def normalized_depth(self):
        # normalize depth. Ft to unitless ~0-1.0
        d = self.fields['LEVEL'][1] / self.depth_max
        self.fields['LEVEL'].append(d)
        
    def calc_area_max(self):
        # Calculate the area of the conduit at meter location.
        # *Assume* circular conduit...
        self.area_max = np.pi * ( self.depth_max / 2 ) ** 2
        
    def calc_percent_area(self):
        # Determine the percent of total area of sewer that is filled.
        # Again, assumes circular conduit. Uses geometry of circles to
        # estimate the area occupied.
        # % = A_currentCrossSection / A_max
        r = self.depth_max / 2
        h = self.fields['LEVEL'][1]
        t = self.fields['LEVEL'][0]
        
        # If depth is greater than half the pipe:
        if h > r:
            h = self.depth_max - self.fields['LEVEL'][1]
            theta = 2 * np.arccos((r-h)/r)
            A = np.pi * r**2 - (r**2 * ( theta - np.sin(theta)))/2
            
        # Depth less than half the pipe:
        else:
            theta = 2 * np.arccos((r-h)/r)
            A = (r**2 * (theta - np.sin(theta))) / 2
            
        pa = A / self.area_max
        self.percent_area = [t, pa]
        
    def calc_dcost(self,*args):
        # Used to determine downstream cost in MBC calculations
        # Accepts one extra argument that will change the field that the cost is calculated with.
        field = 'LEVEL'
        for arg in args:
            field = arg
        
        self.d_cost = [self.fields[field][0]]
        d = ( self.fields[field][2] - self.set_point[0] ) * self.d_param[0]
        self.d_cost.append(d)
        
class cso_basin(asset):
    # Asset Subclass. For the CSO basins and like assets.
    def __str__(self):
        return "Basin and Other: " + super().__str__()
    
    def __init__(self, name, measure, fields, *args, **kwargs):
        super().__init__(name,measure,fields)
        
    def normalized_depth(self):
        # Converts from elevation/level in ft to ~0-1
        for field,invert,dmax in zip(self.to_normalize,self.invert,self.max_depth,):
            d = ( self.fields[field][1] - invert ) / dmax
            self.fields[field].append(d)
            
    def calc_dcost(self):
        # Used to determine downstream cost in MBC calculations
        self.d_cost = [self.fields['BASIN_LEVEL'][0]]
        
        if self.fields['BASIN_LEVEL'][2] < 0.0:
            d = ( 0.0 - self.set_point[0] ) * self.d_param[0]
        else:
            d = ( self.fields['BASIN_LEVEL'][2] - self.set_point[0] ) * self.d_param[0]
        
        self.d_cost.append(d)
        
            
class valve(asset):
    # Asset sub class
    def __str__(self):
        return "VALVE: " + super().__str__()
    
    def __init__(self, name, measure, fields, *args, **kwargs):
        super().__init__(name,measure,fields)
        
    
class report():
    # Class to push reporting and warnings to a txt file.
    # Use in conjuction with a pipe during the cron to
    # to supress stdout
    def __str__(self):
        return "Find report at: " + self.filename
    
    def __init__(self, filename):
        self.filename = filename
        self.no_header = True
        
    def write(self,queue):   
        if self.no_header:
            self.header()

        # if sent line, put into list to iterate the line as one.
        if isinstance(queue,str):
            queue = [queue]
        
        with open(self.filename,"a+") as f:
            for line in queue:
                f.write(line + "\n")

    def header(self):
        with open(self.filename,"a+") as f:
            header = "\nTime: {0}".format(time_return()[1])
            f.write(header + "\n")
            self.no_header = False
