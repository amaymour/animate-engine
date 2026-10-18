# Animate Engine — 2D YouTube Animations on GitHub Actions

Dashboard + CI pipeline that turns a text topic into a high-quality 2D animation
(video) using Manim + ffmpeg. GitHub runners do the heavy lifting; your laptop
only runs the small dashboard.

## Quick start

```bash
cd /root/animate-engine
pip install -r requirements.txt
python app.py
# open http://localhost:8000
```

## How it works

1. You type a topic + pick a style in the local dashboard.
2. The dashboard generates a Manim scene script and dispatches
   `.github/workflows/render.yml` on GitHub Actions via the `gh` CLI.
3. GitHub runners install ffmpeg + Manim, render the animation (high quality),
   post-process it with ffmpeg (1080p or 1080x1920 Shorts), and upload the MP4
   as a workflow artifact.
4. The dashboard polls the run status and lets you download the finished video.

## Animation styles

- `stick_figure` — talking-head style stick figure
- `whiteboard` — whiteboard explainer with box + label
- `kinetic_typography` — words flying in one by one
- `motion_graphics` — shapes scaling, shifting, rotating
- `puppet` — simple cutout puppet walking across screen
- `infographic` — animated bar chart
- `background_loop` — rotating rings / ambient loop
- `vertical_shorts` — 1080x1920 Shorts-safe animation

## Requirements

- `gh` CLI authenticated (`gh auth login`) — used to trigger workflows.
- A GitHub repo where this code lives with Actions enabled.
- Python 3.10+ locally for the dashboard.

## One-time repo setup

```bash
gh repo create animate-engine --public --source . --remote origin --push
gh workflow run render.yml  # test dispatch
```

Then run `python app.py` and generate animations from the browser.
