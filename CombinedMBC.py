# Author:       Gregory Ewing
# Contact:      gregjewi@umich.edu
# Date:         January 2019

# Description:  Script performs
#               - Query last measure of sewer assets from InfluxDB
#               - Group assets into subgroups of upstream and downstream assets
#               - Determine recommendations from relative states within groups
#               - Push recommendations in flow, volume, and pump/gate status form
#                 to influxDB database


import influxdb
import numpy as np
import datetime as dt
import pytz
import SystemAssets as SA

# Define recommendation time
recommendation_time = 600 # [sec]
# Threshold for lowest amount of time for pump to be "ON"
threshold = 60 * 3  # 3 minutes


# Establish InfluxDB Connection
influx_client = SA.connection('/home/ubuntu/RT_Recs/csv/Influx_Connect_File.csv')
# Bring in Fields To Query
asset_fields = SA.get_asset_fields('/home/ubuntu/RT_Recs/csv/GLWA_infdb_data_structures.csv')

# ---- Define Variables ---- 
# both upstream and downstream

# Pumpstations
con = SA.pumpstation('CON','CONNER',asset_fields['CONNER'])
fre = SA.pumpstation('FRE','FREUD',asset_fields['FREUD'])
fvw = SA.pumpstation('FVW','FAIRVIEW',asset_fields['FAIRVIEW'])

# Conner Creek Basin Forebay
CC_BF = SA.cso_basin('CONNERS_CREEK','CSO_BASIN',asset_fields['CSO_BASIN'])

# DRI Downstream of FVW
# Need to change this to be an aggregate of the outfall elevs.
DRI = SA.sewer_meter('DT_S_8_DRI@JEFFERSONIAN_APT','SEWER_METER',asset_fields['SEWER_METER'])


# ---- Set Physical Attributes ----
con.invert = (44.50,55.0)
con.depth_max = (50,40)
con.flood_el = (95.0,)
con.wet_wells = (2,)

fre.invert = (13.0,)
fre.depth_max = (75.4,)
fre.flood_el = (84.0,)
fre.wet_wells = (1,)

fvw.invert = (0,)
fvw.depth_max = (37,)
fvw.flood_el = (96.0,)
fvw.wet_wells = (1,)

CC_BF.to_normalize = ('FOREBAY_LEVEL','BASIN_LEVEL')
CC_BF.max_depth = (17.5,22.0)
CC_BF.invert = (76.3,78.0)
# CC_BF.flood_el = (95.0,98.0) # (Basin,Forebay)

DRI.depth_max = 11.0
DRI.length = 1796
DRI.set_type = 'LEVEL'


# ---- Set MBC Parameters ----
# -- set values to be used in MBC algo

# -- Upstream Values
con.u_param = {
    'ST' : (0.097,),
    'SN' : (0.651,)
}

fre.u_param = {
    'ST' : (0.029,),
    'SN' : (1.0,)
}

fvw.u_param = {
    'SN' : (0.459,)
}

CC_BF.u_param = {
    'FORE_1' : (0.684,),
    'FORE_2' : (1.0,),
    'BASIN' : (0.419,)
}

# -- Downstream
#       Group 1
CC_BF.set_point = (0.062,)
CC_BF.d_param = (0.588,)

#       Group 2
fvw.d_param = (0.721,)
fvw.set_point = (0.802,)

#       Group 3
DRI.set_point = (0.921,)
DRI.d_param = (0.373,)


# ---- Get Latest Measures from Assets ----
regular_vars = [con,fre,fvw,CC_BF]
[i.query_measures(influx_client) for i in regular_vars];
[i.normalized_depth() for i in regular_vars];

DRI.every_timestep(influx_client)


# ---- Do MBC ----
# -- make normal depth groupings 
d_norm_1 = [ 
    con.fields['WET_WELL_2'][2], 
    fre.fields['WET_WELL_1'][2],
    CC_BF.fields['BASIN_LEVEL'][2]
]
d_norm_1 = np.array(d_norm_1)
d_norm_1[d_norm_1 < 0] = 0.0

d_norm_2 = [ 
    CC_BF.fields['BASIN_LEVEL'][2],
    CC_BF.fields['FOREBAY_LEVEL'][2],
    con.fields['WET_WELL_1'][2]
]
d_norm_2 = np.array(d_norm_2)
d_norm_2[d_norm_2 < 0] = 0.0

d_norm_3 = [
    fvw.fields['WET_WELL_1'][2]
]
d_norm_3 = np.array(d_norm_3)
d_norm_3[d_norm_3 < 0] = 0.0

# -- make u_params into arrays
u_p_1 = [
    con.u_param['ST'][0],
    fre.u_param['ST'][0],
    CC_BF.u_param['FORE_1'][0]
]
u_p_1 = np.array(u_p_1)

u_p_2 = [
    CC_BF.u_param['BASIN'][0],
    CC_BF.u_param['FORE_2'][0],
    con.u_param['SN'][0]
]
u_p_2 = np.array(u_p_2)

u_p_3 = [
    fvw.u_param['SN'][0]
]
u_p_3 = np.array(u_p_3)


# Tank numbers
ntanks1 = len(u_p_1) + 1
ntanks2 = len(u_p_2) + 1
ntanks3 = len(u_p_3) + 1
tanks = np.array([ntanks1,ntanks2,ntanks3])

# Calculate Pwealth
PW_1 = d_norm_1 * u_p_1
PW_2 = d_norm_2 * u_p_2
PW_3 = d_norm_3 * u_p_3
Pwealth = np.array([sum(PW_1),sum(PW_2),sum(PW_3)])

