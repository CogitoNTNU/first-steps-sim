#!/bin/bash
# Quick setup script for IDUN
# Run this after cloning the repository on IDUN

echo "======================================"
echo "IDUN Setup for first-steps-sim"
echo "======================================"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p slurm_outputs
mkdir -p zbot_walking_task

# Check if we're on IDUN
if [[ ! $(hostname) =~ "idun" ]]; then
    echo "⚠️  Warning: This doesn't appear to be an IDUN node"
    echo "   Hostname: $(hostname)"
    echo "   Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Display current location
echo ""
echo "Current directory: $(pwd)"
echo "User: $USER"
echo ""

# Check if we're in the work directory
if [[ ! $(pwd) =~ "/cluster/work" ]]; then
    echo "⚠️  Warning: You should run this from /cluster/work/$USER"
    echo "   Current: $(pwd)"
    echo ""
fi

# Check SLURM account
echo "Checking SLURM account..."
if command -v sacctmgr &> /dev/null; then
    echo "Your SLURM accounts:"
    sacctmgr show user $USER format=user,account -P | grep -v "User|Account"
    echo ""
else
    echo "Note: sacctmgr not available (you might not be on a login node)"
    echo ""
fi

# Update email in SLURM scripts if needed
echo "Current email in SLURM scripts:"
grep "mail-user" *.slurm 2>/dev/null | head -1
echo ""
echo "Update email address? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Enter your NTNU email:"
    read -r email
    for file in *.slurm; do
        if [ -f "$file" ]; then
            sed -i "s/volodymt@stud.ntnu.no/$email/g" "$file"
            echo "Updated $file"
        fi
    done
    echo ""
fi

# Summary
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Submit training job:"
echo "   sbatch slurm_example.slurm"
echo ""
echo "2. Or submit wave demo:"
echo "   sbatch wave_demo.slurm"
echo ""
echo "3. Monitor your job:"
echo "   squeue -u $USER"
echo "   tail -f slurm_outputs/ksim_output.txt"
echo ""
echo "4. Check logs:"
echo "   ls -lh slurm_outputs/"
echo ""
echo "For more details, see IDUN_GUIDE.md"
echo ""
