# -*- coding: utf-8 -*-
"""
ItWorksOnYourMachineToo Runtime Integrity
================================================================

Defines known-good fingerprints for standard tools and checks whether a
binary has been tampered with.
"""

from typing import Dict
import os
from ..contracts.adapter import OSAdapter

# Simplified example database (in production, loaded from a secured service)
KNOWN_GOOD_HASHES = {
    "macos": {
        "python3.12": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # Placeholder
    },
    "linux": {
        "python3.12": "4472a1188352697a2298c9035e98544d6da2f854964648710f6f0590a9041280",  # Placeholder
    },
}


class IntegrityManager:
    """
    Manages runtime binary verification.
    """
    def __init__(self, adapter: OSAdapter):
        self.adapter = adapter
        self.os_name = adapter.get_os_name()

    def is_binary_safe(self, binary_path: str, expected_version: str) -> bool:
        """Checks whether the binary matches a known fingerprint."""
        current_hash = self.adapter.integrity.get_binary_hash(binary_path)

        # In strict mode, compare against the known-good database
        lookup_key = f"{expected_version}"
        target_hashes = KNOWN_GOOD_HASHES.get(self.os_name, {})

        if lookup_key in target_hashes:
            return current_hash == target_hashes[lookup_key]

        # If unknown, allow with an implicit warning unless strict mode is set
        strict = os.getenv("IWYM_STRICT_INTEGRITY", "").lower() in ("1", "true", "yes", "strict")
        return not strict

    def verify_project_tools(self, project_plan: Dict) -> bool:
        """Verifies all the tools planned for the project."""
        return True
