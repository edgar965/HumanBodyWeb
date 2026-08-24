# -*- coding: utf-8 -*-
"""Die sechs Einstellungsseiten — eine Klasse je Datei.

Aus `core/api/einstellungen.py` (332 Zeilen, sechs freie Funktionen mit
demselben Rumpf) am 17.08.2026 hierher aufgeteilt. `urls.py` ruft weiter
`einstellungen.app_settings_model` — die Namen bleiben, der Weg dahinter ist
jetzt eine Klasse (siehe `basis.py`).

Die beiden JSON-Endpunkte, die nur wegen ihres Namens hier lagen
(`ui_prefs_api`, `animationen_der_kategorie`), stehen in
`core/api/ui_vorgaben.py`.
"""

from .basis import Einstellungsseite
from .dreidseite import DreiDEinstellungen
from .ergebnisseite import ErgebnisEinstellungen
from .modellseite import ModellEinstellungen
from .smplseite import SmplEinstellungen
from .szenenseite import SzeneEinstellungen
from .zweidseite import ZweiDEinstellungen

__all__ = [
    'Einstellungsseite', 'ModellEinstellungen', 'ErgebnisEinstellungen',
    'SzeneEinstellungen', 'ZweiDEinstellungen', 'DreiDEinstellungen',
    'SmplEinstellungen',
    'app_settings_model', 'app_settings_result', 'app_settings_scene',
    'app_settings_videobvh_2d', 'app_settings_videobvh_3d', 'app_settings_smpl',
]

app_settings_model = ModellEinstellungen.ansicht('app_settings_model')
app_settings_result = ErgebnisEinstellungen.ansicht('app_settings_result')
app_settings_scene = SzeneEinstellungen.ansicht('app_settings_scene')
app_settings_videobvh_2d = ZweiDEinstellungen.ansicht('app_settings_videobvh_2d')
app_settings_videobvh_3d = DreiDEinstellungen.ansicht('app_settings_videobvh_3d')
app_settings_smpl = SmplEinstellungen.ansicht('app_settings_smpl')
