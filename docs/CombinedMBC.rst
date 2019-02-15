.. role:: raw-math(raw)
	:format: latex html

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

.. note:: Most user-defined inputs are tuples to take advantage of the data type's immutable characteristic, and therefore accidental changing of the value during operations.

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


Market-Based Control and Purchasing Power
-------------------------------------------

The lines 118 through 189 of code follow the methodology for determining individual's purhcasing power, as described in :doc:`WaterExchangeMarket`.
Normalized depths and parameter weights for both upstream assets and downstream locations are collected into arrays. 
In the case that the measured and normalized depth is a negative number, the normalized value is set to zero. 
(This can occur in cases where an instrument reports a wet well depth that can be below the invert elevation of the reservoir, and which the conceptual model recognizes as the asset's bottom.)
The indexing of asset normal depth and the upstream weighting parameters should be the same.
Once the arrays are made, upstream Wealth and downstream Cost are calculated for each group.
Pareto price for each group is then calculated using Wealth and Cost.
With the paretor price of each group in hand, purchasing price for individual assets is determined.
If the purchasing power of an asset is negative, the value is set to zero.

The following code is an example of the workflow for a single grouping:

.. code-block:: python
	
	# Make array of normalized depths
	d_norm_1 = [ 
	    con.fields['WET_WELL_2'][2], 
	    fre.fields['WET_WELL_1'][2],
	    CC_BF.fields['BASIN_LEVEL'][2]
	]
	d_norm_1 = np.array(d_norm_1)

	# if depth is negative, make zero
	d_norm_1[d_norm_1 < 0] = 0.0

	# -- Collect u_params of assets into arrays
	u_p_1 = [
	    con.u_param['ST'][0],
	    fre.u_param['ST'][0],
	    CC_BF.u_param['FORE_1'][0]
	]
	u_p_1 = np.array(u_p_1)


	# Tank numbers
	ntanks1 = len(u_p_1) + 1


	# Calculate Pwealth of upstream group
	PW_1 = d_norm_1 * u_p_1

	# Calculate Downstream Costs
	downstreamAsset.calc_dcost()

	dcost = downstreamAsset.d_cost[1]


	# Calculate the Pareto Price
	Pareto = ( Pwealth + dcost ) / ntanks1


	# Calculate Purchasing Power
	Ppower_1 = PW_1 - Pareto

	# Set purchasing power to 0 if negative
	Ppower1[Ppower1 < 0] = 0


Purchasing Power to Recommendations
------------------------------------
This section outlines how we transform purchasing power, as calculated in the section above, into a recommendation that is understandable and actionable by humans.

The purchasing power of an individual asset does not have intrinsic physical meaning to how much can be released downstream.
Rather, it is a value providing insite into the relation between the different asset states.
To make the purchasing power a meaningful value, relatable to the physical world, it is transformed into a volume of downstream capacity.
Having "purchased" downstream volume, the volume can be divided by the time interval to determine a target flow rate.
Knowing the target flow rate for each control point, we can make special recommendations for each that is based on our knowledge of the control capabilities.  
For example, given a recommended flow rate for a pump station, the number of pumps to turn on can be calculated. 
Likewise with a target flow rate and knowledge of the hydraulic conditions, a recommendation can be made for how to operate gates and valves.

These actions are completed in lines 191-296 of ``CombinedMBC.py``.


Calculate Available Fraction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The available fraction, :math:`f_{available}`, of the downstream is thought of as:

	:math:`f_{availabe} = 1 - f_{measured}`

**Conner Creek Retention Basin** and **Fairview Wet Well**: For retention basins or wet wells, we assume a linear relationship between depth and volume [#f1]_ .
Therefore we can approximate the available volume, :math:`V_{available}`, by

	:math:`V_{available} = f_{available} * Depth_{max} * A_{cs}`

	where:

		- :math:`V_{available}` is the available volume at a downstream point,
		- :math:`f_{available}` is the available fraction of depth,
		- :math:`Depth_{max}` is the maximum depth in the wet well or basin, and
		- :math:`A_{cs}` is the horizontal cross sectional area of the basin, assumed to be constant at all depths.

.. [#f1] The assumption of linearity was based up the GDRSS model. The constants used to calculate available volume were taken from this model.

**DRI**: For metered sewer locations that serve as the downstream point in a group, such as the DT-S-8 in the DRI, the available volume, :math:`V_{available}`, is calculated differently that basins and reservoirs. 
This is because in a sewer line we do not have a clear control volume like a well defined basin or wet well.
Instead we have assumed that there is 1,000-foot section of sewer, centered around sewer meter DT-S-8 where its measurements are representative of the section.
Doing so, we can approximate the available volume, :math:`V_{available}`, in the sewer by

	:math:`V_{available} = f_{available} * A_{max} * L_{rep}`

	where:

		- :math:`V_{available}` is the available volume at a downstream point,
		- :math:`f_{available}` is the fraction area available at the sensored location,
		- :math:`A_{max}` is the maximum vertical cross sectional area of the sewer at the meter location, and
		- :math:`L_{rep}` is the length of sewer that we assume the value of the measure is accurate for.


These calculations can be found in line 191-202 below.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 191-202


Available Volume to Numeric Goals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An available *inflow* rate to be supplied to the downstream point is calculated as,

	:math:`Q_{in, available} = V_{available} / T_{interval} + Q_{out}`

	where:

		- :math:`Q_{in, available}` is the available flowrate to be supplied to the downstream location,
		- :math:`V_{available}` is the available volume as calculated in the section above,
		- :math:`T_{interval}` is the recommendation interval,
		- :math:`Q_{out}` is the outflow of the control volume at the downstream point [#f2]_ .

.. [#f2] We ignore the outflow from the Conner Creek Retention Basin because: 1) the maximum storage volume is much larger than the dewatering pumps' capacity, and 2) the outflow from these dewatering pumps are not known.

With the total available flow and the available volume calculated, we can distribute that amonst the upstream agents via their calculated Purchasing Power. This is calculated as follows,

.. math::

	Q_{goals,j} = \begin{bmatrix} 
		q_{goal,1} \\ 
		q_{goal,2} \\ 
		\vdots \\ 
		q_{goal,n} 
		\end{bmatrix}_{j} =  Q_{available,j} \times \begin{bmatrix}
		P_{power,1} \\
		P_{power,2} \\
		\vdots \\
		P_{power,n}
		\end{bmatrix}_{j}

where,
	- :math:`Q_{goals,j}` is an :math:`\begin{bmatrix}n \times 1 \end{bmatrix}` array where :math:`n` is the number of upstream agents in group :math:`j`
	- :math:`Q_{available,j}` 
	- :math:`P_{power}` is an :math:`\begin{bmatrix}n \times 1 \end{bmatrix}` array the Purchasing Powers of the :math:`n` upstream agents in group :math:`j`


Likewise, calculating the volume available to each upstream agent is done in the same manner. These calculations are done in lines 202-215 and can be found below. 

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 203-216


Placing Recommendations to Object Containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In lines 221-257 the flow and volume recommendations (or 'goals') calculated in the section above are added to the respective asset objects to which they correspond.
Also, because asset objects themselves can hold multiple control points operating in multiple markets (or groupings,) the group that the recommendation corresponds to is passed as well. An example can be found below.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 221-229


..Asset objects can operate such that their control points can contribute to different groups. For example Conner Creek Pump Station sanitary pumps directly contribute to flow received to the Fairview Pump Station, while the storm pumps contribute directly to the Conner Creek Retention Basin. In the development of our groupings, Conner Creek Retention Basin is the downstream point for Group 1 and Fairview Pump Station is the downstream point for Group 2.



Writing Recommendations
-------------------------
Finally, recommendations for assets are written to the Influx DB, so that the recommendations can be used for the :doc:`DecisionSupportDashboard`.
Flow and volume recommendations are written directly using the method ``.write_goals()`` in lines 259-261.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 259-261

Additionally in lines 264-297 numeric flow and volume values are discretized into pump action recommendations.
These discretized recommendations are written to the InfluxDB as well to be viewed on the Decision Support Dashboard.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\CombinedMBC.py
	:lines: 264-297



.. note:: Asset-specific operation recommendations for the Sewer Gates to Conner Creek Retention Basin from the Forebay are forthcoming. At this time, only flow rate recommendations are available.