# AR Business Card — test build

Free, no-app WebAR: point a phone camera at a card, a gaussian splat appears
in place. Runs in Safari (iOS) and Chrome (Android) — no download required.

**Stack (all free/open source):**
- [MindAR](https://github.com/hiukim/mind-ar-js) — image tracking, runs entirely client-side
- [@mkkellogg/gaussian-splats-3d](https://github.com/mkkellogg/GaussianSplats3D) — Three.js-based gaussian splat renderer
- Three.js — glue between the two
- No backend, no build step — it's a static HTML page, loads its libraries from CDN

Right now this repo runs on **two placeholders** so we can prove the pipeline
works before committing real assets:
1. The AR target is MindAR's own public sample card (not your business card yet).
2. The splat is a generated rainbow point-cloud (`assets/placeholder.splat`), not a real capture.

---

## 1. Test it locally right now (with placeholders)

You need a local web server (camera access requires either `localhost` or HTTPS —
opening `index.html` directly as a `file://` URL won't work).

```bash
cd ar-business-card
python3 -m http.server 8080
```

Then on the **same computer**, open `http://localhost:8080` in Chrome — you
should see a camera permission prompt and a "Looking for target…" status.
To trigger it: open
https://cdn.jsdelivr.net/gh/hiukim/mind-ar-js@1.0.0/examples/image-tracking/assets/card-example/card.png
on a second screen or printed out, and point your camera at it. You should
see a small rainbow point-cloud hovering above it — that's the placeholder
splat rendering, anchored to the tracked image.

**Note:** testing on your *phone* requires HTTPS (a plain `http://<your-ip>`
won't get camera permission on most mobile browsers). Easiest options once
you're happy with local testing:
- Deploy to GitHub Pages / Netlify / Vercel (all free, all give you HTTPS automatically) — see step 4.
- Or tunnel your local server with a tool like `ngrok` / `cloudflared` for quick phone testing before deploying properly.

---

## 2. Swap in your real business card as the AR target

MindAR needs your card image "compiled" into a `.mind` target file (this is
what makes tracking reliable — it's not just the raw image).

1. Go to MindAR's free browser-based compiler: https://hiukim.github.io/mind-ar-js-doc/tools/compile
2. Upload a clean, high-contrast image of your card artwork (avoid large
   plain/blank areas — the compiler needs visual detail to track against).
3. Download the resulting `card.mind` file, drop it into `assets/` here.
4. In `index.html`, change:
   ```js
   const TARGET_SRC = "https://cdn.jsdelivr.net/gh/hiukim/mind-ar-js@1.0.0/examples/image-tracking/assets/card-example/card.mind";
   ```
   to:
   ```js
   const TARGET_SRC = "./assets/card.mind";
   ```

---

## 3. Swap in a real gaussian splat

Options, in order of least to most effort:

- **Splat.js** (Arrival.Space) — trains a gaussian splat *from photos, entirely
  in your browser tab*, no upload/account needed. Good first real capture to try.
- **Polycam** or **KIRI Engine** apps (free tier) — capture a walk-around on
  your phone, export as `.splat` or `.ply`.
- Reuse one of Kyal's existing gaussian splat captures if there's already
  usable output from the projection-mapping demo location.

Once you have a `.ply` or `.splat` file:
1. Drop it into `assets/` (e.g. `assets/card-splat.ply`).
2. In `index.html`, change:
   ```js
   const SPLAT_SRC = "./assets/placeholder.splat";
   ```
   to point at your real file, e.g. `"./assets/card-splat.ply"`.
3. You may need to tweak `scale` / `position` in the `addSplatScene()` call
   so the splat sits sensibly relative to the card size — real captures are
   at whatever scale they were shot at, unlike our tuned placeholder.

---

## 4. Deploy (free hosting with HTTPS)

Easiest: **GitHub Pages**
```bash
# from inside ar-business-card/
git init
git add .
git commit -m "AR business card test"
# push to a new GitHub repo, then enable Pages on the repo (Settings > Pages > deploy from main branch)
```
Or drag-and-drop the folder into **Netlify Drop** (netlify.com/drop) for an
instant HTTPS link with zero setup — good for quick phone testing.

---

## 5. Performance check before printing anything

Live gaussian splat rendering is heavier than a flat video. Before committing
to a print run:
- Test on a **recent iPhone** and a **mid-range Android**, not just your dev machine.
- Watch for load time and frame rate once the splat appears.
- **Fallback plan** if performance is shaky on older/budget phones: bake the
  splat into a short orbit video instead of rendering it live — still reads
  as "real captured 3D work," just less interactive.

---

## Open items (see ClickUp task)
- [ ] Compile real card art as `.mind` target
- [ ] Generate/select real splat capture
- [ ] Test across a real device spread
- [ ] Decide QR-first vs. direct scan flow for the final card
- [ ] Deploy to permanent hosting
