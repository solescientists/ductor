"""Self-update observer: periodic version check + upgrade execution."""

# DISABLED: UpdateObserver._loop and perform_upgrade_pipeline have been
# commented out. The bot will never poll PyPI or run pip/pipx/uv to upgrade
# itself. Sentinel helpers (write/consume) are retained for restart notifications.

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
# import os
# import sys
from collections.abc import Awaitable, Callable
from pathlib import Path

from ductor_bot.infra.version import VersionInfo, _parse_version, check_pypi  # noqa: F401

logger = logging.getLogger(__name__)

# _CHECK_INTERVAL_S = 3600  # 60 minutes
# _INITIAL_DELAY_S = 60  # 1 minute after startup
# _VERIFY_DELAYS_S: tuple[float, ...] = (0.15, 0.35, 0.75, 1.5)

VersionCallback = Callable[[VersionInfo], Awaitable[None]]

_UPGRADE_SENTINEL_NAME = "upgrade-sentinel.json"


class UpdateObserver:
    """Background task that checks PyPI for new versions periodically. DISABLED."""

    def __init__(self, *, notify: VersionCallback) -> None:
        self._notify = notify
        self._task: asyncio.Task[None] | None = None
        self._last_notified: str = ""

    def start(self) -> None:
        # DISABLED: version polling has been removed.
        # self._task = asyncio.create_task(self._loop())
        pass

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def _loop(self) -> None:
        # DISABLED: outbound PyPI contact removed.
        # await asyncio.sleep(_INITIAL_DELAY_S)
        # while True:
        #     try:
        #         info = await check_pypi()
        #         if info and info.update_available and info.latest != self._last_notified:
        #             self._last_notified = info.latest
        #             await self._notify(info)
        #     except Exception:
        #         logger.debug("Update check failed", exc_info=True)
        #     await asyncio.sleep(_CHECK_INTERVAL_S)
        pass


# ---------------------------------------------------------------------------
# Upgrade execution  (DISABLED)
# ---------------------------------------------------------------------------


# def _normalize_target_version(target_version: str | None) -> str | None:
#     """Normalize optional target version value for upgrade commands."""
#     if target_version is None:
#         return None
#     normalized = target_version.strip()
#     if not normalized or normalized.lower() == "latest":
#         return None
#     return normalized


def _is_newer_version(candidate: str, current: str) -> bool:
    """Return True when *candidate* is strictly newer than *current*."""
    return _parse_version(candidate) > _parse_version(current)


# def _build_upgrade_command(
#     *,
#     mode: str,
#     target_version: str | None,
#     force_reinstall: bool,
# ) -> list[str]:
#     """Build provider-specific upgrade command."""
#     if mode == "pipx":
#         if target_version is None and not force_reinstall and sys.platform != "win32":
#             return ["pipx", "upgrade", "--force", "ductor"]
#         spec = f"ductor=={target_version}" if target_version else "ductor"
#         cmd = ["pipx", "runpip", "ductor", "install", "--upgrade", "--no-cache-dir"]
#         if force_reinstall:
#             cmd.append("--force-reinstall")
#         cmd.append(spec)
#         return cmd
#     if mode == "uv":
#         spec = f"ductor=={target_version}" if target_version else "ductor"
#         cmd = ["uv", "tool", "upgrade"]
#         if force_reinstall:
#             cmd.append("--reinstall")
#         cmd.append(spec)
#         return cmd
#     spec = f"ductor=={target_version}" if target_version else "ductor"
#     cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir"]
#     if force_reinstall:
#         cmd.append("--force-reinstall")
#     cmd.append(spec)
#     return cmd


# async def _run_upgrade_command(
#     cmd: list[str],
#     *,
#     env: dict[str, str],
# ) -> tuple[bool, str]:
#     """Execute one upgrade command and return ``(success, output)``."""
#     proc = await asyncio.create_subprocess_exec(
#         *cmd,
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.STDOUT,
#         env=env,
#     )
#     stdout, _ = await proc.communicate()
#     output = stdout.decode(errors="replace") if stdout else ""
#     return (proc.returncode or 0) == 0, output


