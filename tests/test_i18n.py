import os
import json
import pytest
from unittest.mock import MagicMock
from src.app.ports import IConfigProvider
from src.infra.translation_service import TranslationService

@pytest.fixture
def temp_locales_dir(tmp_path):
    loc_dir = tmp_path / "locales"
    loc_dir.mkdir()
    
    pt_data = {
        "welcome": "Bem-vindo!",
        "fine_amount": "Multa: ${amount}",
        "only_in_pt": "Apenas PT"
    }
    en_data = {
        "welcome": "Welcome!",
        "fine_amount": "Fine: ${amount}"
    }
    fr_data = {
        "welcome": "Bienvenue!"
    }
    es_data = {
        "welcome": "¡Bienvenido!"
    }
    de_data = {
        "welcome": "Willkommen!"
    }
    
    (loc_dir / "pt.json").write_text(json.dumps(pt_data), encoding="utf-8")
    (loc_dir / "en.json").write_text(json.dumps(en_data), encoding="utf-8")
    (loc_dir / "fr.json").write_text(json.dumps(fr_data), encoding="utf-8")
    (loc_dir / "es.json").write_text(json.dumps(es_data), encoding="utf-8")
    (loc_dir / "de.json").write_text(json.dumps(de_data), encoding="utf-8")
    
    return str(loc_dir)

def test_translation_basic(temp_locales_dir):
    service = TranslationService(locales_dir=temp_locales_dir)
    service.set_locale("en")
    assert service.translate("welcome") == "Welcome!"
    assert service.translate("fine_amount", amount="5.00") == "Fine: $5.00"

def test_translation_fallback_to_pt(temp_locales_dir):
    service = TranslationService(locales_dir=temp_locales_dir)
    service.set_locale("en")
    # 'only_in_pt' is only defined in pt.json, should fallback to pt
    assert service.translate("only_in_pt") == "Apenas PT"

def test_translation_key_not_found(temp_locales_dir):
    service = TranslationService(locales_dir=temp_locales_dir)
    assert service.translate("non_existent_key") == "non_existent_key"

def test_locale_resolution_config_ini(temp_locales_dir):
    config_mock = MagicMock(spec=IConfigProvider)
    config_mock.get_language.return_value = "de"
    
    service = TranslationService(config_provider=config_mock, locales_dir=temp_locales_dir)
    assert service.get_locale() == "de"
    assert service.translate("welcome") == "Willkommen!"

def test_locale_resolution_env_var(temp_locales_dir, monkeypatch):
    monkeypatch.setenv("LANG", "es_ES.UTF-8")
    service = TranslationService(locales_dir=temp_locales_dir)
    assert service.get_locale() == "es"
    assert service.translate("welcome") == "¡Bienvenido!"

def test_locale_resolution_default(temp_locales_dir, monkeypatch):
    # Clear env vars
    monkeypatch.delenv("LANG", raising=False)
    monkeypatch.delenv("LC_ALL", raising=False)
    monkeypatch.delenv("LC_MESSAGES", raising=False)
    
    # Mock locale.getdefaultlocale to return None
    import locale
    monkeypatch.setattr(locale, "getdefaultlocale", lambda: (None, None))
    
    service = TranslationService(locales_dir=temp_locales_dir)
    assert service.get_locale() == "pt"
    assert service.translate("welcome") == "Bem-vindo!"

def test_set_locale_invalid(temp_locales_dir):
    service = TranslationService(locales_dir=temp_locales_dir)
    with pytest.raises(ValueError):
        service.set_locale("invalid_lang")
