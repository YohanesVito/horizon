#!/usr/bin/env bash
set -euo pipefail
# Match Docker bridge MTU to the VPS uplink before any application is started.
# Preserve existing daemon options and validate before restarting Docker.
test -z "$(docker ps -q)" || { echo 'Refusing to restart Docker with active containers'; exit 1; }
python3 - <<'PY'
from pathlib import Path
import json, shutil, subprocess
routes = json.loads(subprocess.check_output(['ip', '-j', 'route', 'show', 'default']))
interface = routes[0]['dev']
mtu = int(Path('/sys/class/net', interface, 'mtu').read_text())
assert 1200 <= mtu <= 1500
path = Path('/etc/docker/daemon.json')
path.parent.mkdir(parents=True, exist_ok=True)
config = json.loads(path.read_text()) if path.exists() else {}
config['mtu'] = mtu
config.setdefault('default-network-opts', {}).setdefault('bridge', {})['com.docker.network.driver.mtu'] = str(mtu)
candidate = path.with_suffix('.candidate.json')
candidate.write_text(json.dumps(config, indent=2) + '\n')
subprocess.run(['dockerd', '--validate', '--config-file', str(candidate)], check=True)
if path.exists():
    shutil.copy2(path, path.with_suffix('.pre-horizon.json'))
candidate.replace(path)
print('DOCKER_BRIDGE_MTU', mtu, flush=True)
PY
systemctl restart docker
docker run --rm --entrypoint python python:3.12-slim-bookworm -c '
import urllib.request
with urllib.request.urlopen("https://pypi.org/simple/annotated-doc/", timeout=15) as response:
    assert response.status == 200
    print("CONTAINER_PYPI_HTTPS_PASSED")
'
