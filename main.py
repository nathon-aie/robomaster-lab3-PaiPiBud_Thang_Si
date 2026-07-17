import time
from typing import Optional
from src.chassis import Chassis
from src.logger import DataLogger
from robomaster import robot
from src.config_loader import load_settings


def run_chassis_test(ep_robot: Optional[robot.Robot] = None) -> None:
    settings = load_settings("config/settings.yaml")
    connection_type = settings.get("robot", {}).get("connection", {}).get("type", "ap")
    chassis_settings = settings.get("chassis", {}).get("speed", {})
    logger_settings = settings.get("logger", {})

    default_x = chassis_settings.get("default_x", 0.5)
    default_y = chassis_settings.get("default_y", 0.5)
    default_w = chassis_settings.get("default_w", 30.0)
    freq = logger_settings.get("frequency_hz", 10)

    print("Using settings:")
    print(f"  connection type: {connection_type}")
    print(f"  default_x (speed): {default_x}")
    print(f"  default_y (speed): {default_y}")
    print(f"  default_w (angular speed): {default_w}")
    print(f"  logger frequency: {freq} Hz")

    with Chassis(
        ep_robot=ep_robot,
        conn_type=connection_type,
        default_x=default_x,
        default_y=default_y,
        default_w=default_w,
    ) as chassis:
        # Initialize and start telemetry logger
        logger = DataLogger(ep_robot=chassis.robot, frequency_hz=freq)
        logger.start()

        try:
            print("\n--- Part 1: Displacement-based movements (from 01_move.py) ---")

            # 1. Forward 0.6m
            print("1. Moving forward 0.6m...")
            chassis.move_forward(distance=0.6)

            # 2. Turn right 90 degrees
            print("2. Turning right 90 degrees...")
            chassis.turn_right(angle=90)

            # 3. Forward 0.6m
            print("3. Moving forward 0.6m...")
            chassis.move_forward(distance=0.6)

            # 4. Turn right 90 degrees
            print("4. Turning right 90 degrees...")
            chassis.turn_right(angle=90)

            # 5. Forward 0.6m
            print("5. Moving forward 0.6m...")
            chassis.move_forward(distance=0.6)

            # 6. Turn right 90 degrees
            print("6. Turning right 90 degrees...")
            chassis.turn_right(angle=90)

            # 7. Forward 0.6m
            print("7. Moving forward 0.6m...")
            chassis.move_forward(distance=0.6)

            # 8. Turn right 90 degrees
            print("8. Turning right 90 degrees...")
            chassis.turn_right(angle=90)

            print("Stopping chassis...")
            chassis.stop(timeout=5)
        finally:
            logger.stop()
            logger.save()


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    try:
        run_chassis_test(ep_robot)
    finally:
        print("Closing robot connection...")
        ep_robot.close()
