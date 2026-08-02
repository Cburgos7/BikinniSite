---
phase: quick-260802-lvy
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - sections/page-models.liquid
autonomous: true
requirements: [QUICK-260802-lvy]

must_haves:
  truths:
    - "sections/page-models.liquid differs from its state at commit c60308f"
    - "The change is committed on main and pushed to origin/main"
    - "The section's rendered output and schema behavior are unchanged"
  artifacts:
    - path: "sections/page-models.liquid"
      provides: "Models page section markup + schema, now with a touched file mtime/blob hash so Shopify's GitHub integration re-uploads it"
      contains: "{% schema %}"
  key_links:
    - from: "sections/page-models.liquid"
      to: "origin/main"
      via: "git push"
      pattern: "page-models\\.liquid"
---

<objective>
Force Shopify's GitHub integration to re-upload `sections/page-models.liquid` by making a
harmless, non-rendering change to the file and pushing it to `main`.

Purpose: The live theme is missing this one section (Section Rendering API returns 0 bytes for
`page-models` while sibling sections render fine), which makes `/pages/models` return 404. The
repo file is valid; Shopify's sync silently dropped it, and because the file has not changed
since June no subsequent push has re-uploaded it. Changing the file's content is the only way to
put it back in the integration's changed-files set.

Output: One commit on `main` touching `sections/page-models.liquid`, pushed to `origin/main`.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@sections/page-models.liquid

Established diagnostics (do NOT re-investigate):
- `/?section_id=page-models` on velvet-tide-2.myshopify.com returns 0 bytes; all other page-*
  sections render normally.
- The Admin page `/pages/models` exists, is published, and has templateSuffix `models`.
  Swapping it to the `about` template returns 200 — the template/section is the culprit.
- The repo file is clean: no BOM, valid `{% schema %}` JSON, LF line endings, committed in
  `aacb080` and `300db97`, and `origin/main` is current at `c60308f`.

Sibling section files (`sections/page-about.liquid`, `sections/page-faq.liquid`) open with an
HTML comment header such as `<!-- Page Hero (D-10) -->`. `sections/page-models.liquid` currently
opens directly with `<section class="bg-deep text-cream py-16 lg:py-24">`.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add a non-rendering header comment to page-models.liquid and commit</name>
  <files>sections/page-models.liquid</files>
  <action>
    Insert a single Liquid comment line as the very first line of `sections/page-models.liquid`,
    immediately above the existing opening `<section class="bg-deep text-cream py-16 lg:py-24">`
    tag. Use the whitespace-stripping Liquid comment form so rendered output is byte-identical to
    today's output: an opening `comment` tag with leading/trailing hyphens, the text
    `Models page — metaobject-driven grid (D-10 page hero + model cards)`, then the matching
    closing `endcomment` tag, all on one line. Use a Liquid comment rather than the HTML comment
    style used by sibling sections specifically because Liquid comments emit nothing, so the live
    page HTML cannot change.

    Do NOT touch anything else in the file: leave the `{% schema %}` block, its JSON, every
    existing tag, class list, and the LF line endings exactly as they are. Do not reformat, do not
    reorder settings, do not add a trailing newline change. The entire diff must be one added line.

    Then stage only this file and commit with message:
    `chore: touch page-models section to re-trigger Shopify GitHub sync`

    Do not amend or rebase prior commits — the fix depends on a NEW commit reaching origin.
  </action>
  <verify>
    <automated>git diff HEAD~1 --stat -- sections/page-models.liquid | grep -q '1 +' && git diff HEAD~1 -- sections/page-models.liquid | grep -c '^+' | grep -qx 2 && git diff HEAD~1 --name-only | grep -qx 'sections/page-models.liquid'</automated>
  </verify>
  <done>
    HEAD is a new commit whose only changed file is `sections/page-models.liquid`, and the diff
    consists of exactly one added line (the Liquid comment) with no deletions. The `{% schema %}`
    block is unchanged.
  </done>
</task>

<task type="auto">
  <name>Task 2: Push to origin/main so the integration re-uploads the file</name>
  <files>sections/page-models.liquid</files>
  <action>
    Push the branch to origin: `git push origin main`. This is the load-bearing step — the Shopify
    GitHub integration only re-uploads files that appear in the changed-file set of a push to the
    connected branch. If the push is rejected as non-fast-forward, fetch and rebase onto
    `origin/main`, then push again; do not force-push.

    After the push succeeds, confirm the remote actually carries the change by checking that
    `origin/main` points at the new commit and that the commit lists `sections/page-models.liquid`.

    Do not attempt to verify the live storefront — the orchestrator performs the
    Section Rendering API and `/pages/models` checks afterward.
  </action>
  <verify>
    <automated>git fetch origin main -q && test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" && git show --name-only --format= origin/main | grep -qx 'sections/page-models.liquid'</automated>
  </verify>
  <done>
    `origin/main` equals local `HEAD`, and the tip commit on `origin/main` includes
    `sections/page-models.liquid` in its changed files.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| repo → Shopify theme (GitHub integration) | Pushed Liquid is executed server-side when rendering the storefront |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-lvy-01 | Tampering | sections/page-models.liquid | mitigate | Diff is constrained to one added Liquid comment; verify gate asserts exactly one added line and zero deletions, so no logic or schema can be altered under cover of the touch |
| T-lvy-02 | Information disclosure | rendered /pages/models HTML | mitigate | Liquid comment form is used instead of an HTML comment, so nothing new is emitted to the client |
| T-lvy-03 | Denial of service | live theme | accept | Change is non-functional; worst case the integration no-ops and the page stays 404, i.e. status quo. No force-push, so remote history cannot be damaged |
</threat_model>

<verification>
- `git diff c60308f..HEAD -- sections/page-models.liquid` shows exactly one added line, no deletions.
- `git rev-parse HEAD` equals `git rev-parse origin/main`.
- Orchestrator (post-plan): `/?section_id=page-models` returns non-zero bytes and `/pages/models`
  returns 200.
</verification>

<success_criteria>
- A new commit exists on `main` modifying only `sections/page-models.liquid`.
- The modification is a single non-rendering Liquid comment; schema and markup are untouched.
- The commit is present on `origin/main`.
</success_criteria>

<output>
Create `.planning/quick/260802-lvy-re-trigger-shopify-github-sync-for-secti/260802-lvy-SUMMARY.md` when done
</output>
