import sys
sys.stdout.reconfigure(encoding='utf-8')

f = r'c:\Users\user\Downloads\wumpus_huntbot_light\wumpus\github\index.html'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

patches = [
    (
        'state.log.push({ msg: "\U0001f3c6 TREASURE SECURED! +1000", type: "ok" });',
        'state.log.push({ msg: "\U0001f3c6 TREASURE SECURED! +1000", type: "ok" }); playSound(\'gold\'); goldBurst();'
    ),
    (
        'state.log.push({ msg: "\U0001f389 MISSION COMPLETE! Agent escaped with treasure!", type: "ok" });',
        'state.log.push({ msg: "\U0001f389 MISSION COMPLETE! Agent escaped with treasure!", type: "ok" }); playSound(\'escape\');'
    ),
    (
        'state.log.push({ msg: `\U0001f3f9 Arrow fired! Wumpus at (${wr},${wc}) eliminated! -10`, type: "warn" });',
        'state.log.push({ msg: `\U0001f3f9 Arrow fired! Wumpus at (${wr},${wc}) eliminated! -10`, type: "warn" }); playSound(\'arrow\');'
    ),
    (
        'state.log.push({ msg: "\u26a0 No safe move available. Agent is stuck.", type: "err" });',
        'state.log.push({ msg: "\u26a0 No safe move available. Agent is stuck.", type: "err" }); playSound(\'stuck\');'
    ),
    (
        'state.log.push({ msg: `\U0001f480 Fell into a pit at (${nr},${nc})!`, type: "err" });',
        'state.log.push({ msg: `\U0001f480 Fell into a pit at (${nr},${nc})!`, type: "err" }); playSound(\'death_pit\');'
    ),
    (
        'state.log.push({ msg: `\U0001f480 Eaten by the Wumpus at (${nr},${nc})!`, type: "err" });',
        'state.log.push({ msg: `\U0001f480 Eaten by the Wumpus at (${nr},${nc})!`, type: "err" }); playSound(\'death_wumpus\');'
    ),
]

for old, new in patches:
    if old in c:
        c = c.replace(old, new, 1)
        print(f"OK: {old[:60]}")
    else:
        print(f"MISS: {repr(old[:70])}")

# Also patch stench/breeze sound into encode_percepts
old_stench = 'if (cell.stench) {\n        if (!kb.stenches.includes(key(r, c))) kb.stenches.push(key(r, c));'
new_stench = 'if (cell.stench) {\n        playSound(\'stench\');\n        if (!kb.stenches.includes(key(r, c))) kb.stenches.push(key(r, c));'
if old_stench in c:
    c = c.replace(old_stench, new_stench, 1)
    print("Stench sound OK")
else:
    print("Stench MISS")

old_breeze = 'if (cell.breeze) {\n        if (!kb.breezes.includes(key(r, c))) kb.breezes.push(key(r, c));'
new_breeze = 'if (cell.breeze) {\n        playSound(\'breeze\');\n        if (!kb.breezes.includes(key(r, c))) kb.breezes.push(key(r, c));'
if old_breeze in c:
    c = c.replace(old_breeze, new_breeze, 1)
    print("Breeze sound OK")
else:
    print("Breeze MISS")

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print("\nDone. Saved.")
