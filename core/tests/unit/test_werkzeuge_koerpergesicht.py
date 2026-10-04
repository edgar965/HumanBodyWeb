# -*- coding: utf-8 -*-
"""Die sechs Werkzeuggruppen „Körper und Gesicht“ des Reiters „Tools“ (Hilfe → Architektur → 2D3D, 03.10.2026): Körper-Regler, Haltung und Rig, Gesicht, Haut,
Mesh to 3D, Proportionen. Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM: Die Seite soll anderen Sessions sagen, welches Werkzeug sie wie aufrufen. Eine Zeile mit einer Klasse, die es nicht gibt, einer Rezeptzeile, die das Modell nicht
kennt, oder einer Adresse, die in keiner urls*.py steht, wäre genau der Fehler, den die Seite verhindern soll. Die Tests lesen nur Quelltext — ohne Daz-Bibliothek, ohne
Grafikkarte; die Rezeptzeilen gehen durch dieselbe Prüfung wie ein echtes Rezept (`G9rezept.pruefen`) und werden gegen die Signatur gebunden.
Sabotage: einen Klassennamen oder eine Adresse in einer Gruppe verändern → die passende Prüfung wird rot.
"""
import inspect
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.architektur2d3dklassen import Architektur2d3dklassen
from core.dienste.werkzeuggesicht import Werkzeuggesicht
from core.dienste.werkzeughaltung import Werkzeughaltung
from core.dienste.werkzeughaut import Werkzeughaut
from core.dienste.werkzeugkoerper import Werkzeugkoerper
from core.dienste.werkzeugmeshfigur import Werkzeugmeshfigur
from core.dienste.werkzeugproportionen import Werkzeugproportionen

GRUPPEN = (Werkzeugkoerper, Werkzeughaltung, Werkzeuggesicht, Werkzeughaut, Werkzeugmeshfigur, Werkzeugproportionen)
ARTEN = ('rezept', 'api', 'cli', 'python', 'seite', 'regel')
#: ae/oe/ue-Umschreibungen, die auf der Seite nichts zu suchen haben (Bezeichner im Aufruf zählen nicht).
UMSCHREIBUNG = re.compile(r'\b(fuer|ueber|Faelle|Koerper|Staerke|Ruecken|moeglich|koennen|muessen|waehlen|Groesse|Aenderung|Loesung|Aufloesung)\b')


def zeilen_von(gruppe):
    return [dict(zip(('werkzeug', 'wofuer', 'art', 'aufruf', 'klassen', 'hinweis'), z, strict=True)) for z in gruppe.ZEILEN]


def klassen_von(gruppe):
    return {name for z in gruppe.ZEILEN for _datei, name in z[4]}


def quelltext(*ordner):
    wurzel = Path(settings.TOOLS_ROOT)
    teile = []
    for o in ordner:
        for datei in (wurzel / o).rglob('*.py'):
            teile.append(datei.read_text(encoding='utf-8', errors='replace'))
    return '\n'.join(teile)


class WerkzeugeKoerperGesichtAufbauTest(SimpleTestCase):
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


class WerkzeugeKoerperGesichtKlassenTest(SimpleTestCase):
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
                self.assertIn(b[0], klassen, '%s: %s' % (g.KENNUNG, b))
                self.assertIn(b[2], klassen, '%s: %s' % (g.KENNUNG, b))
                self.assertTrue(b[3].strip(), '%s: %s ohne womit' % (g.KENNUNG, b))

    def test_jede_gruppe_hat_drei_bis_fuenfundzwanzig_beziehungen(self):
        for g in GRUPPEN:
            self.assertGreaterEqual(len(g.BEZIEHUNGEN), 3, g.KENNUNG)
            self.assertLessEqual(len(g.BEZIEHUNGEN), 25, g.KENNUNG)


class WerkzeugeKoerperGesichtRezeptTest(SimpleTestCase):
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

    def test_das_rezept_kennt_keine_gesichtsfunktion_sonst_waere_werkzeuggesicht_veraltet(self):
        from Genesis9.modellmitkleidern import ModellMitKleidern
        namen = {n for n, _sig, _text in ModellMitKleidern.hilfe()}
        gesicht = [n for n in namen if n.startswith('gesicht')]
        self.assertFalse(gesicht, 'Werkzeuggesicht sagt: Kopfregler gehen über koerper_regler')


class WerkzeugeKoerperGesichtAdressenTest(SimpleTestCase):
    @staticmethod
    def _routen():
        muster = set()
        for datei in sorted((Path(settings.TOOLS_ROOT) / 'HumanBodyWeb' / 'core').glob('urls*.py')):
            text = datei.read_text(encoding='utf-8')
            for treffer in re.finditer(r"path\(\s*'([^']*)'", text):
                muster.add(re.sub(r'<[^>]*>', '<>', treffer.group(1)))
        return muster

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
        routen = self._routen()
        for g in GRUPPEN:
            for z in zeilen_von(g):
                if z['art'] not in ('api', 'seite'):
                    continue
                for adresse in self._adressen(z['aufruf'], z['art']):
                    stelle = '%s / %s' % (g.KENNUNG, z['werkzeug'])
                    self.assertIn(adresse, routen, '%s: /%s steht in keiner urls*.py' % (stelle, adresse))
