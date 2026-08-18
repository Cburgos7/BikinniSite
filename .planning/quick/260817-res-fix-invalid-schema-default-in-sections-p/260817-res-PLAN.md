---
phase: quick-260817-res
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - sections/page-models.liquid
  - sections/list-collections.liquid
autonomous: true
requirements: [QUICK-260817-RES]

must_haves:
  truths:
    - "sections/page-models.liquid schema contains no empty-string default value"
    - "sections/list-collections.liquid schema contains no empty-string default value"
    - "Both {% schema %} blocks parse as valid JSON"
    - "The subtitle setting still exists in both files with unchanged type, id, and label"
    - "Rendered Liquid output is byte-identical for any given set of section settings"
  artifacts:
    - path: "sections/page-models.liquid"
      provides: "Models page section with Shopify-valid schema"
      contains: "\"id\": \"subtitle\""
    - path: "sections/list-collections.liquid"
      provides: "Collections index section with Shopify-valid schema"
      contains: "\"id\": \"subtitle\""
  key_links:
    - from: "sections/page-models.liquid"
      to: "section.settings.subtitle"
      via: "blank-guarded Liquid render"
      pattern: "if section\\.settings\\.subtitle != blank"
    - from: "sections/list-collections.liquid"
      to: "section.settings.subtitle"
      via: "blank-guarded Liquid render"
      pattern: "if section\\.settings\\.subtitle != blank"
---

<objective>
Remove the invalid `"default": ""` key from the `subtitle` text setting in `sections/page-models.liquid` and `sections/list-collections.liquid`.

