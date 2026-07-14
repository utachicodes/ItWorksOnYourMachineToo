# -*- coding: utf-8 -*-
from ItWorksOnYourMachineToo.core import i18n


def test_default_locale_is_english():
    i18n.set_locale("en")
    assert i18n.t("success") == "Success"


def test_set_locale_switches_to_french():
    i18n.set_locale("fr")
    try:
        assert i18n.t("success") == "Succès"
    finally:
        i18n.set_locale("en")


def test_set_locale_rejects_unknown_language_by_falling_back_to_english():
    i18n.set_locale("xx")
    try:
        assert i18n.t("success") == "Success"
    finally:
        i18n.set_locale("en")


def test_t_returns_key_when_message_missing():
    i18n.set_locale("en")
    assert i18n.t("no_such_key") == "no_such_key"
