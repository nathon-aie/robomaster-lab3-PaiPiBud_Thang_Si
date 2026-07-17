import time
from typing import Optional
from src.chassis import Chassis
from src.logger import DataLogger
from robomaster import robot


def run_chassis_test(ep_robot: Optional[robot.Robot] = None) -> None:
    with Chassis(ep_robot=ep_robot) as chassis:
        # Initialize and start telemetry logger (defaults loaded from settings.yaml)
        logger = DataLogger(ep_robot=chassis.robot)

        print("Using settings:")
        print(f"  default_x (speed): {chassis.default_x}")
        print(f"  default_y (speed): {chassis.default_y}")
        print(f"  default_w (angular speed): {chassis.default_w}")
        print(f"  logger frequency: {logger.frequency} Hz")

        logger.start()

        try:
            print("\n--- Part 1: Displacement-based movements (from 01_move.py) ---")

            # 1. Forward
            print("1. Moving forward...")
            chassis.move_forward()

            # 2. Turn right
            print("2. Turning right...")
            chassis.turn_right()

            # 3. Forward
            print("3. Moving forward...")
            chassis.move_forward()

            # 4. Turn right
            print("4. Turning right...")
            chassis.turn_right()

            # 5. Forward
            print("5. Moving forward...")
            chassis.move_forward()

            # 6. Turn right
            print("6. Turning right...")
            chassis.turn_right()

            # 7. Forward
            print("7. Moving forward...")
            chassis.move_forward()

            # 8. Turn right
            print("8. Turning right...")
            chassis.turn_right()

            print("Stopping chassis...")
            chassis.stop(timeout=5)
        finally:
            logger.stop()
            logger.save()


if __name__ == '__main__':
    run_chassis_test()
