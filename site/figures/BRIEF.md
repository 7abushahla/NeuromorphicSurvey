# Figure brief, NeuromorphicSurvey

You are drawing one figure for a TMLR-style survey rendered with the distill
template. The survey is `/Users/hamza/Documents/GitHub/Thesis/NeuromorphicSurvey`.
Its visual sibling, whose conventions you must match exactly, is
`/Users/hamza/Documents/GitHub/QuantizationSurvey/index.html`.

## The one hard rule

Every figure in the sibling survey is **hand-authored inline SVG**. There are no
raster images, no external image files, no JavaScript charting, no build step.
Seventeen figures, seventeen `<svg>` elements written directly into the page.
Produce the same thing. Do not produce a PNG, a matplotlib script, a Mermaid
diagram, or a placeholder.

## Study the sibling first

Before drawing anything, read at least three complete figures out of
`QuantizationSurvey/index.html` so the house style is in your hands rather than
in your imagination. `figure-3` (uniform vs non-uniform quantization) is the
best single model for an axis-and-trace figure. `figure-10` and `figure-15`
carry the class `tax-fig` and are the model for a boxed taxonomy layout.
`figure-17` is the large full-stack figure. Extract them with python rather than
grepping, the lines are very long:

```python
s = open('/Users/hamza/Documents/GitHub/QuantizationSurvey/index.html').read()
i = s.index('<figure class="pfig" id="figure-3"'); print(s[i:s.index('</figure>', i)+9])
```

## Conventions, observed from the sibling

- Wrap the SVG: `<div style="max-width: 720px; margin: 0 auto;"><svg viewBox="0 0 W H" role="img" aria-label="...">...</svg></div>`. Use a `viewBox` and no `width`/`height` attributes, so the figure scales to the column.
- Author in a generous internal coordinate space (the sibling uses roughly 1100x470 for a two-panel figure) and let `max-width` scale it down. Internal font sizes are therefore large, 15px to 25px.
- Label text: `style="font-family:Arial,Helvetica,sans-serif;font-size:24px" fill="#000"`. Panel titles run 25px, axis labels 24px, subscripts and annotations 15px to 18px.
- Math symbols inside a label switch font mid-string with a tspan: `<tspan style="font-family:'Times New Roman',Times,serif;font-style:italic">x</tspan>`, with subscripts as `<tspan dy="6" style="font-size:15px">int</tspan>`. Use this for every variable name (V, θ, t, T, λ).
- Structure strokes are `stroke="#000"` at `stroke-width="2.2"`; data traces are heavier, `stroke-width="4.6"`.
- Arrowheads come from a `<marker>` in `<defs>`. **Give every id in your figure a prefix unique to your figure number** (`f4a`, `f4grad`, ...). All five figures land in one HTML document and a duplicate id silently breaks another figure's arrowheads.
- The accent color is `#D63A2F`. Secondary fills seen in the sibling's boxed figures include `#CCFFCC`, `#CDEBCD`, `#CFE2F3`, `#8fbfef`, `#FFDDA6`, `#F9D4EA`, `#FFFF66`, `#d5dbe2`. Stay inside that palette. Use color to carry meaning, not decoration.
- **No dark mode.** The sibling contains zero `prefers-color-scheme` rules. Draw for black on white.
- Hover affordances are native SVG `<title>` children, which the browser renders as a tooltip, on a `<g>` that also carries an invisible hit rectangle (`fill="#000" opacity="0" pointer-events="all"`). A CSS rule gives that group `cursor: help` and fades in a highlight band. Add tooltips wherever a reader would reasonably ask "what am I looking at", and make the tooltip text a real sentence that teaches something, not a restatement of the label.
- American English. No em dashes in any figure text (the sibling uses `&#8212;` inside tooltips; do not follow it there, use a comma or a full stop instead). Avoid colons in prose.

## What you deliver

Exactly two files, both under
`/Users/hamza/Documents/GitHub/Thesis/NeuromorphicSurvey/site/figures/`.

1. `figure-N.html`, containing the complete `<figure>` element and nothing else.
   Keep the existing `id="figure-N"`. Keep the `<figcaption>` opening with
   `<b>Figure N:</b>`, but **rewrite the caption text**. The current caption is a
   drawing instruction addressed to me and is not publishable prose. Write the
   caption a TMLR reader should see, one to three sentences, describing what the
   figure shows and why it matters. Never write "Redraw of", never name a source
   file, never mention the thesis or a vault.

2. `figure-N.css`, containing only rules scoped with `#figure-N`, or an empty
   file if your figure needs none. I merge these into the page stylesheet myself.
   Do not edit any file outside your two, and in particular do not touch
   `site/sec-02.html` or `tools/clone-template.py`. Four other agents are working
   in parallel and will collide with you.

## Self-check before you finish

- Open your `figure-N.html` in a browser (or render it headless) and actually
  look at it. Text that overflows its box, lines that cross labels, and
  collisions between panels are the failure mode here, and they are invisible if
  you only read the markup.
- Confirm no element falls outside the `viewBox`.
- Confirm every id in the file carries your figure's prefix.
- Confirm the figure still reads at column width, roughly 720 CSS pixels for a
  `l-body` figure and roughly 1100 for `l-page`. If your 24px internal labels
  scale down below about 9 effective pixels, the figure is too dense. Cut
  content rather than shrinking type.

Report back with the viewBox you chose, the layout in two sentences, and
anything you deliberately left out.
