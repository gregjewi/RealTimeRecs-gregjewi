.. image:: images/LOGOS.png

==========================================
Market-Based Control Recommendation Engine
==========================================

``CombinedMBC.py`` performs the calculations required to serve recommendations to operators. At its most basic it:

1. Queries InfluxDB for most recent sensor readings across the system.

2. Uses these data to compute a recommended flow for control assets with the study area.

3. Transform the numeric flow recommendations into actionable recommendations.

4. Write recommendations to InfluxDB.


Code
=====

User-Defined Input
-------------------

Proper execution of the control and recommendation proocedure requires user input to define variables critical to the calculations.

``recommendation_time`` is the interval, in seconds, between each run of ``CombineMBC.py``. It is also the time interval used when providing recommendations. ``threshold`` is the lowest amount of time, in seconds, that a recommendation must have for it to be written to the InfluxDB (and then provided to the operator.) Changing either would impact the recommendation quantities.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 18-23

