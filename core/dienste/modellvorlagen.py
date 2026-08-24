# -*- coding: utf-8 -*-
"""Modellvorlagen — die gespeicherten Figuren aus dem Modellordner.

Stand zweimal wörtlich im Code (`seite_theatre_einstellungen._modellvorlagen`
und `einstellungen/smplseite._vorlagen`, gefunden 17.08.2026 von `doppelrumpf`):

    ordner = Path(settings.HUMANBODY_MODELS_DIR)
    if not ordner.is_dir():
        return []
    return [f.stem for f in sorted(ordner.glob('*.json'))
            if not f.name.endswith('.scene.json')]

DIE AUSNAHME IST DER GANZE WITZ: `*.json` findet auch die SZENEN — eine Szene
(`.scene.json`) enthält mehrere Figuren samt Licht und Kamera und ist als
Vorgabemodell unbrauchbar. Wer die Zeile beim Kopieren vergisst, bekommt
Szenennamen in der Modellauswahl, und das fällt erst beim Laden auf.
"""

from pathlib import Path

from django.conf import settings


class Modellvorlagen:
    """Namen der Modelldateien — ohne Szenen."""

    #: Diese Endung kennzeichnet eine SZENE, nicht ein Modell.
    SZENE = '.scene.json'

    @classmethod
    def ordner(cls):
        return Path(settings.HUMANBODY_MODELS_DIR)

    @classmethod
    def namen(cls):
        """Sortierte Liste der Modellnamen (Dateiname ohne Endung)."""
        ordner = cls.ordner()
        if not ordner.is_dir():
            return []
        return [f.stem for f in sorted(ordner.glob('*.json'))
                if not f.name.endswith(cls.SZENE)]
