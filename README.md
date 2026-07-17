*This project has been created as part of the 42 curriculum by <jpaim-so>.*

# Fly-in

## Description

Fly-in is a drone traffic simulation project developed as part of the 42
curriculum.

The objective is to simulate multiple drones travelling simultaneously through
a network of interconnected zones while respecting all movement constraints
defined by the map.

Every turn, the simulator computes valid movements for every drone, resolves
conflicts caused by limited zone or connection capacity, and prints the
resulting simulation until every drone reaches the destination.

The project focuses on graph algorithms, pathfinding, scheduling, state
management and performance. A graphical visualization using Pygame is also
provided to help understand the simulation and debug drone movement.

---

# Features

- Reverse Dijkstra pathfinding;
- Simultaneous movement of multiple drones;
- Zone capacity enforcement;
- Restricted connection handling with multi-turn travel;
- Automatic conflict resolution when several drones compete for the same
destination;
- Priority-zone aware pathfinding;
- Pygame visualization of the simulation;
- Text-based simulation output.

---

# Instructions

## Requirements

- Python 3.12+
- Pygame

## Installation

`make`

## Run

`make run`

or

`python3 main.py <map_file>`

Example:

`python3 main.py maps/simple.txt`

---

# Resources

## Documentation

- https://docs.python.org/3/
- https://docs.python.org/3/library/heapq.html
- https://www.pygame.org/docs/
- https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

## AI Usage

AI tools were used throughout the development process as an assistant,
including:

- discussing algorithm design;
- reviewing implementation choices;
- debugging specific issues;
- explaining Python language features;
- improving documentation and code comments.

All design decisions, implementation, testing and final validation were
performed manually.

---

# Algorithm

## Pathfinding

The navigation graph is built from the parsed map by creating an adjacency
list representing every connection between zones.

A reverse Dijkstra algorithm is executed once from the end zone.

The cost of entering each zone is:

| Zone type | Cost |
|-----------|-----:|
| Normal | 1 |
| Priority | 1 |
| Restricted | 2 |
| Blocked | Not traversable |

Running the search backwards allows the shortest distance to the goal to be
precomputed for every reachable zone.

Whenever multiple shortest paths exist, the algorithm first prefers paths
whose next hop is a priority zone. If multiple equivalent candidates still
remain, all valid next moves are stored. During the simulation, drones
deterministically select one of those alternatives, providing load
distribution while still following an optimal route.

Because the pathfinding information is computed only once, no graph searches
are performed during the simulation itself.

---

## Scheduling

Every simulation turn follows four phases:

1. Advance drones currently travelling through restricted connections.
2. Compute movement proposals for every active drone.
3. Filter proposals according to zone and connection capacity.
4. Commit all valid moves simultaneously.

Moves are never applied immediately after being proposed. Instead, every
proposal is validated first to guarantee that no capacity constraints are
violated.

Travel to restricted zones is treated differently from normal movement:

- to go to a restricted zone a drone must first stop in a restricted
  connection;
- the destination restricted zone is occupied only after the required travel
time;
- the connection becomes available again once the drone reaches the restricted
zone so another drone can take it.

---

## Conflict Resolution

When several drones attempt incompatible moves during the same turn:

- blocked moves are rejected;
- valid moves are committed simultaneously;
- rejected drones simply retry during the next turn.

Zone occupancy is tracked dynamically while validating proposals, allowing
drones leaving a zone during the current turn to immediately free capacity for
incoming drones.

---

# Visual Representation

A Pygame window provides a real-time visualization of the simulation.

The visualization displays:

- map layout;
- zones;
- connections;
- drone positions;
- drones travelling through restricted connections;
- turn-by-turn progression.

The graphical interface greatly simplifies debugging and makes it easier to
verify that movement, congestion and restricted connections behave as expected.

---

# Example

## Input

`python3 main.py maps/easy/02_simple_fork.txt`

## Expected Output

```text
D1-A D2-B
D1-End D2-End
```

The simulation prints one line per turn, listing all drone movements that occur
during that turn. The simulation ends when all drones have reached the
destination zone.

---

# Project Structure

```
.
├── main.py
├── parser.py
├── data.py
├── pathfinder.py
├── scheduler.py
├── simulation.py
├── map_renderer.py
├── demo_window.py
├── assets/
└── README.md
```

---

# Technical Choices

Several implementation decisions were made to keep the simulation efficient:

- Reverse Dijkstra is executed only once.
- Shortest-path information is shared by every drone.
- Dictionary lookups are used extensively for constant-time access.
- Drone movement is separated into proposal, validation and commit phases.
- Restricted connections are modelled explicitly rather than as ordinary zones.
- Multiple shortest-path alternatives are supported while preserving
  optimality.
- Priority zones are used as a tie-breaker when multiple shortest paths have
  the same total cost.

---

# Design

The project follows an object-oriented design where each component is
responsible for a specific part of the simulation.

The main components are:

- **Parser** parses and validates the map file;
- **MapData** stores the parsed map configuration and simulation data;
- **NavGraph** builds the navigation graph and computes shortest paths using
  reverse Dijkstra;
- **Scheduler** proposes, validates and commits drone movements every turn;
- **Simulation** coordinates turn progression and restricted-connection
  handling;
- **MapRenderer** is responsible for drawing the map and simulation objects;
- **DemoWindow** manages user interaction, animation and visualization.

Simulation entities such as drones, zones, connections and moves are
represented as dedicated data classes, separating application state from the
algorithms that operate on it.

This separation of responsibilities keeps parsing, pathfinding, scheduling,
simulation logic and rendering independent, making the code easier to maintain,
test and extend.

---