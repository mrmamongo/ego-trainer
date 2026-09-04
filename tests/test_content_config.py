"""Regression tests for :class:`ego_server.content_config.TasksRepoConfig`.

Covers ``resolved_local_path`` only: bare local paths, file-URL percent
decoding, query/fragment rejection, and platform-specific (Windows/POSIX)
file-URL conversion. Platform-specific cases are guarded with
``pytest.mark.skipif`` so the suite is cross-platform green.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from ego_server.content_config import TasksRepoConfig


class TestBareLocalPath:
    def test_bare_local_path_unchanged(self) -> None:
        cfg = TasksRepoConfig(url="/var/lib/ego-tasks")
        assert cfg.resolved_local_path == Path("/var/lib/ego-tasks")

    def test_bare_relative_path_unchanged(self) -> None:
        cfg = TasksRepoConfig(url="relative/tasks")
        assert cfg.resolved_local_path == Path("relative/tasks")


class TestPercentDecoding:
    def test_percent_decoded_in_file_url(self) -> None:
        cfg = TasksRepoConfig(url="file:///var/data/my%20tasks")
        assert cfg.resolved_local_path == Path("/var/data/my tasks")


class TestQueryFragmentRejected:
    def test_query_rejected(self) -> None:
        cfg = TasksRepoConfig(url="file:///var/data/tasks?ref=main")
        with pytest.raises(ValueError, match="query or fragment"):
            _ = cfg.resolved_local_path

    def test_fragment_rejected(self) -> None:
        cfg = TasksRepoConfig(url="file:///var/data/tasks#section")
        with pytest.raises(ValueError, match="query or fragment"):
            _ = cfg.resolved_local_path


@pytest.mark.skipif(os.name != "nt", reason="Windows file-URL conversion")
class TestWindowsFileURLs:
    def test_drive_letter_file_url(self) -> None:
        cfg = TasksRepoConfig(url="file:///C:/Users/example/tasks")
        assert cfg.resolved_local_path == Path(r"C:\Users\example\tasks")

    def test_unc_file_url(self) -> None:
        cfg = TasksRepoConfig(url="file://server/share/tasks")
        assert cfg.resolved_local_path == Path(r"\\server\share\tasks")


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file-URL conversion")
class TestPosixFileURLs:
    def test_absolute_file_url(self) -> None:
        cfg = TasksRepoConfig(url="file:///var/lib/tasks")
        assert cfg.resolved_local_path == Path("/var/lib/tasks")
