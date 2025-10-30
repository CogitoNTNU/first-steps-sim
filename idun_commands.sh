#!/bin/bash
# IDUN Quick Reference - Common Commands
# Save this as: ~/idun-commands.sh
# Source it: source ~/idun-commands.sh

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== IDUN Quick Commands ===${NC}"
echo ""

# Aliases for common commands
alias myq='squeue -u $USER'
alias myj='sacct -u $USER --starttime $(date -d "7 days ago" +%Y-%m-%d) --format=JobID,JobName,Partition,State,Elapsed,TimeLimit'
alias mycost='cost -u --account studiegrupper-cogito'
alias gpuinfo='sinfo -p GPUQ --format="%20P %5D %14F %10m %11l %N"'

# Functions
function submit() {
    echo -e "${YELLOW}Submitting job: $1${NC}"
    mkdir -p slurm_outputs
    sbatch "$1"
}

function tail-job() {
    if [ -z "$1" ]; then
        echo "Usage: tail-job <output|error>"
        return 1
    fi
    if [ "$1" = "output" ] || [ "$1" = "o" ]; then
        tail -f slurm_outputs/ksim_output.txt
    elif [ "$1" = "error" ] || [ "$1" = "e" ]; then
        tail -f slurm_outputs/ksim_error.txt
    else
        echo "Unknown option. Use 'output' or 'error'"
    fi
}

function cancel-all() {
    echo -e "${YELLOW}Cancelling all your jobs...${NC}"
    scancel -u $USER
}

function job-info() {
    if [ -z "$1" ]; then
        echo "Usage: job-info <job_id>"
        return 1
    fi
    sacct -j "$1" --format=JobID,JobName,Partition,State,Elapsed,TimeLimit,MaxRSS,AllocCPUS,AllocGPUS
}

function gpu-check() {
    if [ -z "$1" ]; then
        echo "Usage: gpu-check <node-name>"
        echo "Example: gpu-check idun-gpu01"
        return 1
    fi
    ssh "$1" nvidia-smi
}

# Print available commands
echo "Available commands:"
echo "  myq              - Show your jobs in queue"
echo "  myj              - Show your job history (last 7 days)"
echo "  mycost           - Check account usage"
echo "  gpuinfo          - Check GPU availability"
echo "  submit <file>    - Submit a SLURM job"
echo "  tail-job output  - Tail output log"
echo "  tail-job error   - Tail error log"
echo "  cancel-all       - Cancel all your jobs"
echo "  job-info <id>    - Get detailed job info"
echo "  gpu-check <node> - Check GPU usage on node"
echo ""
