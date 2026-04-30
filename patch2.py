import sys, re
sys.stdout.reconfigure(encoding='utf-8')

f = r'c:\Users\user\Downloads\wumpus_huntbot_light\wumpus\github\index.html'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

# ── Fix CSS (use exact marker that exists) ──
css_inject = """
    /* ── Difficulty Buttons ─────────────────────── */
    .diff-btn {
      flex: 1; padding: 6px 0; font-family: 'Space Mono', monospace;
      font-size: 10px; letter-spacing: 1px; cursor: pointer;
      background: rgba(255,255,255,.04); border: 1px solid var(--dim);
      color: var(--muted); border-radius: 6px; transition: all .2s;
    }
    .diff-btn:hover { border-color: var(--accent); color: var(--accent); }
    .diff-btn.active.easy-btn   { border-color: #4ade80; color: #4ade80; background: rgba(74,222,128,.1); }
    .diff-btn.active.normal-btn { border-color: var(--accent); color: var(--accent); background: rgba(99,102,241,.1); }
    .diff-btn.active.hard-btn   { border-color: var(--danger); color: var(--danger); background: rgba(239,68,68,.1); }

    /* ── Particle canvas overlay ─────────────────── */
    #particle-canvas {
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      pointer-events: none; z-index: 9999; display: none;
    }

"""

# Find a reliable CSS anchor
anchor = '    /* ── Overlay'
if anchor in c:
    c = c.replace(anchor, css_inject + anchor, 1)
    print("CSS injected OK")
else:
    # try another anchor
    anchor2 = '#overlay {'
    if anchor2 in c:
        c = c.replace(anchor2, css_inject + anchor2, 1)
        print("CSS injected via fallback anchor")
    else:
        print("CSS ANCHOR NOT FOUND - searching...")
        idx = c.find('</style>')
        if idx >= 0:
            c = c[:idx] + css_inject + c[idx:]
            print("CSS injected before </style>")

# ── Fix sound patches - find actual text in file ──
lines = c.split('\n')
for i, line in enumerate(lines):
    if 'TREASURE SECURED' in line or 'MISSION COMPLETE' in line or 'Arrow fired' in line \
       or 'Fell into a pit' in line or 'Eaten by the Wumpus' in line or 'No safe move' in line:
        print(f"L{i}: {line.strip()[:120]}")

print("---")
with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print("Saved")
