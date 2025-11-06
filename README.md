# Multi-robot-Navigation

This project demonstrates a complete system for coordinated, multi-robot task allocation and navigation within a simulated environment. It uses a Genetic Algorithm (GA) to solve the complex Job Shop Scheduling Problem (JSSP) for efficient task distribution, and then executes the resulting plan using multiple TurtleBot's in a ROS 2 simulation.

---

## Project Process & Workflow

The core of this project is a two-stage process: first, an optimal schedule is calculated, and second, that schedule is executed by the robot fleet.

### 1. Stage 1: Task Scheduling (The "Brain")

The central challenge in coordinating multiple robots is efficiently deciding "who does what, and when." This project models this as a **Job Shop Scheduling Problem (JSSP)**.

* **Problem:** Given a set of *jobs* (tasks) and a set of *machines* (our robots, or AMRs), find the optimal sequence of operations to minimize the total completion time (the "makespan").
* **Solution:** This repository implements a **Genetic Algorithm (GA)** in Python (`src/JobShopGA/JobShopGAimpl.py`) to find a high-quality, near-optimal solution to this problem.
* **GA Process:**
    1.  **Initialization:** A population of random "chromosomes" is generated, where each chromosome represents one possible complete schedule. This population is seeded with solutions from heuristics like Shortest Processing Time (SPT) and Longest Processing Time (LPT) to start with a good baseline.
    2.  **Evaluation:** Each schedule's "fitness" is calculated, which is its `Cmax` (total completion time). This calculation includes not only the processing time at each machine but also the **AMR travel time** between machine locations, using a predefined `distance_matrix`.
    3.  **Evolution:** The algorithm "evolves" the population over `T` generations (e.g., `T = 100`). In each generation:
        * **Selection:** A `tournament` selection process picks the fittest individuals.
        * **Crossover:** Parents are "bred" using `single_point_crossover` or `double_point_crossover` to create new offspring (new schedules).
        * **Mutation:** Random changes are introduced using `single_bit_mutation`, `swapping`, and `inversion` to explore new, potentially better solutions.
    4.  **Completion:** After all generations, the algorithm selects the best chromosome (the schedule with the lowest `Cmax`) found.

### 2. Stage 2: Schedule Execution (The "Body")

Once the Genetic Algorithm converges on a final, optimized schedule, that plan is fed to the robotics system for execution.

1.  **Simulation Launch:** The user launches the ROS 2 simulation. The `warehouse_multibot_launch.py` script starts the **Gazebo simulator** with the `warehouse.world` and spawns two TurtleBot 3s (`robot1` and `robot2`) at their starting positions. It also launches an independent **Nav2 (Navigation 2)** stack for each robot, allowing them to navigate autonomously.
2.  **Plan Hand-off:** The `JobShopGAimpl.py` script saves its final, best schedule to a file named `amr_data.json`. This file contains the optimized `machine_sequence` for each robot (AMR).
3.  **Plan Execution:**
    * The `follow_waypoints.py` script runs for each robot.
    * It uses a `watchdog` observer to continuously monitor the `amr_data.json` file.
    * As soon as this file is updated by the GA, the script reads and parses it to get its assigned `machine_sequence`.
    * It translates this sequence of machine IDs (e.g., `0`, `1`, `3`, `-1`, `-2`) into a list of [x, y] coordinates in the map, using a hard-coded dictionary of `poses` (e.g., `m1`, `m2`, `m4`, `loading_dock`, `unloading_dock`).
    * Finally, it uses the `BasicNavigator` from the Nav2 commander library to send this list of waypoints to its robot. The robot then begins autonomously navigating to each point in the sequence to execute the plan.

---

## Project Output

The project produces two distinct sets of outputs: the *scheduling plan* from the GA and the *physical simulation* from ROS 2.

### 1. Scheduling (GA) Outputs

When the `JobShopGAimpl.py` script finishes, it generates several key results (if enabled in the parameters):

* **`amr_data.json`**: This is the most critical output. It's a data file containing the final, optimized machine sequences for each robot, ready to be consumed by the ROS `follow_waypoints` node.
* **Gantt Chart:** The script uses `matplotlib` to plot and save a Gantt chart. This chart (`PlotGanttChar_with_amr`) visualizes the optimized schedule, showing the timeline of tasks for each robot and each machine, including travel times. This is the best way to verify the schedule's efficiency.
* **Convergence Plot:** A line graph is generated (if `display_convergence = 1`) showing the `Cmax` (fitness) of the best solution at each generation. This plot proves that the algorithm successfully "learned" and improved the schedule over time.
* **Log File:** A `.txt` file is created (if `create_txt_file = 1`) that logs the final `Cmax`, the GA parameters used for the run, and the raw data of the best chromosome (solution).

### 2. Simulation (ROS) Outputs

When the ROS 2 system runs, you can observe the following outputs:

* **Gazebo Simulation:** The primary visual output. You can watch the two TurtleBot 3s physically moving through the `warehouse.world`. You will see them navigate from the loading dock, visit their assigned "machine" locations in the order prescribed by the GA, and finally proceed to the unloading dock.
* **RViz Visualization:** The launch file opens RViz, which acts as a "dashboard". Here, you can see the static map of the warehouse, the robots' estimated positions, their laser sensor data, and the paths being planned and executed by the Nav2 stack in real-time.
* **Terminal Logs:** The `follow_waypoints.py` node prints its progress to the terminal as it executes the plan, showing which waypoint it is currently navigating to (e.g., `Executing current waypoint: 3/7`).
