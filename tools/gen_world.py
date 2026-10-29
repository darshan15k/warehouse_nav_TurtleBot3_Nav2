#!/usr/bin/env python3
"""Generates worlds/warehouse.world. Edit the lists below, then re-run."""
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

GREY, BROWN, WOOD = "0.6 0.6 0.6 1", "0.45 0.3 0.15 1", "0.7 0.5 0.25 1"
parts = []

# Outer walls
parts += [
    box("wall_n", 0,  HALF, 2*HALF + WALL_T, WALL_T, WALL_H, GREY),
    box("wall_s", 0, -HALF, 2*HALF + WALL_T, WALL_T, WALL_H, GREY),
    box("wall_e",  HALF, 0, WALL_T, 2*HALF, WALL_H, GREY),
    box("wall_w", -HALF, 0, WALL_T, 2*HALF, WALL_H, GREY),
]

# Shelves: (x, y, size_x, size_y). Last gap (S3 -> S4) is 0.8 m.
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

world = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="warehouse">
    <include><uri>model://ground_plane</uri></include>
    <include><uri>model://sun</uri></include>
    <gui><camera name="user_camera"><pose>0 -9 11 0 0.9 1.5708</pose></camera></gui>
    {''.join(parts)}
  </world>
</sdf>
"""
out = Path(__file__).resolve().parent.parent / "worlds" / "warehouse.world"
out.write_text(world)
print("wrote", out)
