# TensorBoard Visualization Guide

Complete guide for visualizing your ZBot training with TensorBoard.

## Overview

When you run training with `python -m train`, ksim automatically creates a directory structure that includes TensorBoard logs. The training framework logs metrics, videos, and other visualizations that you can view in real-time.

## Directory Structure

After starting training, you'll see this structure:

```
zbot_walking_task/
└── run_0/                    # First run (increments: run_1, run_2, etc.)
    ├── checkpoints/          # Model checkpoints
    │   └── ckpt.bin
    ├── tensorboard/          # TensorBoard event files
    │   └── events.out.tfevents.*
    └── videos/               # Rendered videos (if enabled)
        └── *.mp4
```

## Quick Start - Local Training

### 1. Start Training

In one terminal (with venv activated):

```powershell
cd C:\Projects\Cogito\Zeroth01\first-steps-sim
.\venv_z\Scripts\activate
python -m train
```

The training will print a TensorBoard URL, something like:
```
TensorBoard logs: http://localhost:6006
```

### 2. Open TensorBoard

In a **second terminal** (with venv activated):

```powershell
cd C:\Projects\Cogito\Zeroth01\first-steps-sim
.\venv_z\Scripts\activate
tensorboard --logdir zbot_walking_task
```

You should see:
```
TensorBoard 2.x.x at http://localhost:6006/ (Press CTRL+C to quit)
```

### 3. View in Browser

Open your browser to:
```
http://localhost:6006
```

## What You'll See in TensorBoard

### Scalars Tab
Tracks numerical metrics over time:

**Rewards & Performance:**
- `reward/total` - Total reward per episode
- `reward/tracking_linear_velocity` - How well robot tracks velocity commands
- `reward/tracking_angular_velocity` - Yaw tracking performance
- `reward/feet_height` - Foot clearance during swing phase
- `reward/orientation` - Robot staying upright
- `reward/survive` - Survival bonus

**Penalties:**
- `penalty/joint_acceleration` - Smoothness of motion
- `penalty/action_rate` - Action changes between steps
- `penalty/energy` - Power consumption
- `penalty/joint_position` - Joint limit violations

**Training Stats:**
- `train/actor_loss` - Policy loss
- `train/critic_loss` - Value function loss
- `train/learning_rate` - Current learning rate
- `train/entropy` - Policy exploration
- `train/clip_fraction` - PPO clipping percentage

**Validation:**
- `val/episode_return` - Average episode return
- `val/episode_length` - Steps per episode

### Images Tab
Visual snapshots from the simulator (if enabled).

### Distributions Tab
Histograms of:
- Action distributions
- Value function estimates
- Reward components

### Text Tab
Configuration and hyperparameters.

## Viewing Previous Runs

### View Specific Run

```powershell
tensorboard --logdir zbot_walking_task/run_0
```

### Compare Multiple Runs

```powershell
# View all runs together
tensorboard --logdir zbot_walking_task

# Or specify multiple runs
tensorboard --logdir run0:zbot_walking_task/run_0,run1:zbot_walking_task/run_1
```

Each run will appear as a separate line in the graphs with different colors.

## TensorBoard Options

### Change Port

```powershell
tensorboard --logdir zbot_walking_task --port 6007
```

### Bind to Specific Host

```powershell
tensorboard --logdir zbot_walking_task --host 0.0.0.0 --port 6006
```

This allows access from other devices on your network at `http://your-ip:6006`.

### Reload Interval

```powershell
# Reload every 5 seconds (default is 5)
tensorboard --logdir zbot_walking_task --reload_interval 5
```

### Limit Memory Usage

```powershell
tensorboard --logdir zbot_walking_task --max_reload_threads 1 --samples_per_plugin scalars=1000
```

## TensorBoard on IDUN

Since IDUN compute nodes don't have direct internet access, you need SSH tunneling.

### Method 1: SSH Port Forwarding (Recommended)

#### Step 1: Start TensorBoard on IDUN

```bash
# On IDUN (in a screen or tmux session)
cd /cluster/work/$USER/first-steps-sim

# Load conda
module load Anaconda3/2024.02-1
source activate /cluster/work/$USER/first-steps-sim/ksim-env/

# Start TensorBoard
tensorboard --logdir zbot_walking_task --host 0.0.0.0 --port 6006
```

