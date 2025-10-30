"""Demo script to make the robot wave its arm."""

import time
import numpy as np
from pathlib import Path
from typing import TYPE_CHECKING

# Optional imports for viewer mode
try:
    import mujoco
    import mujoco.viewer
    MUJOCO_AVAILABLE = True
except ImportError:
    MUJOCO_AVAILABLE = False
    if TYPE_CHECKING:
        import mujoco


def create_wave_trajectory(t: float, wave_speed: float = 2.0, wave_amplitude: float = 0.8) -> dict[str, float]:
    """
    Create joint angles for a waving motion.
    
    Args:
        t: Time in seconds
        wave_speed: Speed of the wave (cycles per second)
        wave_amplitude: Amplitude of the wave motion in radians
    
    Returns:
        Dictionary mapping joint names to target angles
    """
    # Calculate wave phase
    phase = 2 * np.pi * wave_speed * t
    
    # Right arm joints for waving
    # Lift the arm up (shoulder_pitch negative = up)
    shoulder_pitch = -1.2  # Raised position
    
    # Wave motion side to side (shoulder_roll)
    shoulder_roll = -0.5 + wave_amplitude * np.sin(phase)
    
    # Bend elbow slightly
    elbow_roll = 0.5 + 0.3 * np.sin(phase * 2)  # Twice as fast for more dynamic motion
    
    # Keep gripper neutral
    gripper_roll = 0.0
    
    return {
        "right_shoulder_pitch": shoulder_pitch,
        "right_shoulder_roll": shoulder_roll,
        "right_elbow_roll": elbow_roll,
        "right_gripper_roll": gripper_roll,
    }


def load_robot_model():
    """Load the ZBot robot model from XML."""
    if not MUJOCO_AVAILABLE:
        raise ImportError("MuJoCo is not available")
    
    # Try to find the robot XML file
    possible_paths = [
        Path("assets/robot.xml"),
        Path("robot.xml"),
        Path("zbot.xml"),
    ]
    
    # You may need to adjust this path based on your robot model location
    # For now, we'll create a simple standing pose script
    print("Looking for robot model...")
    for path in possible_paths:
        if path.exists():
            print(f"Found model at: {path}")
            return mujoco.MjModel.from_xml_path(str(path))
    
    print("Robot XML not found. Please specify the path to your robot model.")
    print("You can modify this script to point to the correct XML file.")
    raise FileNotFoundError("Robot model XML file not found")


def wave_demo_simple():
    """
    Simple demo that prints the joint angles for waving.
    Use this if you don't have direct access to the MuJoCo model.
    """
    print("\n=== ZBot Waving Motion Demo ===\n")
    print("Generating 5 seconds of waving motion...\n")
    
    duration = 5.0
    dt = 0.02  # Control timestep (50 Hz)
    
    for i in range(int(duration / dt)):
        t = i * dt
        wave_joints = create_wave_trajectory(t)
        
        if i % 25 == 0:  # Print every 0.5 seconds
            print(f"Time: {t:.2f}s")
            for joint_name, angle in wave_joints.items():
                print(f"  {joint_name}: {angle:.3f} rad ({np.degrees(angle):.1f}°)")
            print()
    
    print("\n=== Joint Control Summary ===")
    print("\nTo make the robot wave, you need to control these joints:")
    print("1. right_shoulder_pitch: -1.2 rad (raises arm up)")
    print("2. right_shoulder_roll: oscillate between -1.3 and 0.3 rad (side-to-side wave)")
    print("3. right_elbow_roll: oscillate between 0.2 and 1.1 rad (bend elbow)")
    print("4. right_gripper_roll: 0.0 rad (neutral)")
    print("\nThe oscillation should be sinusoidal at about 2 Hz for a natural wave.")


