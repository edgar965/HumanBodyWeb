# -*- coding: utf-8 -*-
"""Die vierzehn Werkzeuggruppen „Kleider und Haar“ des Reiters „Tools“ (Hilfe → Architektur → 2D3D, 03.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM: Eine Zeile mit einer Klasse, die es nicht gibt, einer Rezeptzeile, die das Modell nicht kennt, einer Adresse ohne Eintrag in den urls*.py oder einem Befehl
ohne Datei wäre genau der Fehler, den die Seite verhindern soll. Die Tests lesen nur Quelltext (keine Daz-Bibliothek, keine Grafikkarte); Rezeptzeilen gehen durch
`G9rezept.pruefen` und werden gegen die Signatur gebunden. Sabotage: einen Klassennamen, eine Adresse oder einen Rezeptnamen verändern → die Prüfung wird rot.
"""
import ast
import importlib
import inspect
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.architektur2d3dklassen import Architektur2d3dklassen
from core.dienste.werkzeugkleidunghilfe import Werkzeugkleidunghilfe

#: Die Dateien `werkzeug<name>.py` dieser Gruppen; die Klasse heißt wie die Datei, groß geschrieben (so sucht sie Architektur2d3dwerkzeuge).
DATEIEN = ('werkzeugrezeptkleidung', 'werkzeugkleidform', 'werkzeugdrapieren', 'werkzeugkleidgenerisch', 'werkzeuggarderobe', 'werkzeuggarmentcode',
           'werkzeugkleidtextur', 'werkzeugfotostuecke', 'werkzeughaar', 'werkzeughaarform', 'werkzeughaarfoto', 'werkzeugkleidunghilfe',
           'werkzeugkleidbau', 'werkzeugkleiderautomatik')
GRUPPEN = tuple(getattr(importlib.import_module('core.dienste.' + d), d.capitalize()) for d in DATEIEN)
ARTEN = ('rezept', 'api', 'cli', 'python', 'seite', 'regel')
#: ae/oe/ue-Umschreibungen, die auf der Seite nichts zu suchen haben (Bezeichner im Aufruf zählen nicht).
UMSCHREIBUNG = re.compile(r'\b(fuer|ueber|Faelle|Koerper|Staerke|Ruecken|moeglich|koennen|muessen|waehlen|Groesse|Aenderung|Loesung|Aufloesung)\b')
HILFE_PRAEFIX = 'hilfe/kleidung/'


def zeilen_von(gruppe):
    return [dict(zip(('werkzeug', 'wofuer', 'art', 'aufruf', 'klassen', 'hinweis'), z, strict=True)) for z in gruppe.ZEILEN]


def klassen_von(gruppe):
    return {name for z in gruppe.ZEILEN for _datei, name in z[4]}


def wurzel():
    return Path(settings.TOOLS_ROOT)


def quelltext(*ordner):
    return '\n'.join(d.read_text(encoding='utf-8', errors='replace') for o in ordner for d in (wurzel() / o).rglob('*.py'))


