from typing import Optional, Any
from robomaster import robot
from src.config_loader import load_settings


class Chassis:
    """Wrapper for the RoboMaster chassis control interface.

    Supports both speed control (continuous movement) and displacement/coordinate control.
    """

    def __init__(
        self,
        ep_robot: Optional[robot.Robot] = None,
        conn_type: Optional[str] = None,
        default_x: Optional[float] = None,
        default_y: Optional[float] = None,
        default_w: Optional[float] = None,
        default_distance: Optional[float] = None,
        default_angle: Optional[float] = None,
    ) -> None:
        """Initializes the Chassis wrapper.

        Args:
            ep_robot: An existing initialized robomaster.robot.Robot instance.
                       If None, a new Robot instance will be created and initialized.
            conn_type: Connection type ('ap' or 'sta') to use if creating a new Robot instance.
            default_x: Default translation speed/displacement scale along the X-axis (m/s or meters).
            default_y: Default translation speed/displacement scale along the Y-axis (m/s or meters).
            default_w: Default angular speed/displacement scale around the Z-axis (deg/s or degrees).
            default_distance: Default displacement distance (meters).
            default_angle: Default turn angle (degrees).
        """
        settings = load_settings()
        robot_settings = settings.get("robot", {})
        chassis_settings = settings.get("chassis", {}).get("speed", {})
        displacement_settings = settings.get("chassis", {}).get("displacement", {})

        resolved_conn_type = conn_type if conn_type is not None else robot_settings.get("connection", {}).get("type", "ap")

        self._owns_robot = ep_robot is None
        if self._owns_robot:
            self.robot = robot.Robot()
            # Map friendly names to standard SDK connection types (ap, sta, rndis)
            conn_map = {
                "wifi": "ap",
                "station": "sta",
                "sta": "sta",
                "ap": "ap",
                "direct": "ap",
                "rndis": "rndis",
                "usb": "rndis"
            }
            mapped_conn_type = conn_map.get(resolved_conn_type.lower(), "ap")
            self.robot.initialize(conn_type=mapped_conn_type)
        else:
            self.robot = ep_robot

        self._chassis = self.robot.chassis
        self.default_x = default_x if default_x is not None else chassis_settings.get("default_x", 0.5)
        self.default_y = default_y if default_y is not None else chassis_settings.get("default_y", 0.5)
        self.default_w = default_w if default_w is not None else chassis_settings.get("default_w", 30.0)
        self.default_distance = default_distance if default_distance is not None else displacement_settings.get("default_distance", 0.6)
        self.default_angle = default_angle if default_angle is not None else displacement_settings.get("default_angle", 90.0)

    def drive_speed(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, timeout: Optional[float] = 5.0) -> None:
        """Drive the robot with a continuous speed command.

        Args:
            x: Forward/backward speed in m/s (positive forward, negative backward).
            y: Right/left lateral speed in m/s (positive right, negative left).
            z: Rotational speed (yaw) in deg/s (positive counter-clockwise/left, negative clockwise/right).
            timeout: Optional command timeout in seconds.
        """
        self._chassis.drive_speed(x=x, y=y, z=z, timeout=timeout)

    def move(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        xy_speed: Optional[float] = None,
        z_speed: Optional[float] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """Move the chassis to a relative coordinate/displacement.

        This is a blocking task command.

        Args:
            x: Forward/backward displacement in meters.
            y: Right/left displacement in meters.
            z: Yaw rotation angle in degrees (positive counter-clockwise/left, negative clockwise/right).
            xy_speed: Speed of translation in m/s.
            z_speed: Speed of rotation in deg/s.
            timeout: Optional command timeout in seconds.
        """
        xy_speed = self.default_x if xy_speed is None else xy_speed
        z_speed = self.default_w if z_speed is None else z_speed
        action = self._chassis.move(x=x, y=y, z=z, xy_speed=xy_speed, z_speed=z_speed).wait_for_completed()
        # action.wait_for_completed(timeout=timeout)

    def stop(self, timeout: Optional[float] = 5.0) -> None:
        """Stop the chassis immediately by setting speed to 0."""
        self.drive_speed(0.0, 0.0, 0.0, timeout=timeout)

    def move_forward(
        self,
        speed: Optional[float] = None,
        distance: Optional[float] = None,
        timeout: Optional[float] = 5.0,
    ) -> None:
        """Move the robot forward.

        If `distance` is specified (meters), it performs a relative movement and blocks until finished.
        Otherwise, it defaults to the configured default_distance.
        """
        speed = self.default_x if speed is None else speed
        dist = self.default_distance if distance is None else distance
        self.move(x=dist, xy_speed=speed, timeout=timeout)

    def move_backward(
        self,
        speed: Optional[float] = None,
        distance: Optional[float] = None,
        timeout: Optional[float] = 5.0,
    ) -> None:
        """Move the robot backward.

        If `distance` is specified (meters), it performs a relative movement and blocks until finished.
        Otherwise, it defaults to the configured default_distance.
        """
        speed = self.default_x if speed is None else speed
        dist = self.default_distance if distance is None else distance
        self.move(x=-dist, xy_speed=speed, timeout=timeout)

    def move_left(
        self,
        speed: Optional[float] = None,
        distance: Optional[float] = None,
        timeout: Optional[float] = 5.0,
    ) -> None:
        """Move the robot to the left.

        If `distance` is specified (meters), it performs a relative movement and blocks until finished.
        Otherwise, it defaults to the configured default_distance.
        """
        speed = self.default_y if speed is None else speed
        dist = self.default_distance if distance is None else distance
        self.move(y=-dist, xy_speed=speed, timeout=timeout)

    def move_right(
        self,
        speed: Optional[float] = None,
        distance: Optional[float] = None,
        timeout: Optional[float] = 5.0,
    ) -> None:
        """Move the robot to the right.

        If `distance` is specified (meters), it performs a relative movement and blocks until finished.
        Otherwise, it defaults to the configured default_distance.
        """
        speed = self.default_y if speed is None else speed
        dist = self.default_distance if distance is None else distance
        self.move(y=dist, xy_speed=speed, timeout=timeout)

    def turn_left(
        self,
        angular_speed: Optional[float] = None,
        angle: Optional[float] = None,
        timeout: Optional[float] = 5.0,
    ) -> None:
        """Turn the robot to the left (counter-clockwise).

        If `angle` is specified (degrees), it performs a relative rotation and blocks until finished.
        Otherwise, it defaults to the configured default_angle.
        """
        angular_speed = self.default_w if angular_speed is None else angular_speed
        ang = self.default_angle if angle is None else angle
        self.move(z=ang, z_speed=angular_speed, timeout=timeout)

    def turn_right(
        self,
        angular_speed: Optional[float] = None,
        angle: Optional[float] = None,
        timeout: Optional[float] = 5.0,
    ) -> None:
        """Turn the robot to the right (clockwise).

        If `angle` is specified (degrees), it performs a relative rotation and blocks until finished.
        Otherwise, it defaults to the configured default_angle.
        """
        angular_speed = self.default_w if angular_speed is None else angular_speed
        ang = self.default_angle if angle is None else angle
        self.move(z=-ang, z_speed=angular_speed, timeout=timeout)

    def close(self) -> None:
        """Close the underlying robot connection if this wrapper owns it."""
        if self._owns_robot:
            self.robot.close()

    def __enter__(self) -> "Chassis":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()