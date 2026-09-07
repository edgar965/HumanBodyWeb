# -*- coding: utf-8 -*-
u"""Zwei Quellen fuer denselben Ort duerfen nicht auseinanderlaufen.

WARUM (07.09.2026, Umzug der 18 mh-Dienste nach `A:\\3DTools\\MakeHuman`)
=======================================================================
Das Paket `MakeHuman` fragt seit dem Umzug kein Django mehr: `Mhpfade`
rechnet seine fuenf Verzeichnisse aus der eigenen Lage. Die Einstellungen
fuehren `MAKEHUMAN_ROOT` und die vier Ableitungen aber weiter — der
Language-Server braucht sie (`ls_extra_pfade`), die Nur-Lesen-Pruefung
(`daten_nur_lesen`) und `local_settings.py`, das ausdruecklich anbietet,
Pfade umzulenken.

**Damit gibt es zwei Wahrheiten.** Sie stimmen heute ueberein; ob sie es
morgen noch tun, entscheidet niemand bewusst — wer eine der beiden Seiten
verschiebt, merkt nichts. Der Fehler taucht erst beim Laden eines Netzes
auf, und dort sieht er aus wie eine fehlende Datei.

Dieser Fall ist die Klammer. Er ist absichtlich stumpf: Er prueft
Gleichheit, nicht Existenz — wo der Bestand liegt, ist eine andere Frage
(`Mhpfade.vorhanden()`).
"""
from django.conf import settings
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.assets()

from MakeHuman.pfade import Mhpfade                        # noqa: E402


class MhpfadeTest(SimpleTestCase):

    databases = []

    #: (Methode von `Mhpfade`, Name der Einstellung)
    PAARE = (('wurzel', 'MAKEHUMAN_ROOT'),
             ('daten', 'MAKEHUMAN_DATA_DIR'),
             ('ziele', 'MAKEHUMAN_ZIELE_DIR'),
             ('modifikatoren', 'MAKEHUMAN_MODIFIER_DIR'),
             ('zielablage', 'MAKEHUMAN_ZIELABLAGE'),
             ('kleiderbibliothek', 'HUMANBODY_GARMENT_LIBRARY_DIR'))

    def test_paket_und_einstellungen_meinen_denselben_ort(self):
        abweichend = []
        for methode, einstellung in self.PAARE:
            paket = str(getattr(Mhpfade, methode)())
            gesetzt = str(getattr(settings, einstellung))
            if paket != gesetzt:
                abweichend.append('%s: %s != settings.%s (%s)'
                                  % (methode, paket, einstellung, gesetzt))
        self.assertEqual(abweichend, [], '; '.join(abweichend))

    def test_der_bestand_liegt_da(self):
        u"""`base.obj` ist die Probe: Ohne sie gelten die Vertexnummern
        aller 1.280 Ziele nicht mehr."""
        self.assertTrue(Mhpfade.vorhanden(), Mhpfade.wurzel())
        self.assertTrue(Mhpfade.kleider_vorhanden(),
                        Mhpfade.kleiderbibliothek())

    def test_umlenken_und_zuruecksetzen(self):
        u"""Beide Angaben muessen zurueckkommen.

        `zuruecksetzen()` hat anfangs nur die Wurzel geloest — eine
        umgelenkte Kleiderbibliothek waere im naechsten Testfall stehen
        geblieben, und der haette auf einem leeren Ordner gemessen
        (`~/.claude/rules/test-isolation.md`).
        """
        self.addCleanup(Mhpfade.zuruecksetzen)
        Mhpfade.setzen(r'X:\gibtsnicht')
        Mhpfade.kleider_setzen(r'X:\auchnicht')
        self.assertEqual(str(Mhpfade.wurzel()), r'X:\gibtsnicht')
        self.assertEqual(str(Mhpfade.daten()),
                         r'X:\gibtsnicht\makehuman\data')
        self.assertEqual(str(Mhpfade.kleiderbibliothek()), r'X:\auchnicht')
        self.assertFalse(Mhpfade.vorhanden())
        Mhpfade.zuruecksetzen()
        self.assertEqual(str(Mhpfade.wurzel()),
                         str(settings.MAKEHUMAN_ROOT))
        self.assertEqual(str(Mhpfade.kleiderbibliothek()),
                         str(settings.HUMANBODY_GARMENT_LIBRARY_DIR))

    def test_das_paket_fragt_kein_django(self):
        u"""Die eigentliche Aussage des Umzugs — und sie ist pruefbar.

        Ein `from django.conf import settings` in einem der 20 Module
        bindet das ganze Paket wieder an die Web-Anwendung. Kommentare und
        Docstrings sind ausgenommen: Dort steht die Begruendung.
        """
        import ast
        from pathlib import Path
        wurzel = Path(str(settings.MAKEHUMAN_ROOT))
        treffer = []
        for pfad in sorted(wurzel.glob('*.py')):
            baum = ast.parse(pfad.read_text(encoding='utf-8'))
            for knoten in ast.walk(baum):
                namen = []
                if isinstance(knoten, ast.Import):
                    namen = [t.name for t in knoten.names]
                elif isinstance(knoten, ast.ImportFrom):
                    namen = [knoten.module or '']
                if any(n.split('.')[0] == 'django' for n in namen):
                    treffer.append('%s:%d' % (pfad.name, knoten.lineno))
        self.assertEqual(treffer, [], 'Django im Paket: %s' % treffer)
