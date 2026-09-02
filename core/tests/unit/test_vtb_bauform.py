# -*- coding: utf-8 -*-
u"""Der Aufbau des Wrapperbaums bleibt, wie er nach dem Umbau ist.

* **Zwei Quellen fuer dasselbe.** Modell laden, Gelenke rechnen, Masse
  nehmen — dreimal wortgleich in zwei Dateien, und zwei Korrekturen
  hatten nur eine der beiden erreicht. Gemessen: 16,4 cm Unterschied in
  der gemeldeten Koerpergroesse.
* **Das Fortschrittsprotokoll.** `TOTAL:`, `PROGRESS:` und `STATUS:`
  liest Django zeilenweise aus stdout. Wer sie auf einen Logger
  umstellt — was jede Aufraeumregel nahelegt —, laesst den
  Fortschrittsbalken stehen, ohne dass etwas rot wird.
* **Monolithen.** Drei Dateien lagen ueber 300 Zeilen, die groesste bei
  796.

Die Lehren (feste Pfade, Systemablage, tote Parameter) stehen in
`test_vtb_struktur.py`.

BDD - GEGEBEN / DANN
====================
    EineQuelle               ... Modell und Masse gibt es nur einmal
    DasFortschrittsprotokoll ... bleibt `print` mit `flush`
    DieDateigroesse          ... bleibt unter der Faustregel
    JederRunnerLiefertSeineFelder ... nichts faellt beim Umbau weg
"""
import ast
import re
import unittest

from ._wrappersuchpfad import Wrappersuchpfad, WRAPPERS
from ._wrapperquellen import Wrapperquellen

Wrappersuchpfad.setzen()


class EineQuelle(unittest.TestCase):
    u"""Was zweimal dastand, hat zwei Korrekturen nur halb bekommen."""

    #: Namen, die es im Baum genau EINMAL auf Modulebene geben darf.
    EINMALIG = ('Smplxmodell', 'Koerpermasse', 'Baum', 'Videolauf',
                'Csvschreiber', 'Koerperpunkte', 'Smplskelett',
                'Unterlauf', 'Backendpruefung', 'Fremdlauf')

    def test_jede_klasse_gibt_es_nur_einmal(self):
        namen = Wrapperquellen.modulebene()
        for name in self.EINMALIG:
            with self.subTest(name=name):
                self.assertEqual(len(namen.get(name, [])), 1,
                                 '%s steht in %s' % (name, namen.get(name)))

    def test_die_masse_werden_an_einer_stelle_gerechnet(self):
        u"""Der Befund: zwei `_body_measurements` mit anderem Ergebnis."""
        treffer = [p.name for p, t in Wrapperquellen.texte()
                   if 'def _masse_aus' in t or 'def _body_measurements' in t]
        self.assertEqual(treffer, ['smplxmodell.py'])

    def test_das_modell_wird_an_einer_stelle_geladen(self):
        treffer = [p.name for p, t in Wrapperquellen.texte()
                   if re.search(r'np\.load\([^)]*SMPLX|def _load_model', t)]
        self.assertEqual(treffer, [])

    def test_die_gelenkindizes_stehen_einmal(self):
        u"""`_J` lag als Kopie in zwei Dateien."""
        treffer = [p.name for p, t in Wrapperquellen.texte()
                   if re.search(r'^\s*(GELENK|_J)\s*=\s*dict\(', t, re.M)]
        self.assertEqual(treffer, ['smplxmodell.py'])

    def test_die_hoehe_kommt_aus_dem_netz(self):
        u"""Der Fix vom 15.08.2026 — er hatte nur eine der zwei Kopien.

        OHNE MODELLDATEI WIRD NICHT UEBERSPRUNGEN: „nichts zu pruefen"
        ist ein ERGEBNIS. Ein `skipTest` meldet gruen und faellt nie
        auf — auch dann nicht, wenn `laden()` selbst kaputtgeht und
        deshalb `None` liefert. Geprueft wird deshalb beides: dass
        `None` wirklich nur bei fehlender Datei kommt, und die Messung,
        sobald es sie gibt.
        """
        import os

        from baum import Baum
        from smplxmodell import Smplxmodell

        modell = Smplxmodell.laden('neutral')
        datei = Baum.smplx_datei('neutral')
        self.assertEqual(modell is None, not os.path.isfile(datei),
                         'Modell nicht ladbar, obwohl %s da ist' % datei)
        if modell is None:
            return

        mit_netz = modell.masse([0.0] * 10).hoehe
        aus_gelenken = modell.masse_aus_gelenken(
            modell.gelenke([0.0] * 10)).hoehe
        self.assertGreater(mit_netz - aus_gelenken, 0.15)
        self.assertAlmostEqual(mit_netz, 1.719, places=2)


