"""Regression tests for worker loop safety tunables."""

from __future__ import annotations

import importlib


def _reload_worker(monkeypatch):
    import app.worker as worker

    return importlib.reload(worker)


def test_worker_concurrency_alias_is_honored(monkeypatch):
    monkeypatch.delenv("ARCHON_MAX_CONCURRENT_RUNS", raising=False)
    monkeypatch.setenv("ARCHON_WORKER_CONCURRENCY", "4")

    worker = _reload_worker(monkeypatch)

    assert worker._MAX_CONCURRENT_RUNS == 4


def test_primary_concurrency_env_takes_precedence(monkeypatch):
    monkeypatch.setenv("ARCHON_MAX_CONCURRENT_RUNS", "7")
    monkeypatch.setenv("ARCHON_WORKER_CONCURRENCY", "4")

    worker = _reload_worker(monkeypatch)

    assert worker._MAX_CONCURRENT_RUNS == 7


def test_worker_scan_interval_is_configurable(monkeypatch):
    monkeypatch.setenv("ARCHON_WORKER_SCAN_INTERVAL", "42")

    worker = _reload_worker(monkeypatch)

    assert worker._WORKER_SCAN_INTERVAL == 42


def test_loop_backoff_is_bounded(monkeypatch):
    monkeypatch.setenv("ARCHON_LOOP_BACKOFF_MAX_SECONDS", "5")

    worker = _reload_worker(monkeypatch)

    assert worker._loop_backoff_seconds(0) == 0
    assert 1 <= worker._loop_backoff_seconds(1) <= 5
    assert 1 <= worker._loop_backoff_seconds(20) <= 5
