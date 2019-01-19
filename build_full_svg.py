# Author: 		Gregory Ewing
# Contact: 		gregjewi@umich.edu
# Date: 		January 2019

# Description:	Combine svg layers base, latest, and recommended into a single svg 
#				file base_latest_recommended.svg'

import svgutils.transform as sg
import subprocess
import datetime as dt

## DIFFERENT SCRIPT IN FINAL
final = sg.SVGFigure("19in","11.5in")

base = sg.fromfile('/home/ubuntu/RT_Recs/GRAPHICS/base_v2.svg')
base = base.getroot()

latest = sg.fromfile('/home/ubuntu/RT_Recs/GRAPHICS/latest.svg')
latest = latest.getroot()

recs = sg.fromfile('/home/ubuntu/RT_Recs/GRAPHICS/recommended.svg')
recs = recs.getroot()

t_str = "Dash Build Time: " + dt.datetime.utcnow().strftime("%m-%d %H:%M") + " UTC"
build_time = sg.TextElement(25,60,t_str,size=12,color='red')

final.append([base,latest,recs,build_time])
final.set_size(["1900px","1150px"])
final.save('/home/ubuntu/RT_Recs/GRAPHICS/base_latest_recommended.svg')