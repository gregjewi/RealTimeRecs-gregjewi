# Author:       Gregory Ewing
# Contact:      gregjewi@umich.edu
# Date:         January 2019

# DESCRIPTION:  Determines which pumps are *recommended* to be on. Builds and outputs 'recommended.svg',
#               a layer with the proper 'ON' graphics showing for pumps/gates.

import SystemAssets as SA
import svgutils.transform as sg
import datetime as dt

# Establish InfluxDB Connection
influx_client = SA.connection('PATH/TO/Influx_Connect_File.csv')
# Bring in Fields To Query
asset_fields = SA.get_asset_fields('PATH/TO/GLWA_infdb_data_structures.csv')

# Pumpstation class needs: site_name, measure, query_fields
fvw = SA.pumpstation('FVW','FAIRVIEW',asset_fields['FAIRVIEW'])
con = SA.pumpstation('CON','CONNER',asset_fields['CONNER'])
fre = SA.pumpstation('FRE','FREUD',asset_fields['FREUD'])

add_to_base = []
for ps in [con,fre,fvw]:
    ps.pump_dict()
    ps.pumps_recommended(influx_client)
    
    for key in ps.recommended:
        if ps.recommended[key] > 0:
            fstr = 'GRAPHICS/{0}/REC/{1}/{2}.svg'.format(ps.measure,key,ps.recommended[key])
            add_to_base.append(fstr)
            

build = sg.SVGFigure("19in","11.5in")

svg_list = []

for fstr in add_to_base:
    layer = sg.fromfile(fstr)
    layer = layer.getroot()
    #layer.moveto(5,280)
    svg_list.append(layer)
    

t_str = "Rec Build Time: " + dt.datetime.utcnow().strftime("%m-%d %H:%M") + " UTC"
build_time = sg.TextElement(25,40,t_str,size=12,color='red')
svg_list.append(build_time)

# Make Rec Pump Layer 
build.append(svg_list)
build.save('PATH/TO/GRAPHICS/recommended.svg')