class WerkzeugeKleidungHaarAufbauTest(SimpleTestCase):
    def test_jede_gruppe_hat_kennung_titel_einleitung_und_zeilen(self):
        for g in GRUPPEN:
            self.assertTrue(g.TITEL.strip() and g.EINLEITUNG.strip(), g.__name__)
            self.assertTrue(g.ZEILEN, g.__name__)

    def test_die_kennungen_sind_ascii_klein_und_eindeutig_denn_sie_sind_die_anker_der_seite(self):
        kennungen = [g.KENNUNG for g in GRUPPEN]
        for k in kennungen:
            self.assertRegex(k, r'^[a-z0-9]+$')
        self.assertEqual(len(kennungen), len(set(kennungen)))

    def test_der_klassenname_folgt_dem_dateinamen_wie_ihn_architektur2d3dwerkzeuge_sucht(self):
        for g in GRUPPEN:
            self.assertEqual(g.__name__, g.__module__.rsplit('.', 1)[-1].capitalize())

    def test_jede_zeile_hat_sechs_felder_und_keine_leeren_texte(self):
        for g in GRUPPEN:
            for z in g.ZEILEN:
                stelle = '%s / %s' % (g.KENNUNG, z[0])
                self.assertEqual(len(z), 6, stelle)
                for text in (z[0], z[1], z[3], z[5]):
                    self.assertTrue(str(text).strip(), stelle)

    def test_die_art_jeder_zeile_ist_bekannt(self):
        for g in GRUPPEN:
            for z in zeilen_von(g):
                self.assertIn(z['art'], ARTEN, '%s / %s' % (g.KENNUNG, z['werkzeug']))

    def test_eine_zeile_ohne_klasse_ist_nur_bei_regel_und_seite_erlaubt(self):
        for g in GRUPPEN:
            for z in zeilen_von(g):
                self.assertTrue(z['klassen'] or z['art'] in ('regel', 'seite'), '%s / %s' % (g.KENNUNG, z['werkzeug']))

    def test_ein_werkzeug_steht_in_genau_einer_gruppe(self):
        namen = [z[0] for g in GRUPPEN for z in g.ZEILEN]
        doppelt = sorted({n for n in namen if namen.count(n) > 1})
        self.assertEqual(doppelt, [], 'Dubletten zwischen den Gruppen')

    def test_keine_beschreibung_umschreibt_umlaute_mit_ae_oe_ue(self):
        for g in GRUPPEN:
            for z in zeilen_von(g):
                gefunden = UMSCHREIBUNG.search(z['wofuer'] + ' ' + z['hinweis'])
                self.assertIsNone(gefunden, '%s / %s: %s' % (g.KENNUNG, z['werkzeug'], gefunden and gefunden.group(0)))
            self.assertIsNone(UMSCHREIBUNG.search(g.TITEL + ' ' + g.EINLEITUNG), g.KENNUNG)

    def test_keine_datei_ist_laenger_als_dreihundert_zeilen(self):
        for g in GRUPPEN:
            text = Path(inspect.getsourcefile(g)).read_text(encoding='utf-8')
            self.assertLessEqual(text.count('\n') + 1, 300, g.__name__)


