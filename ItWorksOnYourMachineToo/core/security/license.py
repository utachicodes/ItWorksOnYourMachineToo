# -*- coding: utf-8 -*-
import os


class LicenseManager:
    """
    Handles license integrity and authorship verification.
    """
    AUTHOR = "Abdoullah Ndao"

    @staticmethod
    def verify_license() -> bool:
        license_path = os.path.join(os.getcwd(), "LICENSE")
        if not os.path.exists(license_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            license_path = os.path.join(base_dir, "LICENSE")
        return os.path.exists(license_path)

    @staticmethod
    def get_branding_header() -> str:
        status = "✅ OK" if LicenseManager.verify_license() else "⚠️ LICENSE not found"
        return (
            "[bold blue]ItWorksOnYourMachineToo v2.1.0[/bold blue] | "
            f"[bold white]Created by {LicenseManager.AUTHOR}[/bold white] | "
            f"[italic]{status}[/italic]"
        )
