Theory
======

.. image:: images/LOGOS.png

.. In this section you will find:

.. * An explanation of the market-based approach (MBA),
.. * Definition of terms, 
.. * MBA's application to stormwater systems,
.. * The mathematical framework of MBA for a single objective,
.. * An example market set up, and
.. * The extension of the single objective framework to multi-objective, multi-measurement market framework.


Stormwater Conveyance Networks, An Application
----------------------------------------------

Consider a stormwater conveyance network. 
By nature, its purpose is to transport water to a final, and oftentimes shared, location such as a Water Reuse and Recovery Facility (WRRF,) or an outfall. 
As such these networks are directional in nature. 
Likewise, infrastructure within these networks such as pumps, gates, and valves can be thought of as upstream of common downstream locations like a major trunkline or the WRRF.
The state of a downstream location like a WRRF is contingent upon the combination of states upstream of it; a change in the state upstream impacts the downstream state.
In other words, coordinating states upstream can result in a desired state at the downstream.
.. In other words, upstream agents can coordinate their actions to nudge the system towards a global objective at a downstream point.

The Market-Based Control method presented here is a framework to drive coordinated decision-making of upstream actors, or *agents*, to meet downstream objectives within a stormwater conveyance network.
Upstream agents' actions are based upon their relative states compared to other agents within a group, or *market*.
The phrase "Market-Based" is used because economic models describing markets of "buyers" and "sellers" motivate the approach. 
An agent's "wealth" determines its ability to take actions and in this way mimics agents in a marketplace purchasing a good in an amount proportional to their purchasing power.


Terms
-----

Market and Commodity
^^^^^^^^^^^^^^^^^^^^

A **market** is a set of agents with the ability to give and/or receive a commodity. 
**Commodities** are characteristics/states of the system, associated with an agent, that can be exchanged among member agents of the market. 
For example the commodities of volume, depth, total suspended solids (TSS), chemical concentration, etc. of an agent may be exchanged or passed to another agent.
Entering into this exchange is achieved via the action of an asset (considered to be part of an agent,) whose own state can be changed (e.g., valve position or pump on/off.)

Agents
^^^^^^

We define *agents* as discrete entities within a network that possess characteristics and interact with other agents through a mathematical framework.
There are two categories of agents: upstream agents and downstream agents. At minimum, a market must have one of each agent.

**Upstream Agents** are defined physically as the pair of an actionable feature and a body upon which it acts.
A body must have at least one measureable characteristic/commodity that can change on account of an action.
For example, a pumpstation wet well has a level or volume (the commodity) that can change via a pump's action (on/off.)
Another possible commodity that a wet well could measure is the Total Suspended Solids (TSS) concentration, or a different water quality measure.

**Downstream Agents**, unlike upstream agents, do not have control points [#]_.
Rather, they are defined as a control volume that is downstream from the confluence of all upstream agents and has at least one measureable characteristic/commodity.
Downstream agents also have a operator-defined setpoint for the measured characteristic/commodity.
The definition of a downstream agent is purposefully loose to accommodate the variety of downstream locations in a network that can be used as a downstream agent.
A simple example of a downstream agent could be the headworks to a WRRF that has a well-defined reservoir where a meter can measure the real-time volume or depth. 
A more abstract example of a downstream agent would be a length of pipe (which forms the control volume,) where measurements from a sewer meter, or meters, can approximate the aggregate value of a commodity (depth, volume, TSS, etc.,) within the section of pipe.

Both upstream agents and downstream agents have have weighting parameters associated with each of their characteristics/commodities (see `Mathematical Framework`_.)

.. [#] Note: In reality, many ideal downstream locations for a market are also upstream agents within a different market, and therefore you could have a control point co-located with the downstream agent. We consider these to be *nested* or *sub* markets.



Mathematical Framework
----------------------

Market-Based Control is flexible enough to generate control actions for a variety of upstream control agents acting to meet multiple objectives of the downstream agent.
To start, however, we will consider the case of determining decisions based upon a single commodity and later extend that framework for use with multiple commodities and multiple downstream objectives.

Single Commodity Objective
^^^^^^^^^^^^^^^^^^^^^^^^^^

Consider a set of upstream agents whose actions are to be coordinated to achieve an objective at a downstream location. Actions 

(e.g., pump stations, storage basins, inflatable storage dams), and the sellers are downstream points within the sewer network, more specifically the water resources recovery facility. 
The downstream point has an operator-defined setpoint to achieve; the downstream capacity is determined as the current volume above or below this setpoint. 
Price of the commodity fluctuates through time and is based on the current state of the system: how much capacity is available and how greatly it is demanded by upstream agents. 
Water is moved throughout the system via ''purchases'' of capacity by upstream agents, which dictate how much stored water each upstream agent can release to the downstream agents. 
Because the system considered here is so large and spatially distributed, we divide the system into sub-markets, each with its own price of capacity, one
seller/downstream agent, and potentially several buyers/upstream agents.

Each buyer/upstream agent has a particular wealth with which to ''purchase'' capacity which is based on its current volume normalized to its maximum volume capacity; thus, if a storage agent is close to using all of its available volume, it poses more wealth to ''purchase'' more capacity from downstream, that is release more water to avoid flooding locally. 
The wealth for upstream agent :math:`i` is computed via

:math:`P_{wealth,i} = uparam_i \times D_{up,i}`

where :math:`uparam_i` is a weighting parameter describing priority toward mitigating local upstream flooding, :math:`V_{up,i}` is the normalized volume of upstream agent :math:`i`.

The sum of wealth within each sub-market is computed via

:math:`G_{weatlth} = P_{wealth} * groupM^T`

where :math:`groupM^T` is a binary matrix denoting the sub-market that each upstream agent belongs to.

Each seller/downstream agent determines the cost it places on
the commodity based on its current volume about the desired setpoint. The cost of downstream agent :math:`j` is computed as

:math:`D_{cost,j} = \left( V_{down,j} - setpt_j \right) \times dparam_j`

where
	- :math:`V_{down,j}` is the normalized volume of downstream agent :math:`j`
	- :math:`setpoint_j` is the operator-defined normalized volumetric setpoint of agent :math:`j`, and
	- :math:`dparam` is a weighting parameter describing priority toward achieving the setpoint.

The price of volumetric capacity within sub-market :math:`j` is computed via

:math:`p_j = \frac{G_{wealth,j} + D_{cost,j}}{n_j + 1}`

where :math:`n_j` is the number of buyers/upstream agents in the submarket :math:`j`. It is crucial to note that this results in a *pareto optimal* distribution of capacity for each sub-market, meaning that any benefit to one agent would results in a detriment of other agents. 

The purchasing power of each upstream agent :math:`i` in sub-market :math:`j` is computed via

:math:`P_{power,i} = \max\left( P_{wealth,i} - p_j, 0\right)`

The available volumetric capacity in sub-market :math:`j` is computed as

:math:`V_{available,j} = (1 - V_{down,j}) \times V_{max,j}`

where :math:`V_{max,j}` is the maximum possible volume at downstream agent :math:`j`.

Thus, the available flow capacity in sub-market :math:`j` is

:math:`Q_{available,j} = \frac{V_{available,j}}{T}`

where :math:`T` is the timestep of the simulation.

Finally, the flow to be released from buyer/upstream agent :math:`i` is computed as

:math:`Q_{goal,i} = Q_{available,j} \times P_{power,i}`