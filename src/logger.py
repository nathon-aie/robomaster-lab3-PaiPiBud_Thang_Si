import csv
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from robomaster import robot
from src.config_loader import load_settings


class DataLogger:
    """Logs sensor and telemetry data from the RoboMaster robot to CSV files.

    Supports subscribing to:
    - Chassis position (x, y, z)
    - Chassis attitude (yaw, pitch, roll)
    - Chassis IMU (accelerometer and gyroscope data)
    """

    def __init__(
        self,
        ep_robot: robot.Robot,
        output_dir: Optional[str] = None,
        frequency_hz: Optional[int] = None,
    ) -> None:
        """Initializes the DataLogger.

        Args:
            ep_robot: An initialized Robot instance.
            output_dir: Directory where CSV files will be saved. If None, defaults to project_root/data/raw.
            frequency_hz: Subscription frequency for sensor data (1 to 50 Hz). If None, loaded from settings.yaml.
        """
        self.robot = ep_robot
        settings = load_settings()
        logger_settings = settings.get("logger", {})

        if output_dir is None:
            self.output_dir = Path(__file__).resolve().parents[1] / "data" / "raw"
        else:
            self.output_dir = Path(output_dir)
        self.frequency = frequency_hz if frequency_hz is not None else logger_settings.get("frequency_hz", 10)

        # Telemetry registry mapping
        self.telemetry: Dict[str, Dict[str, Any]] = {
            "position": {
                "data": [],
                "headers": ["timestamp", "x", "y", "z"],
                "sub": self.robot.chassis.sub_position,
                "unsub": self.robot.chassis.unsub_position,
                "callback": self._position_handler
            },
            "attitude": {
                "data": [],
                "headers": ["timestamp", "yaw", "pitch", "roll"],
                "sub": self.robot.chassis.sub_attitude,
                "unsub": self.robot.chassis.unsub_attitude,
                "callback": self._attitude_handler
            },
            "imu": {
                "data": [],
                "headers": ["timestamp", "acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z"],
                "sub": self.robot.chassis.sub_imu,
                "unsub": self.robot.chassis.unsub_imu,
                "callback": self._imu_handler
            },
            "esc": {
                "data": [],
                "headers": ["timestamp", "speed", "angle", "esc_timestamp", "state"],
                "sub": self.robot.chassis.sub_esc,
                "unsub": self.robot.chassis.unsub_esc,
                "callback": self._esc_handler
            }
        }

        # Mutably aliased list properties for backward compatibility
        self.position_data = self.telemetry["position"]["data"]
        self.attitude_data = self.telemetry["attitude"]["data"]
        self.imu_data = self.telemetry["imu"]["data"]
        self.esc_data = self.telemetry["esc"]["data"]

        # State tracking
        self.start_time: float = 0.0
        self._is_logging: bool = False
        self.current_run_dir: Optional[Path] = None

    def _position_handler(self, position_info: Any) -> None:
        """Callback for chassis position subscription."""
        if not self._is_logging:
            return
        x, y, z = position_info
        self.position_data.append({
            "timestamp": int(time.time()),
            "x": x,
            "y": y,
            "z": z
        })

    def _attitude_handler(self, attitude_info: Any) -> None:
        """Callback for chassis attitude subscription."""
        if not self._is_logging:
            return
        yaw, pitch, roll = attitude_info
        self.attitude_data.append({
            "timestamp": int(time.time()),
            "yaw": yaw,
            "pitch": pitch,
            "roll": roll
        })

    def _imu_handler(self, imu_info: Any) -> None:
        """Callback for chassis IMU subscription."""
        if not self._is_logging:
            return
        acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = imu_info
        self.imu_data.append({
            "timestamp": int(time.time()),
            "acc_x": acc_x,
            "acc_y": acc_y,
            "acc_z": acc_z,
            "gyro_x": gyro_x,
            "gyro_y": gyro_y,
            "gyro_z": gyro_z
        })

    def _esc_handler(self, esc_info: Any) -> None:
        """Callback for chassis ESC subscription."""
        if not self._is_logging:
            return
        speed, angle, esc_timestamp, state = esc_info
        self.esc_data.append({
            "timestamp": int(time.time()),
            "speed": speed,
            "angle": angle,
            "esc_timestamp": esc_timestamp,
            "state": state
        })

    def start(self) -> None:
        """Starts subscribing to chassis sensors and logging data."""
        if self._is_logging:
            print("Logger is already running.")
            return

        # Ensure base output directory exists
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)

        # Detect the next available run folder name (run1, run2, etc.)
        run_idx = 1
        while (self.output_dir / f"run{run_idx}").exists():
            run_idx += 1
        self.current_run_dir = self.output_dir / f"run{run_idx}"

        print(f"Starting telemetry logging at {self.frequency} Hz (saving to {self.current_run_dir.name})...")
        for sensor in self.telemetry.values():
            sensor["data"].clear()

        self.start_time = time.time()
        self._is_logging = True

        # Subscribe to chassis sensors
        for sensor in self.telemetry.values():
            sensor["sub"](freq=self.frequency, callback=sensor["callback"])

    def stop(self) -> None:
        """Stops subscriptions and pauses logging."""
        if not self._is_logging:
            print("Logger is not running.")
            return

        print("Stopping telemetry logging and unsubscribing...")
        self._is_logging = False

        # Unsubscribe from chassis sensors
        for key, sensor in self.telemetry.items():
            try:
                sensor["unsub"]()
            except Exception as e:
                print(f"Error while unsubscribing {key}: {e}")

    def save(self, prefix: Optional[str] = None) -> None:
        """Saves logged data to CSV files inside the current run folder.

        Args:
            prefix: Optional prefix to prepend to CSV filenames. If omitted, uses current date in YYYYMMDD.
        """
        if self.current_run_dir is None:
            if not self.output_dir.exists():
                self.output_dir.mkdir(parents=True, exist_ok=True)
            run_idx = 1
            while (self.output_dir / f"run{run_idx}").exists():
                run_idx += 1
            self.current_run_dir = self.output_dir / f"run{run_idx}"

        self.current_run_dir.mkdir(parents=True, exist_ok=True)

        date_str = prefix if prefix else time.strftime("%Y%m%d")

        for key, sensor in self.telemetry.items():
            filename = f"log_{date_str}_{key}.csv"
            self._write_csv(
                self.current_run_dir / filename,
                sensor["headers"],
                sensor["data"]
            )

    def _write_csv(self, file_path: Path, headers: List[str], data: List[Dict[str, float]]) -> None:
        """Helper function to write a list of dictionaries to a CSV file."""
        if not data:
            print(f"No data to save for {file_path.name}.")
            return

        try:
            with file_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            print(f"Saved: {file_path}")
        except Exception as e:
            print(f"Failed to save {file_path.name}: {e}")