Purpose: Shopify's theme file validator rejects an empty-string `default` on a `text` setting with `FILE_VALIDATION_ERROR: Invalid schema: setting with id="subtitle" default can't be blank`. Every upload attempt for these two files — including Shopify's GitHub auto-sync — has been rejected since June, which is why both sections are absent from the live theme and `/pages/models` returns 404. Re-pushing the files cannot fix this; the schema itself must be corrected.

Output: Two `.liquid` files whose `{% schema %}` blocks pass Shopify validation, with no change to settings, ids, labels, or rendered markup.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md

@sections/page-models.liquid
@sections/list-collections.liquid

<diagnosis>
<!-- Established via live Shopify Admin API. Do NOT re-investigate. -->

Root cause: Shopify treats `"default": ""` on a `text` setting as a blank default and rejects the whole file.
The fix is to OMIT the `default` key entirely — not to set it to a placeholder string, and not to
change the setting type. Both settings are optional by design and both are already guarded in Liquid
with `{%- if section.settings.subtitle != blank -%}`, so omitting the default preserves current behavior
exactly (an unset text setting evaluates as `blank`).

A repo-wide grep for `"default": ""` returns exactly two hits — line 58 of `sections/page-models.liquid`
and line 68 of `sections/list-collections.liquid`. No other theme file is affected.

Both files are confirmed missing from the live theme's section list. All other `page-*` sections are
present and healthy.
</diagnosis>

<current_schema_state>
<!-- The exact JSON fragments to be edited. Note the trailing comma on the "label" line, -->
<!-- which must be removed along with the "default" line to keep the JSON valid.        -->

sections/page-models.liquid (lines 54-59):

    {
      "type": "text",
      "id": "subtitle",
      "label": "Hero subtitle (optional)",
      "default": ""
    }

sections/list-collections.liquid (lines 64-69):

    {
      "type": "text",
      "id": "subtitle",
      "label": "Subtitle",
      "default": ""
    }
</current_schema_state>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Remove empty-string schema defaults from both section files</name>
  <files>sections/page-models.liquid, sections/list-collections.liquid</files>
  <action>
In each of the two files, edit the `{% schema %}` JSON so the `subtitle` setting object no longer
declares a `default` key.

For `sections/page-models.liquid`: delete the line `      "default": ""` and remove the trailing
comma from the preceding line so it reads `      "label": "Hero subtitle (optional)"`.

For `sections/list-collections.liquid`: delete the line `      "default": ""` and remove the trailing
comma from the preceding line so it reads `      "label": "Subtitle"`.

Constraints — do NOT do any of the following:
- Do NOT delete or rename the `subtitle` setting itself; it stays with the same `type`, `id`, and `label`.
- Do NOT substitute a placeholder default value (e.g. `"default": " "` or `"default": "Subtitle"`).
  Shopify only accepts the key being absent. A whitespace default would also change rendered output by
  making the `!= blank` guard behave differently.
- Do NOT touch the `heading` setting in either file — its non-empty default is valid.
- Do NOT modify any Liquid markup, the `presets` array, the section `name`, or any class names.

The only bytes that change are the removal of the two `"default": ""` lines and the two trailing commas.
  </action>
  <verify>
    <automated>node -e "const fs=require('fs');for(const f of ['sections/page-models.liquid','sections/list-collections.liquid']){const s=fs.readFileSync(f,'utf8');const m=s.match(/{%-?\s*schema\s*-?%}([\s\S]*?){%-?\s*endschema\s*-?%}/);if(!m)throw new Error('no schema block: '+f);const j=JSON.parse(m[1]);const sub=j.settings.find(x=>x.id==='subtitle');if(!sub)throw new Error('subtitle setting missing: '+f);if('default' in sub)throw new Error('default key still present: '+f);if(JSON.stringify(j).includes('\"default\":\"\"'))throw new Error('empty default remains: '+f);console.log('OK '+f);}"</automated>
  </verify>
  <done>
The node command exits 0 and prints `OK` for both files. Specifically: each `{% schema %}` block parses
as valid JSON, each still contains a setting with `id: "subtitle"`, that setting has no `default` key,
and no empty-string default exists anywhere in either schema.

Additionally, `git diff --stat` shows exactly 2 files changed with 2 insertions and 4 deletions
(two removed `default` lines plus two comma-only rewrites of the `label` lines).
  </done>
</task>

<task type="auto">
  <name>Task 2: Commit the schema fix</name>
  <files>sections/page-models.liquid, sections/list-collections.liquid</files>
  <action>
Stage only the two edited section files and commit.

Commit message:

  fix(quick-260817-res): remove invalid empty schema default blocking theme sync

  Shopify rejects `"default": ""` on text settings with
  FILE_VALIDATION_ERROR: setting with id="subtitle" default can't be blank.
  This silently blocked every upload of these two sections since June,
  leaving them absent from the live theme and /pages/models returning 404.
  The key is now omitted; both settings remain optional and are already
  guarded by `{%- if section.settings.subtitle != blank -%}`.

Do NOT push. Do NOT attempt to upload to the live theme — the orchestrator handles deployment and
live-site verification after this plan completes.
  </action>
  <verify>
    <automated>git log -1 --name-only --format=%s | tr -d '\r' | grep -q "fix(quick-260817-res)" && git status --porcelain sections/ | grep -c . | grep -q '^0$' && echo COMMIT_OK</automated>
  </verify>
  <done>`COMMIT_OK` is printed: the most recent commit subject matches the fix message and `sections/` has no uncommitted changes remaining.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Merchant admin → theme settings | Merchant-entered `subtitle` text is stored in section settings and rendered into the page |
| Repo → Shopify theme (GitHub sync / Admin API) | Theme files cross into the hosted storefront |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-260817-01 | Tampering | `subtitle` setting rendering in both sections | mitigate | Existing `\| escape` filter on `{{ section.settings.subtitle }}` is preserved unchanged; Task 1 forbids touching Liquid markup |
| T-260817-02 | Denial of Service | Shopify theme file validator | mitigate | This plan IS the mitigation — the invalid schema is a self-inflicted availability failure taking two sections offline. Task 1 verification asserts valid JSON before commit |
| T-260817-03 | Tampering | Schema edit collateral damage | mitigate | Task 1 verification asserts the `subtitle` setting still exists by `id`; `git diff --stat` bound of 2 insertions / 4 deletions detects unintended edits |
| T-260817-SC | Tampering | npm/pip/cargo installs | n/a | No package installs in this plan — zero dependency surface change |
</threat_model>

<verification>
1. `{% schema %}` JSON in both files parses cleanly (Task 1 automated check).
2. The `subtitle` setting survives in both files with unchanged `type`, `id`, and `label`.
3. No `default` key exists on either `subtitle` setting.
4. The `heading` setting and its valid non-empty default are untouched in both files.
5. Liquid markup, `presets`, and section `name` values are unchanged — confirm via `git diff` that no
   line outside the two `subtitle` setting objects was modified.
6. Working tree is clean for `sections/` after commit.
</verification>

<success_criteria>
- Repo-wide grep for `"default": ""` returns zero matches.
- Both `{% schema %}` blocks are valid JSON containing an `id: "subtitle"` setting with no `default` key.
- `git diff` for the commit touches only the two `subtitle` setting objects — no Liquid, no other settings.
- Change is committed locally on `main` with the `fix(quick-260817-res)` subject; nothing pushed or deployed.

Out of scope (orchestrator handles after this plan): uploading the corrected files to the live theme
via Admin API, and verifying `/pages/models` and `/collections` render on the live storefront.
</success_criteria>

<output>
Create `.planning/quick/260817-res-fix-invalid-schema-default-in-sections-p/260817-res-SUMMARY.md` when done
</output>
