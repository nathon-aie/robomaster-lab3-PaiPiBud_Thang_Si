from typing import Optional
from robomaster import robot


class Chassis:
    """Wrapper for the RoboMaster chassis control interface."""

    def __init__(
        self,
        ep_robot: Optional[robot.Robot] = None,
        conn_type: str = "ap",
        default_x: float = 0.5,
        default_y: float = 0.5,
        default_w: float = 30.0,
    ) -> None:
        if ep_robot is None:
            self.robot = robot.Robot()
            self.robot.initialize(conn_type=conn_type)
            self._owns_robot = True
        else:
            self.robot = ep_robot
            self._owns_robot = False

        self._chassis = self.robot.chassis
        self.default_x = default_x
        self.default_y = default_y
        self.default_w = default_w

    def drive_speed(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, timeout: float = 5.0) -> None:
        """Drive the robot with a continuous speed command."""
        self._chassis.drive_speed(x=x, y=y, z=z, timeout=timeout)

    def stop(self, timeout: float = 5.0) -> None:
        """Stop the chassis immediately."""
        self.drive_speed(0.0, 0.0, 0.0, timeout=timeout)

    def move_forward(self, speed: Optional[float] = None, timeout: float = 5.0) -> None:
        speed = self.default_x if speed is None else speed
        self.drive_speed(x=speed, y=0.0, z=0.0, timeout=timeout)

    def move_backward(self, speed: Optional[float] = None, timeout: float = 5.0) -> None:
        speed = self.default_x if speed is None else speed
        self.drive_speed(x=-speed, y=0.0, z=0.0, timeout=timeout)

    def move_left(self, speed: Optional[float] = None, timeout: float = 5.0) -> None:
        speed = self.default_y if speed is None else speed
        self.drive_speed(x=0.0, y=-speed, z=0.0, timeout=timeout)

    def move_right(self, speed: Optional[float] = None, timeout: float = 5.0) -> None:
        speed = self.default_y if speed is None else speed
        self.drive_speed(x=0.0, y=speed, z=0.0, timeout=timeout)

    def turn_left(self, angular_speed: Optional[float] = None, timeout: float = 5.0) -> None:
        angular_speed = self.default_w if angular_speed is None else angular_speed
        self.drive_speed(x=0.0, y=0.0, z=-angular_speed, timeout=timeout)

    def turn_right(self, angular_speed: Optional[float] = None, timeout: float = 5.0) -> None:
        angular_speed = self.default_w if angular_speed is None else angular_speed
        self.drive_speed(x=0.0, y=0.0, z=angular_speed, timeout=timeout)

    def close(self) -> None:
        """Close the underlying robot connection if this wrapper owns it."""
        if self._owns_robot:
            self.robot.close()

    def __enter__(self) -> "Chassis":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()