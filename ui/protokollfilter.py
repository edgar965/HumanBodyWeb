# -*- coding: utf-8 -*-
u"""Testläufe schreiben nicht in die Produktivlogs.

DER BEFUND (10.09.2026, gemessen an `logs/error.log`)
=====================================================
Von 2.799 Fehlerzeilen stammten **1.661 (59 %)** erkennbar aus Testläufen —
und das ist eine Untergrenze, weil nur eindeutige Marken gezählt wurden:
`RuntimeError: kein CUDA` aus `test_hybridlauf`, `Probe: Bild nicht gefunden`
aus den Unterlauf-Fällen, `payload_to_scene_input failed` aus
`test_cloth_bruecke`, und 219-mal „BVH-Wurzel nicht bestimmbar —
HUMANBODY_BVH_DIR='A:\\3DTools\\HumanBody\\data'", was `test_safe_paths` sich
selbst so einstellt.

Das ist keine Kosmetik. **Hilfe → Logs, Reiter „Exceptions", ist der Ort, an
dem ein echter Fehler auffallen soll** — dafür gibt es ihn (siehe
`ui/settings/protokoll.py`: „Eine leere Fehlerseite liest sich wie ‚keine
Fehler'"). Eine Fehlerseite, die zu 59 % aus absichtlich erzeugten Fehlern
besteht, ist genauso unbrauchbar, nur andersherum: Man findet den echten
nicht mehr. Am selben Tag hat ein `ReferenceError` zwölf Tage überlebt, weil
er nur auf der Browserkonsole stand — Fehler sichtbar zu machen und sie
gleichzeitig zuzuschütten, hebt sich auf.

WIE DER TESTLAUF ERKANNT WIRD
=============================
Nicht über `sys.argv`: Hilfe → Tests startet die Suite IM LAUFENDEN PROZESS
(djangoBase `test_befehle`), da steht in `argv` „runserver". Maßgeblich ist
Djangos eigener Schalter — `setup_test_environment()` hängt `outbox` an
`django.core.mail` und `teardown_test_environment()` nimmt es wieder weg.
Genau so lange läuft ein Test.

WAS NICHT GEFILTERT WIRD: die Konsole. Wer einen Testlauf ansieht, soll seine
Meldungen sehen; nur die fünf Dateien bleiben sauber.
"""
import logging

__all__ = ['Testlauf']


class Testlauf(logging.Filter):
    u"""Lässt Datensätze durch, solange KEIN Testlauf läuft."""

    @staticmethod
    def laeuft():
        u"""Ist Djangos Testumgebung gerade aufgebaut?"""
        try:
            from django.core import mail
        except Exception:                      # pragma: no cover
            return False
        return hasattr(mail, 'outbox')

    def filter(self, datensatz):
        return not Testlauf.laeuft()
