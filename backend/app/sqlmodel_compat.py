"""Compatibility shim for SQLModel's timezone-aware ``DateTime`` mapping.

SQLModel >= 0.0.25 maps a plain ``datetime`` field to ``UTCDateTime``, whose
``process_bind_param`` raises on naive values. This codebase stores naive UTC
everywhere (36 ``_utcnow()`` default factories, 53 ``datetime.utcnow()`` call
sites), so every insert fails with::

    ValueError: Datetime values must have timezone information.

Treat naive values as UTC instead of touching 89 call sites.

Imported for its side effect from ``app.main``; without ``UTCDateTime`` (older
SQLModel, or a rename) the shim is a no-op.
"""

from __future__ import annotations

from datetime import datetime, timezone

try:  # pragma: no cover - depends on the installed SQLModel version
    from sqlmodel.sql.sqltypes import UTCDateTime
except ImportError:  # pragma: no cover
    UTCDateTime = None  # type: ignore[assignment,misc]

if UTCDateTime is not None:  # pragma: no branch
    _original_process_bind_param = UTCDateTime.process_bind_param

    def _process_bind_param(self, value, dialect):  # type: ignore[no-untyped-def]
        """Assume UTC for naive datetimes, then defer to SQLModel."""
        if isinstance(value, datetime) and value.utcoffset() is None:
            value = value.replace(tzinfo=timezone.utc)
        return _original_process_bind_param(self, value, dialect)

    UTCDateTime.process_bind_param = _process_bind_param  # type: ignore[method-assign]
