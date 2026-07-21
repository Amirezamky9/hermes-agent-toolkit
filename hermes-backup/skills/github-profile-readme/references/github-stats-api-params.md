# GitHub Stats Cards — Parameter Reference

## github-readme-stats (https://github.com/anuraghazra/github-readme-stats)

### API endpoint
```
https://github-readme-stats.vercel.app/api?username={user}&params...
https://github-readme-stats.vercel.app/api/top-langs/?username={user}&params...
```

### Common params

| Param | Values | Default | Description |
|---|---|---|---|
| `username` | string | — | GitHub username (required) |
| `show_icons` | `true`, `false` | `false` | Show repo star/fork icons |
| `theme` | `dark`, `radical`, `merko`, `gruvbox`, `tokyonight`, `onedark`, `cobalt`, `synthwave`, `highcontrast`, `dracula` | — | Color theme |
| `hide_border` | `true`, `false` | `false` | Hide the card border |
| `bg_color` | hex color (e.g. `0D1117`) | theme default | Card background |
| `title_color` | hex color (e.g. `00D9FF`) | theme default | Title text color |
| `icon_color` | hex color | theme default | Icon color |
| `text_color` | hex color | theme default | Body text color |
| `border_color` | hex color | theme default | Border color |
| `hide` | comma-separated (e.g. `stars,commits,prs,issues,contribs`) | — | Hide specific stats from the card |
| `count_private` | `true`, `false` | `false` | Include private contributions |
| `include_all_commits` | `true`, `false` | `false` | Include all years of commits |
| `line_height` | number | — | Card line height |
| `custom_title` | URL-encoded string | — | Override the card title |
| `disable_animations` | `true`, `false` | `false` | Disable animations |
| `locale` | language code (e.g. `cn`, `de`, `fa`) | `en` | Localize card text |

### Top langs specific params

| Param | Values | Default | Description |
|---|---|---|---|
| `layout` | `compact`, `donut`, `donut-vertical`, `pie` | — | Layout style |
| `langs_count` | number (up to 10) | 5 | Number of languages to show |
| `hide_progress` | `true`, `false` | `false` | Hide the progress bars |
| `size_weight` | number | 0.5 | How much repo size matters in language weight calculation |
| `count_weight` | number | 1.0 | How much repo count matters in language weight calculation |

## github-readme-streak-stats (https://github.com/DenverCoder1/github-readme-streak-stats)

### API endpoint
```
https://github-readme-streak-stats.herokuapp.com/?user={user}&params...
```

### Common params

| Param | Values | Default | Description |
|---|---|---|---|
| `user` | string | — | GitHub username (required) |
| `theme` | `dark`, `highcontrast`, `radical`, `merko`, `gruvbox`, `tokyonight`, `onedark`, `cobalt`, `synthwave`, `dracula` | — | Color theme |
| `hide_border` | `true`, `false` | `false` | Hide border |
| `background` | hex color | theme default | Card background |
| `stroke` | hex color | theme default | Border/separator lines color |
| `ring` | hex color | theme default | Ring (current streak circle) color |
| `fire` | hex color | theme default | Fire/flame icon color |
| `currStreakLabel` | hex color | theme default | "Current Streak" label text color |
| `currStreakNum` | hex color | theme default | Current streak number color |
| `sideNums` | hex color | theme default | Side labels (longest streak, total) color |
| `sideLabels` | hex color | theme default | Side label text color |
| `dates` | hex color | theme default | Date text color |
| `locale` | language code | `en` | Localize text |

## Recommended dark theme colors

```
bg_color/background = 0D1117
title_color/ring/fire/currStreakLabel = 00D9FF (cyan accent)
icon_color = 00D9FF
text_color = c9d1d9 (light gray)
stroke = 00D9FF
hide_border = true
```
