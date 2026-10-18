"""Local dashboard: topic -> GitHub Actions render -> download MP4."""
import os
import subprocess
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Animate Engine Dashboard")

BASE = Path(__file__).parent
STATIC = BASE / "static"
DOWNLOADS = BASE / "static" / "downloads"
DOWNLOADS.mkdir(parents=True, exist_ok=True)

# Change this to your repo if different.
GITHUB_REPO = os.environ.get("GITHUB_REPO", "amaymour/animate-engine")
WORKFLOW = "render.yml"

app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


def gh(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["gh"] + args, capture_output=True, text=True)


@app.get("/", response_class=HTMLResponse)
async def index():
    return (STATIC / "index.html").read_text()


@app.post("/generate")
async def generate(
    request: Request,
    topic: str = Form(...),
    anim_type: str = Form(...),
    duration: str = Form("8"),
    quality: str = Form("high"),
    orientation: str = Form("landscape"),
):
    run_id = str(uuid.uuid4())[:8]
    cmd = [
        "workflow", "run", WORKFLOW,
        "--ref", "main",
        "--repo", GITHUB_REPO,
        "--field", f"topic={topic}",
        "--field", f"anim_type={anim_type}",
        "--field", f"duration={duration}",
        "--field", f"quality={quality}",
        "--field", f"orientation={orientation}",
    ]
    res = gh(cmd)
    if res.returncode != 0:
        return JSONResponse(
            {"ok": False, "error": res.stderr.strip() or res.stdout.strip()},
            status_code=500,
        )

    # gh workflow run prints the run URL on success; parse last line containing run id
    run_url = ""
    for line in res.stdout.splitlines():
        if "actions/runs/" in line:
            run_url = line.strip()
            break

    return JSONResponse({
        "ok": True,
        "run_id": run_id,
        "run_url": run_url,
        "status_url": f"/status/{run_id}",
        "download_url": f"/download/{run_id}",
    })


@app.get("/status/{run_id}")
async def status(run_id: str):
    # We don't map run_id to a real GH run id here; instead we fetch the latest
    # run for this workflow and report its status. Good enough for a single-user
    # dashboard; improve by storing the real run id if needed.
    res = gh(["run", "list", "--repo", GITHUB_REPO, "--workflow", WORKFLOW,
              "--limit", "1", "--json", "status,conclusion,createdAt,url"])
    if res.returncode != 0:
        return JSONResponse({"ok": False, "error": res.stderr.strip()}, status_code=500)
    import json
    try:
        data = json.loads(res.stdout)
    except json.JSONDecodeError:
        return JSONResponse({"ok": False, "error": res.stdout[:500]}, status_code=500)

    if not data:
        return JSONResponse({"ok": True, "status": "queued"})
    run = data[0]
    return JSONResponse({
        "ok": True,
        "status": run.get("status", "unknown"),
        "conclusion": run.get("conclusion"),
        "url": run.get("url"),
    })


@app.get("/download/{run_id}")
async def download(run_id: str):
    # Download latest successful artifact for this workflow.
    res = gh(["run", "list", "--repo", GITHUB_REPO, "--workflow", WORKFLOW,
              "--limit", "1", "--json", "databaseId,status,conclusion"])
    import json
    try:
        data = json.loads(res.stdout)
    except json.JSONDecodeError:
        return JSONResponse({"ok": False, "error": res.stdout[:500]}, status_code=500)

    if not data:
        return JSONResponse({"ok": False, "error": "no runs found"}, status_code=404)
    run = data[0]
    if run.get("conclusion") != "success":
        return JSONResponse({"ok": False, "error": "run not successful yet"}, status_code=400)

    run_db_id = run["databaseId"]
    out_dir = DOWNLOADS / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    dl = gh(["run", "download", str(run_db_id), "--repo", GITHUB_REPO,
             "--dir", str(out_dir), "--name", f"animation-{run_db_id}"])
    if dl.returncode != 0:
        # Try generic download (artifact name may differ slightly)
        dl = gh(["run", "download", str(run_db_id), "--repo", GITHUB_REPO,
                 "--dir", str(out_dir)])
        if dl.returncode != 0:
            return JSONResponse({"ok": False, "error": dl.stderr.strip()}, status_code=500)

    mp4s = list(out_dir.glob("*.mp4"))
    if not mp4s:
        return JSONResponse({"ok": False, "error": "no mp4 found in artifact"}, status_code=500)
    return FileResponse(str(mp4s[0]), media_type="video/mp4", filename="animation.mp4")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
