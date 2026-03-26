import argparse
from pathlib import Path
import subprocess

def pull_docker_image(version: str) -> int:
    """
    Runs `docker pull thingsboard/tb-postgres:{version}` and prints the output.
    Returns the process return code.
    """
    cmd = ["docker", "pull", f"thingsboard/tb-postgres:{version}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")
        return result.returncode
    except FileNotFoundError:
        print("Error: 'docker' command not found. Please ensure Docker is installed and in PATH.")
        return 127

def run_upgrade_container(target_version: str) -> int:
    """
    Runs:
      docker run -it -v /var/lib/thingsboard/data:/data --rm \
        thingsboard/tb-postgres:{target_version} \
        upgrade-tb.sh --fromVersion={current_version}
    Prints combined stdout/stderr and returns the exit code.
    """
    cmd = [
        "docker", "run", "-it",
        "-v", "/var/lib/thingsboard/data:/data",
        "--rm",
        f"thingsboard/tb-postgres:{target_version}",
        "upgrade-tb.sh",
    ]
    try:
        result = subprocess.run(cmd, captureOutput := False, text=True)
        return result.returncode
    except FileNotFoundError:
        print("Error: 'docker' command not found. Please ensure Docker is installed and in PATH.")
        return 127

def main():
    parser = argparse.ArgumentParser(description="Upgrade to a new version of Thingsboard")
    parser.add_argument("-v", "--version", required=True, help="Target Version")
    args = parser.parse_args()

    print(f"Version provided: {args.version}")
    rc = pull_docker_image(args.version)
    if rc != 0:
        print(f"Docker pull failed with exit code {rc}")
        return

    rc = run_upgrade_container(args.version)
    if rc != 0:
        print(f"Upgrade container exited with code {rc}")

if __name__ == "__main__":
    main()

