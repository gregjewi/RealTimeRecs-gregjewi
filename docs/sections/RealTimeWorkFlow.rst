Real-Time Workflow
==================

Recommendations are currently provided on a 10 minute interval, refreshed on the 7s (ie. 0:07, 0:17, 0:27, etc.) The procedure is written in Python and executed from an Amazon Web Service (AWS) instance.

Process
-------
0. *(Every 10 minutes on the 5's)* Scripts on GLWA local server pushes data from assets in study area to University of Michigan hosted database on InfluxDB instance. **Note: scripts and code in this step will not be covered in documentation. For information on this process, contact Joe.Burchi@glwater.org.**

1. **'CombinedMBC.py'**: Queries InfluxDB for most recent system states, performs control routine with those data, writes recommendations back to InfluxDB.
2. **'latest.py'**: Queries InfluxDB for most recent system states of individual pumps and gates. Builds .svg file that reflects these states.
3. **'recommended.py'**: Queries InfluxDb for most recent *recommended* states for individual pumps and gates, as determined from the CombinedMBC.py run. Builds .svg file that reflects the recommendation.
4. **'build_full_svg.py'**: Builds a new .svg file from the .svg files in steps 2-3 and a base file. This essentially builds a real-time graphic of pump & gate current states and recommendations.
	- On the command line using Inkscape, the built .svg file is converted to a .png
5. **'obj_to_s3.py'**: Uploads the .png image to an Amazon S3 bucket, publically visable so that the image can be used for the base graphic in a Grafana dashboard.

.. toctree::
	:maxdepth: 1
	:caption: Contents:

	WorkFlow/CombinedMBC
	WorkFlow/BuildingTheSVGs
	WorkFlow/ObjectToS3