class WerkzeugeKleidungHaarKlassenTest(SimpleTestCase):
    def test_jede_klasse_der_zeilen_steht_in_ihrer_datei(self):
        for g in GRUPPEN:
            for z in g.ZEILEN:
                for datei, klasse in z[4]:
                    with self.subTest(gruppe=g.KENNUNG, werkzeug=z[0], klasse=klasse):
                        self.assertEqual(Architektur2d3dklassen.zeile(datei, klasse)['fehlt'], '')

    def test_eine_klasse_steht_in_einer_gruppe_nur_in_einer_datei(self):
        for g in GRUPPEN:
            dateien = {}
            for z in g.ZEILEN:
                for datei, klasse in z[4]:
                    self.assertEqual(dateien.setdefault(klasse, datei), datei, '%s: %s' % (g.KENNUNG, klasse))

    def test_jede_beziehung_nennt_zwei_klassen_aus_den_zeilen_der_gruppe(self):
        for g in GRUPPEN:
            klassen = klassen_von(g)
            for b in g.BEZIEHUNGEN:
                self.assertEqual(len(b), 4, '%s: %r' % (g.KENNUNG, b))
                self.assertEqual(b[1], 'ruft', '%s: %s' % (g.KENNUNG, b))
                self.assertIn(b[0], klassen, '%s: %s' % (g.KENNUNG, b))
                self.assertIn(b[2], klassen, '%s: %s' % (g.KENNUNG, b))
                self.assertTrue(b[3].strip(), '%s: %s ohne womit' % (g.KENNUNG, b))

    def test_jede_gruppe_hat_drei_bis_fuenfundzwanzig_beziehungen(self):
        for g in GRUPPEN:
            self.assertGreaterEqual(len(g.BEZIEHUNGEN), 3, g.KENNUNG)
            self.assertLessEqual(len(g.BEZIEHUNGEN), 25, g.KENNUNG)

    def test_jede_methode_oder_konstante_die_eine_beziehung_nennt_steht_im_klassenkoerper(self):
        for g in GRUPPEN:
            dateien = {klasse: datei for z in g.ZEILEN for datei, klasse in z[4]}
            for b in g.BEZIEHUNGEN:
                for klasse, name in re.findall(r'\b([A-Za-z0-9_]+)\.([A-Za-z_][A-Za-z0-9_]*)\b', b[3]):
                    if klasse not in dateien:
                        continue
                    baum = ast.parse((wurzel() / dateien[klasse]).read_text(encoding='utf-8'))
                    knoten = next(k for k in baum.body if isinstance(k, ast.ClassDef) and k.name == klasse)
                    namen = set()
                    for k in knoten.body:
                        if isinstance(k, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            namen.add(k.name)
                        elif isinstance(k, ast.Assign):
                            namen.update(t.id for t in k.targets if isinstance(t, ast.Name))
                        elif isinstance(k, ast.AnnAssign) and isinstance(k.target, ast.Name):
                            namen.add(k.target.id)
                    self.assertIn(name, namen, '%s: %s.%s steht nicht in der Klasse (%s)' % (g.KENNUNG, klasse, name, b))


class WerkzeugeKleidungHaarRezeptTest(SimpleTestCase):
    def test_jede_rezeptzeile_nennt_eine_methode_die_es_im_code_gibt(self):
        quellen = quelltext('Genesis9', '2d3DIterationen', 'HumanBodyWeb/core/dienste')
        for g in GRUPPEN:
            for z in zeilen_von(g):
                if z['art'] != 'rezept':
                    continue
                for name in re.findall(r'\bm\.([a-z_0-9]+)\(', z['aufruf']):
                    self.assertIn('def %s(' % name, quellen, '%s / %s: m.%s gibt es nicht' % (g.KENNUNG, z['werkzeug'], name))

    def test_jede_rezeptzeile_ist_ein_gueltiges_rezept_und_ihre_argumente_passen_zur_signatur(self):
        from Genesis9.modellmitkleidern import ModellMitKleidern
        from Genesis9.modellrezept import G9rezept
        for g in GRUPPEN:
            for z in zeilen_von(g):
                if z['art'] != 'rezept':
                    continue
                stelle = '%s / %s' % (g.KENNUNG, z['werkzeug'])
                zeilen = [t for t in z['aufruf'].splitlines() if t.strip().startswith('m.')]
                self.assertTrue(zeilen, stelle)
                for _zeile, name, args, kwargs in G9rezept.pruefen('\n'.join(zeilen)):
                    signatur = inspect.signature(getattr(ModellMitKleidern, name))
                    try:
                        signatur.bind(None, *args, **kwargs)
                    except TypeError as fehler:
                        self.fail('%s: m.%s passt nicht zu %s (%s)' % (stelle, name, signatur, fehler))

    def test_jede_kleid_und_haarfunktion_des_rezepts_hat_eine_zeile_in_diesen_gruppen(self):
        from Genesis9.modellmitkleidern import ModellMitKleidern
        gedeckt = set()
        for g in GRUPPEN:
            for z in zeilen_von(g):
                if z['art'] == 'rezept':
                    gedeckt.update(re.findall(r'\bm\.([a-z_0-9]+)\(', z['aufruf']))
        meine = ('kleid', 'haar', 'morph', 'bild', 'passform', 'uebergang', 'textur')       # Körper und Haltung gehören zu T1
        fehlend = sorted(n for n, _sig, _text in ModellMitKleidern.hilfe() if n.startswith(meine) and n not in gedeckt)
        self.assertEqual(fehlend, [], 'neue Rezeptfunktionen für Kleider oder Haar ohne Zeile: in der passenden Gruppe ergänzen')


class WerkzeugeKleidungHaarVerhaltenTest(SimpleTestCase):
    """Die Aussagen der Hinweise, die man ohne Daz-Bibliothek nachrechnen kann."""

    STUECKE = [{'id': 'erstes'}, {'id': 'zweites'}, {'id': 'drittes'}]

    def test_ein_stueck_ohne_gesetzten_regler_gilt_nur_beim_ersten_der_liste_als_vorgabe_eins(self):
        from Genesis9.kleidgenerischwahl import G9kleidgenerischwahl
        self.assertEqual(G9kleidgenerischwahl.anteile(self.STUECKE, {'sorte.zweites': 1.0}), {'erstes': 1.0, 'zweites': 1.0})

    def test_stehen_alle_anteile_auf_null_gilt_wieder_das_erste_stueck(self):
        from Genesis9.kleidgenerischwahl import G9kleidgenerischwahl
        self.assertEqual(G9kleidgenerischwahl.anteile(self.STUECKE, {'sorte.erstes': 0.0, 'sorte.zweites': 0.0}), {'erstes': 1.0})

    def test_eine_unbekannte_kennung_wird_still_ignoriert(self):
        from Genesis9.kleidgenerischwahl import G9kleidgenerischwahl
        self.assertEqual(G9kleidgenerischwahl.anteile(self.STUECKE, {'sorte.gibtesnicht': 1.0}), {'erstes': 1.0})

    def test_der_uebergang_ist_in_metern_und_auf_null_komma_fuenf_bis_zehn_zentimeter_gekappt(self):
        from Genesis9.kleidgenerischwahl import G9kleidgenerischwahl
        self.assertAlmostEqual(G9kleidgenerischwahl.uebergang({}), 0.03)
        self.assertAlmostEqual(G9kleidgenerischwahl.uebergang({'mischung:uebergang': 20}), 0.10)
        self.assertAlmostEqual(G9kleidgenerischwahl.uebergang({'mischung:uebergang': 0.1}), 0.005)

    def test_alle_getragenen_stuecke_werden_gemischt_es_gibt_keine_grenze_mehr(self):
        """Die Grenze von vier Stücken ist weg („Kleidung ohne Stückgrenze", Commit 93a9332 vom 03.10.2026): bei zwölf Stücken fielen Hemd, Hose und Stiefel nackt weg."""
        from Genesis9.kleidgenerischwahl import G9kleidgenerischwahl
        stuecke = [{'id': 's%d' % i} for i in range(6)]
        werte = {'sorte.s%d' % i: 1.0 for i in range(6)}
        self.assertIsNone(G9kleidgenerischwahl.HOECHSTENS)
        self.assertEqual(len(G9kleidgenerischwahl.mischung(stuecke, werte)), 6)

    def test_die_passform_wird_auf_zwanzig_und_drei_bis_sechs_zentimeter_gekappt(self):
        from Genesis9.modellmitkleidern import ModellMitKleidern
        m = ModellMitKleidern().passform(laenge_cm=-40, weite_cm=9)
        self.assertEqual((m.kleidung['passform:laenge'], m.kleidung['passform:weite']), (-20.0, 6.0))

    def test_die_schrittsuche_geht_nach_einem_schlechteren_schritt_mit_halbem_schritt_zurueck(self):
        from iterationen2d3d.schrittsuche import Schrittsuche
        self.assertEqual(Schrittsuche(0.0, 0.2, 0.0, 1.0).naechster([(0.2, 34.4), (0.4, 34.8)]), 0.3)


class WerkzeugeKleidungHaarAdressenTest(SimpleTestCase):
    @staticmethod
    def _routen(*dateien):
        muster = set()
        for datei in dateien:
            text = datei.read_text(encoding='utf-8')
            for treffer in re.finditer(r"path\(\s*'([^']*)'", text):
                muster.add(re.sub(r'<[^>]*>', '<>', treffer.group(1)))
        return muster

    @classmethod
    def _alle_routen(cls):
        return cls._routen(*sorted((wurzel() / 'HumanBodyWeb' / 'core').glob('urls*.py')))

    @staticmethod
    def _adressen(aufruf, art):
        aus = []
        for zeile in aufruf.splitlines():
            zeile = zeile.strip()
            if art == 'api':
                treffer = re.match(r'^(GET|POST)\s+(/\S+)', zeile)
                if treffer and '…' not in treffer.group(2):
                    aus.append(treffer.group(2))
            else:
                aus.extend(t.group(1) for t in re.finditer(r'(?:^|\s)(/[A-Za-z0-9_\-<>/.]+)', zeile))
        return [re.sub(r'<[^>]*>', '<>', re.split(r'[?#]', a)[0]).lstrip('/') for a in aus]

    def test_jede_api_adresse_und_jede_seitenadresse_steht_in_den_urls(self):
        routen = self._alle_routen()
        hilfe = self._routen(wurzel() / 'HumanBodyWeb' / 'core' / 'urls_hilfe.py')
        for g in GRUPPEN:
            for z in zeilen_von(g):
                if z['art'] not in ('api', 'seite'):
                    continue
                for adresse in self._adressen(z['aufruf'], z['art']):
                    stelle = '%s / %s' % (g.KENNUNG, z['werkzeug'])
                    if adresse.startswith(HILFE_PRAEFIX):          # das Präfix hängt in ui/urls.py, die Seite in urls_hilfe.py
                        self.assertIn(adresse[len(HILFE_PRAEFIX):], hilfe, '%s: /%s steht nicht in urls_hilfe.py' % (stelle, adresse))
                    else:
                        self.assertIn(adresse, routen, '%s: /%s steht in keiner urls*.py' % (stelle, adresse))

    def test_jede_hilfeseite_der_gruppe_nennt_die_view_klasse_der_url(self):
        text = (wurzel() / 'HumanBodyWeb' / 'core' / 'urls_hilfe.py').read_text(encoding='utf-8')
        for z in zeilen_von(Werkzeugkleidunghilfe):
            self.assertEqual(z['art'], 'seite')
            self.assertIn('%s.ansicht()' % z['klassen'][0][1], text, z['werkzeug'])


class WerkzeugeKleidungHaarBefehleTest(SimpleTestCase):
    def test_jeder_manage_befehl_und_jedes_modul_und_jedes_skript_im_aufruf_hat_seine_datei(self):
        for g in GRUPPEN:
            for z in zeilen_von(g):
                if z['art'] != 'cli':
                    continue
                stelle = '%s / %s' % (g.KENNUNG, z['werkzeug'])
                for befehl in re.findall(r'manage\.py ([a-z_0-9]+)', z['aufruf']):
                    self.assertTrue((wurzel() / 'HumanBodyWeb' / 'core' / 'management' / 'commands' / (befehl + '.py')).is_file(), '%s: %s' % (stelle, befehl))
                for modul in re.findall(r'-m ([A-Za-z0-9_.]+)', z['aufruf']):
                    self.assertTrue((wurzel() / (modul.replace('.', '/') + '.py')).is_file(), '%s: %s' % (stelle, modul))
                for skript in re.findall(r'(ProjektTemp/[A-Za-z0-9_/.\-]+\.py)', z['aufruf']):
                    self.assertTrue((wurzel() / skript).is_file(), '%s: %s' % (stelle, skript))

    def test_die_in_den_hinweisen_genannten_dateien_gibt_es(self):
        pfad = re.compile(r'(?<![A-Za-z0-9_./-])((?:HumanBodyWeb|Genesis9|Assets|2d3DIterationen|Kleidung|Haar|Stoffsolver)/[A-Za-z0-9_./-]+\.(?:json|py|js|md)\b)')
        for g in GRUPPEN:
            texte = [g.EINLEITUNG] + [z[5] for z in g.ZEILEN] + [z[3] for z in g.ZEILEN]
            for text in texte:
                for treffer in pfad.findall(text):
                    kandidaten = [wurzel() / treffer, wurzel() / 'HumanBodyWeb' / 'static' / 'viewer' / treffer]
                    self.assertTrue(any(k.exists() for k in kandidaten), '%s: %s gibt es nicht' % (g.KENNUNG, treffer))
