# -*- coding: utf-8 -*-
"""
LexWorksEverywhere Logging Utilities - Utilitaires de journalisation
=======================================================

Ce module fournit des utilitaires de journalisation pour LexWorksEverywhere :
- Configuration du système de journalisation
- Gestion des niveaux de journalisation
- Journalisation structurée
- Métriques de performance

Projet développé par : Alexandre Albert Ndour
Date de naissance : 29 janvier 2005
Nationalité : Sénégalaise
"""

import logging
import os
from pathlib import Path
import json
import time
from typing import Dict, Any, Optional
import atexit
from datetime import datetime


class LexWorksEverywhereLogger:
    """Gestionnaire de journalisation pour LexWorksEverywhere."""

    def __init__(self, name: str = "lexworkseverywhere", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self.log_dir = Path.home() / ".lexworks" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.file_handler = logging.FileHandler(self.log_dir / f"lexworks_{datetime.now().strftime('%Y%m%d')}.log")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.console_handler = None
        if os.getenv("LEXWORKS_DEBUG", "").lower() in ("1", "true", "yes"):
            self.console_handler = logging.StreamHandler()
            self.console_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.console_handler)

    def get_logger(self) -> logging.Logger:
        """Retourne le logger configuré."""
        return self.logger

    def log_operation(self, operation: str, details: Dict[str, Any]):
        """
        Journalise une opération avec des détails structurés.
        """
        log_data = {"operation": operation, "timestamp": datetime.now().isoformat(), "details": details}
        self.logger.info(f"OPERATION: {json.dumps(log_data)}")

    def log_error(self, operation: str, error: Exception, details: Dict[str, Any] = None):
        """
        Journalise une erreur avec des détails.
        """
        error_details = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self.logger.error(f"ERROR: {json.dumps(error_details)}")


class PerformanceMetrics:
    """Gestionnaire de métriques de performance pour LexWorksEverywhere."""

    def __init__(self):
        self.metrics = {}
        self.start_times = {}
        atexit.register(self.save_metrics)

    def start_timer(self, operation: str):
        """Démarre un minuteur pour une opération."""
        self.start_times[operation] = time.time()

    def stop_timer(self, operation: str) -> float:
        """Arrête un minuteur et retourne le temps écoulé."""
        if operation in self.start_times:
            elapsed = time.time() - self.start_times[operation]
            del self.start_times[operation]
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(elapsed)
            return elapsed
        return 0.0

    def get_average_time(self, operation: str) -> Optional[float]:
        """Retourne le temps moyen d'une opération."""
        if operation in self.metrics and self.metrics[operation]:
            return sum(self.metrics[operation]) / len(self.metrics[operation])
        return None

    def get_total_operations(self, operation: str) -> int:
        """Retourne le nombre total d'opérations effectuées."""
        return len(self.metrics.get(operation, []))

    def save_metrics(self):
        """Sauvegarde les métriques dans un fichier."""
        metrics_file = Path.home() / ".lexworks" / "metrics.json"
        try:
            with open(metrics_file, "w") as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des métriques: {e}")


_lexworkseverywhere_logger = None
_performance_metrics = PerformanceMetrics()


def get_logger(name: str = "lexworkseverywhere", log_level: str = "INFO") -> logging.Logger:
    """Retourne une instance de logger pour LexWorksEverywhere."""
    global _lexworkseverywhere_logger
    if _lexworkseverywhere_logger is None:
        _lexworkseverywhere_logger = LexWorksEverywhereLogger(name, log_level)
    return _lexworkseverywhere_logger.get_logger()


def log_operation(operation: str, details: Dict[str, Any]):
    """Journalise une opération."""
    global _lexworkseverywhere_logger
    if _lexworkseverywhere_logger is None:
        _lexworkseverywhere_logger = LexWorksEverywhereLogger()
    _lexworkseverywhere_logger.log_operation(operation, details)


def log_error(operation: str, error: Exception, details: Dict[str, Any] = None):
    """Journalise une erreur."""
    global _lexworkseverywhere_logger
    if _lexworkseverywhere_logger is None:
        _lexworkseverywhere_logger = LexWorksEverywhereLogger()
    _lexworkseverywhere_logger.log_error(operation, error, details)


def start_timer(operation: str):
    """Démarre un minuteur."""
    _performance_metrics.start_timer(operation)


def stop_timer(operation: str) -> float:
    """Arrête un minuteur."""
    return _performance_metrics.stop_timer(operation)


def get_average_time(operation: str) -> Optional[float]:
    """Retourne le temps moyen d'une opération."""
    return _performance_metrics.get_average_time(operation)


def get_total_operations(operation: str) -> int:
    """Retourne le nombre total d'opérations effectuées."""
    return _performance_metrics.get_total_operations(operation)