#### Step 2: Create SSH Tunnel (from your local machine)

```powershell
# On your Windows machine
ssh -L 6006:localhost:6006 volodymt@idun-login1.hpc.ntnu.no
```

Keep this SSH session open!

#### Step 3: Access in Browser

Open: `http://localhost:6006`

### Method 2: Download Logs Locally

If SSH tunneling doesn't work, download the logs and view them locally:

```powershell
# On your local machine
cd C:\Projects\Cogito\Zeroth01\first-steps-sim

# Download all training data
scp -r volodymt@idun-login1.hpc.ntnu.no:/cluster/work/volodymt/first-steps-sim/zbot_walking_task .

# Start TensorBoard locally
.\venv_z\Scripts\activate
tensorboard --logdir zbot_walking_task
```

Open: `http://localhost:6006`

### Method 3: VS Code Remote Tunnels

If you use VS Code with Remote-SSH extension:

1. Connect to IDUN via VS Code Remote-SSH
2. Open terminal in VS Code
3. Run: `tensorboard --logdir zbot_walking_task --port 6006`
4. VS Code will automatically forward the port
5. Click the popup notification to open in browser

## Monitoring Training Progress

### Key Metrics to Watch

**Early Training (0-100 steps):**
- `reward/total` should increase from negative to positive
- `reward/survive` should go toward 1.0
- `reward/orientation` should improve
- Robot should stand up in videos

**Mid Training (100-500 steps):**
- `reward/tracking_linear_velocity` should increase
- Robot should start walking forward
- `penalty/joint_acceleration` should decrease (smoother motion)

**Late Training (500+ steps):**
- All rewards should stabilize
- Robot walks confidently with various commands
- Low penalties indicate efficient motion

### Signs of Good Training

✅ Total reward steadily increasing  
✅ Survival rate at 100%  
✅ Low joint acceleration penalties  
✅ Smooth tracking of velocity commands  
✅ Decreasing critic loss  

### Warning Signs

⚠️ Reward plateaus early (might need hyperparameter tuning)  
⚠️ Survival drops (robot keeps falling)  
⚠️ Oscillating rewards (learning rate too high)  
⚠️ NaN losses (exploding gradients - restart with lower LR)  

## Customizing Logs

### Change Log Frequency

In `train.py`, adjust the config:

```python
ZbotWalkingTask.launch(
    ZbotWalkingTaskConfig(
        # ... other params ...
        epochs_per_log_step=1,  # Log every N epochs (decrease for more logs)
        valid_every_n_steps=5,  # Validation every N steps
    ),
)
```

### Enable Video Rendering

Videos are automatically rendered based on:

```python
ZbotWalkingTaskConfig(
    # ... other params ...
    render_full_every_n_seconds=10,  # Render video every 10 seconds
    render_azimuth=145.0,  # Camera angle
)
```

Videos are saved to `zbot_walking_task/run_X/videos/` as MP4 files.

## Advanced Usage

### Smoothing in TensorBoard

In the TensorBoard UI, use the "Smoothing" slider in the left sidebar to reduce noise in curves. Try values between 0.6-0.9 for cleaner plots.

### Download Data as CSV

Click the "⋮" menu on any plot → "Export as CSV" to download raw data.

### Compare Experiments

Tag your runs by editing training command:

```powershell
# Add tags to separate experiments
python -m train learning_rate=1e-3  # This will be run_0
python -m train learning_rate=5e-4  # This will be run_1
```

Then compare in TensorBoard:
```powershell
tensorboard --logdir zbot_walking_task
```

### Embedding Projector (Advanced)

If you want to visualize learned embeddings:

```python
# Add to your training code (advanced)
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter('zbot_walking_task/run_X/tensorboard')
writer.add_embedding(embeddings, metadata=labels)
```

## Troubleshooting

### TensorBoard Not Starting

**Error: `tensorboard: command not found`**

Solution:
```powershell
pip install tensorboard
```

**Error: `Port 6006 is already in use`**

Solution:
```powershell
# Use a different port
tensorboard --logdir zbot_walking_task --port 6007

# Or kill the existing TensorBoard
# On Windows (PowerShell):
Get-Process -Name tensorboard | Stop-Process

# On Linux/IDUN:
pkill tensorboard
```

### No Data Showing

