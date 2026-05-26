# Quantera Demo Video Pipeline

A Remotion-based pipeline that produces a ~3.5 minute looping demo video showcasing 8 queries against the Quantera system. Designed to run on the demo table after the live presentation.

## Structure

```
demo_video/
├── tapes/              # VHS tape scripts (one per query)
├── recordings/         # Terminal recordings (MP4) — produced by VHS
├── remotion/           # Remotion project (React/TypeScript)
│   ├── src/
│   │   ├── index.ts
│   │   ├── Root.tsx
│   │   ├── QuanteraDemo.tsx
│   │   ├── queries.ts          # Metadata for all 8 queries
│   │   └── components/
│   │       ├── Intro.tsx
│   │       ├── Outro.tsx
│   │       ├── LabelCard.tsx
│   │       └── ClipFrame.tsx
│   ├── public/
│   │   └── recordings -> ../../recordings  (symlink)
│   └── out/                    # Rendered MP4 lands here
└── record_all.sh       # Runs VHS on all 8 tapes
```

## End-to-end workflow

### Step 1 — Prep the demo system

```bash
cd quantera
make demo-prep                          # Reset database + pre-index documents
# Start FreeLLMAPI on localhost:3001 in a separate terminal
curl http://localhost:3001/v1/models    # Verify it responds
```

### Step 2 — Record terminal sessions (VHS)

VHS uses headless Chromium so it has to run on a real desktop, not in a sandboxed container.

```bash
cd quantera/demo_video
./record_all.sh                         # Records all 8 tapes to recordings/
ls -lh recordings/                      # Should show 8 MP4 files
```

If one query produces a weird/incomplete answer, just re-run that one tape:
```bash
vhs tapes/02_compare_margins.tape
```

### Step 3 — Render the composed video (Remotion)

```bash
cd quantera/demo_video/remotion
npm install                             # First time only
npm run build                           # Render to out/quantera-demo.mp4
```

The render takes a few minutes. The final MP4 is at `out/quantera-demo.mp4`.

### Step 4 — Iterate visually (optional)

```bash
cd quantera/demo_video/remotion
npm start                               # Opens Remotion Studio in browser
```

Live-edit components in `src/` and see changes instantly. Useful for tweaking colors, timing, label text.

## The 8 queries

| # | Category | Label | What it demonstrates |
|---|----------|-------|----------------------|
| 1 | STRENGTH | Precise data lookup | Single-document fact retrieval |
| 2 | STRENGTH | Multi-document comparison | Cross-document analysis |
| 3 | STRENGTH | Structured KPI extraction | KPI agent routing + JSON-style output |
| 4 | STRENGTH | Portfolio-wide aggregation | All 4 documents synthesised |
| 5 | STRENGTH | Executive briefing | Briefing agent routing |
| 6 | ROBUSTNESS | Out-of-scope query | Handles companies not in portfolio |
| 7 | ROBUSTNESS | Missing information | No hallucination when data isn't present |
| 8 | STRENGTH | Surfaces critical details | Highlights negative FCF |

## Modifying the video

**Change a query** — edit the `.tape` file in `tapes/`, re-run that tape, then re-render.

**Change the label/description** — edit `remotion/src/queries.ts`, no re-recording needed, just re-render.

**Change visual design** — edit components in `remotion/src/components/`. Use `npm start` for live preview.

**Change pacing** — adjust `clipDurationSeconds` per query in `queries.ts`, or `LABEL_CARD_DURATION_SECONDS` / `INTRO_DURATION_SECONDS` etc. for global pacing.

## Prerequisites

- VHS (Charmbracelet) — `~/.local/bin/vhs`
- ttyd (VHS dependency) — `~/.local/bin/ttyd`
- ffmpeg — system package
- Node 18+ and npm — for Remotion
- Quantera demo data prepared (`make demo-prep`)
- FreeLLMAPI running on `localhost:3001`
