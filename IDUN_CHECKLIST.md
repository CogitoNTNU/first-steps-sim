# IDUN Deployment Checklist

Use this checklist when deploying to IDUN for the first time or after major changes.

## Pre-Deployment (Local Machine)

- [ ] Code is working locally (at least tested with small parameters)
- [ ] All dependencies are listed in `requirements.txt`
- [ ] Git repository is up to date
- [ ] You're on the correct branch (`volodymyr` or your feature branch)
- [ ] Committed all changes and pushed to remote

```bash
git add .
git commit -m "Ready for IDUN deployment"
git push origin volodymyr
```

## Initial Setup on IDUN

- [ ] SSH into IDUN successfully
```bash
ssh your-username@idun-login1.hpc.ntnu.no
```

- [ ] Navigate to work directory (NOT home directory)
```bash
cd /cluster/work/$USER
```

- [ ] Clone repository (or pull latest changes)
```bash
git clone git@github.com:CogitoNTNU/first-steps-sim.git
cd first-steps-sim
git checkout volodymyr
```

- [ ] Run setup script
```bash
bash setup_idun.sh
```

- [ ] Verify SLURM script email is correct
```bash
grep "mail-user" *.slurm
```

- [ ] Check available resources
```bash
sinfo -p GPUQ --format="%20P %5D %14F %10m %11l %N"
```

## Configuration

- [ ] Choose appropriate SLURM script:
  - `slurm_example.slurm` for full training (GPU, 24h)
  - `wave_demo.slurm` for wave demo (CPU, 30min)

- [ ] Adjust time limit if needed (in SLURM script)
- [ ] Adjust memory if needed (in SLURM script)
- [ ] Set training parameters (in SLURM script's python command)

## Job Submission

- [ ] Create output directory
```bash
mkdir -p slurm_outputs
```

- [ ] Submit job
```bash
sbatch slurm_example.slurm  # or wave_demo.slurm
```

- [ ] Note the job ID from output
- [ ] Verify job is queued
```bash
squeue -u $USER
```

## Monitoring

- [ ] Check job status regularly
```bash
squeue -u $USER
```

- [ ] Monitor output logs
```bash
tail -f slurm_outputs/ksim_output.txt
```

- [ ] Check for errors
```bash
tail -f slurm_outputs/ksim_error.txt
```

- [ ] Verify GPU is being used (should see "gpu" backend)
```bash
grep "Checking JAX backend" slurm_outputs/ksim_output.txt
```

- [ ] Confirm training started (look for tensorboard output)

## During Training

- [ ] Check job is still running (not failed)
```bash
squeue -u $USER
```

- [ ] Monitor progress in logs
```bash
# Look for training step numbers
tail -20 slurm_outputs/ksim_output.txt
```

- [ ] Verify checkpoints are being saved
```bash
ls -lht zbot_walking_task/run_*/checkpoints/ | head
```

- [ ] (Optional) Check GPU utilization
```bash
# Get node name from squeue, then:
ssh <node-name> nvidia-smi
```

## After Training

- [ ] Check job completed successfully
```bash
sacct -u $USER --format=JobID,JobName,State,Elapsed
```

- [ ] Verify final checkpoint exists
```bash
ls -lh zbot_walking_task/run_*/checkpoints/ckpt.bin
```

- [ ] Check training logs for final metrics
```bash
tail -50 slurm_outputs/ksim_output.txt
```

- [ ] Download checkpoint to local machine
```bash
# On local machine:
scp your-username@idun-login1.hpc.ntnu.no:/cluster/work/$USER/first-steps-sim/zbot_walking_task/run_XXX/checkpoints/ckpt.bin ./
```

- [ ] (Optional) Download tensorboard logs
```bash
# On local machine:
scp -r your-username@idun-login1.hpc.ntnu.no:/cluster/work/$USER/first-steps-sim/zbot_walking_task ./
```

## Validation

- [ ] Test checkpoint locally in view mode
```bash
python -m train run_mode=view load_from_ckpt_path=ckpt.bin
```

- [ ] Convert to kinfer model (if deploying to robot)
```bash
python -m convert ckpt.bin model.kinfer
```

- [ ] Visualize in kinfer-sim
```bash
kinfer-sim model.kinfer kbot --start-height 0.32 --save-video video.mp4
```

## Cleanup (Optional)

- [ ] Delete old run directories to save space
```bash
# Be careful! This deletes training data
rm -rf zbot_walking_task/run_0  # Adjust run number
```

- [ ] Archive successful runs
```bash
# On local machine:
scp -r your-username@idun-login1.hpc.ntnu.no:/cluster/work/$USER/first-steps-sim/zbot_walking_task ./backup/
```

- [ ] Clean old SLURM logs
```bash
rm slurm_outputs/ksim_output.txt.old
rm slurm_outputs/ksim_error.txt.old
```

## Troubleshooting Checklist

If something goes wrong:

- [ ] Check SLURM error file first
```bash
cat slurm_outputs/ksim_error.txt
```

- [ ] Verify conda environment was created
```bash
ls -la /cluster/work/$USER/first-steps-sim/ksim-env/
```

- [ ] Check if dependencies installed correctly
```bash
# Look for "Successfully installed" messages
grep -i "successfully installed" slurm_outputs/ksim_output.txt
```

- [ ] Verify JAX has GPU access
```bash
grep "JAX backend" slurm_outputs/ksim_output.txt
```

- [ ] Check if out of memory
```bash
grep -i "memory\|OOM" slurm_outputs/ksim_error.txt
```

- [ ] Check if out of disk space
```bash
df -h /cluster/work/$USER
```

- [ ] Review job details
```bash
sacct -j <job_id> --format=JobID,JobName,State,Elapsed,MaxRSS,AllocCPUS,AllocGPUS
```

## Re-running After Fixes

- [ ] Cancel old job if still running
```bash
scancel <job_id>
```

- [ ] Update code on IDUN
```bash
cd /cluster/work/$USER/first-steps-sim
git pull origin volodymyr
```

- [ ] Clear old conda environment if needed
```bash
rm -rf /cluster/work/$USER/first-steps-sim/ksim-env/
```

- [ ] Resubmit job
```bash
sbatch slurm_example.slurm
```

## Success Criteria

Your deployment is successful when:

- [x] Job runs without errors
- [x] JAX backend shows "gpu"
- [x] Training progresses (step numbers increase)
- [x] Checkpoints are saved regularly
- [x] TensorBoard logs are generated
- [x] Final checkpoint can be loaded and visualized

---

**Pro Tip**: Copy this checklist and mark items as you go. Save your notes for next time!

## Quick Reference

```bash
# Submit
sbatch slurm_example.slurm

# Monitor
squeue -u $USER
tail -f slurm_outputs/ksim_output.txt

# Cancel
scancel <job_id>

# Download checkpoint
scp user@idun:/cluster/work/$USER/first-steps-sim/zbot_walking_task/run_X/checkpoints/ckpt.bin ./
```

For detailed help, see [IDUN_GUIDE.md](IDUN_GUIDE.md)
