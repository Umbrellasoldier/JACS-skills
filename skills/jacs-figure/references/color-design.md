# Light, comfortable color / 淡亮配色

This palette implements the user's preference. The study supports light-fill/strong-edge
patterns (N03, N13, N17, N32), but does not establish a unique JACS color scheme or an
objective universal measure of visual comfort.

| Role | Blue 蓝 | Apricot 杏 | Teal 青绿 | Lavender 淡紫 | Rose 玫瑰 | Gold 米金 |
|---|---|---|---|---|---|---|
| Fill / marker face | `#A8CEE8` | `#F3C8A8` | `#A4D6C8` | `#CBBDE4` | `#EDC0CF` | `#E8DCA9` |
| Line / outline | `#4E86AF` | `#B98255` | `#428F80` | `#8873AB` | `#B6798D` | `#A48F45` |

Use **blue + apricot** for a clean two-group comparison, **blue + apricot + teal** for three,
or **teal + lavender** for paired chemical hosts. Keep a method's mapping stable across the
manuscript. Six available colors are not an invitation to use all six in each panel.
Prefer one color plus neutral reference for a single question. Use charcoal `#303C4B` for
text, gray `#74808C` for axes, and faint gray `#DCE3E9` for guides.

Pale fills cover area; medium lines carry precise positions. Small pale marks need a stronger
edge. Do not use pale yellow for small text, white text on a pale bar, excessive transparency
on thin lines, or washed-out axes. Keep light backgrounds white rather than tinting every
panel. Bands may use low-opacity fills, but data lines and markers remain legible.

Quantitative color has a different job: use the supplied sequential blue map for ordered
magnitudes and the blue–neutral–apricot map for meaningful negative/positive deviations.
Give quantity, units, limits and center. Keep absent cells gray with an explicit missing
label; do not interpolate a fake value or replace it by zero. Colorbar limits must not
silently clip data. A diverging map is not required just because two groups are compared.

Check **the actual rendered chart**, not only palette swatches: grayscale, protan/deutan
and tritan simulations, small-size reading and white-background line visibility. The
six hues can become similar under altered color vision, especially in dense overlapping
marks. Shapes, open fills, dashes, direct labels or facets are essential. Simulations are
model-based previews, not certification of accessibility for every reader or display.
The optional `preview_color.py` creates review images without changing the scientific data.
