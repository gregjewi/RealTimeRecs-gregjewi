# Author:       Gregory Ewing
# Contact:      gregjewi@umich.edu
# Date:         January 2019

# Description: calls each script required for the recommendation service.

import subprocess
import SystemAssets as SA

commands = [
'/home/ubuntu/py3env/bin/python /home/ubuntu/RT_Recs/CombinedMBC.py',
'/home/ubuntu/py3env/bin/python /home/ubuntu/RT_Recs/latest.py',
'/home/ubuntu/py3env/bin/python /home/ubuntu/RT_Recs/recommended.py',
'/home/ubuntu/py3env/bin/python /home/ubuntu/RT_Recs/build_full_svg.py',
'inkscape --export-png=/home/ubuntu/RT_Recs/GRAPHICS/base_latest_recommended.png /home/ubuntu/RT_Recs/GRAPHICS/base_latest_recommended.svg',
'/home/ubuntu/py3env/bin/python /home/ubuntu/RT_Recs/obj_to_s3.py'
]

report_file = "/home/ubuntu/RT_Recs/_MBC_scripts_reports.txt"
warnings = []

with open(report_file,"a+") as out:
	for cmd in commands:
		run = subprocess.run(cmd, shell=True, stdout=out)
		if run.returncode:
			warnings.append("Warning during: {0}".format(cmd))

report = SA.report(report_file)
if warnings:
	report.write(warnings)
else:
	report.write(["No Warnings"])