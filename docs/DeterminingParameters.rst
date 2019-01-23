Determing Parameters to Use in Water Exchange Market Price Calculations
=======================================================================

.. image:: images/LOGOS.png

At the highest level, our objective is to improve the water quality of receiving bodies in the urban hydrosphere.
Practically this statement could mean different things for different systems, requiring different solutions.
Likewise, the method for evaluating success of a solution can differ.
For example, a solution to improve water quality of a receiving water body could be evaluated on its ability to: reduce CSO volumes or events; deliver near-steady state inflow to the WRRF; supply the WRRF with influent that satisfies a desired water quality profile; reduce real cost.

Our formulation of Water Exchange Markets to dictate dynamic control of the stormwater assets is a proposed *solution* to achieve the *objective* of improving water quality of receiving water bodies.
For the GLWA Eastside application, evaluation of performance is done by comparing the solution's ability to reduce the volume and event occurrence of CSOs throughout the system.


Water Exchange Market Parameters
--------------------------------

In the formulation of the :doc:`WaterExchangeMarket`, there are three types of parameters that are user-defined:

* :math:`\mu` is the weighting parameter for an upstream agent characteristic
* :math:`\beta` is the weighting parameter for a downstream location characteristic, and
* :math:`setpt` is the user-defined setpoint for a downstream location characteristic [#]_.

.. [#] There is also the possibility for a user to define the behaviour of the "Central Bank", though this is a complication that will not be covered here.

The values -- and their relations to each other -- of these user-defined parameters help determine the purchasing power assets have in an exchange and, subsequently, the amount of water they can release at any given time.
Therefore, performance of the control engine depends on the values of these parameters.

The determination of these parameters, however, is a nontrivial task due to the complexity of the stormwater systems, layers of exchange markets, and changing inputs into the system (i.e. unique precipitation events.)
For these reasons it is nearly impossible to know *a priori* which set of parameters will perform best for any give strorm [#]_.
Therefore, a methodology is required to explore parameter sets and evaluate their performance under a number of conditions.

.. [#] The idea of "best" is a fuzzy one and requires more discussion. For now, the "best" set of parameters is the set that performs best compared to all other sets that 

The questions we set out to answer are:

	1. Given a storm event, what set of market parameters would result in the best *global* outcome of the system?
	2. Repeating the above step over multiple storms, of varying intensities and durations, does there exist a set of parameters that performs well for all storm types?


Genetic Algorithms
------------------

Defining Performance
--------------------




.. **Complex Networks**: Real stormwater networks are complex, where interactions within the system are poorly understood and highly non-linear. 
.. **Multi-Layered Exchange Markets**: In complex stormwater networks it makes sense to simplify the problem by creating submarkets of assets contributing to common downstream locations. With nested and layered markets, it is hard to determine what the outcome of the parameters will be.
.. **Changing Inputs**: No two precipitation events are exactly alike in intensity, duration, or location. One parameterization may be more effective with one type of storm over another.
.. Experimentation with varying numbers of exchanges for the GLWA Eastside system has provided some evidence that multiple, nested markets provide more responsiveness to upstream agents compared to all agents competing in a single exchange.