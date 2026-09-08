# -*- coding: utf-8 -*-
u"""Die laufende Fassung muss in Hilfe → Versionen auch vorkommen.

DER BEFUND (Edgar, 08.09.2026: „warum steht in der Hilfe 0.58 als Version, im
UI aber 0.57? 0.57 fehlt in der Hilfe - Versionen")
==================================================================
Zwei Quellen, die auseinanderlaufen können: Das UI zeigt `wurzeln.VERSION`, die
Historie kommt aus den **Commit-Betreffs** (`djangobase/views/versions.py`,
`_fetch_commits` — erkannt wird `v0.57` oder `Version 0.57`). Der Bump auf 0.57
steckte in `93b8fa1` („UMA Python gegen Unity gemessen …"), also ohne Marke;
nur HumanBodyBlender hatte einen Commit namens „Version 0.57". Auf der Seite
gemessen: 13× `v0.58-dev` (das Etikett für „noch nicht ausgeliefert"), 1× 0.57.

DIESER TEST PRÜFT DIE ODER-BEDINGUNG, NICHT DEN EINTRAG
=======================================================
Richtig ist die Fassung genau dann vertreten, wenn sie **entweder** ein
Commit-Betreff nennt **oder** `manual_versions` sie nachträgt. Auf den Eintrag
allein zu prüfen wäre falsch: Beim nächsten sauber benannten Bump gibt es ihn
zu Recht nicht, und der Test wäre rot, obwohl die Seite stimmt. Auf den Betreff
allein zu prüfen wäre ebenso falsch — dann müsste die Historie umgeschrieben
werden, sobald einmal etwas durchgerutscht ist.

Der Test liest `git log` aus dem Arbeitsverzeichnis; ohne Repo (Auslieferung
ohne `.git`) zählt nur die manuelle Liste, und das genügt ihm.
"""
import re
import subprocess
import unittest

from django.conf import settings
from django.test import SimpleTestCase

#: Dieselbe Erkennung wie in djangoBase — Marke irgendwo im Betreff.
MARKE = re.compile(r"(?:^|[\s\(\[\+,—\-])(?:v|Version\s+)(\d+\.\d+(?:\.\d+)?)\b",
                   re.I)

#: So viele Betreffs reichen: Ein Bump liegt nie hundert Commits zurück.
TIEFE = 100


def _betreff_fassungen():
    u"""Fassungsnummern aus den letzten Commit-Betreffs dieses Repos."""
    try:
        lauf = subprocess.run(
            ["git", "-C", str(settings.BASE_DIR), "log", "-%d" % TIEFE,
             "--pretty=format:%s"],
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.TimeoutExpired):
        return set()
    if lauf.returncode != 0:
        return set()
    gefunden = set()
    for zeile in lauf.stdout.splitlines():
        treffer = MARKE.search(zeile.strip())
        if treffer:
            gefunden.add(treffer.group(1))
    return gefunden


def _manuelle_fassungen():
    eintraege = (getattr(settings, "DJANGOBASE", {}) or {}).get(
        "manual_versions") or []
    return {str(e.get("version", "")).lstrip("v").strip() for e in eintraege}


class VersionshistorieTest(SimpleTestCase):
    u"""Was das UI zeigt, muss die Versionsseite auch kennen."""

    def test_laufende_fassung_ist_in_der_historie_vertreten(self):
        laufend = str(settings.VERSION).lstrip("v").strip()
        betreffe = _betreff_fassungen()
        manuell = _manuelle_fassungen()
        self.assertIn(
            laufend, betreffe | manuell,
            u"Fassung %s steht im UI, aber Hilfe → Versionen kennt sie nicht: "
            u"kein Commit-Betreff mit der Marke (gefunden: %s) und kein "
            u"Eintrag in ui/settings/versionsliste.py (dort: %s). Beim Bump "
            u"gehört die Nummer in den Commit-Betreff; nachträglich hilft nur "
            u"die manuelle Liste." % (laufend,
                                      ", ".join(sorted(betreffe)) or "keine",
                                      ", ".join(sorted(manuell)) or "keine"))

    def test_die_erkennung_findet_wirklich_etwas(self):
        u"""Gegenprobe: Ein Prüfer, der nie etwas findet, meldet immer Erfolg.

        Ohne diesen Fall wäre der Test oben auch dann grün, wenn `git` fehlt
        UND jemand die manuelle Liste als Sammelbecken benutzt — die Bedingung
        würde nur noch von der Liste getragen, ohne dass es auffällt.
        """
        if not _betreff_fassungen():
            self.skipTest(u"Kein Git-Repo erreichbar — nur manuelle Liste.")
        self.assertTrue(_betreff_fassungen(),
                        u"Die Betreff-Erkennung findet in 100 Commits keine "
                        u"einzige Fassung — dann prüft der Test oben nichts.")

    def test_die_marke_greift_wie_bei_djangobase(self):
        u"""Dieselben Formen, die `_fetch_commits` erkennt — und die falschen."""
        for zeile, erwartet in (
                ("Version 0.57", "0.57"),
                ("v0.57: Umbau", "0.57"),
                ("MakeHuman zieht aus — Version 0.56", "0.56"),
                ("UMA Python gegen Unity gemessen: Kopf, Skelett", None),
                ("LongRunner: elf Module über 5 s heraus", None)):
            treffer = MARKE.search(zeile)
            self.assertEqual(treffer.group(1) if treffer else None, erwartet,
                             u"Betreff %r wurde falsch eingestuft" % zeile)


if __name__ == "__main__":
    unittest.main()