# Downstream Costs
downstream = [CC_BF,fvw, DRI]
[d.calc_dcost() for d in downstream]
dcosts = np.array([d.d_cost[1] for d in downstream])

# Pareto Price
Pareto = ( Pwealth + dcosts ) / tanks

Ppower1 = PW_1 - Pareto[0]
Ppower2 = PW_2 - Pareto[1]
Ppower3 = PW_3 - Pareto[2]

Ppower1[Ppower1 < 0] = 0
Ppower2[Ppower2 < 0] = 0
Ppower3[Ppower3 < 0] = 0

# Calculate Available Downstream
if CC_BF.fields['BASIN_LEVEL'][2] < 0.0:
    f_1 = CC_BF.max_depth[1]
else:
    f_1 = (1 - CC_BF.fields['BASIN_LEVEL'][2] ) * CC_BF.max_depth[1]
    
f_2 = (1 - fvw.fields['WET_WELL_1'][2] ) * fvw.depth_max[0]
f_3 = (1 - DRI.percent_area[1]) * DRI.area_max * DRI.length
    
# V = SA.depth_to_volume() # Feature coming soon
V_1 = f_1 * 192041.8 # Constant from GDRSS SWMM
V_2 = f_2 * 1000.0 # Constant from GDRSS SWMM

Qavail_1 = V_1 / recommendation_time # + Q_out, if known
Qavail_2 = V_2 / recommendation_time + fvw.fields['STATION_FLOWRATE'][1]
Qavail_3 = f_3 / recommendation_time
Qavail_3 = Qavail_3 + DRI.fields['FLOW'][1]

q_goal_1 = Qavail_1 * Ppower1
q_goal_2 = Qavail_2 * Ppower2
q_goal_3 = Qavail_3 * Ppower3

v_goal_1 = V_1 * Ppower1
v_goal_2 = V_2 * Ppower2
v_goal_3 = q_goal_3 * recommendation_time

# Group1: [con,fre,CC_BF]
# Group2: [BASIN,FORE_2,ConSN]
# Group3: [FVW]

# Conner Station
con.q_goal = {
    'ST' : [ con.fields['WET_WELL_2'][0],  q_goal_1[0], 1 ],
    'SN' : [ con.fields['WET_WELL_1'][0], q_goal_2[2], 2 ]
}
con.v_goal = {
    'ST' : [ con.fields['WET_WELL_2'][0],  v_goal_1[0], 1 ],
    'SN' : [ con.fields['WET_WELL_1'][0], v_goal_2[2], 2 ]
}

# Freud Station
fre.q_goal = {
    'ST' : [ fre.fields['WET_WELL_1'][0],  q_goal_1[1], 1 ]
}
fre.v_goal = {
    'ST' : [ fre.fields['WET_WELL_1'][0],  v_goal_1[1], 1 ]
}

# Fairview Station
fvw.q_goal = {
    'SN' : [ fvw.fields['WET_WELL_1'][0], q_goal_3[0], 3 ]
}
fvw.v_goal = {
    'SN' : [ fvw.fields['WET_WELL_1'][0], v_goal_3[0], 3 ]
}

# Conner Forebay and Basin
CC_BF.q_goal = {
    'FORE_1' : [ CC_BF.fields['FOREBAY_LEVEL'][0], q_goal_1[2], 1 ],
    'FORE_2' : [ CC_BF.fields['FOREBAY_LEVEL'][0],  q_goal_2[1], 2 ],
    'BASIN' : [ CC_BF.fields['BASIN_LEVEL'][0],  q_goal_2[0], 2 ]
}
CC_BF.v_goal = {
    'FORE_1' : [ CC_BF.fields['FOREBAY_LEVEL'][0], v_goal_1[2], 1 ],
    'FORE_2' : [ CC_BF.fields['FOREBAY_LEVEL'][0],  v_goal_2[1], 2 ],
    'BASIN' : [ CC_BF.fields['BASIN_LEVEL'][0],  v_goal_2[0], 2 ]
}

for asset in [con,fre,fvw,CC_BF]:
    asset.write_goals(influx_client,"FLOW_REC")
    asset.write_goals(influx_client,"VOLUME_REC")


# Determine recommendations at pump On/Off level of detail. Write to DB
for ps in [con,fre,fvw]:
    
    # Initialize a dictionary of pumps (class Pump) for each station
    ps.pump_dict()
    
    # walk through volume goals for each group the station is active in
    for goal in ps.v_goal:
        
        # Available volume downstream for the asset.
        # To divide between different pumps within station.
        avail = ps.v_goal[goal][1]
        
        # Filter pumps to that correspond to v_goal's group
        group_pumps = [p for p in ps.pumps if ps.pumps[p].group == ps.v_goal[goal][2] ]
        for pump in group_pumps:
            
            avail = SA.calc_avail(avail, ps.pumps[pump], 600) # Sets pump.rec in process too.
            
            seconds = ps.pumps[pump].rec
            ps.pumps[pump].rec = dict()
            ps.pumps[pump].rec['REC_SECONDS'] = seconds
            
            if seconds < threshold:
                ps.pumps[pump].rec['REC_STR'] = '' # "No action"
                ps.pumps[pump].rec['REC_BOOL'] = False # Recommend "Pump Off"
                
            else:
                time = dt.datetime(2000,1,1) + dt.timedelta(seconds = seconds)
                time_str = time.strftime('%M')
                ps.pumps[pump].rec['REC_STR'] = time_str # Pump "ON" for X-Minutes
                ps.pumps[pump].rec['REC_BOOL'] = True # "Pump ON", for viz
    
    ps.write_pump_recs(influx_client)
    
    # Next, Write CC_BF recommendations from flow/volume recommendations
    # accomplish with swmm solver.