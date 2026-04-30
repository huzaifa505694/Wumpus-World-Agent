import sys, re
sys.stdout.reconfigure(encoding='utf-8')

f = r'c:\Users\user\Downloads\wumpus_huntbot_light\wumpus\github\index.html'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

print("File loaded, length:", len(c))

# ── 1. ADD CSS for difficulty buttons + particle canvas ──
css_inject = """
    /* ── Difficulty Buttons ─────────────────────── */
    .diff-btn {
      flex: 1; padding: 6px 0; font-family: 'Space Mono', monospace;
      font-size: 10px; letter-spacing: 1px; cursor: pointer;
      background: rgba(255,255,255,.04); border: 1px solid var(--dim);
      color: var(--muted); border-radius: 6px; transition: all .2s;
    }
    .diff-btn:hover { border-color: var(--accent); color: var(--accent); }
    .diff-btn.active.easy-btn { border-color: #4ade80; color: #4ade80; background: rgba(74,222,128,.1); }
    .diff-btn.active.normal-btn { border-color: var(--accent); color: var(--accent); background: rgba(99,102,241,.1); }
    .diff-btn.active.hard-btn { border-color: var(--danger); color: var(--danger); background: rgba(239,68,68,.1); }

    /* ── Particle canvas overlay ─────────────────── */
    #particle-canvas {
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      pointer-events: none; z-index: 9999; display: none;
    }
"""
c = c.replace('    /* ── Overlay', css_inject + '    /* ── Overlay')
print("1. CSS injected:", '.diff-btn' in c)

# ── 2. ADD PARTICLE CANVAS element after <body> ──
c = c.replace('<div id="start-screen"', '<canvas id="particle-canvas"></canvas>\n  <div id="start-screen"')
print("2. Canvas element injected:", 'particle-canvas' in c)

# ── 3. ADD DIFFICULTY UI BLOCK before the sep+btn-init ──
diff_html = """        <div class="ctrl-section" style="margin-top:4px;">
          <div class="ctrl-label">\u2694\ufe0f Difficulty</div>
          <div class="ctrl-row" style="gap:6px;">
            <button class="diff-btn easy-btn active" id="diff-easy" onclick="setDifficulty('easy')">Easy</button>
            <button class="diff-btn normal-btn" id="diff-normal" onclick="setDifficulty('normal')">Normal</button>
            <button class="diff-btn hard-btn" id="diff-hard" onclick="setDifficulty('hard')">Hard</button>
          </div>
          <div id="diff-desc" style="font-size:9px;color:#6b7280;margin-top:4px;font-family:'Space Mono',monospace;letter-spacing:.5px;">\u2b50 Relaxed: 4\xd74 grid, 2 pits, slow speed</div>
        </div>
"""

old_sep = '        <div class="sep"></div>\n        <button class="btn btn-init" id="btn-init">'
c = c.replace(old_sep, diff_html + old_sep, 1)
print("3. Difficulty HTML injected:", 'diff-easy' in c)

