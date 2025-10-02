#!/usr/bin/env python3
"""
Docker Environment Installer for Cursor Background Agents
Purpose: Set up Docker environment for Cursor background agents
Version: 1.0 - Initial setup
Date: 2024-12-19
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def log(message, level="INFO"):
    """Simple logging function"""
    print(f"[{level}] {message}")

def run_command(command, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_docker_installed():
    """Check if Docker is installed and running"""
    log("Checking Docker installation...")
    success, stdout, stderr = run_command("docker --version", check=False)
    if not success:
        log("Docker is not installed or not in PATH", "ERROR")
        return False
    
    log(f"Docker version: {stdout.strip()}")
    
    # Check if Docker daemon is running
    success, stdout, stderr = run_command("docker info", check=False)
    if not success:
        log("Docker daemon is not running. Please start Docker Desktop or Docker service.", "ERROR")
        return False
    
    log("Docker is running properly")
    return True

def build_docker_image():
    """Build the Docker image for background agents"""
    log("Building Docker image for Cursor background agents...")
    
    # Check if Dockerfile exists
    dockerfile_path = Path(".cursor/Dockerfile")
    if not dockerfile_path.exists():
        log("Dockerfile not found at .cursor/Dockerfile", "ERROR")
        return False
    
    # Build the image
    build_command = "docker build -t cursor-bg-agent .cursor/"
    success, stdout, stderr = run_command(build_command)
    
    if not success:
        log(f"Failed to build Docker image: {stderr}", "ERROR")
        return False
    
    log("Docker image built successfully")
    return True

def verify_environment():
    """Verify the environment.json configuration"""
    log("Verifying environment configuration...")
    
    env_path = Path(".cursor/environment.json")
    if not env_path.exists():
        log("environment.json not found", "ERROR")
        return False
    
    try:
        with open(env_path, 'r') as f:
            config = json.load(f)
        
        if 'build' not in config:
            log("Missing 'build' section in environment.json", "ERROR")
            return False
        
        if config['build'].get('dockerfile') != 'Dockerfile':
            log("Dockerfile path mismatch in environment.json", "WARNING")
        
        log("Environment configuration is valid")
        return True
        
    except json.JSONDecodeError as e:
        log(f"Invalid JSON in environment.json: {e}", "ERROR")
        return False

def test_docker_image():
    """Test the built Docker image"""
    log("Testing Docker image...")
    
    test_command = "docker run --rm cursor-bg-agent echo 'Docker environment test successful'"
    success, stdout, stderr = run_command(test_command)
    
    if not success:
        log(f"Docker image test failed: {stderr}", "ERROR")
        return False
    
    log("Docker image test passed")
    return True

def main():
    """Main installation process"""
    log("Starting Docker environment installation for Cursor background agents")
    
    # Check prerequisites
    if not check_docker_installed():
        log("Please install Docker and ensure it's running, then try again.", "ERROR")
        sys.exit(1)
    
    # Verify environment configuration
    if not verify_environment():
        log("Please fix environment.json configuration", "ERROR")
        sys.exit(1)
    
    # Build Docker image
    if not build_docker_image():
        log("Failed to build Docker image", "ERROR")
        sys.exit(1)
    
    # Test the image
    if not test_docker_image():
        log("Docker image test failed", "ERROR")
        sys.exit(1)
    
    log("Docker environment installation completed successfully!")
    log("Your Cursor background agents are ready to use.")
    
    # Show usage information
    print("\n" + "="*50)
    print("USAGE INFORMATION:")
    print("="*50)
    print("• The Docker image 'cursor-bg-agent' is now available")
    print("• Cursor will automatically use this environment for background agents")
    print("• To rebuild the image: python .cursor/scripts/install_docker_env.py")
    print("• To test manually: docker run --rm -it cursor-bg-agent bash")
    print("="*50)

if __name__ == "__main__":
    main()

