#!/bin/bash
# This script is executed by tini and is responsible for starting
# the sshd daemon and then executing the main container command.

set -e

echo "--- Starting SSHD as root ---"
# The sshd daemon MUST be started as root to read the host keys.
sudo /usr/sbin/sshd

echo "--- SSHD started. Verifying user SSH permissions ---"
# List permissions for the jovyan user's home, .ssh directory, and authorized_keys file.
# This is critical for debugging public key authentication issues.
ls -ld /home/jovyan
ls -ld /home/jovyan/.ssh
ls -l /home/jovyan/.ssh/authorized_keys

echo "--- Permissions verified. Executing Jupyter Lab ---"
# Now, execute the command that was passed to this script.
# In the Dockerfile, this will be the jupyter lab command.
# The 'exec' command replaces the shell process with the new process,
# which is the correct way to run the main application.
exec "$@"
