# OpenClaw Docker-Compose Note and Usage Guide
## Build
`docker compose build`

## Running
* `docker compose up` to run in the current terminal
* `docker compose up -d` to detach and enable as a service.

## Post-deployment interactions
* Enter the running container: `docker exec -it openclaw-gateway <cmd>`
* Run openclaw cli in the container: `docker exec -it openclaw-gateway openclaw <cmd>`
* Run setup: `docker exec -it openclaw-gateway openclaw setup`
* Run onboarding: `docker exec -it openclaw-gateway openclaw onboard`
* Run doctor: `docker exec -it openclaw-gateway openclaw doctor` (Add --fix to fix things)

## Configuration to enable ssh into a remote host (perform on target hosts)
```
# 1. Create group "shared" to share files with openclaw_agent user
sudo groupadd shared

# 2. Create dedicated service user on Art.lan
sudo useradd -m -s /bin/bash openclaw_agent

# 3. Set up SSH directory for openclaw_agent
sudo mkdir -p /home/openclaw_agent/.ssh
sudo chmod 700 /home/openclaw_agent/.ssh

# 4. Add Hal's OpenClaw SSH public key
sudo cp hal_ed25519.pub /home/openclaw_agent/.ssh/authorized_keys
# or echo "YOUR_HAL_OPENCLAW_SSH_PUBLIC_KEY" | sudo tee -a /home/openclaw_agent/.ssh/authorized_keys
sudo chmod 600 /home/openclaw_agent/.ssh/authorized_keys
sudo chown -R openclaw_agent:openclaw_agent /home/openclaw_agent/.ssh

# 5. Ensure openclaw_agent has read access to your image store on Art.lan
sudo usermod -aG shared openclaw_agent
```
### Verify Pubkey authentication is enabled on server
```aiexclude
sudo grep -E 'PubkeyAuthentication|AuthorizedKeysFile' /etc/ssh/sshd_config
    
PubkeyAuthentication yes
AuthorizedKeysFile	.ssh/authorized_keys
```

### Setup .ssh/config in Openclaw
```aiexclude
Host hal.lan
    HostName hal.lan
    User openclaw_agent
    IdentityFile /home/node/.ssh/hal_ed25519
    IdentitiesOnly yes
Host art.lan
    HostName art.lan
    User openclaw_agent
    IdentityFile /home/node/.ssh/hal_ed25519
    IdentitiesOnly yes
```