# async def _perform_upgrade_impl(
#     *,
#     target_version: str | None,
#     force_reinstall: bool,
# ) -> tuple[bool, str]:
#     from ductor_bot.infra.install import detect_install_mode
#     mode = detect_install_mode()
#     if mode == "dev":
#         return False, "Running from source (editable install). Use `git pull` to update."
#     normalized_target = _normalize_target_version(target_version)
#     env = {**os.environ, "PIP_NO_CACHE_DIR": "1"}
#     cmd = _build_upgrade_command(
#         mode=mode,
#         target_version=normalized_target,
#         force_reinstall=force_reinstall,
#     )
#     ok, output = await _run_upgrade_command(cmd, env=env)
#     if ok:
#         return True, output
#     if mode == "pipx" and normalized_target is not None and sys.platform != "win32":
#         fallback_cmd = ["pipx", "upgrade", "--force", "ductor"]
#         fb_ok, fb_output = await _run_upgrade_command(fallback_cmd, env=env)
#         combined = "\n\n".join(part for part in (output.strip(), fb_output.strip()) if part)
#         return fb_ok, combined
#     return False, output


# async def get_installed_version() -> str:
#     proc = await asyncio.create_subprocess_exec(
#         sys.executable,
#         "-c",
#         "from importlib.metadata import version; print(version('ductor'))",
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.DEVNULL,
#     )
#     stdout, _ = await proc.communicate()
#     return stdout.decode().strip() if stdout else "0.0.0"


# async def _wait_for_version_change(previous_version: str) -> str:
#     installed = await get_installed_version()
#     if installed != previous_version:
#         return installed
#     for delay in _VERIFY_DELAYS_S:
#         await asyncio.sleep(delay)
#         installed = await get_installed_version()
#         if installed != previous_version:
#             return installed
#     return previous_version


# def _combine_outputs(outputs: list[str]) -> str:
#     parts = [part.strip() for part in outputs if part and part.strip()]
#     return "\n\n".join(parts)


# async def _resolve_retry_target(current_version: str, target_version: str | None) -> str | None:
#     normalized_target = _normalize_target_version(target_version)
#     if normalized_target and _is_newer_version(normalized_target, current_version):
#         return normalized_target
#     info = await check_pypi(fresh=True)
#     if info and _is_newer_version(info.latest, current_version):
#         return info.latest
#     return None


async def perform_upgrade_pipeline(
    *,
    current_version: str,
    target_version: str | None = None,  # noqa: ARG001
) -> tuple[bool, str, str]:
    """Disabled: self-upgrade has been removed.

    Always returns (False, current_version, message) without contacting
    PyPI or running pip/pipx/uv.
    """
    # DISABLED: upgrade execution commented out.
    # outputs: list[str] = []
    # _ok, output = await _perform_upgrade_impl(target_version=None, force_reinstall=False)
    # outputs.append(output)
    # installed = await _wait_for_version_change(current_version)
    # if installed != current_version:
    #     return True, installed, _combine_outputs(outputs)
    # retry_target = await _resolve_retry_target(current_version, target_version)
    # if retry_target is None:
    #     return False, current_version, _combine_outputs(outputs)
    # _retry_ok, retry_output = await _perform_upgrade_impl(
    #     target_version=retry_target,
    #     force_reinstall=True,
    # )
    # outputs.append(retry_output)
    # installed = await _wait_for_version_change(current_version)
    # if installed != current_version:
    #     return True, installed, _combine_outputs(outputs)
    # combined = _combine_outputs(outputs)
    # if "No matching distribution found" in combined:
    #     outputs.append(
    #         "The new version may not have propagated to all PyPI mirrors yet. "
    #         "Please try again in a few minutes."
    #     )
    # return False, current_version, _combine_outputs(outputs)
    return False, current_version, "Self-update is disabled in this build."


# ---------------------------------------------------------------------------
# Upgrade sentinel (post-restart notification)
# ---------------------------------------------------------------------------


def write_upgrade_sentinel(
    sentinel_dir: Path,
    *,
    chat_id: int,
    old_version: str,
    new_version: str,
) -> None:
    """Write sentinel so the bot can notify the user after upgrade restart."""
    from ductor_bot.infra.atomic_io import atomic_bytes_save

    path = sentinel_dir / _UPGRADE_SENTINEL_NAME
    content = json.dumps(
        {"chat_id": chat_id, "old_version": old_version, "new_version": new_version}
    )
    atomic_bytes_save(path, content.encode())


def consume_upgrade_sentinel(sentinel_dir: Path) -> dict[str, str | int] | None:
    """Read and delete the upgrade sentinel. Returns None if absent."""
    path = sentinel_dir / _UPGRADE_SENTINEL_NAME
    if not path.exists():
        return None
    try:
        data: dict[str, str | int] = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.exception("Failed to read upgrade sentinel")
        path.unlink(missing_ok=True)
        return None
    else:
        path.unlink(missing_ok=True)
        logger.info(
            "Upgrade sentinel consumed: %s -> %s", data.get("old_version"), data.get("new_version")
        )
        return data
