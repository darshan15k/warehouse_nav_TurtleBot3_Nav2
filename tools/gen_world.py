#!/usr/bin/env python3
"""Generates worlds/warehouse.world with 3 non-tipping dynamic obstacles."""
from pathlib import Path

HALF, WALL_T, WALL_H = 5.0, 0.15, 1.0

def box(name, x, y, sx, sy, sz, color, collide=True, z=None):
    z = sz / 2 if z is None else z
    col = (f'<collision name="c"><geometry><box><size>{sx} {sy} {sz}</size>'
           f'</box></geometry></collision>') if collide else ''
    return f"""
    <model name="{name}"><static>true</static><pose>{x} {y} {z} 0 0 0</pose>
      <link name="link">{col}
        <visual name="v"><geometry><box><size>{sx} {sy} {sz}</size></box></geometry>
          <material><ambient>{color}</ambient><diffuse>{color}</diffuse></material>
        </visual></link></model>"""

def cyl(name, x, y, r, h, color):
    return f"""
    <model name="{name}"><static>true</static><pose>{x} {y} {h/2} 0 0 0</pose>
      <link name="link">
        <collision name="c"><geometry><cylinder><radius>{r}</radius><length>{h}</length></cylinder></geometry></collision>
        <visual name="v"><geometry><cylinder><radius>{r}</radius><length>{h}</length></cylinder></geometry>
          <material><ambient>{color}</ambient><diffuse>{color}</diffuse></material>
        </visual></link></model>"""

def moving_box(name, x, y, color="1 0.4 0 1"):
    return f"""
    <model name="{name}"><pose>{x} {y} 0.255 0 0 0</pose>
      <link name="base_link">
        <kinematic>false</kinematic>
        <gravity>true</gravity>
        <inertial>
          <mass>20.0</mass>
          <pose>0 0 -0.20 0 0 0</pose>
          <inertia>
            <ixx>10.0</ixx><ixy>0.0</ixy><ixz>0.0</ixz>
            <iyy>10.0</iyy><iyz>0.0</iyz>
            <izz>1.0</izz>
          </inertia>
        </inertial>
        <collision name="c">
          <geometry><box><size>0.35 0.35 0.5</size></box></geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.0</mu>
                <mu2>0.0</mu2>
                <slip1>1.0</slip1>
                <slip2>1.0</slip2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="v">
          <geometry><box><size>0.35 0.35 0.5</size></box></geometry>
          <material><ambient>{color}</ambient><diffuse>{color}</diffuse></material>
        </visual>
      </link>
      <plugin name="{name}_drive" filename="libgazebo_ros_planar_move.so">
        <ros><namespace>/{name}</namespace></ros>
        <command_topic>cmd_vel</command_topic>
        <publish_odom>true</publish_odom>
        <publish_odom_tf>false</publish_odom_tf>
        <odometry_Rate>20.0</odometry_Rate>
        <robot_base_frame>base_link</robot_base_frame>
      </plugin>
    </model>"""

GREY, BROWN, WOOD = "0.6 0.6 0.6 1", "0.45 0.3 0.15 1", "0.7 0.5 0.25 1"
parts = []

# Outer walls
parts += [
    box("wall_n", 0,  HALF, 2*HALF + WALL_T, WALL_T, WALL_H, GREY),
    box("wall_s", 0, -HALF, 2*HALF + WALL_T, WALL_T, WALL_H, GREY),
    box("wall_e",  HALF, 0, WALL_T, 2*HALF, WALL_H, GREY),
    box("wall_w", -HALF, 0, WALL_T, 2*HALF, WALL_H, GREY),
]

# Shelves
shelves = [(-2.0, 1.5, 0.5, 5.0), (0.0, 1.5, 0.5, 5.0),
           (2.0, 1.5, 0.5, 5.0), (3.3, 1.5, 0.5, 5.0)]
for i, (x, y, sx, sy) in enumerate(shelves, 1):
    parts.append(box(f"shelf_{i}", x, y, sx, sy, 1.0, BROWN))

# Crates and a pillar
for i, (x, y) in enumerate([(-3.5, -0.5), (1.0, -3.0), (-0.8, -4.0)], 1):
    parts.append(box(f"crate_{i}", x, y, 0.6, 0.6, 0.6, WOOD))
parts.append(cyl("pillar_1", 4.2, -2.5, 0.3, 1.0, GREY))

# Floor zones (visual only)
for name, x, y, col in [("pickup_zone", -4.0, 3.0, "0 0.8 0 1"),
                        ("dropoff_zone", 4.3, 3.0, "0.9 0 0 1"),
                        ("home_zone", -4.0, -4.0, "0 0.3 0.9 1")]:
    parts.append(box(name, x, y, 1.2, 1.2, 0.01, col, collide=False, z=0.006))

# Dynamic obstacles
parts.append(moving_box("obstacle_1", -2.5, -2.0, "1.0 0.4 0.0 1"))  # Orange
parts.append(moving_box("obstacle_2", -1.0, -1.0, "0.8 0.1 0.8 1"))  # Purple
parts.append(moving_box("obstacle_3",  1.0,  3.5, "0.0 0.8 0.8 1"))  # Cyan

world = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="warehouse">
    <physics type="ode">
      <real_time_update_rate>1000.0</real_time_update_rate>
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
    </physics>
    <include><uri>model://ground_plane</uri></include>
    <include><uri>model://sun</uri></include>
    <gui><camera name="user_camera"><pose>0 -9 11 0 0.9 1.5708</pose></camera></gui>
    {''.join(parts)}
  </world>
</sdf>
"""
out = Path(__file__).resolve().parent.parent / "worlds" / "warehouse.world"
out.write_text(world)
print("Successfully generated:", out)