class DasFortschrittsprotokoll(unittest.TestCase):
    u"""`TOTAL:`/`PROGRESS:`/`STATUS:` liest Django zeilenweise."""

    #: Die Vorsaetze, die `Erkennungsfortschritt` auswertet.
    VORSAETZE = ('TOTAL:', 'PROGRESS:', 'STATUS:')

    def test_die_vorsaetze_stimmen_mit_django_ueberein(self):
        from core.pipelines.erkennungsfortschritt import Erkennungsfortschritt
        quelle = __import__('inspect').getsource(
            Erkennungsfortschritt.zeile_lesen)
        for vorsatz in self.VORSAETZE:
            with self.subTest(vorsatz=vorsatz):
                self.assertIn("'%s'" % vorsatz, quelle)

    def test_der_videolauf_meldet_beide(self):
        text = (WRAPPERS / 'videolauf.py').read_text(encoding='utf-8')
        self.assertIn("'TOTAL:%d'", text)
        self.assertIn("'PROGRESS:%d/%d'", text)

    def test_jede_protokollzeile_wird_geleert(self):
        u"""Ohne `flush` haelt Windows die Ausgabe im Puffer zurueck —
        und die aufrufende Seite beendet den Prozess wegen Stille.

        Geprueft wird die ganze `print`-Anweisung, nicht die Zeile: Die
        erste Fassung meldete zwei mehrzeilige Aufrufe, bei denen
        `flush=True` eine Zeile weiter unten stand.
        """
        for pfad, text in Wrapperquellen.texte():
            for knoten, argument in Wrapperquellen.druckaufrufe(ast.parse(text)):
                if not any(v in argument for v in self.VORSAETZE):
                    continue
                geleert = any(w.arg == 'flush' for w in knoten.keywords)
                with self.subTest(datei=pfad.name, zeile=knoten.lineno):
                    self.assertTrue(geleert,
                                    '%s:%d meldet ohne `flush`'
                                    % (pfad.name, knoten.lineno))

    def test_die_pruefung_merkt_ein_fehlendes_flush(self):
        u"""Gegenprobe zur vorigen Zusicherung."""
        baum = ast.parse("print('PROGRESS:%d/%d' % (1, 2))\n"
                         "print('TOTAL:%d' % 3, flush=True)\n")
        ohne = [k for k, a in Wrapperquellen.druckaufrufe(baum)
                if not any(w.arg == 'flush' for w in k.keywords)]
        self.assertEqual(len(ohne), 1)
        self.assertEqual(ohne[0].lineno, 1)

    def test_kein_logger_statt_protokoll(self):
        u"""Ein Logger schreibt in eine Datei, nicht auf stdout."""
        for pfad, text in Wrapperquellen.texte():
            for vorsatz in self.VORSAETZE:
                with self.subTest(datei=pfad.name, vorsatz=vorsatz):
                    self.assertNotRegex(
                        text, r"logger\.\w+\(\s*'%s" % vorsatz)


class DieDateigroesse(unittest.TestCase):
    u"""Keine Monolithen — die Regel gilt auch hier."""

    #: Faustregel aus den Projektregeln.
    GRENZE = 300

    def test_keine_datei_ueber_300_zeilen(self):
        zu_gross = []
        for pfad, text in Wrapperquellen.texte():
            zeilen = len(text.split('\n'))
            if zeilen > self.GRENZE:
                zu_gross.append('%s (%d)' % (pfad.name, zeilen))
        self.assertEqual(zu_gross, [])

    def test_jedes_modul_nennt_seinen_zweck(self):
        for pfad, text in Wrapperquellen.texte():
            with self.subTest(datei=pfad.name):
                self.assertIsNotNone(ast.get_docstring(ast.parse(text)),
                                     '%s hat keinen Docstring' % pfad.name)

    def test_jede_klasse_nennt_ihren_zweck(self):
        for pfad, text in Wrapperquellen.texte():
            for knoten in ast.parse(text).body:
                if isinstance(knoten, ast.ClassDef):
                    with self.subTest(datei=pfad.name, klasse=knoten.name):
                        self.assertIsNotNone(ast.get_docstring(knoten))

    def test_keine_stumme_ausnahme_ohne_vermerk(self):
        u"""Ein `except: pass` ohne Begruendung verschluckt Befunde."""
        for pfad, text in Wrapperquellen.texte():
            zeilen = text.split('\n')
            for knoten in ast.walk(ast.parse(text)):
                if not isinstance(knoten, ast.ExceptHandler):
                    continue
                nur_pass = (len(knoten.body) == 1
                            and isinstance(knoten.body[0], ast.Pass))
                if not nur_pass:
                    continue
                umfeld = '\n'.join(zeilen[max(0, knoten.lineno - 3):
                                          knoten.lineno + 2])
                with self.subTest(datei=pfad.name, zeile=knoten.lineno):
                    self.assertTrue(
                        'stumm gewollt' in umfeld or 'Absichtlich' in umfeld,
                        '%s:%d verschluckt eine Ausnahme ohne Vermerk'
                        % (pfad.name, knoten.lineno))


