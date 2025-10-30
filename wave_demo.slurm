#!/bin/sh
#SBATCH --account=studiegrupper-cogito
#SBATCH --job-name="zbot-wave-demo"
#SBATCH --time=00:30:00
#SBATCH --partition=CPUQ
#SBATCH --mem=8GB
#SBATCH --nodes=1
#SBATCH --output=slurm_outputs/wave_demo_output.txt
#SBATCH --error=slurm_outputs/wave_demo_error.txt
#SBATCH --mail-user=volodymt@stud.ntnu.no
#SBATCH --mail-type=ALL

WORKDIR=${SLURM_SUBMIT_DIR}
cd ${WORKDIR}
echo "Running from directory: $SLURM_SUBMIT_DIR"
echo "Job name: $SLURM_JOB_NAME"
echo "Job ID: $SLURM_JOB_ID"
echo "Node(s): $SLURM_JOB_NODELIST"

# Create output directory if it doesn't exist
mkdir -p slurm_outputs

# Path to your conda env (change if needed)
ENV_PATH="/cluster/work/$USER/first-steps-sim/ksim-env/"

module purge
module load Anaconda3/2024.02-1

# Create conda environment if it doesn't exist
if [ ! -d "$ENV_PATH" ]; then
  conda create -y --prefix ${ENV_PATH} python=3.11
fi

# Activate environment
source activate ${ENV_PATH}

# Install minimal dependencies for wave demo (numpy only)
pip install numpy

echo "Installed packages:"
pip freeze | grep -i numpy

# Run wave demo in simple mode (no visualization, just prints joint angles)
echo "========================================"
echo "Running Wave Demo"
echo "========================================"
python wave_demo.py --mode simple --wave-speed 2.0 --wave-amplitude 0.8

echo ""
echo "========================================"
echo "Running Integration Guide"
echo "========================================"
python wave_demo.py --mode integration

conda deactivate

echo "Job finished successfully!"
