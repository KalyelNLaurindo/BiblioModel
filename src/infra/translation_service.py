import os
import json
import locale
from typing import Dict, Any, Optional
from src.app.ports import ITranslationService, IConfigProvider

class TranslationService(ITranslationService):
    """
    Concrete adapter for loading localized string resources from locales/ directory,
    resolving the active language from a hierarchical resolution path, and performing translation.
    """

    def __init__(self, config_provider: IConfigProvider = None, locales_dir: str = None) -> None:
        self.config_provider = config_provider
        if not locales_dir:
            import sys
            base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
            locales_dir = os.path.join(base_path, "locales")
        self.locales_dir = locales_dir
        self._active_locale: Optional[str] = None
        self._translations: Dict[str, Dict[str, str]] = {}
        self._load_all_locales()

    def _load_all_locales(self) -> None:
        supported = ["pt", "en", "fr", "es", "de"]
        for lang in supported:
            file_path = os.path.join(self.locales_dir, f"{lang}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self._translations[lang] = json.load(f)
                except Exception:
                    self._translations[lang] = {}
            else:
                self._translations[lang] = {}

    def set_locale(self, locale_str: str) -> None:
        """
        Manually overrides the active locale.
        """
        lang = locale_str.split("_")[0].lower()
        if lang in self._translations:
            self._active_locale = lang
        else:
            raise ValueError(f"Unsupported locale: {locale_str}")

    def get_locale(self) -> str:
        """
        Resolves the active language using the hierarchy:
        1. Manually overridden active locale
        2. config.ini [library] lang entry
        3. System environment/locale settings
        4. Default fallback: 'pt'
        """
        if self._active_locale:
            return self._active_locale

        # 2. Config Provider
        if self.config_provider:
            cfg_lang = self.config_provider.get_language()
            if cfg_lang:
                lang = cfg_lang.strip().lower()
                if lang in self._translations:
                    return lang

        # 3. System environment/locale settings
        try:
            for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
                val = os.environ.get(var)
                if val:
                    lang = val.split(".")[0].split("_")[0].lower()
                    if lang in self._translations:
                        return lang
            
            loc = locale.getdefaultlocale()[0]
            if loc:
                lang = loc.split("_")[0].lower()
                if lang in self._translations:
                    return lang
        except Exception:
            pass

        # 4. Default pt
        return "pt"

    def translate(self, key: str, **kwargs) -> str:
        """
        Translates a string resource key into the active locale, interpolating variables.
        """
        lang = self.get_locale()
        
        # Check active locale first
        strings = self._translations.get(lang, {})
        template = strings.get(key)
        
        # Fallback to 'en' if not found and active is not 'en'
        if template is None and lang != "en":
            strings_en = self._translations.get("en", {})
            template = strings_en.get(key)
            
        # Fallback to 'pt' if still not found and active is not 'pt'
        if template is None and lang != "pt":
            strings_pt = self._translations.get("pt", {})
            template = strings_pt.get(key)

        if template is None:
            # If still not found, return key itself
            return key

        try:
            return template.format(**kwargs)
        except Exception:
            return template
