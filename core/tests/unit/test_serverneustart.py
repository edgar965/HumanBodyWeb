# -*- coding: utf-8 -*-
u"""`restart_server.py` darf nur den Server DIESES Projekts beenden.

WAS PASSIERT IST (10.09.2026): Die alte Fassung suchte so:

    if 'python' in text and 'manage.py' in text and 'runserver' in text:
        proc.kill()

Darauf passt jeder Django-Entwicklungsserver auf diesem Rechner. Ein Lauf
hat neben den beiden eigenen auch

    A:\\shortlongx\\pythonVENV\\Scripts\\python.exe manage.py runserver_dual
        [::]:5020 --noreload --nostatic

beendet — ein fremdes Projekt. Edgar arbeitet regelmäßig mit mehreren
Projekten gleichzeitig; ein Werkzeug, das „alle Django-Server" trifft,
bricht fremde Arbeit ab.

Der zweite Fehler war subtiler und hätte die Reparatur selbst getroffen:
Ein Diagnoseskript, das mit `python -c "…manage.py…runserver…"` nach genau
diesen Servern sucht, trägt die Wörter in seiner eigenen Kommandozeile.
Wer den zusammengesetzten Text prüft, beendet damit sich selbst.

Hier steht deshalb beides fest: was als Server GILT, und was nicht.
"""

import importlib.util
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

WURZEL = Path(settings.BASE_DIR)


def _laden():
    u"""`restart_server.py` liegt in der Projektwurzel, nicht im Paket."""
    pfad = WURZEL / 'restart_server.py'
    spec = importlib.util.spec_from_file_location('restart_server', pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul.Serverneustart


class ServerneustartTest(SimpleTestCase):

    def setUp(self):
        self.neustart = _laden()

    # --------------------------------------------- Was als Server gilt

    def test_ein_echter_runserver_wird_erkannt(self):
        self.assertTrue(self.neustart._ist_runserver(
            ['python.exe', 'manage.py', 'runserver', '8081']))

    def test_auch_mit_vollem_pfad_und_eigenem_befehl(self):
        u"""`runserver_dual` ist shortlongx' Variante — auch ein Server."""
        self.assertTrue(self.neustart._ist_runserver(
            ['python.exe', 'A:/x/manage.py', 'runserver_dual', '[::]:5020']))

    def test_ein_pruefskript_ist_kein_server(self):
        u"""Sonst beendet die Reparatur sich selbst."""
        self.assertFalse(self.neustart._ist_runserver(
            ['python.exe', '-c', 'import psutil  # manage.py runserver suchen']))

    def test_ein_grep_darueber_ist_kein_server(self):
        self.assertFalse(self.neustart._ist_runserver(
            ['bash.exe', '-c', 'grep manage.py runserver logs/django.log']))

    def test_andere_manage_befehle_bleiben_unberuehrt(self):
        u"""Ein laufender Testlauf oder eine Migration ist kein Server."""
        for befehl in ('test', 'migrate', 'shell', 'collectstatic'):
            self.assertFalse(
                self.neustart._ist_runserver(['python.exe', 'manage.py', befehl]),
                befehl)

    # ------------------------------------------ Was als „unseres" gilt

    def test_nur_das_eigene_verzeichnis_zaehlt(self):
        u"""Der Kern: ein fremdes Projekt darf nie getroffen werden."""
        eigen = mock.Mock()
        eigen.cwd.return_value = str(self.neustart.WURZEL)
        fremd = mock.Mock()
        fremd.cwd.return_value = r'A:\shortlongx\shortlongxWeb'
        self.assertTrue(self.neustart._hier(eigen))
        self.assertFalse(self.neustart._hier(fremd))

    def test_ein_unlesbares_verzeichnis_bleibt_am_leben(self):
        u"""Im Zweifel lieber ein Server zu viel als ein fremder weniger."""
        import psutil
        stumm = mock.Mock()
        stumm.cwd.side_effect = psutil.AccessDenied(1)
        self.assertFalse(self.neustart._hier(stumm))

    # ------------------------------------------------------ Der Start

    def test_gestartet_wird_mit_dem_python_dieses_laufs(self):
        u"""Nicht `python` aus dem PATH — damit kam der Server nicht hoch."""
        import sys
        self.assertEqual(self.neustart.python(), sys.executable)

    def test_der_port_wird_ueber_127_0_0_1_geprueft(self):
        u"""Nie `localhost`: Die IPv6-Aufloesung kostet unter Windows Sekunden.

        (`~/.claude/rules/zeit-messen.md` — dort ist derselbe Fehler mit
        2,05 s gegen 0,03 s gemessen.)
        """
        with mock.patch('socket.create_connection') as verbindung:
            self.neustart.erreichbar()
        adresse, _ = verbindung.call_args[0]
        self.assertEqual(adresse[0], '127.0.0.1')