def wave_demo_with_viewer():
    """
    Demo with MuJoCo viewer (requires robot model XML).
    This will open an interactive viewer showing the robot waving.
    """
    if not MUJOCO_AVAILABLE:
        print("\nError: MuJoCo is not installed.")
        print("Install it with: pip install mujoco")
        print("\nFalling back to simple demo...\n")
        wave_demo_simple()
        return
    
    try:
        model = load_robot_model()
        data = mujoco.MjData(model)
        
        print("\n=== Opening MuJoCo Viewer ===")
        print("The robot will wave its right arm.")
        print("Use your mouse to rotate the view.")
        print("Press ESC to exit.\n")
        
        with mujoco.viewer.launch_passive(model, data) as viewer:
            start_time = time.time()
            
            # Set robot to standing position first
            # You may need to adjust these initial positions
            standing_pose = {
                "right_hip_pitch": -0.4,
                "right_knee_pitch": -0.8,
                "right_ankle_pitch": -0.4,
                "left_hip_pitch": -0.4,
                "left_knee_pitch": -0.8,
                "left_ankle_pitch": -0.4,
            }
            
            # Get joint indices
            joint_indices = {}
            for i in range(model.njnt):
                joint_name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i)
                if joint_name:
                    joint_indices[joint_name] = i
            
            while viewer.is_running():
                step_start = time.time()
                
                # Calculate current time
                sim_time = time.time() - start_time
                
                # Get wave trajectory
                wave_joints = create_wave_trajectory(sim_time)
                
                # Apply standing pose
                for joint_name, angle in standing_pose.items():
                    if joint_name in joint_indices:
                        idx = joint_indices[joint_name]
                        data.qpos[idx] = angle
                
                # Apply wave motion
                for joint_name, angle in wave_joints.items():
                    if joint_name in joint_indices:
                        idx = joint_indices[joint_name]
                        data.qpos[idx] = angle
                
                # Step simulation
                mujoco.mj_step(model, data)
                
                # Update viewer
                viewer.sync()
                
                # Maintain real-time rate
                time_until_next_step = model.opt.timestep - (time.time() - step_start)
                if time_until_next_step > 0:
                    time.sleep(time_until_next_step)
    
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nFalling back to simple demo...\n")
        wave_demo_simple()


def integrate_wave_into_policy():
    """
    Example of how to integrate waving into the trained policy.
    """
    print("\n=== Integrating Wave into Policy ===\n")
    print("To make your trained policy wave, you need to:")
    print("\n1. Modify the action output in train.py:")
    print("   - Add a 'wave mode' command that overrides arm joint actions")
    print("   - Keep leg actions from the policy for balance")
    print("\n2. In the Model forward pass, add:")
    print("""
    # Pseudocode:
    if command['wave_mode'] == 1:
        # Get wave trajectory
        wave_joints = create_wave_trajectory(sim_time)
        
        # Override arm actions (joints 16-19 for right arm)
        action[16] = wave_joints['right_shoulder_pitch']
        action[17] = wave_joints['right_shoulder_roll']
        action[18] = wave_joints['right_elbow_roll']
        action[19] = wave_joints['right_gripper_roll']
    """)
    print("\n3. Or create a custom command that blends waving with walking")
    print("   - The robot can walk while waving by only modifying arm joints")
    print("   - Use the trained policy for leg control and scripted wave for arms")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ZBot Waving Demo")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["simple", "viewer", "integration"],
        default="simple",
        help="Demo mode: 'simple' prints angles, 'viewer' shows 3D visualization, 'integration' shows how to add to policy"
    )
    parser.add_argument(
        "--wave-speed",
        type=float,
        default=2.0,
        help="Wave speed in Hz (default: 2.0)"
    )
    parser.add_argument(
        "--wave-amplitude",
        type=float,
        default=0.8,
        help="Wave amplitude in radians (default: 0.8)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "simple":
        wave_demo_simple()
    elif args.mode == "viewer":
        wave_demo_with_viewer()
    elif args.mode == "integration":
        integrate_wave_into_policy()
