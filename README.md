*This project has been created as part of the 42 curriculum by <jpaim-so>.*

# Fly-in

## Description

Fly-in is a pathfinding and scheduling simulation in which autonomous drones must travel from a start hub to an end hub through a network of interconnected zones.

Each turn, the simulator computes valid movements for every drone while respecting the constraints imposed by the map:

- zone capacities;
- restricted zones requiring multi-turn traversal;
- blocked zones;
- connection capacities;
- priority zones.

The objective is to move all drones to the destination in as few turns as possible while ensuring that every movement remains valid according to the project rules.

A Pygame visualizer is included to display the simulation and make the drone movements easier to follow.

---

## Features

- Reverse Dijkstra pathfinding
- Per-turn movement scheduling
- Zone capacity management
- Restricted (multi-turn) connections
- Connection capacity validation
- Priority zone support
- Pygame visualization
- Multiple test maps

---

## Instructions

### Requirements

- Python 3.12+
- Pygame

### Installation

```bash
make
```

or

```bash
pip install pygame
```

### Run

```bash
make run
```

The simulator prints the drone positions for every turn and opens the graphical visualizer.

---

## Algorithm

### Pathfinding

The navigation graph is built from the map connections.

Rather than computing a path for every drone independently, a reverse Dijkstra search is executed once from the destination hub. This produces:

- the minimum distance from every zone to the goal;
- the next optimal move from every reachable zone.

Movement costs are:

| Zone type | Cost |
|-----------|------|
| Normal | 1 |
| Priority | 1 |
| Restricted | 2 |
| Blocked | Not traversable |

When several shortest paths have the same total cost, paths through priority zones are preferred.

Each drone therefore obtains its route by following the precomputed next-hop table.

### Scheduling

Each simulation turn consists of three stages:

1. Advance drones currently traversing restricted connections.
2. Compute movement proposals for drones that are ready to move.
3. Validate proposals before committing them.

Validation checks:

- destination zone capacity;
- restricted connection capacity.

Since drones leaving a zone free that zone during the same turn, departures are processed before validating arrivals.

### Restricted zones

Restricted zones require two turns to enter.

The scheduler first moves the drone into the connection. During the next simulation step the drone arrives at the restricted zone, after which it may continue moving normally.

This behaviour is managed through the drone transit state rather than treating restricted zones as ordinary one-turn movements.

---

## Visualization

The project includes a Pygame visualizer that displays the simulation turn by turn.

The visualizer provides:

- graphical representation of the map;
- live drone positions;
- restricted connection traversal animations;
- turn-by-turn simulation playback.

This makes it considerably easier to verify the correctness of the scheduling algorithm and identify movement or capacity conflicts during development.

---

## Resources

### Documentation

- Python documentation — https://docs.python.org/3/
- heapq module — https://docs.python.org/3/library/heapq.html
- Pygame documentation — https://www.pygame.org/docs/
- Dijkstra's Algorithm — https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

### AI Usage

ChatGPT (OpenAI) was used as a development assistant for:

- discussing algorithm design;
- reviewing scheduling logic;
- debugging edge cases involving restricted zones and connection capacities;
- improving code readability and documentation;
- generating docstrings and the project README.

All implementation decisions, testing and final code integration were performed manually.

---

## Project Structure

```
.
├── data.py
├── parser.py
├── pathfinder.py
├── scheduler.py
├── simulation.py
├── demo_window.py
├── renderer.py
├── main.py
└── maps/
```

---

## Bonus

The implementation aims to optimise the total number of turns while respecting all project constraints.

Performance was evaluated using the provided maps, including the more demanding challenge maps.
