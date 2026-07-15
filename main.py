import time
from src.chassis import Chassis
from robomaster import robot
from src.config_loader import load_settings


def run_chassis_test() -> None:
    settings = load_settings("config/settings.yaml")
    connection_type = settings.get("robot", {}).get("connection", {}).get("type", "ap")
    chassis_settings = settings.get("chassis", {}).get("speed", {})

    default_x = chassis_settings.get("default_x", 0.5)
    default_y = chassis_settings.get("default_y", 0.5)
    default_w = chassis_settings.get("default_w", 30.0)

    print("Using settings:")
    print(f"  connection type: {connection_type}")
    print(f"  default_x: {default_x}")
    print(f"  default_y: {default_y}")
    print(f"  default_w: {default_w}")

    with Chassis(
        conn_type=connection_type,
        default_x=default_x,
        default_y=default_y,
        default_w=default_w,
    ) as chassis:
        print("Testing move_forward")
        chassis.move_forward()
        time.sleep(3)

        print("Testing move_backward")
        chassis.move_backward()
        time.sleep(3)

        print("Testing move_left")
        chassis.move_left()
        time.sleep(3)

        print("Testing move_right")
        chassis.move_right()
        time.sleep(3)

        print("Testing turn_left")
        chassis.turn_left()
        time.sleep(3)

        print("Testing turn_right")
        chassis.turn_right()
        time.sleep(3)

        print("Stopping chassis")
        chassis.stop(timeout=5)


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    run_chassis_test()

