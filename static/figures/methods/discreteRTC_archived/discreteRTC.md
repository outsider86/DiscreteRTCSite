# discrete_rtc_full_figure_revision.md

## Goal
Create a revised full figure for the **Discrete RTC** method, based on the existing RTC-with-flow-matching figure, but with the following conceptual and visual changes.

The new figure should keep the **same overall layout** as the current composed figure:

- large **main figure on the left**
- three **supporting subfigures on the right**
  - top-right: one rectangular subfigure
  - bottom-left: one small subfigure
  - bottom-right: one small subfigure

The figure should remain clean, academic, and publication-style.

---

## Global title change
Change the left main title from:

- `RTC with Flow-matching Head`

to:

- `RTC with Discrete Diffusion Head`

Keep the title large, bold, centered above the left main figure, and in the same general style as the existing figure.

---

# 1. Left main figure revision

## Keep the same overall structure
Keep the same main layout and annotations as the current left figure:

- `Before Inference` on the left
- downward arrow with `\Pi_GDM`
- `After Inference` on the left
- the same two vertical dashed separators
- the same bottom region annotations:
  - `Inference Delay`
  - `Intermediate Region`
  - `Execution Horizon`
- the same bracket structure and same overall spatial arrangement

Only change the **internal representation of each action**.

---

## Replace each action cell with a 3x3 token grid
Previously, each action was represented by one solid square.

Now, each action should be represented as:

- one larger square cell
- containing a **3x3 grid of small square tokens**
- each small square represents one **action token**

So the full action chunk is still a **1x8 horizontal strip of actions**, but each action is internally visualized as a **3x3 token patch**.

### Important
- keep the outer action cells aligned as before
- each action cell should still read as one time step / one action
- inside each action cell, clearly show the 3x3 tokenization

---

## Before Inference row
The top chunk should now show token-level masking / unmasking.

### Action-level structure
Keep the same three temporal regions as before:

1. left region: trusted prefix
2. middle region: partially revealed intermediate region
3. right region: fully masked future region

### Token coloring semantics
Use:
- **green** = unmasked token
- **yellow** = masked token

No gradients inside one token.
Each token should be either green or yellow.

### Prefix actions
For the first two actions:
- all 9 tokens are unmasked
- show them as **fully green 3x3 grids**

This corresponds to fully trusted prefix actions.

### Intermediate region actions
For the middle actions:
- show **partially unmasked 3x3 grids**
- some tokens are green, some are yellow
- these actions should visually indicate progressive partial unmasking

Important:
- do not use random scattered patterns that look noisy or messy
- use a structured progressive reveal pattern
- for example, each later action in the intermediate region can contain more green tokens than the previous one, or vice versa depending on the intended direction
- the key message is: these actions are **partially unmasked**, not fully known and not fully masked

### Final region actions
For the final actions:
- all 9 tokens are masked
- show them as **fully yellow 3x3 grids**

This corresponds to fully masked future actions.

---

## After Inference row
The bottom chunk keeps the same layout as before, but again each action is now a 3x3 token grid.

For every action in the bottom row:
- all 9 tokens should be green
- every action becomes a **fully unmasked 3x3 grid**

This visually communicates that inference completes the entire token chunk.

---

## Main figure styling
- keep the same minimal publication style
- same light background
- same dashed vertical separators
- same bracket and text layout under the main figure
- same arrow position and general scale
- token grids should be clean and geometric
- thin internal token borders are allowed if needed for readability

---

# 2. Top-right subfigure revision

## Purpose
This subfigure should replace the previous comparison-style panel.

Now it should communicate that **discrete diffusion naturally treats inpainting as part of pre-training**, and therefore does **not require extra fine-tuning**.

---

## Remove the old split structure
Remove:
- the internal left/right split
- the vertical dashed divider inside this subfigure
- the comparison between `(a) Pre-training` and `(b) Inference / Fine-tuning`

Instead, create **one single denoising process panel**.

---

## Panel title
At the top-left of this subfigure, use:

- **(a) Inpainting as Pre-training**

This is the new title for this panel.

Do not use:
- `(b) Inference / Fine-tuning`
- any internal split titles

---

## Core visual
Use one simple denoising pipeline, similar in spirit to the main figure but smaller.

### Structure
- one top action chunk
- one downward arrow
- one bottom action chunk

### Action representation
Again use the **3x3 token grid per action** representation.

You do not need 8 actions here if space is tight, but keeping the same 1x8 strip is preferred for consistency.

