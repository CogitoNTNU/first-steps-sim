# Running on IDUN (NTNU HPC Cluster)

This guide explains how to run the ZBot training and wave demo on IDUN, NTNU's high-performance computing cluster.

## Prerequisites

1. **IDUN Account**: Make sure you have access to IDUN
2. **SSH Access**: Set up SSH keys for passwordless login
3. **Cogito Account**: The SLURM scripts use the `studiegrupper-cogito` account

## Quick Start on IDUN

### 1. Connect to IDUN

```bash
ssh your-username@idun-login1.hpc.ntnu.no
```

### 2. Navigate to Your Work Directory

```bash
cd /cluster/work/$USER
```

### 3. Clone Your Repository

```bash
# If not already cloned
git clone git@github.com:CogitoNTNU/first-steps-sim.git
cd first-steps-sim

# Switch to your branch
git checkout volodymyr
```

### 4. Submit Training Job

For full training with GPU:

```bash
# Create output directory
mkdir -p slurm_outputs

# Submit the job
sbatch slurm_example.slurm
```

### 5. Submit Wave Demo Job

For just running the wave demo (no GPU needed):

```bash
sbatch wave_demo.slurm
```

## Monitoring Your Jobs

### Check job status:
```bash
squeue -u $USER
```

### Check job output (live):
```bash
tail -f slurm_outputs/ksim_output.txt
```

### Check errors:
```bash
tail -f slurm_outputs/ksim_error.txt
```

### Cancel a job:
```bash
scancel <job_id>
```

### Check completed job info:
```bash
sacct -j <job_id> --format=JobID,JobName,Partition,State,Time,Elapsed
```

## File Structure on IDUN

```
/cluster/work/$USER/first-steps-sim/
├── train.py                    # Main training script
├── wave_demo.py               # Wave demo script
├── slurm_example.slurm        # Training SLURM script (GPU)
├── wave_demo.slurm            # Wave demo SLURM script (CPU)
├── slurm_outputs/             # Job output logs
│   ├── ksim_output.txt
│   ├── ksim_error.txt
│   ├── wave_demo_output.txt
│   └── wave_demo_error.txt
├── ksim-env/                  # Conda environment (created automatically)
└── zbot_walking_task/         # Training outputs (checkpoints, logs)
    └── run_XXX/
        ├── checkpoints/
        ├── tensorboard/
        └── videos/
```

## SLURM Script Configuration

### For Training (GPU Required)

The `slurm_example.slurm` script is configured for:
- **Partition**: GPUQ (GPU queue)
- **GPU**: 1x (A100, H100, or H200 with 40GB or 80GB memory)
- **Time**: 24 hours
- **Memory**: 40GB RAM
- **Account**: studiegrupper-cogito

### For Wave Demo (CPU Only)

The `wave_demo.slurm` script is configured for:
- **Partition**: CPUQ (CPU queue, cheaper and faster to schedule)
- **Time**: 30 minutes
- **Memory**: 8GB RAM
- **Account**: studiegrupper-cogito

## Customizing SLURM Scripts

### Change Email Notifications

Edit the `--mail-user` line in the SLURM script:

```bash
#SBATCH --mail-user=your-email@stud.ntnu.no
```

### Change Time Limit

```bash
#SBATCH --time=48:00:00  # 48 hours
```

### Change GPU Type

```bash
# For any available GPU
#SBATCH --gres=gpu:1

# For specific GPU with memory requirement
#SBATCH --constraint="a100&gpu80g"
```

### Change Memory

```bash
#SBATCH --mem=64GB  # Request 64GB RAM
```

## Training Arguments on IDUN

You can pass arguments to the training script by editing the SLURM file:

```bash
# In slurm_example.slurm, change the last line:
python -m train max_steps=1000 num_envs=8192 learning_rate=5e-4
```

Or create a custom SLURM script:

```bash
cp slurm_example.slurm my_experiment.slurm
# Edit my_experiment.slurm with your parameters
sbatch my_experiment.slurm
```

## Viewing Results

### TensorBoard on IDUN

Since IDUN nodes don't have direct internet access, you need to set up port forwarding:

#### Method 1: SSH Tunneling

1. Start TensorBoard on IDUN (in a separate session or screen):
```bash
# On IDUN
module load Anaconda3/2024.02-1
source activate /cluster/work/$USER/first-steps-sim/ksim-env/
tensorboard --logdir zbot_walking_task --host 0.0.0.0 --port 6006
```

2. On your local machine, create SSH tunnel:
```bash
ssh -L 6006:idun-login1.hpc.ntnu.no:6006 your-username@idun-login1.hpc.ntnu.no
```

3. Open browser to: `http://localhost:6006`

#### Method 2: Copy Results Locally

```bash
# On your local machine
scp -r your-username@idun-login1.hpc.ntnu.no:/cluster/work/$USER/first-steps-sim/zbot_walking_task ./
tensorboard --logdir zbot_walking_task
```

