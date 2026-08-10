# SASE Beam Console

A dashboard for exploring synthetic SASE X-ray beam diagnostics,
built to mirror the train/pulse indexed structure used at European
XFEL (XGM pulse energy + spectrometer data). Not real facility data,
built for practicing the analysis and visualization workflow.

## Local development

```bash
pip install numpy
python3 generate_data.py
python3 -m http.server 8000
```

Then open `http://localhost:8000`. The dashboard fetches
`data/sase_data.json`, which `generate_data.py` produces and which is
gitignored (CI regenerates it fresh on every deploy, see below).

## Deployment

Pushes to `main` automatically redeploy via
`.github/workflows/deploy.yml` (GitHub Actions -> GitHub Pages). The
workflow regenerates the dataset on every run, so changing
`generate_data.py` and pushing is enough to update the live site.

One-time setup: repo **Settings > Pages > Source = GitHub Actions**.

## Live playback mode

The dashboard auto-plays by default: steps through every pulse in
acquisition order, updating the spectrum view, sliders, and a
scrolling XGM stream chart each tick. Use the LIVE/PAUSE button and
speed selector to control it; dragging a slider pauses playback and
jumps straight to that shot.