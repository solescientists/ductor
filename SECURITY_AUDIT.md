# Security Audit — solescientists/ductor fork

Audited against upstream `PleasePrompto/ductor` v0.16.3.

---

## Changes Made in This Fork

### Self-update and outbound network calls — DISABLED

All outbound network calls and the self-update pipeline have been commented out.

**Files changed:**

| File | Change |
|------|--------|
| `ductor_bot/infra/version.py` | `check_pypi()` and `fetch_changelog()` are no-ops, always return `None`. All HTTP to `pypi.org` and `api.github.com` commented out. |
| `ductor_bot/infra/updater.py` | `UpdateObserver` loop disabled. `perform_upgrade_pipeline()` returns immediately. All `pip`/`pipx`/`uv` subprocess calls commented out. |
| `ductor_bot/messenger/telegram/startup.py` | `UpdateObserver` start and upgrade sentinel handling commented out. |
| `ductor_bot/messenger/telegram/upgrade_handler.py` | Upgrade callback handler returns a "disabled" notice instead of running anything. |
| `ductor_bot/messenger/matrix/bot.py` | Same — upgrade handler returns "disabled". |
| `ductor_bot/orchestrator/commands.py` | `/upgrade` Telegram command returns "Self-update disabled". |
| `ductor_bot/cli_commands/lifecycle.py` | `ductor upgrade` CLI prints "disabled" and exits. |
| `ductor_bot/messenger/telegram/app.py` | `/info` button keyboard with PyPI and upstream GitHub release links commented out. |

All original code is preserved as comments — nothing was deleted.

**Why:** The self-update pipeline was a supply chain risk. An upstream package update could silently modify bundled workspace templates (CLAUDE.md, AGENTS.md, GEMINI.md, tool scripts) that get written into the Claude/Codex working directory on every restart, changing agent behaviour without user awareness.

---

## Security Audit Findings

### CRITICAL — None found

- No hardcoded IPs or external domains outside expected services
- No obfuscated payloads (no `eval`/`exec` of dynamic strings, no suspicious base64)
- No hidden Unicode or steganographic tricks
- No post-install scripts or malicious `pyproject.toml` entry points
- No telemetry, analytics, or "phone home" functions
- No `shell=True` subprocess calls (all use `asyncio.create_subprocess_exec` with explicit arg lists)

---

### HIGH — Design risks (legitimate but powerful)

**1. Zone 2 file overwrite on every start** *(supply chain risk — mitigated by disabling updates)*

`ductor_bot/workspace/init.py` overwrites `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and several tool scripts under `~/.ductor/workspace/tools/` on every startup from bundled templates.

With updates disabled and the package version pinned, the bundled templates are frozen — this is no longer a supply chain risk. If you re-enable updates in future, review the Zone 2 files for unexpected changes after any upgrade.

**2. Docker sandbox gives `node` user passwordless `sudo`**

`Dockerfile.sandbox` gives the container's `node` user passwordless `sudo`. This is intentional for Claude Code's operation inside the container, but means any code the agent executes inside the sandbox can escalate to root within the container.

Mitigation: Use Docker's `--cap-drop` flags if container escape is a concern.

---

### MEDIUM — Architecture observations

**3. `permission_mode` defaults to `"bypassPermissions"`**

`cli/base.py`: `CLIConfig` defaults `permission_mode = "bypassPermissions"`. Claude Code and Codex both run with all tool permissions enabled — no approval prompts for file reads, writes, or shell execution.

For Codex specifically, this passes `--dangerously-bypass-approvals-and-sandbox`, removing Codex's sandbox entirely. Claude Code's built-in safety model still partially applies even in bypass mode, but Codex has no equivalent.

**Recommendation:** Set `permission_mode = "default"` or `"ask"` unless running inside Docker.

**4. No system prompt separation for Codex**

Claude Code has a dedicated `--system-prompt` flag keeping instructions separate from user messages. Codex CLI has no such flag — ductor concatenates system context directly into the top of the user message. A prompt injection in a Telegram message sits in the same text block as your instructions.

**5. Inter-agent API is localhost-only**

The multiagent internal API (`http://127.0.0.1:{port}/interagent/*`) only binds to localhost. Clean.

---

### LOW

**6. Prompt injection filter (`security/content.py`)**

Detects common injection patterns (ignore previous instructions, role hijack, CLI flag injection, etc.). Decent baseline but bypassable with creative phrasing. The Telegram `allowed_user_ids` allowlist is the real gate.

**7. GitHub Actions publish workflow uses major-version-pinned actions**

`actions/checkout@v4`, `actions/setup-python@v5`, `pypa/gh-action-pypi-publish@release/v1` — pinned to major versions, not commit SHAs. Mild supply chain risk from unpinned actions.

Mitigation: Pin actions to full commit SHAs for maximum safety.

---

### Dependency Audit — Clean

No typosquatted or suspicious packages. All dependencies are well-known:
`aiogram`, `aiohttp`, `pydantic`, `cronsim`, `rich`, `questionary`, `Pillow`, `filetype`, `tzdata`, `PyNaCl`, `matrix-nio`.

---

## Remaining Risks

| Risk | Severity | Status |
|------|----------|--------|
| Supply chain via self-update | HIGH | **Mitigated** — updates disabled in this fork |
| Zone 2 overwrite via package upgrade | HIGH | **Mitigated** — updates disabled; templates frozen at current version |
| `bypassPermissions` default (Codex has no sandbox) | MEDIUM | **Open** — set `permission_mode = "default"` to address |
| Prompt injection easier with Codex (no `--system-prompt`) | MEDIUM | **Open** — architectural limitation of Codex CLI |
| Passwordless sudo inside Docker sandbox | MEDIUM | **Open** — use `--cap-drop` if needed |
| Prompt injection filter bypassable | LOW | **Open** — allowlist is primary control |
| Unpinned GitHub Actions SHAs | LOW | **Open** — pin to commit SHAs for full safety |
