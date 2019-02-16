.. image:: images/LOGOS.png

==================
Real-Time Workflow
==================

.. toctree::
	:maxdepth: 1
	:caption: Contents:

	CombinedMBC
	BuildingTheSVGs
	ObjectToS3

Process
==========

**0.** (Every 10 minutes on the 5's) Scripts on the GLWA local server pushes data from assets in the study area to a University of Michigan hosted InfluxDB database instance. Scripts and code in this step will not be covered in our documentation here. For information on this process, contact Joe Burchi at GLWA.



``command_queue.py`` is called from an AWS instance on the 7's (ie. 0:07, 0:17, 0:27, etc.) to allow time for the proper execution of Step 0 above. This python script serves as a shell, which calls other scripts which can be grouped into three parts:

**1.** :doc:`CombinedMBC`: ``CombinedMBC.py`` queries InfluxDB for most recent system states, performs control routine with those data, writes recommendations back to InfluxDB.

**2.** :doc:`BuildingTheSVGs`: ``command_queue.py`` calls three python scripts and one operation from the command line, which together construct the pieces of the real-time recommendation graphic. They are:

	**-** ``latest.py``: Queries InfluxDB for most recent system states of individual pumps and gates. Builds .svg file that reflects these states.

	**-** ``recommended.py``: Queries InfluxDb for most recent *recommended* states for individual pumps and gates, as determined from the ``CombinedMBC.py`` run. Builds a ``.svg`` file that reflects the recommendation.
	
	**-** ``build_full_svg.py``: Builds a new ``.svg`` file from the ``.svg`` files in steps 2-3 and a base file. This essentially builds a real-time graphic of pump & gate current states and recommendations.
	
	**-** ``inkscape --export-png=/output/path/pic.png /input/path/built.svg``: Converts ``.svg`` to ``.png`` using Inkscape command line.

**3.** :doc:`ObjectToS3`: ``obj_to_s3.py`` uploads the ``.png`` image to an Amazon S3 bucket, publically visable so that the image can be used for the base graphic in a Grafana dashboard.
