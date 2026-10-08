"""Write a safe operational snapshot without environment values or full inspect logs."""
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import subprocess
import urllib.request


def output(*args):
    return subprocess.check_output(args, text=True).strip()


units = ["curation-realtime", "curation-recorder", "curation-reversal-paper",
         "curation-reversal-paper-v2", "curation-zone-paper"]
report = {"at_utc": datetime.now(timezone.utc).isoformat(), "curation_services": {}}
for name in units:
    fields = output("systemctl", "show", name, "-p", "ActiveState", "-p", "SubState",
                    "-p", "MainPID", "-p", "UnitFileState")
    report["curation_services"][name] = dict(line.split("=", 1) for line in fields.splitlines())
ids = output("docker", "ps", "--filter", "label=com.docker.compose.project=horizon", "-q").split()
report["containers"] = []
for container_id in ids:
    # Inspect stays in memory; only this allowlist is persisted.
    info = json.loads(output("docker", "inspect", container_id))[0]
    report["containers"].append({
        "name": info["Name"], "image_id": info["Image"],
        "status": info["State"]["Status"],
        "healthy": info["State"].get("Health", {}).get("Status"),
        "started_at": info["State"]["StartedAt"], "restart_count": info["RestartCount"],
        "user": info["Config"]["User"],
        "read_only": info["HostConfig"]["ReadonlyRootfs"],
        "memory_limit": info["HostConfig"]["Memory"],
        "restart_policy": info["HostConfig"]["RestartPolicy"]["Name"],
        "cap_drop": info["HostConfig"]["CapDrop"],
    })
report["io_pressure"] = Path("/proc/pressure/io").read_text().strip()
report["disk_free_bytes"] = shutil.disk_usage("/opt/horizon").free
report["docker_bridge_mtu"] = int(Path("/sys/class/net/docker0/mtu").read_text())
with urllib.request.urlopen("http://127.0.0.1/api/health", timeout=15) as response:
    report["origin_health"] = json.load(response)
Path("/opt/horizon/runtime-verification.json").write_text(json.dumps(report, indent=2) + "\n")
print("SAFE_RUNTIME_SNAPSHOT_WRITTEN")