# ── 4. ADD ALL JS before </script> ──
js_code = r"""
    // ─────────────────────────────────────────────────
    // DIFFICULTY SYSTEM
    // ─────────────────────────────────────────────────
    let CURRENT_DIFFICULTY = 'easy';
    const DIFFICULTY_PRESETS = {
      easy:   { rows: 4, cols: 4, pits: 2, speed: 900,  label: '\u2b50 Relaxed: 4\xd74 grid, 2 pits, slow speed' },
      normal: { rows: 5, cols: 5, pits: 3, speed: 600,  label: '\u26a1 Standard: 5\xd75 grid, 3 pits, medium speed' },
      hard:   { rows: 7, cols: 7, pits: 5, speed: 300,  label: '\u2620\ufe0f Expert: 7\xd77 grid, 5 pits, fast speed' }
    };

    function setDifficulty(level) {
      CURRENT_DIFFICULTY = level;
      const preset = DIFFICULTY_PRESETS[level];
      document.getElementById('rows').value   = preset.rows;
      document.getElementById('cols').value   = preset.cols;
      document.getElementById('pits').value   = preset.pits;
      document.getElementById('speed').value  = preset.speed;
      document.getElementById('speed-val').textContent = preset.speed + ' ms';
      document.getElementById('diff-desc').textContent = preset.label;
      // update button styles
      ['easy','normal','hard'].forEach(d => {
        const btn = document.getElementById('diff-' + d);
        btn.classList.remove('active');
      });
      const activeBtn = document.getElementById('diff-' + level);
      activeBtn.classList.add('active');
      playSound('click');
    }

    // ─────────────────────────────────────────────────
    // SOUND EFFECTS  (Web Audio API — no files needed)
    // ─────────────────────────────────────────────────
    let audioCtx = null;

    function getAudioCtx() {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      return audioCtx;
    }

    function playTone(freq, type, duration, gain, delay = 0) {
      try {
        const ctx = getAudioCtx();
        const osc = ctx.createOscillator();
        const gainNode = ctx.createGain();
        osc.connect(gainNode);
        gainNode.connect(ctx.destination);
        osc.type = type;
        osc.frequency.setValueAtTime(freq, ctx.currentTime + delay);
        gainNode.gain.setValueAtTime(gain, ctx.currentTime + delay);
        gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + duration);
        osc.start(ctx.currentTime + delay);
        osc.stop(ctx.currentTime + delay + duration + 0.05);
      } catch(e) {}
    }

    function playSound(type) {
      switch(type) {
        case 'click':
          playTone(440, 'sine', 0.08, 0.15);
          break;
        case 'step':
          playTone(330, 'triangle', 0.12, 0.1);
          break;
        case 'stench':
          playTone(180, 'sawtooth', 0.25, 0.12);
          playTone(160, 'sawtooth', 0.25, 0.1, 0.1);
          break;
        case 'breeze':
          playTone(800, 'sine', 0.2, 0.07);
          playTone(900, 'sine', 0.2, 0.06, 0.05);
          playTone(700, 'sine', 0.2, 0.05, 0.1);
          break;
        case 'gold':
          // triumphant jingle
          [523, 659, 784, 1047].forEach((f, i) => playTone(f, 'sine', 0.25, 0.18, i * 0.1));
          break;
        case 'escape':
          // victory fanfare
          [392, 523, 659, 784, 1047].forEach((f, i) => playTone(f, 'triangle', 0.3, 0.2, i * 0.08));
          break;
        case 'arrow':
          playTone(1200, 'square', 0.05, 0.15);
          playTone(400,  'square', 0.2,  0.12, 0.05);
          break;
        case 'death_pit':
          [300, 250, 200, 150].forEach((f, i) => playTone(f, 'sawtooth', 0.3, 0.15, i * 0.07));
          break;
        case 'death_wumpus':
          [200, 180, 160].forEach((f, i) => playTone(f, 'sawtooth', 0.4, 0.2, i * 0.1));
          break;
        case 'stuck':
          [300, 280, 260].forEach((f, i) => playTone(f, 'triangle', 0.3, 0.1, i * 0.12));
          break;
      }
    }

    // ─────────────────────────────────────────────────
    // PARTICLE BURST SYSTEM
    // ─────────────────────────────────────────────────
    const particleCanvas = document.getElementById('particle-canvas');
    const pctx = particleCanvas ? particleCanvas.getContext('2d') : null;
    let particles = [];
    let particleAnimId = null;

    function resizeParticleCanvas() {
      if (!particleCanvas) return;
      particleCanvas.width  = window.innerWidth;
      particleCanvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resizeParticleCanvas);
    resizeParticleCanvas();

    function spawnParticles(x, y, count, colors, type = 'confetti') {
      if (!particleCanvas || !pctx) return;
      particleCanvas.style.display = 'block';
      for (let i = 0; i < count; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = 4 + Math.random() * 10;
        particles.push({
          x, y,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed - (type === 'confetti' ? 3 : 0),
          color: colors[Math.floor(Math.random() * colors.length)],
          size: type === 'confetti' ? (4 + Math.random() * 8) : (2 + Math.random() * 5),
          alpha: 1,
          rot: Math.random() * Math.PI * 2,
          rotV: (Math.random() - 0.5) * 0.3,
          shape: type === 'confetti' ? (Math.random() > 0.5 ? 'rect' : 'circle') : 'circle',
          gravity: type === 'confetti' ? 0.25 : 0.15,
          decay: 0.012 + Math.random() * 0.01
        });
      }
      if (!particleAnimId) animateParticles();
    }

    function animateParticles() {
      if (!pctx) return;
      pctx.clearRect(0, 0, particleCanvas.width, particleCanvas.height);
      particles = particles.filter(p => p.alpha > 0.01);
      for (const p of particles) {
        p.x  += p.vx;
        p.y  += p.vy;
        p.vy += p.gravity;
        p.vx *= 0.99;
        p.alpha -= p.decay;
        p.rot += p.rotV;
        pctx.save();
        pctx.globalAlpha = Math.max(0, p.alpha);
        pctx.fillStyle = p.color;
        pctx.translate(p.x, p.y);
        pctx.rotate(p.rot);
        if (p.shape === 'rect') {
          pctx.fillRect(-p.size/2, -p.size/4, p.size, p.size/2);
        } else {
          pctx.beginPath();
          pctx.arc(0, 0, p.size/2, 0, Math.PI*2);
          pctx.fill();
        }
        pctx.restore();
      }
      if (particles.length > 0) {
        particleAnimId = requestAnimationFrame(animateParticles);
      } else {
        particleAnimId = null;
        particleCanvas.style.display = 'none';
      }
    }

    function goldBurst() {
      const cx = window.innerWidth / 2, cy = window.innerHeight / 2;
      const goldColors = ['#fbbf24','#f59e0b','#fcd34d','#fef08a','#ffffff','#facc15'];
      spawnParticles(cx, cy, 180, goldColors, 'confetti');
    }

    function escapeBurst() {
      const cx = window.innerWidth / 2, cy = window.innerHeight / 2;
      const winColors = ['#a78bfa','#6366f1','#818cf8','#c4b5fd','#fbbf24','#34d399','#ffffff'];
      // Burst from multiple points
      spawnParticles(cx, cy, 120, winColors, 'confetti');
      setTimeout(() => spawnParticles(cx - 200, cy + 100, 80, winColors, 'confetti'), 150);
      setTimeout(() => spawnParticles(cx + 200, cy + 100, 80, winColors, 'confetti'), 300);
      setTimeout(() => spawnParticles(cx, cy - 150, 60, winColors, 'confetti'), 200);
    }
"""

