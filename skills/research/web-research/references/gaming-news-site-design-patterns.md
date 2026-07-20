# Gaming News Website Design Patterns

Researched: IGN, Polygon, Kotaku, Rock Paper Shotgun (July 2026)

## Universal Section Structure (all 4 sites)

| Section | Description | Frequency |
|---------|-------------|-----------|
| **Dark Navbar** | Logo + category links + trending sub-nav, fixed top | 4/4 |
| **Hero / Featured** | 1–3 large featured articles with hero images | 4/4 |
| **Latest News** | Chronological responsive card grid (6–12 articles) | 4/4 |
| **Trending / Popular** | Most-read or editor-picked highlights | 3/4 |
| **Category Sections** | Reviews, Guides, Previews, Features — each with its own grid | 4/4 |
| **Sidebar** | Desktop only (~300px), trending/ads/newsletter; hidden mobile | 3/4 |
| **Footer** | About, Contact, Social icons, Copyright | 4/4 |

## Layout Patterns

- **Responsive CSS Grid**: 1 col → 2 cols → 3–4 cols as viewport widens
- **Card component**: image + category badge + title + excerpt + date/author
- **Hero banner**: Single large feature or 2–3 featured stories in a grid
- **Section-based grouping**: Each content category gets titled section with grid of cards
- **Typical homepage**: 50–60+ article cards on the page

## Color Schemes

| Site | Background | Text | Accent | Dark Elements |
|------|-----------|------|--------|---------------|
| IGN | White #fff, Light #f6f8f7 | Dark #41495a | **Red #bf1313** | Nav/header #181c25 |
| Polygon | White #fff, Light #f2f2f2 | Dark #333, Gray #777 | **Magenta #e90c59** | #181818, #101010 |
| Kotaku | White #fff | Black #000, Gray #3C434A | **Red #dc3232** | Navbar bg #171717 |
| RPS | White #fff, Light #f3f6f8 | Black #000, Gray #333 | **Teal #00866b** | Minimal dark |

**Universal pattern**: Dark nav/header → white/light content → single vibrant accent color.

## Recommended Palette for Student Projects

- Dark nav: `#1a1a2e` or `#0f0f0f`
- Content bg: `#ffffff` or `#f8f9fa`
- Accent: `#e94560` (red-pink) or `#7c3aed` (purple) — gaming-appropriate
- Text: `#1a1a1a` (headings), `#6b7280` (meta)
- Cards: white with subtle border or shadow
