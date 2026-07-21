# Visual Elements API Reference

## Capsule Render (Animated Header/Footer)
**URL:** `https://capsule-render.vercel.app/api`

### Parameters
| Param | Values | Description |
|---|---|---|
| `type` | `waving`, `venom`, `rect`, `slice`, `shell`, `wave`, `soft`, `transparent` | Header shape. `waving` most popular. |
| `color` | gradient: `0:HEX,50:HEX,100:HEX` | Gradient stops (0-100 range) |
| `height` | number (px) | Header height. 180-220 for header, 60-100 for footer. |
| `section` | `header`, `footer` | Which section to render |
| `text` | URL-encoded string | Main text (name) |
| `fontSize` | number | Main text size (40-60 typical) |
| `fontColor` | hex color | Text color (ffffff for dark bg) |
| `animation` | `fadeIn`, `blink`, `scale`, `blur`, `bounce` | Entry animation |
| `fontAlignY` | number | Y position of main text (30-40 typical) |
| `desc` | URL-encoded string | Subtitle (role) |
| `descSize` | number | Subtitle size (14-20) |
| `descAlignY` | number | Y position of subtitle (50-60 typical) |
| `descAlign` | `left`, `center`, `right` | Subtitle horizontal align |

### Recommended dark palette
```
color=0:0D1117,50:00D9FF,100:0D1117
```
(dark → cyan → dark gradient)

---

## GitHub Activity Graph
**URL:** `https://github-readme-activity-graph.vercel.app/graph`

### Parameters
| Param | Values | Description |
|---|---|---|
| `username` | string | GitHub username |
| `bg_color` | hex | Background color |
| `color` | hex | Contribution dot color |
| `line` | hex | Line color |
| `point` | hex | Point marker color |
| `area_color` | hex | Area fill under line |
| `area` | `true`, `false` | Show area fill |
| `hide_border` | `true`, `false` | Hide card border |
| `custom_title` | URL-encoded string | Title above graph |

### Recommended dark theme
```
bg_color=0D1117&color=00D9FF&line=00D9FF&point=FFFFFF&area_color=00D9FF&area=true&hide_border=false
```

---

## GitHub Profile Trophy
**URL:** `https://github-profile-trophy.vercel.app/`

### Parameters
| Param | Values | Description |
|---|---|---|
| `username` | string | GitHub username |
| `theme` | `radical`, `dark`, `tokyonight`, etc. | Color theme |
| `no-frame` | `true`, `false` | Remove outer frame |
| `no-bg` | `true`, `false` | Transparent background |
| `column` | number (1-7) | Number of trophy columns |
| `margin-w` | number | Margin between trophies |
| `row` | number | Number of rows |

### Recommended config
```
theme=radical&no-frame=true&no-bg=true&column=7&margin-w=10&row=1
```

---

## Profile Views Counter (komarev)
**URL:** `https://komarev.com/ghpvc/`

### Parameters
| Param | Values | Description |
|---|---|---|
| `username` | string | GitHub username |
| `label` | string | Badge label text |
| `color` | hex (without #) | Badge color |
| `style` | `flat`, `flat-square`, `for-the-badge`, `social` | Badge style |

### Recommended config
```
username={user}&label=Profile%20Views&color=00D9FF&style=for-the-badge
```

---

## Section Divider SVGs

### Animated horizontal line (Platane)
```
https://raw.githubusercontent.com/Platane/dot/541b3d3e44a06724944a2e9b892f6e80c31c113e/art/horizontal.svg
```

Usage: `<img width="100%" src="..." alt="divider" />`

---

## shields.io Badge Styles

| Style | Best for | Example |
|---|---|---|
| `for-the-badge` | Hero section, CTA buttons, section headers | Large, bold, professional |
| `flat-square` | Card headers, category labels | Clean, modern, sharp corners |
| `flat` | Inline references | Small, rounded |
| `social` | Social links (GitHub, Twitter) | Brand-colored with logo |

### Brand colors for common tech
| Tech | Color | Logo key |
|---|---|---|
| n8n | EA4B71 | `n8n` |
| Python | 3776AB | `python` |
| FastAPI | 009688 | `fastapi` |
| PostgreSQL | 4169E1 | `postgresql` |
| Docker | 2496ED | `docker` |
| Telegram | 26A5E4 | `telegram` |
| Linux | FCC624 | `linux` |
| Git | F05032 | `git` |
| OpenAI | 412991 | `openai` |
| Google/Gemini | 4285F4 | `google` |
