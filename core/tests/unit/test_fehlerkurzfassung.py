# -*- coding: utf-8 -*-
u"""`Fehlerkurzfassung`: die eine Zeile, die in die Auftragsliste passt.

WARUM DIESE TESTS ERST JETZT ENTSTEHEN (29.08.2026)
===================================================
Die Rechnung stand in `BVHJob.error_summary` — und `core/models/` war für den
ganzen Werkzeugkasten UNSICHTBAR: `"models"` stand in der Ausschlussliste von
djangoBase, gedacht für Ordner mit ML-Gewichten. Vierzehn Dateien lagen
außerhalb jeder Prüfung, diese acht Verzweigungen mittendrin.

WAS DIE FÄLLE FESTNAGELN
========================
* Die LETZTE `Fehlertyp: Text`-Zeile gewinnt. Bei verketteten Ausnahmen
  („During handling of the above exception …") ist die letzte die, die
  wirklich abgebrochen hat — die erste ist die, die überdeckt wurde.
* `File "...", line 42` wird übergangen. Sie enthält einen Doppelpunkt und
  steht im Traceback direkt vor der gesuchten Zeile; ohne die Ausnahme wäre
  sie das Ergebnis.
* Der Vorspann bleibt. Die Pipeline schreibt vor dem Traceback ihre eigene
  Einordnung („GVHMR-Lauf gescheitert"); beides zusammen sagt mehr.
"""
from django.test import SimpleTestCase

from core.daten.fehlerkurzfassung import Fehlerkurzfassung

TRACEBACK = '''GVHMR-Lauf gescheitert:
Traceback (most recent call last):
  File "A:\\3DTools\\VideoToBVH\\gvhmr_lift.py", line 42, in fahren
    modell.laden()
  File "A:\\3DTools\\VideoToBVH\\modell.py", line 7, in laden
    raise RuntimeError('kein CUDA')
RuntimeError: kein CUDA
'''

VERKETTET = '''Traceback (most recent call last):
  File "a.py", line 1, in <module>
    raise ValueError('erste')
ValueError: erste

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "b.py", line 2, in <module>
    raise RuntimeError('zweite')
RuntimeError: zweite
'''


class KurzfassungTest(SimpleTestCase):

    def test_ohne_meldung_kommt_nichts(self):
        self.assertEqual(Fehlerkurzfassung.aus(''), '')
        self.assertEqual(Fehlerkurzfassung.aus(None), '')

    def test_ohne_traceback_die_erste_zeile(self):
        self.assertEqual(
            Fehlerkurzfassung.aus('Datei nicht gefunden\nund noch mehr'),
            'Datei nicht gefunden')

    def test_vorspann_und_fehlerzeile_zusammen(self):
        self.assertEqual(Fehlerkurzfassung.aus(TRACEBACK),
                         'GVHMR-Lauf gescheitert: RuntimeError: kein CUDA')

    def test_die_dateizeile_wird_uebergangen(self):
        u"""`File "...", line 7` steht direkt vor der gesuchten Zeile und
        enthält ebenfalls einen Doppelpunkt."""
        self.assertNotIn('File ', Fehlerkurzfassung.aus(TRACEBACK))

    def test_bei_verketteten_ausnahmen_gewinnt_die_letzte(self):
        u"""Die letzte hat wirklich abgebrochen; die erste wurde überdeckt."""
        self.assertEqual(Fehlerkurzfassung.aus(VERKETTET),
                         'RuntimeError: zweite')

    def test_ohne_vorspann_nur_die_fehlerzeile(self):
        self.assertEqual(Fehlerkurzfassung.aus(VERKETTET).count(':'), 1)

    def test_nur_vorspann_wenn_keine_fehlerzeile_da_ist(self):
        self.assertEqual(
            Fehlerkurzfassung.aus('Abbruch durch den Benutzer:\n'
                                  'Traceback (most recent call last):\n'
                                  '  File "a.py", line 1, in <module>\n'),
            'Abbruch durch den Benutzer')

    def test_ersatztext_wenn_gar_nichts_brauchbar_ist(self):
        u"""Ein abgeschnittener Traceback ohne Vorspann — die Liste zeigt
        dann lieber einen ehrlichen Satz als eine leere Zelle."""
        self.assertEqual(
            Fehlerkurzfassung.aus('Traceback (most recent call last):\n'
                                  '  File "a.py", line 1, in <module>\n'),
            Fehlerkurzfassung.ERSATZ)


class AmModellTest(SimpleTestCase):
    u"""Die Eigenschaft am Auftrag benutzt dieselbe Rechnung."""

    def test_error_summary_reicht_durch(self):
        from core.models import BVHJob
        auftrag = BVHJob(name='x', error_message=TRACEBACK)
        self.assertEqual(auftrag.error_summary,
                         'GVHMR-Lauf gescheitert: RuntimeError: kein CUDA')
