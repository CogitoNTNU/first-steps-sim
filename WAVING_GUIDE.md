# Making the Robot Wave 🤖👋

This guide explains how to make the ZBot robot wave its arm!

## Quick Start

### Option 1: Simple Demo (No Dependencies)
Just see the joint angles printed out:

```powershell
python wave_demo.py --mode simple
```

This will show you the exact joint angles needed for a waving motion over 5 seconds.

### Option 2: 3D Viewer Demo (Requires MuJoCo)
See the robot waving in an interactive 3D viewer:

```powershell
# Make sure mujoco is installed
pip install mujoco

# Run the viewer (requires robot XML file)
python wave_demo.py --mode viewer
```

### Option 3: Integration Guide
Learn how to add waving to your trained policy:

```powershell
python wave_demo.py --mode integration
```

## Customization

### Adjust Wave Speed
```powershell
python wave_demo.py --mode simple --wave-speed 3.0  # Faster wave (3 Hz)
python wave_demo.py --mode simple --wave-speed 1.0  # Slower wave (1 Hz)
```

### Adjust Wave Amplitude
```powershell
python wave_demo.py --mode simple --wave-amplitude 1.2  # Bigger wave
python wave_demo.py --mode simple --wave-amplitude 0.4  # Smaller wave
```

## How It Works

The waving motion controls 4 joints on the right arm:

1. **right_shoulder_pitch** (-1.2 rad): Raises the arm up to waving height
2. **right_shoulder_roll** (oscillating): Creates the side-to-side waving motion
3. **right_elbow_roll** (oscillating): Adds a natural bend to the elbow
4. **right_gripper_roll** (0.0 rad): Keeps the gripper neutral

The motion is generated using sinusoidal functions:
- Shoulder roll oscillates at the base wave frequency
- Elbow roll oscillates at 2x the frequency for more dynamic motion

## Integrating into Your Policy

To make your trained walking robot wave while walking:

### Method 1: Override Arm Actions
In your policy's forward pass, detect a "wave command" and override just the arm joint actions (indices 16-19):

```python
def forward(self, obs, carry):
    # Get actions from the neural network
    action_dist, new_carry = self.actor.forward(obs, carry)
    actions = action_dist.mode()
    
    # If wave command is active
    if command['wave_mode'] == 1:
        t = get_simulation_time()
        wave_joints = create_wave_trajectory(t)
        
        # Override right arm actions (keep leg actions for balance)
        actions[16] = wave_joints['right_shoulder_pitch']
        actions[17] = wave_joints['right_shoulder_roll']
        actions[18] = wave_joints['right_elbow_roll']
        actions[19] = wave_joints['right_gripper_roll']
    
    return actions, new_carry
```

### Method 2: Add as a Command
Extend the `UnifiedCommand` class in `train.py` to include a wave parameter:

```python
@attrs.define(frozen=True)
class UnifiedCommand(ksim.Command):
    # ... existing fields ...
    wave_mode: bool = attrs.field(default=False)
```

Then train the policy to learn when to wave based on the command.

### Method 3: Scripted Motion During Standing
If the robot is standing still (velocity command = 0), trigger the wave:

```python
if abs(cmd_vx) < 0.1 and abs(cmd_vy) < 0.1:
    # Robot is standing, safe to wave
    apply_wave_motion(actions)
```

## Joint Indices Reference

Based on `JOINT_BIASES` in `train.py`:

```python
# Right arm joints (indices 16-19)
16: right_shoulder_pitch
17: right_shoulder_roll
18: right_elbow_roll
19: right_gripper_roll

# Left arm joints (indices 12-15)
12: left_shoulder_pitch
13: left_shoulder_roll
14: left_elbow_roll
15: left_gripper_roll
```

To make the left arm wave instead, use indices 12-15 with adjusted signs for the roll joints.

## Troubleshooting

**The robot falls over when waving:**
- Make sure the robot is balanced (standing or moving slowly)
- Keep the leg actions from the trained policy
- Only override arm joint actions

**The wave looks unnatural:**
- Adjust `wave_speed` (try 1.5-2.5 Hz)
- Adjust `wave_amplitude` (try 0.6-1.0 rad)
- Make sure shoulder_pitch raises the arm high enough

**Can't find robot model XML:**
- The viewer mode needs access to the robot URDF/XML file
- Check if it's in `assets/` or ask your team for the model file
- You can still use `--mode simple` to see the joint angles

## Examples

### Slow, gentle wave:
```powershell
python wave_demo.py --mode simple --wave-speed 1.5 --wave-amplitude 0.6
```

### Fast, enthusiastic wave:
```powershell
python wave_demo.py --mode simple --wave-speed 2.5 --wave-amplitude 1.0
```

### Wave both arms (modify the script):
Copy the `create_wave_trajectory` function and create a version for the left arm with adjusted joint names and signs.

## Next Steps

1. Test the joint angles in your simulator
2. Integrate the waving function into your policy
3. Train the policy to maintain balance while waving
4. Add triggers for when to wave (e.g., on a specific command)

Happy waving! 👋
