# Autonomous Warehouse Navigation with ROS 2 & Nav2

![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble_Hawksbill-blue)
![Simulator](https://img.shields.io/badge/Gazebo-Classic_11-orange)
![Navigation](https://img.shields.io/badge/Nav2-AMCL_%7C_NavFn_%7C_DWB-green)
![Language](https://img.shields.io/badge/Python-3.10-yellow)
![License](https://img.shields.io/badge/License-Apache_2.0-lightgrey)

An end-to-end autonomous mobile robot (AMR) warehouse logistics simulation built on **ROS 2 Humble**, **Gazebo**, and the **Nav2** stack[cite: 3, 5, 6]. The package features procedural SDF warehouse generation, real-time dynamic obstacle patrolling across narrow aisles, tuned AMCL localization and costmap inflation profiles, and an automated multi-waypoint delivery mission (`Pickup` $\rightarrow$ `Drop-off` $\rightarrow$ `Home`) powered by `nav2_simple_commander`[cite: 1, 7, 12, 13].

---

## Simulation Preview

| Gazebo Warehouse Environment | RViz2 Costmaps & Global/Local Planning |
| :---: | :---: |
| ![Gazebo Simulation]<img width="1854" height="1047" alt="Screenshot from 2026-10-30 00-31-47" src="https://github.com/user-attachments/assets/b7d69be2-92b1-4e72-9fe1-ce3deb68a5c8" /> | ![RViz2 Navigation]<img width="1854" height="1047" alt="Screenshot from 2026-10-30 00-31-27" src="https://github.com/user-attachments/assets/fc31f99f-9cd8-4567-8d54-d9a927e01d4e" /> |

---



## Key Features

* **Procedural Warehouse World (`tools/gen_world.py`):** Automatically generates a $10\text{ m} \times 10\text{ m}$ enclosed warehouse SDF environment containing 4 storage racks, narrow aisles, static pallets/crates, a structural pillar, and color-coded operational floor zones (`Pickup`, `Drop-off`, and `Home`)[cite: 4, 13].
* **Multi-Agent Dynamic Obstacles (`obstacle_patrol`):** Spawns 3 independent moving obstacles driven via `libgazebo_ros_planar_move.so` across the main corridor and storage aisles with configurable velocities, axes, and sinusoidal speed modulation[cite: 12, 13].
* **Tuned Nav2 Stack (`config/nav2_params.yaml`):**
  * **AMCL Localization:** Configured with high-confidence likelihood-field laser matching (`z_hit: 0.9`, `max_particles: 3000`) to prevent scan delocalization inside repetitive parallel shelf aisles[cite: 1].
  * **A* Global Planner & DWB Local Controller:** Tuned with steep costmap inflation drop-off (`cost_scaling_factor: 8.0`, `inflation_radius: 0.25`) to safely thread $0.8\text{ m}$ narrow aisles without costmap lockups[cite: 1, 9].
* **Autonomous Delivery Mission (`mission`):** Uses `nav2_simple_commander` (`BasicNavigator`) to execute a sequential `Pickup` $\rightarrow$ `Drop-off` $\rightarrow$ `Home` state machine with live ETA telemetry, simulated cargo loading/unloading dwell timers, automatic costmap clearing on retries, and timeout recovery.

---

## Package Architecture

```text
warehouse_nav/
├── config/
│   └── nav2_params.yaml          # Tuned AMCL, Costmap, A* Planner & DWB Controller parameters
├── launch/
│   ├── bringup.launch.py         # Master launch: Sim + Nav2 + RViz2 + Dynamic Obstacle Patrol
│   └── sim.launch.py             # Gazebo server/client + Robot State Publisher + delayed entity spawn
├── maps/
│   ├── warehouse.pgm             # 2D Occupancy Grid map of the warehouse
│   └── warehouse.yaml            # Map metadata and origin configuration
├── media/                        # Simulation screenshots and demo assets
├── tools/
│   └── gen_world.py              # Procedural SDF generator for warehouse.world
├── warehouse_nav/
│   ├── __init__.py
│   ├── mission.py                # Automated Pickup -> Drop-off -> Home mission node
│   └── obstacle_patrol.py        # Multi-obstacle velocity controller node
├── worlds/
│   └── warehouse.world           # Generated Gazebo SDF world file
├── package.xml
└── setup.py
```

---

## Warehouse Layout & Coordinate Frame

The warehouse spans $[-5.0\text{ m}, +5.0\text{ m}]$ along both the $X$ and $Y$ axes in the `map` / `world` frame[cite: 4, 13]:

| Zone / Entity | Coordinates $(x, y)$ | Description |
| :--- | :--- | :--- |
| **Home Zone (Blue)** | `(-4.0, -4.0)` | Robot spawn location & final return dock[cite: 4, 8, 13] |
| **Pickup Zone (Green)** | `(-4.0,  3.0)` | Cargo loading station ($3.0\text{ s}$ dwell time)[cite: 4, 13] |
| **Drop-off Zone (Red)** | `( 4.3,  3.0)` | Cargo unloading station ($3.0\text{ s}$ dwell time)[cite: 4, 13] |
| **`obstacle_1` (Orange)** | `y = -2.0` (`x: -2.5 <-> 3.0`) | Dynamic obstacle patrolling the south corridor ($0.18\text{ m/s}$)[cite: 12, 13] |
| **`obstacle_2` (Purple)** | `x = -1.0` (`y: -1.0 <-> 3.5`) | Dynamic obstacle patrolling Aisle 1 ($0.10\text{ m/s}$)[cite: 12, 13] |
| **`obstacle_3` (Cyan)** | `x =  1.0` (`y:  3.5 <-> -1.0`) | Dynamic obstacle patrolling Aisle 2 ($0.25\text{ m/s}$)[cite: 12, 13] |

---

## Prerequisites & Installation

### 1. System Requirements
* **OS:** Ubuntu 22.04 LTS
* **ROS 2 Distro:** ROS 2 Humble Hawksbill[cite: 5, 6]

### 2. Install Dependencies
```bash
sudo apt update
sudo apt install -y \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-nav2-simple-commander \
  ros-humble-turtlebot3-gazebo \
  ros-humble-gazebo-ros-pkgs
```

### 3. Clone and Build Workspace
```bash
mkdir -p ~/nav_ws/src
cd ~/nav_ws/src
git clone [https://github.com/](https://github.com/)<YOUR_GITHUB_USERNAME>/warehouse_nav.git

# Regenerate the SDF world file from script
python3 ~/nav_ws/src/warehouse_nav/tools/gen_world.py

# Build the workspace
cd ~/nav_ws
colcon build --symlink-install
source install/setup.bash
```

---

## Usage

### 1. Launch Full Simulation, Nav2 & Dynamic Obstacles
Open a terminal and launch the complete bringup pipeline (Gazebo, TurtleBot3 spawner, Nav2 stack, RViz2, and the `obstacle_patrol` node)[cite: 7, 8]:

```bash
source ~/nav_ws/install/setup.bash
ros2 launch warehouse_nav bringup.launch.py
```

*To launch in a purely static environment without moving obstacles[cite: 7]:*
```bash
ros2 launch warehouse_nav bringup.launch.py obstacle:=false
```

### 2. Run the Autonomous Delivery Mission
Once Gazebo and RViz2 are up and Nav2 reports active, open a **second terminal** to start the automated `Pickup -> Drop-off -> Home` mission:

```bash
source ~/nav_ws/install/setup.bash
ros2 run warehouse_nav mission
```

**Sample Mission Output:**
```text
[INFO] [basic_navigator]: Nav2 is active! Starting warehouse delivery mission.
[INFO] [basic_navigator]: >>> Heading to [Pickup] at (x=-4.0, y=3.0, yaw=0°)
[INFO] [basic_navigator]:     [Pickup] 4.12 m left | ETA: 16.5s | Recoveries: 0
[INFO] [basic_navigator]: *** Reached [Pickup] successfully!
[INFO] [basic_navigator]: --- Loading cargo at [Pickup] for 3.0s ---
[INFO] [basic_navigator]: >>> Heading to [Drop-off] at (x=4.3, y=3.0, yaw=-90°)
[INFO] [basic_navigator]: *** Reached [Drop-off] successfully!
[INFO] [basic_navigator]: --- Unloading cargo at [Drop-off] for 3.0s ---
[INFO] [basic_navigator]: >>> Heading to [Home] at (x=-4.0, y=-4.0, yaw=0°)
[INFO] [basic_navigator]: *** Reached [Home] successfully!
[INFO] [basic_navigator]: === MISSION COMPLETE (Pickup -> Drop-off -> Home) ===
```

### 3. Inspect or Override Dynamic Obstacle Velocities
To monitor the active dynamic obstacle topics or test custom velocity profiles at runtime[cite: 12]:
```bash
ros2 topic list | grep obstacle
ros2 topic echo /obstacle_1/cmd_vel
```

---

## Troubleshooting

* **Gazebo `gzserver` already running error:** If a previous simulation session did not exit cleanly, clear lingering Gazebo processes before relaunching:
  ```bash
  killall -9 gzserver gzclient
  ```
* **World changes not appearing:** After editing `tools/gen_world.py`, re-run `python3 src/warehouse_nav/tools/gen_world.py` so `worlds/warehouse.world` is updated on disk[cite: 9, 13].

---

## Author

**Darshan K R**  
Department of Robotics and Artificial Intelligence Engineering  
Dayananda Sagar College of Engineering, Bengaluru