**Check if directory exists:**
```powershell
ls zbot_walking_task/
```

**Check if event files exist:**
```powershell
ls zbot_walking_task/run_0/tensorboard/
```

**If empty:** Training hasn't logged yet. Wait for first log step (usually within 30 seconds).

### SSH Tunnel Not Working

**Test connection:**
```powershell
ssh volodymt@idun-login1.hpc.ntnu.no "echo Connection works"
```

**Try explicit bind:**
```powershell
ssh -L 6006:localhost:6006 -N volodymt@idun-login1.hpc.ntnu.no
```

The `-N` flag keeps the connection open without executing commands.

### Out of Disk Space

TensorBoard logs can grow large. Clean old runs:

```powershell
# Be careful! This deletes training data
rm -r zbot_walking_task/run_0
rm -r zbot_walking_task/run_1
```

Or archive them:
```powershell
# Compress old runs
tar -czf run_0_backup.tar.gz zbot_walking_task/run_0/
rm -r zbot_walking_task/run_0/
```

## TensorBoard Plugins

### HParams (Hyperparameter Tuning)

Compare hyperparameters across runs:

```python
# In your training code (if you add this)
from tensorboard.plugins.hparams import api as hp

HP_LR = hp.HParam('learning_rate', hp.RealInterval(1e-5, 1e-2))
HP_BATCH = hp.HParam('batch_size', hp.Discrete([128, 256, 512]))
```

View in TensorBoard → HParams tab.

### Profile (Performance Analysis)

Profile training speed:

```python
# Add profiling (advanced)
with tf.profiler.experimental.Profile('logdir'):
    train()
```

View in TensorBoard → Profile tab.

## Quick Reference Commands

```powershell
# Start training
python -m train

# View logs (while training or after)
tensorboard --logdir zbot_walking_task

# View specific run
tensorboard --logdir zbot_walking_task/run_0

# Different port
tensorboard --logdir zbot_walking_task --port 6007

# SSH tunnel (from local to IDUN)
ssh -L 6006:localhost:6006 volodymt@idun-login1.hpc.ntnu.no

# Download logs from IDUN
scp -r volodymt@idun-login1.hpc.ntnu.no:/cluster/work/volodymt/first-steps-sim/zbot_walking_task .

# Kill TensorBoard
Get-Process -Name tensorboard | Stop-Process  # Windows
pkill tensorboard  # Linux/IDUN
```

## Example Workflow

### Local Training

```powershell
# Terminal 1: Training
cd C:\Projects\Cogito\Zeroth01\first-steps-sim
.\venv_z\Scripts\activate
python -m train max_steps=500

# Terminal 2: TensorBoard
cd C:\Projects\Cogito\Zeroth01\first-steps-sim
.\venv_z\Scripts\activate
tensorboard --logdir zbot_walking_task

# Browser: http://localhost:6006
```

### IDUN Training

```bash
# On IDUN: Submit job
cd /cluster/work/$USER/first-steps-sim
sbatch slurm_example.slurm

# On IDUN: Start TensorBoard (in screen session)
screen -S tensorboard
module load Anaconda3/2024.02-1
source activate /cluster/work/$USER/first-steps-sim/ksim-env/
tensorboard --logdir zbot_walking_task --host 0.0.0.0 --port 6006
# Press Ctrl+A then D to detach

# On Local: Create tunnel
ssh -L 6006:localhost:6006 volodymt@idun-login1.hpc.ntnu.no

# Browser: http://localhost:6006
```

## Tips for Better Visualization

1. **Use Descriptive Run Names**: Name experiments clearly for easy comparison
2. **Regular Checkpoints**: Enable frequent checkpoints to save progress
3. **Smooth Curves**: Use TensorBoard's smoothing slider for cleaner plots
4. **Tag Experiments**: Group related runs with consistent naming
5. **Archive Old Runs**: Move completed experiments to free space
6. **Monitor During Training**: Check TensorBoard every ~10-15 minutes
7. **Save Interesting Runs**: Back up runs with good results

## Further Reading

- [TensorBoard Documentation](https://www.tensorflow.org/tensorboard)
- [ksim Documentation](https://docs.kscale.dev/docs/ksim)
- [PPO Algorithm](https://arxiv.org/abs/1707.06347)

Happy training! 📊🚀