### Download Trained Checkpoints

```bash
# From your local machine
scp your-username@idun-login1.hpc.ntnu.no:/cluster/work/$USER/first-steps-sim/zbot_walking_task/run_XXX/checkpoints/ckpt.bin ./
```

## Troubleshooting

### Job Stays in Queue (PENDING)

Check why:
```bash
squeue -u $USER -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"
```

Common reasons:
- `Resources`: Waiting for GPU/CPU availability
- `Priority`: Other jobs have higher priority
- `QOSMaxCPUPerUser`: You've reached CPU limit

### Out of Memory Error

Reduce batch size or number of environments in `slurm_example.slurm`:
```bash
python -m train num_envs=2048 batch_size=128
```

### JAX Not Using GPU

Check the output logs for:
```
Checking JAX backend:
gpu  # Should say "gpu", not "cpu"
```

If it says "cpu", the CUDA installation may have failed. Check error logs.

### MuJoCo Rendering Issues

IDUN is headless (no display), so use:
```bash
export MUJOCO_GL=osmesa
```

This is already set in the SLURM scripts. For viewing trained models, download the checkpoint and run locally.

### Conda Environment Issues

If the environment gets corrupted:
```bash
# On IDUN
rm -rf /cluster/work/$USER/first-steps-sim/ksim-env/
# Re-submit job, it will recreate the environment
```

### Permission Denied

Make sure you're in your work directory:
```bash
cd /cluster/work/$USER
```

Don't run jobs from `/cluster/home/$USER` (limited storage).

## Best Practices

### 1. Use Screen or Tmux for Long Sessions

```bash
# Start a screen session
screen -S training

# Detach: Ctrl+A, then D
# Reattach: screen -r training
```

### 2. Test Locally First

Before submitting expensive GPU jobs, test on login node (CPU only):
```bash
# Quick test (will be slow without GPU)
python -m train max_steps=1 num_envs=4
```

### 3. Use Job Arrays for Hyperparameter Sweeps

Create `sweep.slurm`:
```bash
#SBATCH --array=0-4

# Define parameters
LEARNING_RATES=(1e-3 5e-4 1e-4 5e-5 1e-5)
LR=${LEARNING_RATES[$SLURM_ARRAY_TASK_ID]}

python -m train learning_rate=$LR
```

Submit:
```bash
sbatch sweep.slurm
```

### 4. Save Checkpoints Frequently

The default saves every 60 seconds, which is good. Check the checkpoint directory:
```bash
ls -lh /cluster/work/$USER/first-steps-sim/zbot_walking_task/run_*/checkpoints/
```

### 5. Monitor GPU Usage

While job is running:
```bash
ssh <node-name>  # Use the node from squeue output
nvidia-smi
```

## IDUN Resource Limits

### Cogito Account Limits
- Check current limits: `cost -u --account studiegrupper-cogito`
- Be mindful of shared resources within the group

### GPU Queue Priority
- A100 80GB > A100 40GB > H100 > H200 (in terms of availability)
- Shorter jobs get scheduled faster

### Storage Quotas
- Work directory: `/cluster/work/$USER` (larger quota, use for training)
- Home directory: `/cluster/home/$USER` (limited, use for scripts only)

## Example Workflow

### Complete Training Run

```bash
# 1. Connect to IDUN
ssh your-username@idun-login1.hpc.ntnu.no

# 2. Go to work directory
cd /cluster/work/$USER/first-steps-sim

# 3. Update code
git pull origin volodymyr

# 4. Submit job
mkdir -p slurm_outputs
sbatch slurm_example.slurm

# 5. Monitor
squeue -u $USER
tail -f slurm_outputs/ksim_output.txt

# 6. After ~30 minutes, check results
ls -lh zbot_walking_task/run_*/checkpoints/

# 7. Download checkpoint (on local machine)
scp your-username@idun-login1.hpc.ntnu.no:/cluster/work/$USER/first-steps-sim/zbot_walking_task/run_XXX/checkpoints/ckpt.bin ./
```

## Contact & Support

- **IDUN Documentation**: https://www.hpc.ntnu.no/idun/
- **IDUN Support**: hpc-idun-support@ntnu.no
- **Cogito Discord**: Ask in the #cogito-tech channel

## Quick Reference Commands

```bash
# Submit job
sbatch script.slurm

# Check job status
squeue -u $USER

# Cancel job
scancel <job_id>

# Check job history
sacct -u $USER --starttime 2025-10-29

# Check account usage
cost -u --account studiegrupper-cogito

# Monitor running job output
tail -f slurm_outputs/ksim_output.txt

# Check GPU availability
sinfo -p GPUQ --format="%20P %5D %14F %10m %11l %N"

# Interactive job (for debugging)
srun --account=studiegrupper-cogito --partition=GPUQ --gres=gpu:1 --mem=16GB --time=01:00:00 --pty bash
```

Good luck with your training! 🚀
