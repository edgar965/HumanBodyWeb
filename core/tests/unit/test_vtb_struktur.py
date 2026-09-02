# -*- coding: utf-8 -*-
u"""Die Lehren, die der Wrapperbaum einhalten muss.

Jede Zusicherung hier steht fuer einen Fehler, den es im Baum wirklich
gab:

* **Ein fester Pfad.** `smplest_x_wrapper` verdrahtete das
  SMPL-X-Verzeichnis auf Laufwerk A:, obwohl der Nachbar daneben seit
  dem 12.08.2026 einen relativen Pfad benutzt. Der feste war der, den
  Django benutzt.
* **Ein Zwischenordner im System-Temp.** `_run_pymafx` legte je Lauf
  eine vollstaendige Bildkopie in `%TEMP%` — mit `finally`-Aufraeumen,
  das ein abgebrochener Prozess nicht mehr ausfuehrt. Vorgeschichte im
  Projekt: rund 100 GB Datenmuell auf C:.
* **Ein Parameter, der ins Leere geht.** `vitpose_det.detect(...,
  model_size='h')` nahm die Modellgroesse entgegen und lud darunter
  immer dasselbe Netz.

Der Aufbau des Baums — eine Quelle je Sache, Fortschrittsprotokoll,
Dateigroesse — steht in `test_vtb_bauform.py`. Der Quelltextzugriff
liegt in `_wrapperquellen.Wrapperquellen`; diese Datei war mit ihm
zusammen 405 Zeilen lang und verletzte damit die Faustregel, die sie
selbst prueft.

BDD - GEGEBEN / DANN
====================
    KeineFestenPfade    ... kein Laufwerksbuchstabe im Quelltext
    KeineSystemablage   ... kein `mkdtemp` ohne `dir=`
    JederParameterWirkt ... kein entgegengenommener Wert bleibt liegen
"""
import ast
import re
import unittest

from ._wrappersuchpfad import Wrappersuchpfad, WRAPPERS
from ._wrapperquellen import Wrapperquellen

Wrappersuchpfad.setzen()


class KeineFestenPfade(unittest.TestCase):
    u"""Pfade kommen aus `Baum`, nicht aus dem Quelltext."""

    #: `A:/…` oder `A:\…` — ein Laufwerksbuchstabe mit Doppelpunkt.
    LAUFWERK = re.compile(r'^[A-Za-z]:[/\\]')

    def test_kein_laufwerksbuchstabe_in_einer_zeichenkette(self):
        for pfad, text in Wrapperquellen.texte():
            for knoten in Wrapperquellen.zeichenketten(ast.parse(text)):
                with self.subTest(datei=pfad.name, zeile=knoten.lineno):
                    self.assertIsNone(
                        self.LAUFWERK.match(knoten.value),
                        '%s:%d verdrahtet ein Laufwerk: %r'
                        % (pfad.name, knoten.lineno, knoten.value))

    def test_die_pruefung_faellt_auf_einen_festen_pfad_herein(self):
        u"""Gegenprobe: erkennt sie einen, der wirklich im Code steht?"""
        baum = ast.parse("SMPLX = 'A:/3DTools/3DObjects'\n"
                         "u'''Docstring mit A:/3DTools darin'''\n")
        werte = [k.value for k in Wrapperquellen.zeichenketten(baum)]
        self.assertIn('A:/3DTools/3DObjects', werte)
        self.assertTrue(any(self.LAUFWERK.match(w) for w in werte))

    def test_die_pruefung_uebergeht_doku(self):
        u"""Und laesst den Docstring in Ruhe, der den Befund beschreibt."""
        baum = ast.parse("u'''Hier stand A:/3DTools/3DObjects.'''\n"
                         "from os import sep\n")
        self.assertEqual([k.value for k in Wrapperquellen.zeichenketten(baum)], [])

    def test_baum_kennt_die_fremdprojekte(self):
        from baum import Baum
        for name in ('GVHMR', 'WHAM', 'PromptHMR', 'SMPLest-X', 'PyMAF-X',
                     '4D-Humans', 'MocapNET', 'OpenPose'):
            with self.subTest(projekt=name):
                self.assertTrue(Baum.im_baum(name).endswith(name))

    def test_umgebungsvariablen_haben_vorrang(self):
        u"""Ein anderer Rechner darf ohne Quelltextaenderung auskommen."""
        text = (WRAPPERS / 'baum.py').read_text(encoding='utf-8')
        for name in ('VTB_ROOT', 'OBJEKTE_DIR', 'SMPLX_DIR'):
            with self.subTest(variable=name):
                self.assertIn("os.environ.get('%s')" % name, text)


