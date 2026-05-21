"""Regression tests for bounded repeated structured logs."""

from __future__ import annotations

import importlib
import logging

import pytest
import structlog


def test_repeated_deduped_event_is_dropped(monkeypatch):
    monkeypatch.setenv("ARCHON_LOG_DEDUPE_WINDOW_SECONDS", "300")

    import app.logging_config as logging_config

    logging_config = importlib.reload(logging_config)
    event = {"event": "secret_expired", "path": "secret/foo"}

    assert logging_config._drop_repeated_events(
        logging.getLogger("test"),
        "warning",
        event.copy(),
    )

    with pytest.raises(structlog.DropEvent):
        logging_config._drop_repeated_events(
            logging.getLogger("test"),
            "warning",
            event.copy(),
        )


def test_unlisted_event_is_not_dropped(monkeypatch):
    monkeypatch.setenv("ARCHON_LOG_DEDUPE_WINDOW_SECONDS", "300")

    import app.logging_config as logging_config

    logging_config = importlib.reload(logging_config)
    event = {"event": "unique_operational_message", "path": "secret/foo"}

    assert logging_config._drop_repeated_events(
        logging.getLogger("test"),
        "info",
        event.copy(),
    )
    assert logging_config._drop_repeated_events(
        logging.getLogger("test"),
        "info",
        event.copy(),
    )
