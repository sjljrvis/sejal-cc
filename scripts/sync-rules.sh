#!/usr/bin/env bash
# sync-rules.sh — regenerate .cursor/rules/*.mdc from canonical .agents/rules/*.md
#
# Run this any time you edit a rule under .agents/rules/. It re-writes the
# Cursor mirror with the proper Cursor frontmatter (alwaysApply / globs /
# description) so Cursor auto-loads each rule with the right trigger.
#
# Usage:
#   scripts/sync-rules.sh
#
# To add a new rule:
#   1. Create .agents/rules/NN-title.md with Antigravity frontmatter
#   2. Add an entry to the CURSOR_FRONTMATTER mapping below
#   3. Re-run this script

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/.agents/rules"
DST="$ROOT/.cursor/rules"
mkdir -p "$DST"

# Cursor frontmatter per rule. Format is the literal YAML body that goes
# between the --- markers. Add new rules here when you create them.
get_cursor_frontmatter() {
  case "$1" in
    01-project-core)
      cat <<'EOF'
description: Project core identity, three pillars, strict internal-tool boundary, brand basics
alwaysApply: true
EOF
      ;;
    02-tech-stack-architecture)
      cat <<'EOF'
description: Backend/frontend tech stack choices, folder layout, architectural rules. Load when adding services, picking libraries, or restructuring folders.
alwaysApply: false
EOF
      ;;
    03-ui-animations-standard)
      cat <<'EOF'
description: UI patterns, brand tokens, typography scale, animations, layout conventions for the Ampersand design system.
globs: frontend/src/**/*.tsx,frontend/src/**/*.ts,frontend/src/**/*.css
alwaysApply: false
EOF
      ;;
    04-agent-execution-workflow)
      cat <<'EOF'
description: Step-by-step implementation strategy, pre-commit validation, git discipline (no push), Docker awareness, migration discipline
alwaysApply: true
EOF
      ;;
    05-memory-bank-protocol)
      cat <<'EOF'
description: Session-startup memory bank protocol — read docs/memory-bank/ files on every session, update at end of significant tasks
alwaysApply: true
EOF
      ;;
    06-gemini-ai-patterns)
      cat <<'EOF'
description: AI abstraction layer, prompt engineering, tool/function calling, error handling, AI Policies engine, RuleArchitect conflict checks
globs: app/services/ai/**,app/services/policies/**,app/services/rule_architect.py
alwaysApply: false
EOF
      ;;
    07-mcp-and-tooling)
      cat <<'EOF'
description: MCP servers (BigQuery, Cloud Run, Aikido, Stitch, Google Docs), Make commands, env vars, deployment tooling
alwaysApply: false
EOF
      ;;
    08-api-design-conventions)
      cat <<'EOF'
description: REST URL patterns, response envelopes, status codes, pagination, filtering, Pydantic schema discipline, router organization
globs: app/routers/**,app/schemas/**,app/main.py
alwaysApply: false
EOF
      ;;
    09-testing-strategy)
      cat <<'EOF'
description: What must be tested (backend + frontend), file conventions, fixtures, mocking AI, pre-commit test requirements
globs: tests/**,**/*.test.ts,**/*.test.tsx,**/test_*.py
alwaysApply: false
EOF
      ;;
    10-zero-hardcoded-business-logic)
      cat <<'EOF'
description: The Iron Law — all business decisions must go through AI Policies. Fallback hierarchy, anti-patterns, policy hooks
alwaysApply: true
EOF
      ;;
    11-data-ingestion-architecture)
      cat <<'EOF'
description: IngestionAdapter protocol, POC vs production sources, field mapping, quarantine, config-driven selection
globs: app/services/ingestion/**
alwaysApply: false
EOF
      ;;
    12-developer-guardrails)
      cat <<'EOF'
description: Pillar check, authz enforcement, design quality enforcement, anti-pattern table, entity lifecycle checklist, pre-commit self-check
alwaysApply: false
EOF
      ;;
    13-security-and-secrets)
      cat <<'EOF'
description: Secrets hygiene, env discipline, PII handling, OWASP-aware coding, AI-specific threats (prompt injection, tool-call abuse), pre-commit security check
alwaysApply: true
EOF
      ;;
    14-accessibility)
      cat <<'EOF'
description: WCAG 2.2 AA bar — keyboard nav, semantic HTML, ARIA, color/contrast, forms, images, tables, pre-commit a11y check
globs: frontend/src/**/*.tsx,frontend/src/**/*.ts
alwaysApply: false
EOF
      ;;
    15-observability-and-logging)
      cat <<'EOF'
description: Log levels, structured events, per-subsystem logging conventions, sensitive field masking, audit vs app log boundary
globs: app/**/*.py
alwaysApply: false
EOF
      ;;
    *)
      # Unknown rule — minimal frontmatter so the file at least exists
      printf 'description: See .agents/rules/%s.md\nalwaysApply: false\n' "$1"
      ;;
  esac
}

# Strip the leading YAML frontmatter block from a Markdown file.
strip_frontmatter() {
  awk '
    BEGIN { in_fm = 0; done = 0 }
    NR == 1 && /^---$/ { in_fm = 1; next }
    in_fm && /^---$/   { in_fm = 0; done = 1; next }
    in_fm              { next }
    !in_fm             { print }
  ' "$1"
}

count=0
for src_file in "$SRC"/*.md; do
  base=$(basename "$src_file" .md)
  [ "$base" = "README" ] && continue

  out="$DST/$base.mdc"
  fm="$(get_cursor_frontmatter "$base")"
  body="$(strip_frontmatter "$src_file")"

  {
    printf -- '---\n'
    printf '%s\n' "$fm"
    printf -- '---\n\n'
    printf '<!-- ⚠ MIRROR — canonical: .agents/rules/%s.md. Edit canonical, then run scripts/sync-rules.sh. -->\n\n' "$base"
    printf '%s\n' "$body"
  } > "$out"

  count=$((count + 1))
  printf 'wrote %s\n' "$out"
done

printf '\n✓ Synced %d rules into %s\n' "$count" "$DST"
