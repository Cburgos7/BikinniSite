---
phase: quick-260817-s0a
plan: 01
subsystem: ui
tags: [shopify, liquid, theme-settings, swatch, color-mapping]

requires: []
provides:
  - "Owner-editable `swatch_color_map` theme setting (Colors group) for mapping evocative color names to hex codes"
  - "snippets/swatch-color.liquid: case-insensitive, whitespace-tolerant, colon-aware name-to-hex lookup with legacy fallback"
  - "Both product-card and PDP swatch buttons wired to the new snippet"
affects: [collections, pdp, theme-editor]

tech-stack:
  added: []
  patterns:
    - "Shopify textarea theme setting parsed as `Name: #hex` per-line map, split via newline_to_br + split '<br />' (standard Liquid multiline-parsing idiom)"
    - "Reusable inline-safe Liquid snippet convention: full {%- -%}/{{- -}} whitespace control so render output can sit directly inside an HTML attribute value"

key-files:
  created:
    - snippets/swatch-color.liquid
  modified:
    - config/settings_schema.json
    - snippets/product-card.liquid
    - sections/product-main.liquid
    - templates/list-collections.json
    - templates/page.models.json

key-decisions:
  - "Seeded swatch_color_map default with existing brand tokens (Noir/Ivory/Coral/Sand/Gold) plus one new Midnight value, rather than inventing an empty map, so the setting has a non-blank JSON-valid default per repo constraint"
  - "Hex is parsed from the segment after the LAST colon in each line (via remove_last), allowing color names to contain their own colon (e.g. 'Noir: Limited')"
  - "Fixed two pre-existing invalid JSON template files (Shopify auto-sync artifact) discovered while running the plan's repo-wide validation gate, since they blocked the mandatory 'every JSON file parses' hard gate"

patterns-established:
  - "Data-driven, merchant-editable color swatches: any future swatch render site should call render 'swatch-color', color: <option value> instead of hand-rolling downcase/replace logic"

requirements-completed: [QUICK-260817-S0A]

duration: 25min
completed: 2026-08-18
---

# Quick Task 260817-s0a: Data-Driven Color-to-Hex Swatch Mapping Summary

**Owner-editable `swatch_color_map` theme setting plus a reusable `swatch-color.liquid` snippet replacing the two hard-coded downcase/hyphenate swatch color interpolations on the product card and PDP.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-08-18T00:53:00Z
- **Completed:** 2026-08-18T01:17:50Z
- **Tasks:** 3
- **Files modified:** 6 (4 planned + 2 deviation fixes)

## Accomplishments
- Added a `textarea` setting (`swatch_color_map`) to the theme editor's Colors group, seeded with the brand palette (Noir, Ivory, Coral, Sand, Gold, Midnight)
- Built `snippets/swatch-color.liquid`: case-insensitive, whitespace-tolerant, colon-tolerant `Color Name: #hex` lookup that falls back to the exact legacy `downcase | replace: ' ', '-'` behavior on a miss, with `escape`-guarded output
- Wired both swatch render sites (`snippets/product-card.liquid`, `sections/product-main.liquid`) to the new snippet without disturbing any accessibility or data attribute
- Fixed two pre-existing Shopify auto-sync JSON template files that were failing the repo-wide JSON validation gate

## Task Commits

All work landed in a single atomic commit per plan instructions (Task 3 explicitly bundles Tasks 1-3's artifacts):

1. **Tasks 1-3: Add data-driven color-to-hex swatch mapping** - `b8a291a` (feat)

_Plan explicitly specified one atomic commit for all four target files; the two out-of-scope JSON fixes required by the plan's own repo-wide validation gate were folded into the same commit since they were a hard blocker to satisfying that gate._

## Files Created/Modified
- `config/settings_schema.json` - Added `header` + `textarea` (`swatch_color_map`) settings to the Colors group, seeded with brand hex values
- `snippets/swatch-color.liquid` - New reusable snippet: parses `settings.swatch_color_map`, case-insensitive last-colon hex extraction, legacy fallback, escaped output
- `snippets/product-card.liquid` - Swatch button `style` attribute now renders `swatch-color` snippet instead of inline `downcase | replace`
- `sections/product-main.liquid` - PDP swatch button `style` attribute now renders `swatch-color` snippet instead of inline `downcase | replace`
- `templates/list-collections.json` - Removed invalid JS-style `/* */` comment header (Shopify auto-sync artifact) that broke JSON parsing
- `templates/page.models.json` - Removed invalid JS-style `/* */` comment header (Shopify auto-sync artifact) that broke JSON parsing

## Decisions Made
- Seeded `swatch_color_map` default with existing brand design tokens rather than an empty/placeholder map, satisfying the repo's hard "no blank default" constraint while giving the owner an immediately useful starting point
- Extracted hex value from the segment after the LAST colon per line, so color names may legitimately contain a colon (per plan's worked examples)
- Bundled the two unrelated pre-existing JSON fixes into this task's commit rather than deferring them, because they were flagged by name in the plan's own Task 3 verification gate ("fix anything it flags before committing") and this repo treats broken JSON as a hard, silently-failing production risk

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, plan-directed] Fixed invalid JS-style comment headers in two template JSON files**
- **Found during:** Task 3 (repo-wide validation gate run)
- **Issue:** `templates/list-collections.json` and `templates/page.models.json` each opened with a `/* ... */` comment block (added by a prior Shopify admin auto-sync), which is invalid JSON and made `JSON.parse` fail — this is the exact silent-failure class the project's critical constraints call out
- **Fix:** Removed the comment block from both files, leaving valid JSON template content unchanged otherwise
- **Files modified:** `templates/list-collections.json`, `templates/page.models.json`
- **Verification:** Repo-wide JSON/schema validation gate (`node -e ...` walk) now prints `ALL JSON AND SCHEMA BLOCKS VALID`; `grep -rn '"default": ""'` still returns no matches
- **Committed in:** `b8a291a` (part of the single Task 3 commit, per plan's explicit "fix anything it flags before committing" instruction)

---

**Total deviations:** 1 auto-fixed (Rule 1, explicitly directed by the plan's own Task 3 verification instructions)
**Impact on plan:** Required to satisfy the plan's mandatory repo-wide JSON validity gate; no functional change to the swatch feature itself, no scope creep beyond what the plan's verify step demanded.

## Issues Encountered
None beyond the deviation documented above.

## User Setup Required
None - no external service configuration required. The owner can edit `swatch_color_map` directly in the theme editor (Theme Settings > Colors) once this is deployed; no code change needed for future color additions.

## Next Phase Readiness
- Feature is self-contained and ready for the orchestrator's deploy/verify step
- Not deployed or pushed by this executor per constraints — orchestrator handles merge, push, and live Shopify verification
- `assets/pdp.js` `[data-color-swatch]` selector confirmed untouched; variant selection logic unaffected

---
*Quick Task: 260817-s0a*
*Completed: 2026-08-18*

## Self-Check: PASSED

All claimed files exist (`snippets/swatch-color.liquid`, `config/settings_schema.json`, `snippets/product-card.liquid`, `sections/product-main.liquid`, `templates/list-collections.json`, `templates/page.models.json`) and commit `b8a291a` is present in git log.
