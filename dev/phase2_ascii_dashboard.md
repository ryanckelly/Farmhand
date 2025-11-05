# Phase 2: ASCII Dashboard Template

**Status:** Not Started
**Estimated Time:** 2-3 hours
**Dependencies:** Phase 1 complete

## Goals

- Create beautiful ASCII/terminal-style HTML dashboard
- No JavaScript, no frameworks - pure HTML/CSS
- Render data from `dashboard_state.json`

## Tasks

### 2.1 ASCII Art Components
- [ ] Design progress bar renderer (░ and █ characters)
- [ ] Design sparkline chart renderer (▁▂▃▄▅▆▇█)
- [ ] Design box drawing characters (╔═╗ ║ ╚═╝)
- [ ] Create emoji/symbol system (🔥 ❄️ 📈 📉)

### 2.2 HTML Template Creation
- [ ] Create basic HTML structure
- [ ] Add terminal-style CSS (green on black)
- [ ] Set up monospace font rendering
- [ ] Design responsive layout for terminal aesthetic

### 2.3 Template Renderer
- [ ] Build simple string template system (no Jinja2)
- [ ] Create placeholder replacement logic
- [ ] Add dynamic progress bar generation
- [ ] Add dynamic sparkline generation

### 2.4 Layout Sections
- [ ] Header with timestamp and game date
- [ ] Unlocks section with progress bars
- [ ] Financials section with trends
- [ ] Momentum section (placeholder for Phase 3)
- [ ] Footer with generation info

### 2.5 Testing & Polish
- [ ] Test rendering with sample data
- [ ] Verify ASCII characters display correctly
- [ ] Check alignment and spacing
- [ ] Test in multiple browsers

## Technical Details

### ASCII Components

```python
def generate_progress_bar(percent, width=20):
    """
    Generate: [████████████░░░░░░░░] 60%
    """
    filled = int(percent * width)
    return f"[{'█' * filled}{'░' * (width - filled)}] {int(percent*100)}%"

def generate_sparkline(values, height=8):
    """
    Generate: ░░▁▂▃▄▅▆▇█
    """
    chars = ' ░▁▂▃▄▅▆▇█'
    # Normalize values to 0-8 range
    # Map to chars

def generate_box_section(title, content, width=65):
    """
    Generate:
    ╔═══════════════════╗
    ║  TITLE           ║
    ╠═══════════════════╣
    ║  content         ║
    ╚═══════════════════╝
    """
```

### HTML Template Structure

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Stardew Valley Focus Flow Dashboard</title>
    <style>
        body {
            background: #1e1e1e;
            color: #00ff00;
            font-family: 'Courier New', 'Consolas', monospace;
            padding: 20px;
            margin: 0;
        }
        pre {
            line-height: 1.2;
            margin: 0 auto;
            max-width: 70ch;
        }
        .hot { color: #ff6b6b; font-weight: bold; }
        .cold { color: #74c0fc; font-weight: bold; }
        .rising { color: #51cf66; }
        .falling { color: #ffd43b; }
        .header { color: #ffd700; }
    </style>
</head>
<body>
    <pre>{{DASHBOARD_CONTENT}}</pre>
</body>
</html>
```

### Example Output

```
╔═══════════════════════════════════════════════════════════════╗
║  STARDEW VALLEY FOCUS FLOW DASHBOARD                         ║
║  Generated: 2025-11-03 18:45:23 | Fall 26, Year 2            ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  UNLOCKS PROGRESS                                             ║
║  ────────────────                                             ║
║  Community Center  [████████████████░░░░] 97% (30/31)        ║
║  Museum Collection [█████████████░░░░░░░] 67% (64/95)        ║
║  Cooking Recipes   [██████░░░░░░░░░░░░░░] 30% (22/74)        ║
║  Max Friendships   [██░░░░░░░░░░░░░░░░░░] 09% (3/32)         ║
║  Master Skills     [████████████████░░░░] 80% (4/5)          ║
║                                                               ║
║  FINANCIAL TRENDS                                             ║
║  ────────────────                                             ║
║  Current Balance:  517,664g                                   ║
║  Daily Average:    40,160g/day ↑ 23%                          ║
║  30-Day Trend:     ░░▁▂▃▄▅▆▇█ (accelerating)                ║
║  Best Day:         158,733g on Fall 7, Year 2                 ║
╚═══════════════════════════════════════════════════════════════╝
```

## Completion Criteria

- [ ] `dashboard.html` generates successfully
- [ ] All ASCII characters render correctly
- [ ] Layout is clean and aligned
- [ ] Colors are readable on dark background
- [ ] Dashboard opens in browser automatically

## Notes

- Use `<pre>` tags to preserve ASCII art formatting
- Keep CSS minimal and inline
- Test with actual data from `dashboard_state.json`
- Ensure monospace alignment is perfect

---

**Status:** ⏳ Pending
**Last Updated:** 2025-11-03