### Top chunk
The top chunk should start from a **random masking pattern**:
- each action is a 3x3 token grid
- across the full chunk, tokens are randomly masked/unmasked
- green = visible/unmasked
- yellow = masked

Important:
- this should look like a generic discrete diffusion masking pattern
- it should **not** look like the RTC structured prefix-middle-suffix pattern
- it should look like a random masked training input

### Bottom chunk
The bottom chunk should be:
- fully green 3x3 token grids for all actions
- representing full denoising / complete token recovery

---

## Right-side text cues
On the right side of this subfigure, place two small clean text bullets or numbered short lines:

1. `Inpainting as pre-training`
2. `Fine-tuning Free`

These should be:
- small
- clean
- paper-style
- aligned vertically
- placed on the right side of the panel without cluttering the denoising pipeline

This text is important and should be clearly readable.

---

# 3. Bottom-left subfigure revision

## Title
Change the title from:

- `Guidance Design`

to:

- **Natural Guidance Scale**

Use panel label:
- **(b) Natural Guidance Scale**

---

## Y-axis label change
Change the y-axis label from:

- `Guidance Weight`

to:

- `Num of Unmasked Tokens`

---

## Plot meaning
This subfigure should now show that the guidance scale in discrete diffusion is naturally determined by the number of revealed tokens, rather than by a hand-crafted decay curve.

### Preferred curve / shape
You can keep the same general compact coordinate-plot style, but revise the plotted trend so it matches token-unmasking semantics.

A good choice is:
- a monotonic increasing step-like or smooth increasing curve from low to high
- representing that the number of unmasked tokens naturally increases during denoising

This should feel more natural than the previous hand-designed decay curve.

### Style
- small coordinate plot
- minimal
- no unnecessary decorations
- thin axes
- publication style
- keep it visually compatible with the old panel size

---

# 4. Bottom-right subfigure revision

## Title
Change the title from:

- `Inference Cost`

to:

- **Lower Inference Cost**

Use panel label:
- **(c) Lower Inference Cost**

---

## Change the bar chart direction
Previously this panel showed RTC being more expensive.

Now it should show the opposite message:

- **Original** inference cost = `1`
- **RTC** inference cost = `0.4x`

So the right bar should be **lower**, not higher.

### Bar heights
- left bar: `Original` = 1
- right bar: `RTC` = 0.4

### Arrow annotation
Place a small arrow indicating the reduction from left to right.

Recommended:
- a small downward arrow or a descending curved arrow between the bars

Add text near the arrow:

- `0.4x`

This should indicate the new relative cost.

---

## Axis label
Keep the y-axis as inference-time related, for example:
- `Inference Time`

This can remain unchanged unless visual balance requires slight wording adjustment.

---

## Color suggestion
Use:
- `Original`: neutral gray
- `RTC`: green

This helps emphasize that the new method is the efficient one.

---

# 5. Global consistency requirements

## Keep the same overall page composition
Do not redesign the page from scratch.

Keep:
- left large main figure
- right top rectangular subfigure
- right bottom two smaller subfigures
- same overall proportions and alignment style as the current reference layout

---

## Keep the same general palette
Use the same overall palette family as the existing figure:
- green for valid / revealed / completed tokens
- yellow for masked tokens
- gray for axes, borders, and dividers
- soft light background

---

## Typography
- same paper-style typography
- all panel titles should be bold and readable
- main title should remain the most visually prominent text
- subtitles and axis labels should be smaller and consistent

---

## What the full revised figure should communicate
A reader should immediately understand:

1. **Discrete RTC operates on tokenized actions**
   - each action is represented as a 3x3 token grid

2. **Before inference, tokens have structured mask status**
   - prefix fully visible
   - middle partially unmasked
   - future fully masked

3. **After inference, all action tokens are fully unmasked**

4. **Inpainting is naturally covered by discrete diffusion pre-training**
   - no extra fine-tuning is required

5. **Guidance scale is natural**
   - driven by token unmasking progression

6. **Inference cost is lower**
   - reduced from `1` to `0.4x`

---

## What to avoid
- do not revert to one solid color square per action
- do not keep the old top-right split-panel comparison
- do not keep the old guidance-weight decay semantics
- do not keep the old higher-cost bar chart
- do not make token patterns visually messy
- do not overcrowd the subfigures with extra captions
- do not change the global layout too much

---

## Desired impression
The revised figure should look like a clean, direct, publication-quality upgrade of the existing flow-matching figure into a discrete-diffusion version, while preserving layout familiarity and making the new advantages visually obvious.