# Author:       Gregory Ewing
# Contact:      gregjewi@umich.edu
# Date:         January 2019

# DESCRIPTION:  Determines which pumps are currently on. Builds and output 'latest.svg', a layer
#               with the proper 'ON' graphics showing for pumps and gates

import SystemAssets as SA
import svgutils.transform as sg
import datetime as dt

# Establish InfluxDB Connection
influx_client = SA.connection('/home/ubuntu/RT_Recs/csv/Influx_Connect_File.csv')
# Bring in Fields To Query
asset_fields = SA.get_asset_fields('/home/ubuntu/RT_Recs/csv/GLWA_infdb_data_structures.csv')


# Pumpstation class needs: site_name, measure, query_fields
fvw = SA.pumpstation('FVW','FAIRVIEW',asset_fields['FAIRVIEW'])
con = SA.pumpstation('CON','CONNER',asset_fields['CONNER'])
fre = SA.pumpstation('FRE','FREUD',asset_fields['FREUD'])

# Count which pumps are on for each station
add_to_base = []
for name in [con,fre,fvw]:
    name.query_measures(influx_client)
    name.pump_dict()
    name.pumps_running()

    if name.measure == 'CONNER':
        name.gates_open('SWR_GATE_',9)
        name.running['SG'] = name.open_gates
    
    for key in name.running:        
        if name.running[key] > 0:
            fstr = '/home/ubuntu/RT_Recs/GRAPHICS/{0}/CURRENT/{1}/{2}.svg'.format(name.measure,key,name.running[key])
            add_to_base.append(fstr)
            

# Build "LATEST.SVG" Figure
build = sg.SVGFigure("19in","11.5in")

# Load from file
# base = sg.fromfile('/home/ubuntu/RT_Recs/GRAPHICS/base.svg')
# base = base.getroot()
# base.moveto(5,270)

svg_list = []
# svg_list.append(base)

for fstr in add_to_base:
    layer = sg.fromfile(fstr)
    layer = layer.getroot()
    # layer.moveto(5,280)
    svg_list.append(layer)
    
t_str = "Pump Build Time: " + dt.datetime.utcnow().strftime("%m-%d %H:%M") + " UTC"
build_time = sg.TextElement(25,20,t_str,size=12,color='red')
svg_list.append(build_time)
    
# Make Latest Pump Layer 
build.append(svg_list)
build.save('/home/ubuntu/RT_Recs/GRAPHICS/latest.svg')