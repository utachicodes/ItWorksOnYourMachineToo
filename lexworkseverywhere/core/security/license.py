# -*- coding: utf-8 -*-
import hashlib
import os


class LicenseManager:
    """
    Gère la vérification de l'intégrité de la licence et de la paternité.
    """
    AUTHOR = "Alexandre Albert Ndour"
    # Hash SHA256 de la licence officielle
    LICENSE_HASH = "71eb41a4ea6f24feff3bbfa8ebc7cf9daeefcc2f9c55992efc7079574eb2db7d"

    @staticmethod
    def verify_license() -> bool:
        """Vérifie si le fichier LICENSE local correspond à l'original."""
        license_path = os.path.join(os.getcwd(), "LICENSE")
        if not os.path.exists(license_path):
            # Tenter de trouver le fichier LICENSE à la racine du package s'il est installé
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            license_path = os.path.join(base_dir, "LICENSE")

        if not os.path.exists(license_path):
            return False

        with open(license_path, "rb") as f:
            current_hash = hashlib.sha256(f.read()).hexdigest()

        return current_hash == LicenseManager.LICENSE_HASH

    @staticmethod
    def get_branding_header() -> str:
        """Retourne la bannière officielle de branding avec le drapeau du Sénégal."""
        # Drapeau du Sénégal : Vert, Jaune avec étoile Verte, Rouge
        flag = "[bold green]█[/bold green][on yellow][bold green]★[/bold green][/on yellow][bold red]█[/bold red]"
        status = "✅ Authentique" if LicenseManager.verify_license() else "⚠️ License Modifiée"
        return (
            f"{flag} "
            "[bold blue]LexWorksEverywhere v2.1.0[/bold blue] | "
            f"[bold white]Created by {LicenseManager.AUTHOR}[/bold white] | "
            f"[italic]{status}[/italic]"
        )
