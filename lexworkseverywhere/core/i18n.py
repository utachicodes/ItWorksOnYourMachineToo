LANG = "en"

MESSAGES = {
    "en": {
        "app_title": "LexWorksEverywhere: Universal development environment manager (v2 Core PUR).",
        "scan_start": "Scanning project...",
        "prepare_env": "Preparing environment...",
        "execute": "Executing...",
        "success": "Success",
        "failure": "Execution failed",
        "fatal_error": "Fatal error",
        "profile_saved": "Profile captured and saved to",
        "capture_failed": "Capture failed",
        "doctor_title": "LexWorksEverywhere Doctor - System diagnostics",
        "doctor_table_title": "Environment checks",
        "component": "Component",
        "status": "Status",
        "details": "Details",
        "python_version": "Python version",
        "os_name": "Operating system",
        "memory": "Available memory",
        "disk": "Disk space (/)",
        "adapter": "OS adapter",
        "ready": "Your system is ready for LexWorksEverywhere",
        "attention": "Some critical components need your attention",
        "ok": "OK",
        "low": "Low",
        "warn": "Warning",
        "error": "Error",
        "lang_set": "Language set to",
    },
    "fr": {
        "app_title": "LexWorksEverywhere : Gestionnaire d'environnement universel (v2 Core PUR).",
        "scan_start": "Scan du projet...",
        "prepare_env": "Préparation de l'environnement...",
        "execute": "Exécution...",
        "success": "Succès",
        "failure": "Échec de l'exécution",
        "fatal_error": "Erreur fatale",
        "profile_saved": "Profil capturé et sauvegardé dans",
        "capture_failed": "Échec de la capture",
        "doctor_title": "LexWorksEverywhere Doctor - Diagnostic du système",
        "doctor_table_title": "Vérifications de l'environnement",
        "component": "Composant",
        "status": "Statut",
        "details": "Détails",
        "python_version": "Version Python",
        "os_name": "Système d'exploitation",
        "memory": "Mémoire disponible",
        "disk": "Espace disque (/)",
        "adapter": "Adaptateur OS",
        "ready": "Votre système est prêt pour LexWorksEverywhere",
        "attention": "Certains composants critiques nécessitent votre attention",
        "ok": "OK",
        "low": "Bas",
        "warn": "Avertissement",
        "error": "Erreur",
        "lang_set": "Langue définie sur",
    },
}


def set_locale(lang: str) -> None:
    global LANG
    LANG = "fr" if lang == "fr" else "en"


def t(key: str) -> str:
    return MESSAGES.get(LANG, MESSAGES["en"]).get(key, key)