c = c.replace('  </script>', js_code + '  </script>')
print("4. JS code injected:", 'setDifficulty' in c)

# ── 5. PATCH applyState to call sounds + bursts ──
# Gold grabbed
c = c.replace(
    'state.log.push({ msg: "\\ud83c\\udfc6 TREASURE SECURED! +1000", type: "ok" });',
    'state.log.push({ msg: "\\ud83c\\udfc6 TREASURE SECURED! +1000", type: "ok" }); playSound(\'gold\');'
)
print("5a. Gold sound patched:", 'playSound(\'gold\')' in c)

# Escape / win
c = c.replace(
    'state.log.push({ msg: "\\ud83c\\udf89 MISSION COMPLETE! Agent escaped with treasure!", type: "ok" });',
    'state.log.push({ msg: "\\ud83c\\udf89 MISSION COMPLETE! Agent escaped with treasure!", type: "ok" }); playSound(\'escape\');'
)
print("5b. Escape sound patched:", 'playSound(\'escape\')' in c)

# Arrow fired
c = c.replace(
    'state.log.push({ msg: `\\ud83c\\udff9 Arrow fired! Wumpus at ($\\{wr},$\\{wc}) eliminated! -10`, type: "warn" });',
    'state.log.push({ msg: `\\ud83c\\udff9 Arrow fired! Wumpus at ($\\{wr},$\\{wc}) eliminated! -10`, type: "warn" }); playSound(\'arrow\');'
)
print("5c. Arrow sound patched:", 'playSound(\'arrow\')' in c)

# Death by pit
c = c.replace(
    'state.log.push({ msg: `\\ud83d\\udc80 Fell into a pit at ($\\{nr},$\\{nc})!`, type: "err" });',
    'state.log.push({ msg: `\\ud83d\\udc80 Fell into a pit at ($\\{nr},$\\{nc})!`, type: "err" }); playSound(\'death_pit\');'
)
print("5d. Pit death sound patched:", 'playSound(\'death_pit\')' in c)

# Death by wumpus
c = c.replace(
    'state.log.push({ msg: `\\ud83d\\udc80 Eaten by the Wumpus at ($\\{nr},$\\{nc})!`, type: "err" });',
    'state.log.push({ msg: `\\ud83d\\udc80 Eaten by the Wumpus at ($\\{nr},$\\{nc})!`, type: "err" }); playSound(\'death_wumpus\');'
)
print("5e. Wumpus death sound patched:", 'playSound(\'death_wumpus\')' in c)

# Stuck
c = c.replace(
    'state.log.push({ msg: "\\u26a0 No safe move available. Agent is stuck.", type: "err" });',
    'state.log.push({ msg: "\\u26a0 No safe move available. Agent is stuck.", type: "err" }); playSound(\'stuck\');'
)
print("5f. Stuck sound patched:", 'playSound(\'stuck\')' in c)

# ── 6. PATCH applyState overlay to call burst effects ──
old_overlay = "document.getElementById('overlay').classList.add('show'); stopAuto();"
new_overlay = "document.getElementById('overlay').classList.add('show'); stopAuto(); if(win){ escapeBurst(); } "
c = c.replace(old_overlay, new_overlay)
print("6. Overlay burst patched:", 'escapeBurst()' in c)

# ── 7. PATCH step sound in log ──
c = c.replace(
    "state.log.push({ msg: `\u2192 Step to ($\\{nr},$\\{nc})`, type: \"step\" });",
    "state.log.push({ msg: `\u2192 Step to ($\\{nr},$\\{nc})`, type: \"step\" }); playSound('step');"
)
print("7. Step sound patched:", "playSound('step')" in c)

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print("\nAll patches applied and saved.")
