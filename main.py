import time
from typing import Optional
from src.chassis import Chassis
from robomaster import robot
from src.config_loader import load_settings


def run_chassis_test(ep_robot: Optional[robot.Robot] = None) -> None:
    settings = load_settings("config/settings.yaml")
    connection_type = settings.get("robot", {}).get("connection", {}).get("type", "ap")
    chassis_settings = settings.get("chassis", {}).get("speed", {})

    default_x = chassis_settings.get("default_x", 0.5)
    default_y = chassis_settings.get("default_y", 0.5)
    default_w = chassis_settings.get("default_w", 30.0)

    print("Using settings:")
    print(f"  connection type: {connection_type}")
    print(f"  default_x (speed): {default_x}")
    print(f"  default_y (speed): {default_y}")
    print(f"  default_w (angular speed): {default_w}")

    with Chassis(
        ep_robot=ep_robot,
        conn_type=connection_type,
        default_x=default_x,
        default_y=default_y,
        default_w=default_w,
    ) as chassis:
        # Part 1: Displacement-based movement (derived from 01_move.py SDK example)
        print("\n--- Part 1: Displacement-based movements (from 01_move.py) ---")

        print("Moving forward 0.3m (speed: 0.1 m/s)...")
        chassis.move_forward(speed=0.1, distance=0.3)
        time.sleep(1)

        print("Moving backward 0.3m (speed: 0.1 m/s)...")
        chassis.move_backward(speed=0.1, distance=0.3)
        time.sleep(1)

        print("Moving left 0.6m (speed: 0.7 m/s)...")
        chassis.move_left(speed=0.7, distance=0.6)
        time.sleep(1)

        print("Moving right 0.6m (speed: 0.7 m/s)...")
        chassis.move_right(speed=0.7, distance=0.6)
        time.sleep(1)

        print("Turning left 90 degrees (speed: 45 deg/s)...")
        chassis.turn_left(angular_speed=45, angle=90)
        time.sleep(1)

        print("Turning right 90 degrees (speed: 45 deg/s)...")
        chassis.turn_right(angular_speed=45, angle=90)
        time.sleep(1)

        # Part 2: Speed-based/continuous movement (original main.py behavior)
        print("\n--- Part 2: Speed-based continuous movements (original main.py) ---")

        print("Testing move_forward (continuous speed)...")
        chassis.move_forward()
        time.sleep(3)

        print("Testing move_backward (continuous speed)...")
        chassis.move_backward()
        time.sleep(3)

        print("Testing move_left (continuous speed)...")
        chassis.move_left()
        time.sleep(3)

        print("Testing move_right (continuous speed)...")
        chassis.move_right()
        time.sleep(3)

        print("Testing turn_left (continuous speed - counter-clockwise)...")
        chassis.turn_left()
        time.sleep(3)

        print("Testing turn_right (continuous speed - clockwise)...")
        chassis.turn_right()
        time.sleep(3)

        print("Stopping chassis...")
        chassis.stop(timeout=5)


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    try:
        run_chassis_test(ep_robot)
    finally:
        print("Closing robot connection...")
        ep_robot.close()
