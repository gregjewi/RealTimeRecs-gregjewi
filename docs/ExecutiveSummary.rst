Executive Summary
=================

.. image:: images/LOGOS.png

In 2017 the `Great Lakes Water Authority <https://www.glwater.org/>`_ (GLWA) and the `Real-Time Water Systems Lab <http://107.170.79.190/>`_ began a University-Utility partnership to investigate the application of dynamic control of storm water assets within the GLWA combined sewer system.
The initial scope of the project was to develop a decision support dashboard for a study area of the larger GLWA system.
Recommendations provided via the dashboard would be driven by the control routines developed by researchers in the Real-Time Water Systems Lab.
This unique partnership lowers barriers to the application of innovative approaches in the operation of stormwater assets.

To encourage further innovation and application throughout the greater stormwater operator communitiy, **all materials in support of this effort would be shared**.

This documentation is the product of this effort.


.. note:: **GLWA Operators using the Dashboard at SCC** `CLICK HERE <http://ec2-13-58-223-140.us-east-2.compute.amazonaws.com/DDS_autorefresh.html>`_ .



Approach
----------

1. **Selection of Study Area**: 
A subset on the eastside of the GLWA system was chosen to evaluate the benefits of real-time control. 
The study area includes major control and storage assets such as: Fairview Pump Station, Conner Creek Pump Station, Conner Creek CSO Retention Basin, Conner Creek Forebay and Inline Storage, and Freud Pump Station. 
In total there are 41 pumps, gates, and valves controlling well over 120 million gallons of storage in the study area.

2. **Gather Evaluation Scenarios**: 
A collection of precipiation events of varying intensity, duration, and spatial extent were used to evaluate the performance of the control strategies and objectives within the footprint of the study area. 
These events were derived from real data taken from precipitation gauges across the GDRSS footprint, design storms, and radar-based products.

3. **Implement Control Strategies**: 
Different control strategies are actively under development in the Real-Time Water Systems Lab on theoretical stormwater systems. 
To implement these control strategies on the GDRSS model and in real life, we developed software applications to facilitate the deployment of the control strategies.
More information on these applications can be found in :doc:`SoftwareAndApplications`.

4. **Evaluate Strategies and Scenarios on GDRSS model**:
Implementation of our control strategies in a model setting allows us to simulate control strategies during events and compare the performance of these strategies to each other, and to the best practices currently used by GLWA.
Using this framework iteratively we can determine a "best" strategy or a suite of strategies to be applied in the real system.
More information on this process can be found in :doc:`DeterminingParameters`. 
The results from this process suggest that GLWA has the potential to reduce discharges by up to 100 million gallons from outfalls and CSO Basins.

5. **Apply Findings to Real-Time Control Engine**:
Findings from 4 were then embedded into a Real-Time Control Engine developed specifically for the Great Lakes Water Authority and its operators.
The engine uses the real-time data from the GLWA network to determine recommendations for the control assets in the system.
More information on the processes of the control engine can be found in :doc:`RealTimeWorkFlow`.

6. **Build Visualization Tool for Operators**:
The GLWA Eastside Decision-Support Dashboard was built to communicate the recommendations from the control engine to the operators.
Recommendations are communicated in ways that are directly actionable, like turning on a pump or opening a gate 50%.
Information on the dashboard can be found in :doc:`DecisionSupportDashboard`.

7. **Real-World Evaluation**:
Once the Decision-Support Dashboard is in the hands of the stormwater operators we will begin an evaluation and monitoring phase. 
A description of our monitoring and evaluation plan can be found in :doc:`EvaluationPlan`.

8. **Iterate**: 
Given feedback, return to experimentation above and repeat!


