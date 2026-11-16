"""MCP tools that let coding agents request visual context and briefs."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from oc_worker import package_version
from oc_worker.agent import build_implementation_brief, load_context_payload
from oc_worker.cli import analyze_file
from oc_worker.config import Settings, load_local_env
from oc_worker.models import DetailLevel

INSTRUCTIONS = """\
Use OpenContext when a user provides a video, screen recording, or image that
a text-only model cannot inspect. Analyze local media or read an existing
context JSON, then request an implementation brief for the target repository.
Treat inferred or uncertain evidence as a hypothesis and preserve evidence IDs.
"""


def _settings_for_analysis(offline: bool) -> Settings:
    load_local_env()
    settings = Settings.from_env()
    if not offline:
        return settings
    return replace(
        settings,
        transcription_provider="fixture",
        vision_provider="fixture",
        ocr_provider="fixture",
        text_provider="template",
    )


def build_server() -> MCPServer:
    server = MCPServer(
        "opencontext",
        title="OpenContext",
        description="Evidence-linked visual context for text-only coding agents.",
        instructions=INSTRUCTIONS,
        version=package_version(),
    )

    @server.tool()
    def implementation_brief(
        context_path: str,
        repository_path: str | None = None,
        task: str | None = None,
    ) -> str:
        """Turn an existing OpenContext JSON result into an implementation brief."""
        payload = load_context_payload(context_path)
        return build_implementation_brief(
            payload,
            repository=repository_path,
            task=task,
        )

    def _analyze_local_media(
        media_path: str,
        repository_path: str | None = None,
        task: str | None = None,
        detail_level: str = "MEDIUM",
        offline: bool = False,
    ) -> str:
        media = Path(media_path).expanduser().resolve()
        if not media.is_file():
            raise ValueError(f"Media path is not a file: {media}")
        settings = _settings_for_analysis(offline)
        _markdown, payload = analyze_file(
            media,
            settings,
            detail_level=DetailLevel(detail_level.upper()),
        )
        return build_implementation_brief(
            payload,
            repository=repository_path,
            task=task,
        )

    @server.tool()
    def analyze_media(
        media_path: str,
        repository_path: str | None = None,
        task: str | None = None,
        detail_level: str = "MEDIUM",
        offline: bool = False,
    ) -> str:
        """Analyze a local video or image and return an evidence-linked brief."""
        return _analyze_local_media(
            media_path,
            repository_path=repository_path,
            task=task,
            detail_level=detail_level,
            offline=offline,
        )

    @server.tool()
    def analyze_video(
        video_path: str,
        repository_path: str | None = None,
        task: str | None = None,
        detail_level: str = "MEDIUM",
        offline: bool = False,
    ) -> str:
        """Analyze a local video and return an evidence-linked brief."""
        return _analyze_local_media(
            video_path,
            repository_path=repository_path,
            task=task,
            detail_level=detail_level,
            offline=offline,
        )

    @server.tool()
    def analyze_image(
        image_path: str,
        repository_path: str | None = None,
        task: str | None = None,
        detail_level: str = "MEDIUM",
        offline: bool = False,
    ) -> str:
        """Analyze a local image and return an evidence-linked brief."""
        return _analyze_local_media(
            image_path,
            repository_path=repository_path,
            task=task,
            detail_level=detail_level,
            offline=offline,
        )

    @server.tool()
    def context_evidence(context_path: str, limit: int = 50) -> str:
        """Return the evidence ledger from an OpenContext JSON result."""
        payload = load_context_payload(context_path)
        evidence = payload.get("evidence") or []
        bounded = max(1, min(int(limit), 200))
        return json.dumps(evidence[:bounded], ensure_ascii=False, indent=2)

    return server


def main() -> None:
    build_server().run("stdio")


if __name__ == "__main__":
    main()
