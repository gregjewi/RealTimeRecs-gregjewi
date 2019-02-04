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
=====================

User-Defined Inputs
----------------------

Proper execution of the control and recommendation proocedure requires user input to define variables critical to the calculations.

..note:: Most user-defined inputs are tuples to take advantage of the data type's immutable characteristic, and therefore accidental changing of the value during operations.

Recommendation Interval and Threshold
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``recommendation_time`` is the interval, in seconds, between each run of ``CombineMBC.py``.
It is also the time interval used when providing recommendations. 
``threshold`` is the lowest amount of time, in seconds, that a recommendation must have for it to be written to the InfluxDB (and then provided to the operator.) 
Changing either would impact the recommendation quantities.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 18-23



Asset Objects Instantiation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Asset objects are the umbrellas under which all components of the routine system are grouped. 
They are instantianted by providing asset: name, measurement, and fields as written in InfluxDB.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 30-43

For more information on the asset objects, check out :doc:`SystemAsset` and :doc:`SoftwareAndApplications`

Set Physical Attributes
^^^^^^^^^^^^^^^^^^^^^^^^^
In the real system, asset objects have physical attributes such as invert elevations, the number of wet wells and their max depths, or some other geometric attribute. 
All of these attributes need to be supplied by the user. 
Examples of attribute assignment can be seen in the code block below.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 45-70


Control Routine Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^

User-defined weighting parameters and setpoints are used in the control routine as well. 
These are pre-determined weighting parameters that were determined through offline experimentation.
Therefore, they are supplied by user input.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 72-107

To learn more about how these parameters were determined, check out :doc:`DeterminingParameters`


Query Measures and Normalize
--------------------------------

The control routine uses queried measurements normalized to the asset's respective maximums. 
The following lines query the InfluxDB for measurements and then normalizes them with respect to each asset's maximum depth.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 110-115

The final line, ``DRI.every_timestep(influx_client)``, queries the database and then calculates the normalized cross sectional area in the sewer conduit where the measurement was taken.


Market-Based Control
----------------------

The lines 118 through 189 of code follow the methodology for determining individual's purhcasing power, as described in :doc:`WaterExchangeMarket`.
Normalized depths and upstream parameter weights for assets are collected into arrays. 
In the case that the measured and normalized depth is a negative number, the normalized value is set to zero. 
(This can occur in cases where an instrument reports a wet well depth that can be below the invert elevation of the reservoir, and which the conceptual model recognizes as the asset's bottom.)
Likewise, upstream weighting parameters are collected into arrays.
The indexes for the arrays correspond 