class KeineSystemablage(unittest.TestCase):
    u"""Zwischendateien gehoeren ins Projekt, nicht nach C:."""

    #: Alles, was ohne `dir=` in `%TEMP%` landet.
    ABLAGEN = ('mkdtemp', 'mkstemp', 'NamedTemporaryFile',
               'TemporaryDirectory', 'TemporaryFile')

    def _ablageaufrufe(self, baum):
        u"""Die Aufrufe im CODE — der Docstring daneben zaehlt nicht.

        Die erste Fassung suchte per regulaerem Ausdruck im Text und
        meldete `arbeitsablage.py`: Dort steht der behobene Aufruf im
        Docstring, um den Befund zu erklaeren. Zweiter Treffer derselben
        Sorte an einem Tag.
        """
        aus = []
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call):
                continue
            name = getattr(knoten.func, 'attr', None) or getattr(
                knoten.func, 'id', None)
            if name in self.ABLAGEN:
                aus.append((name, knoten.lineno,
                            {w.arg for w in knoten.keywords}))
        return aus

    def test_kein_zwischenspeicher_ohne_zielordner(self):
        u"""Auch `arbeitsablage.py` selbst — dort steht der einzige Aufruf.

        Eine frueher Fassung nahm die Datei ganz aus („dort steht das
        `dir=` selbst") und merkte deshalb NICHT, als die Sabotageprobe
        genau dieses `dir=` entfernte. Ein Ausschluss, der die einzige
        echte Fundstelle trifft, ist kein Ausschluss, sondern eine
        Luecke.
        """
        gefunden = 0
        for pfad, text in Wrapperquellen.texte():
            for name, zeile, benannt in self._ablageaufrufe(ast.parse(text)):
                gefunden += 1
                with self.subTest(datei=pfad.name, zeile=zeile):
                    self.assertIn('dir', benannt,
                                  '%s:%d — %s() ohne `dir=` legt in %%TEMP%% an'
                                  % (pfad.name, zeile, name))
        self.assertGreater(gefunden, 0, 'Die Pruefung findet gar nichts mehr')

    def test_die_pruefung_merkt_ein_fehlendes_dir(self):
        u"""Gegenprobe — und der Docstring daneben bleibt unbeachtet."""
        baum = ast.parse("u'''Hier stand mkdtemp(prefix=\"x_\")'''\n"
                         "import tempfile\n"
                         "a = tempfile.mkdtemp(prefix='x_')\n"
                         "b = tempfile.mkdtemp(prefix='x_', dir='/projekt')\n")
        ohne = [z for _n, z, benannt in self._ablageaufrufe(baum)
                if 'dir' not in benannt]
        self.assertEqual(ohne, [3])

    def test_die_arbeitsablage_liegt_im_projekt(self):
        u"""Verglichen werden PFADTEILE, nicht Zeichen.

        `startswith` bestuende auch ein Nachbarordner mit gleichem
        Namensanfang: `A:/3DTools/VideoToBVH_alt` faengt genauso an wie
        `A:/3DTools/VideoToBVH`. `is_relative_to` vergleicht Teil fuer
        Teil und faellt darauf nicht herein.
        """
        from pathlib import Path

        from arbeitsablage import Arbeitsablage
        from baum import Baum
        self.assertTrue(
            Path(Arbeitsablage.WURZEL).is_relative_to(Path(Baum.WURZEL)),
            'Zwischendateien liegen ausserhalb des Baums: %s'
            % Arbeitsablage.WURZEL)


class JederParameterWirkt(unittest.TestCase):
    u"""Ein entgegengenommener Wert, der nie gelesen wird, ist eine Luege.

    DER BEFUND (01.09.2026): `vitpose_det.detect(..., model_size='h')`
    nahm die Modellgroesse entgegen und rief darunter
    `_create_body('balanced', device)` — fest. Die Einstellung
    `vitpose_model_size` stand im Formular, wanderte durch drei Schichten
    und verschwand in der vierten. Dieselbe Klasse wie
    `setup_camera_from_payload(sd, root)` in `HumanBody/collision`, wo
    `root` nie gelesen wurde und dabei nahelegte, die Kamera haenge an
    der Szenenwurzel.

    Ein Parameter, der absichtlich unbenutzt bleibt (Signaturtreue),
    traegt einen Unterstrich am Anfang.
    """

    def test_kein_parameter_geht_ins_leere(self):
        tot = Wrapperquellen.unbenutzte_parameter
        for pfad, text in Wrapperquellen.texte():
            for name, arg, zeile in tot(ast.parse(text)):
                self.fail('%s:%d — %s() nimmt `%s` entgegen und liest es nie'
                          % (pfad.name, zeile, name, arg))

    def test_die_pruefung_faellt_auf_einen_toten_parameter_herein(self):
        u"""Gegenprobe: erkennt sie den Fall, den es gab?"""
        baum = ast.parse('def detect(video, ausgabe, model_size="h"):\n'
                         '    return bauen("balanced", video, ausgabe)\n')
        tot = Wrapperquellen.unbenutzte_parameter(baum)
        self.assertEqual([(n, a) for n, a, _z in tot],
                         [('detect', 'model_size')])

    def test_ein_unterstrich_nimmt_aus(self):
        baum = ast.parse('def zeichnen(self, _kontext):\n    return 1\n')
        self.assertEqual(Wrapperquellen.unbenutzte_parameter(baum), [])

    def test_weitergereichte_werte_zaehlen_als_gelesen(self):
        baum = ast.parse('def lift(video, ziel, device="cuda"):\n'
                         '    return fahren(video, ziel, device=device)\n')
        self.assertEqual(Wrapperquellen.unbenutzte_parameter(baum), [])