class JederRunnerLiefertSeineFelder(unittest.TestCase):
    u"""Was ein Runner mitschickt, liest die Django-Seite auch — und umgekehrt.

    DER ANLASS (02.09.2026): Die Ergebnisbildung der drei Foto-Runner
    wurde umgebaut; sie stand vorher als 60 Zeilen Tensor-Auslesen
    mitten im Ablauf. Ein Feld, das dabei wegfaellt, wirft NICHTS: Der
    Runner meldet weiter eine gueltige JSON-Zeile, und die Ausrichtung
    des Netzes ueber dem Foto faellt still auf den orthografischen
    Notweg zurueck.

    Geprueft wird gegen `Analyseergebnis.KAMERAFELDER` — die Liste, die
    Django wirklich liest —, nicht gegen eine Abschrift des heutigen
    Standes.
    """

    #: Zwei Felder stehen nicht in `KAMERAFELDER`, weil sie woanders
    #: gelesen werden: der YOLO-Rahmen in `silhouettenauftrag`, der
    #: Vertexpfad in `smplx_archiv`.
    AUSSERHALB = ('bbox_xyxy', 'posed_vertices_path')

    #: Die Runner mit Zusatzfeldern. `_run_hmr2` hat keine — HMR 2.0
    #: liefert nur die Form, keine Kameradaten.
    RUNNER = ('_run_pymafx.py', '_run_smplest_x.py')

    @staticmethod
    def _zusatzfelder(name):
        u"""Die Schluesselwoerter aus `ergebnis.dazu(...)` einer Datei."""
        text = (WRAPPERS / name).read_text(encoding='utf-8')
        felder = set()
        for knoten in ast.walk(ast.parse(text)):
            if (isinstance(knoten, ast.Call)
                    and getattr(knoten.func, 'attr', None) == 'dazu'):
                felder |= {w.arg for w in knoten.keywords}
        return felder

    def _alle(self):
        felder = set()
        for name in self.RUNNER:
            felder |= self._zusatzfelder(name)
        return felder

    def test_jedes_kamerafeld_kommt_von_einem_runner(self):
        u"""Ein Feld, das Django liest und niemand schickt, ist immer leer."""
        from core.daten.analyseergebnis import Analyseergebnis
        fehlend = set(Analyseergebnis.KAMERAFELDER) - self._alle()
        self.assertEqual(fehlend, set(),
                         'Django liest Felder, die kein Runner schickt: %s'
                         % sorted(fehlend))

    def test_jedes_gesendete_feld_wird_auch_gelesen(self):
        u"""Und andersherum: nichts wird umsonst berechnet."""
        from core.daten.analyseergebnis import Analyseergebnis
        gelesen = set(Analyseergebnis.KAMERAFELDER) | set(self.AUSSERHALB)
        ueberfluessig = self._alle() - gelesen
        self.assertEqual(ueberfluessig, set(),
                         'Diese Felder liest niemand: %s'
                         % sorted(ueberfluessig))

    def test_die_backendnamen_stehen_fest(self):
        u"""`photo_analyzer` waehlt den Runner ueber diesen Namen."""
        erwartet = {'_run_hmr2.py': "'hmr2'", '_run_pymafx.py': "'pymafx'",
                    '_run_smplest_x.py': "'smplest_x'"}
        for name, backend in erwartet.items():
            with self.subTest(runner=name):
                text = (WRAPPERS / name).read_text(encoding='utf-8')
                self.assertIn('Fotoergebnis(%s' % backend, text)

    def test_die_modellart_bleibt_je_runner_dieselbe(self):
        u"""SMPL und SMPL-X haben unvereinbare Netztopologien (6.890 gegen
        10.475 Vertices); wer sie verwechselt, bekommt Netzsalat."""
        for name, art in (('_run_hmr2.py', "'smpl'"),
                          ('_run_pymafx.py', "'smplx'"),
                          ('_run_smplest_x.py', "'smplx'")):
            with self.subTest(runner=name):
                text = (WRAPPERS / name).read_text(encoding='utf-8')
                self.assertIn(', %s,' % art, text)
