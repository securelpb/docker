#!/bin/bash
# This script is executed by tini and is responsible for starting
# the sshd daemon and then executing the main container command.

set -e

echo "--- Starting SSHD as root ---"
# The sshd daemon MUST be started as root to read the host keys.
sudo /usr/sbin/sshd

echo "--- SSHD started. Executing Jupyter Lab ---"
# Now, execute the command that was passed to this script.
# In the Dockerfile, this will be the jupyter lab command.
# The 'exec' command replaces the shell process with the new process,
# which is the correct way to run the main application.
exec "$@"
