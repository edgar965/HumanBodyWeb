# -*- coding: utf-8 -*-
"""Wächter für PipelineProzess — Zeichensatz, stderr und Rückgabewert.

WARUM DIESER TEST EXISTIERT (12.08.2026)
----------------------------------------
Django (3.14) startet die Pipelines in der ML-Umgebung (3.10) und liest deren
stdout als Fortschrittskanal. Vor dem Umbau setzte nur EINE von vier Startstellen
`encoding='utf-8'` — die übrigen verliessen sich auf die Windows-Landeseinstellung
(hier gemessen: cp1252). Und eine Stelle liess `stderr=PIPE` unbeaufsichtigt,
womit ein gesprächiger Kindprozess den Pipe-Puffer füllen und beide Seiten zum
Warten bringen kann.

Beides fällt im Alltag nicht auf: Der Fehler tritt erst auf, wenn eine Ausgabe
Sonderzeichen enthält (ein Dateiname wie `0030_BallettLänger.mp4` genügt) oder
wenn eine Pipeline viel auf stderr schreibt. Deshalb hier echte Subprozesse mit
genau diesen Eigenschaften — kein Mock, denn geprüft wird das Verhalten von
Betriebssystem und Zeichensatz, nicht die eigene Logik.

Die Tests laufen mit dem Django-Python und ohne Grafikkarte; sie brauchen wenige
Sekunden.
"""
import sys

from django.test import SimpleTestCase

from core.pipeline_process import PipelineProzess


class PipelineProzessTest(SimpleTestCase):
    """Startet kleine Python-Prozesse und prüft, was ankommt."""

    def test_umlaute_kommen_unbeschaedigt_an(self):
        """DER FEHLER DER ALTEN STELLEN: cp1252 statt UTF-8.

        Der Kindprozess schreibt bewusst Umlaute und ein Zeichen ausserhalb von
        cp1252 (ein Fortschrittsblock, wie tqdm ihn benutzt)."""
        p = PipelineProzess.starten(
            [sys.executable, '-c',
             'print("TOTAL:5"); print("Datei: 0030_BallettLänger.mp4 █ 50%")'])
        zeilen = [z.strip() for z in p.proc.stdout]
        p.warten(timeout=30)
        self.assertIn('TOTAL:5', zeilen)
        self.assertTrue(any('BallettLänger' in z for z in zeilen),
                        'Umlaut kam nicht durch: %r' % zeilen)
        self.assertTrue(any('█' in z for z in zeilen),
                        'Zeichen ausserhalb cp1252 kam nicht durch: %r' % zeilen)
        self.assertEqual(p.proc.returncode, 0)

    def test_kaputte_bytes_beenden_die_leseschleife_nicht(self):
        """`errors='replace'`: Eine Antwort mit Ersatzzeichen ist brauchbar, ein
        Absturz mitten im Lesen nicht — dann gilt der Auftrag als gescheitert,
        während die Pipeline weiterrechnet."""
        p = PipelineProzess.starten(
            [sys.executable, '-c',
             'import sys; sys.stdout.buffer.write(b"STATUS:\\xff\\xfe kaputt\\n"); '
             'sys.stdout.buffer.write(b"TOTAL:7\\n")'])
        zeilen = [z.strip() for z in p.proc.stdout]     # darf NICHT werfen
        p.warten(timeout=30)
        self.assertIn('TOTAL:7', zeilen)

    def test_viel_stderr_fuehrt_nicht_zum_haenger(self):
        """DER HAENGER-KANDIDAT (OpenPose/Caffe): stderr voll, niemand liest.

        Ohne mitlesenden Faden blockiert der Kindprozess beim Schreiben, sobald
        der Pipe-Puffer voll ist, während der Vater auf die nächste stdout-Zeile
        wartet.

        DIE MENGE IST GEMESSEN (Docu/gegenprobe_stderr_haenger.py, 12.08.2026):
        Der alte Zustand (stderr=PIPE ohne Abräumen) blockiert bereits bei
        49 KB — und zwar dauerhaft, weil die Blockade in `for … in proc.stdout`
        sitzt, wo keine Zeitschranke greift. Der neue Weg läuft in 0,1 s durch.
        Ein erster Messversuch hatte "kein Hänger" gemeldet, weil er nicht wie
        der echte Code von stdout las — deshalb steht die Zahl hier mit Quelle."""
        p = PipelineProzess.starten(
            [sys.executable, '-c',
             'import sys\n'
             'for i in range(2000): sys.stderr.write("W" * 100 + "\\n")\n'
             'sys.stderr.flush()\n'
             'print("TOTAL:9")\n'])
        zeilen = [z.strip() for z in p.proc.stdout]
        code = p.warten(timeout=60)
        self.assertIn('TOTAL:9', zeilen, 'stdout kam nicht an — Puffer-Hänger?')
        self.assertEqual(code, 0)
        self.assertGreater(len(p.stderr_zeilen), 100, 'stderr wurde nicht mitgelesen')

    def test_stderr_wird_begrenzt(self):
        """Die Fehlermeldung soll nicht Zehntausende Fortschrittszeilen halten."""
        p = PipelineProzess.starten(
            [sys.executable, '-c',
             'import sys\n'
             'for i in range(3000): sys.stderr.write(f"Zeile {i}\\n")\n'])
        p.warten(timeout=60)
        self.assertLessEqual(len(p.stderr_zeilen), PipelineProzess.STDERR_ZEILEN + 1)
        self.assertIn('Zeile 2999', p.fehlertext(), 'die LETZTEN Zeilen fehlen')

    def test_rueckgabewert_wird_durchgereicht(self):
        p = PipelineProzess.starten([sys.executable, '-c', 'import sys; sys.exit(3)'])
        self.assertEqual(p.warten(timeout=30), 3)

    def test_umgebung_setzt_utf8_und_entfernt_pythonpath(self):
        """PYTHONPATH darf nicht von 3.14 nach 3.10 durchsickern."""
        env = PipelineProzess.umgebung({'EIGEN': 'wert'})
        self.assertEqual(env['PYTHONIOENCODING'], 'utf-8')
        self.assertEqual(env['PYTHONUTF8'], '1')
        self.assertEqual(env['PYTHONUNBUFFERED'], '1')
        self.assertNotIn('PYTHONPATH', env)
        self.assertNotIn('PYTHONHOME', env)
        self.assertEqual(env['EIGEN'], 'wert')

    def test_beenden_raeumt_den_prozess_ab(self):
        p = PipelineProzess.starten([sys.executable, '-c', 'import time; time.sleep(60)'])
        p.beenden()
        p.proc.wait(timeout=30)
        self.assertIsNotNone(p.proc.poll(), 'Prozess laeuft noch')
