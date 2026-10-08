# -*- coding: utf-8 -*-
"""Reiter „Tools“, Bereich T4 „Bildvergleich Fotos ↔ Modell“ (03.10.2026): acht Gruppen `werkzeugbild*.py` in `core/dienste/`.

WARUM: Diese Seite sagt anderen Sessions, welches Werkzeug sie wie aufrufen. Eine Zeile mit einer Klasse, einer Adresse oder einer Zahl, die es im
Code so nicht gibt, wäre genau der Fehler, den sie verhindern soll. Die Tests halten fest, dass jede genannte Klasse im Code steht, jede Adresse
der API-Zeilen auflösbar ist, die Beziehungen zwei Klassen der Gruppe nennen und die Zahlen der Regeln (Auflösungsstufen, Schwellen der Noten und
der Messgüte) noch die Konstanten des Codes sind. Nicht geprüft werden die Hinweise Satz für Satz — sie tragen ihre Quelle mit Datum."""

import ast
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import resolve

from core.dienste.architektur2d3dklassen import Architektur2d3dklassen
from core.dienste.architektur2d3dwerkzeuge import Architektur2d3dwerkzeuge
from core.dienste.werkzeugbildbefund import Werkzeugbildbefund
from core.dienste.werkzeugbildfotos import Werkzeugbildfotos
from core.dienste.werkzeugbildlauf import Werkzeugbildlauf
from core.dienste.werkzeugbildnote import Werkzeugbildnote
from core.dienste.werkzeugbildrender import Werkzeugbildrender
from core.dienste.werkzeugbildserver import Werkzeugbildserver
from core.dienste.werkzeugbildstufen import Werkzeugbildstufen
from core.dienste.werkzeugbildtafeln import Werkzeugbildtafeln

GRUPPEN = [Werkzeugbildfotos, Werkzeugbildrender, Werkzeugbildnote, Werkzeugbildstufen, Werkzeugbildtafeln, Werkzeugbildbefund,
           Werkzeugbildserver, Werkzeugbildlauf]
#: Kleingeschriebene Funktionswörter, die nie ein Bezeichner sind (Feldnamen wie aufloesung und baender bleiben erlaubt).
FUNKTIONSWOERTER = {'fuer', 'ueber', 'koennen', 'koennte', 'muessen', 'moeglich', 'moegliche', 'waehrend', 'natuerlich', 'zurueck',
                    'dafuer', 'ausser', 'gegenueber', 'unabhaengig', 'abhaengig', 'ergaenzt', 'aendert', 'geaendert'}
#: Stämme, die in einem normal geschriebenen Hauptwort (Großbuchstabe nur vorn) eine Umschreibung verraten.
STAEMME = ('aender', 'groess', 'loesch', 'pruef', 'aufloes', 'auftraeg', 'ergaenz', 'koerper', 'hoehe', 'laenge', 'staerke', 'fuehr',
           'uebe', 'oeff', 'aeus', 'schliess')
#: Namen aus BlenderModel, die in der Prosa stehen (keine Klassen der Gruppen).
FREMDE_NAMEN = {'Kostuemhuelle', 'Kostuemsichtkoerper'}


def alle_klassennamen():
    return {k for g in GRUPPEN for z in g.ZEILEN for _datei, k in z[4]} | FREMDE_NAMEN


def konstante(datei, klasse, name):
    """Wert eines Klassenattributs aus dem Quelltext (ohne Import): einfache und Tupel-Zuweisungen, Verweise auf frühere Namen."""
    baum = ast.parse((Path(settings.TOOLS_ROOT) / datei).read_text(encoding='utf-8'))
    knoten = next(k for k in baum.body if isinstance(k, ast.ClassDef) and k.name == klasse)
    return _suchen(knoten, name)


def _suchen(knoten, name):
    for m in knoten.body:
        if not isinstance(m, ast.Assign):
            continue
        for ziel in m.targets:
            if isinstance(ziel, ast.Name) and ziel.id == name:
                return _wert(m.value, knoten)
            if isinstance(ziel, ast.Tuple) and isinstance(m.value, ast.Tuple):
                for z, w in zip(ziel.elts, m.value.elts, strict=False):
                    if isinstance(z, ast.Name) and z.id == name:
                        return _wert(w, knoten)
    raise AssertionError('%s fehlt' % name)


def _wert(knoten, klasse):
    return _suchen(klasse, knoten.id) if isinstance(knoten, ast.Name) else ast.literal_eval(knoten)


class WerkzeugeBildvergleichSchemaTest(SimpleTestCase):
    def test_jede_gruppe_hat_eine_eindeutige_kennung_einen_titel_eine_einleitung_und_zeilen(self):
        kennungen = [g.KENNUNG for g in GRUPPEN]
        self.assertEqual(len(kennungen), len(set(kennungen)), 'Die Kennung ist der Anker der Seite')
        for g in GRUPPEN:
            self.assertRegex(g.KENNUNG, r'^[a-z0-9]+$', g.__name__)
            self.assertTrue(g.TITEL.strip() and g.EINLEITUNG.strip(), g.__name__)
            self.assertGreater(len(g.ZEILEN), 0, g.__name__)

    def test_jede_zeile_hat_sechs_felder_eine_bekannte_art_und_keine_leeren_texte(self):
        for g in GRUPPEN:
            for z in g.ZEILEN:
                self.assertEqual(len(z), 6, '%s: %r' % (g.KENNUNG, z[:1]))
                werkzeug, wofuer, art, aufruf, klassen, hinweis = z
                stelle = '%s / %s' % (g.KENNUNG, werkzeug)
                self.assertIn(art, Architektur2d3dwerkzeuge.ARTEN, stelle)
                for text in (werkzeug, wofuer, aufruf, hinweis):
                    self.assertTrue(str(text).strip(), stelle)
                self.assertTrue(klassen, stelle + ': ohne Klasse')

    def test_jede_gruppendatei_bleibt_unter_dreihundert_zeilen(self):
        for g in GRUPPEN:
            zeilen = (Path(settings.TOOLS_ROOT) / 'HumanBodyWeb/core/dienste' / (g.__name__.lower() + '.py')).read_text(encoding='utf-8')
            self.assertLessEqual(zeilen.count('\n') + 1, 300, g.__name__)

    def test_die_gruppen_stehen_dort_wo_die_sammlung_sie_findet(self):
        gefunden = {stem for stem, klasse, _fehler in Architektur2d3dwerkzeuge.gruppenklassen() if klasse is not None}
        for g in GRUPPEN:
            self.assertIn(g.__name__.lower(), gefunden, g.__name__)


class WerkzeugeBildvergleichKlassenTest(SimpleTestCase):
    def test_jede_klasse_der_zeilen_gibt_es_in_der_genannten_datei(self):
        for g in GRUPPEN:
            for z in g.ZEILEN:
                for datei, klasse in z[4]:
                    info = Architektur2d3dklassen.zeile(datei, klasse)
                    self.assertEqual(info['fehlt'], '', '%s / %s: %s (%s)' % (g.KENNUNG, z[0], klasse, datei))

    def test_jede_beziehung_nennt_zwei_klassen_der_gruppe_und_sagt_womit(self):
        for g in GRUPPEN:
            klassen = {k for z in g.ZEILEN for _datei, k in z[4]}
            self.assertTrue(3 <= len(g.BEZIEHUNGEN) <= 25, '%s: %d Beziehungen' % (g.KENNUNG, len(g.BEZIEHUNGEN)))
            for von, wie, nach, womit in g.BEZIEHUNGEN:
                stelle = '%s: %s -> %s' % (g.KENNUNG, von, nach)
                self.assertIn(von, klassen, stelle)
                self.assertIn(nach, klassen, stelle)
                self.assertEqual(wie, 'ruft', stelle)
                self.assertTrue(womit.strip(), stelle)

    def test_jede_rezeptzeile_nennt_eine_methode_die_es_im_code_gibt(self):
        wurzel = Path(settings.TOOLS_ROOT)
        zeilen = [(g, z) for g in GRUPPEN for z in g.ZEILEN if z[2] == 'rezept']
        if not zeilen:
            return
        quellen = ''
        for ordner in ('Genesis9', '2d3DIterationen', 'HumanBodyWeb/core/dienste'):
            for datei in (wurzel / ordner).rglob('*.py'):
                quellen += datei.read_text(encoding='utf-8', errors='replace')
        for g, z in zeilen:
            for name in re.findall(r'\bm\.([a-z_0-9]+)\(', z[3]):
                self.assertIn('def %s(' % name, quellen, '%s / %s: m.%s gibt es nicht' % (g.KENNUNG, z[0], name))


class WerkzeugeBildvergleichAdressenTest(SimpleTestCase):
    ADRESSE = re.compile(r'^(GET|POST)\s+(/api/engine2d3dkleider/\S*)', re.MULTILINE)

    def test_jede_adresse_der_api_zeilen_loest_sich_auf_eine_view_auf(self):
        gezaehlt = 0
        for g in GRUPPEN:
            for z in g.ZEILEN:
                if z[2] != 'api':
                    continue
                adressen = self.ADRESSE.findall(z[3])
                self.assertTrue(adressen, '%s / %s: keine Adresse im Aufruf' % (g.KENNUNG, z[0]))
                for _methode, adresse in adressen:
                    pfad = re.sub(r'\?.*$', '', adresse)
                    pfad = pfad.replace('<id>', '00000000-0000-0000-0000-000000000000')
                    pfad = re.sub(r'<[^>]+>', 'x.jpg', pfad)
                    resolve(pfad)
                    gezaehlt += 1
        self.assertGreater(gezaehlt, 15)

    def test_die_adressen_der_api_zeilen_nennen_keinen_localhost(self):
        for g in GRUPPEN:
            for z in g.ZEILEN:
                self.assertNotIn('//localhost', z[3] + z[5], '%s / %s: 127.0.0.1 statt localhost (zeit-messen.md)' % (g.KENNUNG, z[0]))


class WerkzeugeBildvergleichSprachTest(SimpleTestCase):
    @staticmethod
    def umschreibungen(prosa, bekannt):
        aus = []
        for wort in re.findall(r'[A-Za-zÄÖÜäöüß_.0-9]+', prosa):
            if any(s in wort for s in '_.0123456789') or wort in bekannt:
                continue
            if wort.islower():
                if wort in FUNKTIONSWOERTER:
                    aus.append(wort)
            elif wort[0].isupper() and not any(c.isupper() for c in wort[1:]):
                if any(s in wort.lower() for s in STAEMME):
                    aus.append(wort)
        return aus

    def test_die_prosa_enthaelt_keine_ae_oe_ue_umschreibungen(self):
        bekannt = alle_klassennamen()
        for g in GRUPPEN:
            for z in g.ZEILEN:
                prosa = ' '.join((g.TITEL, g.EINLEITUNG, z[0], z[1], z[5]))
                self.assertEqual(self.umschreibungen(prosa, bekannt), [], '%s / %s' % (g.KENNUNG, z[0]))

    def test_die_umschreibungsprobe_schlaegt_an_wenn_sie_sollte(self):
        # Gegenprobe: ohne sie wäre der Test oben ein Test, der nie rot wird.
        self.assertEqual(self.umschreibungen('Die Groesse ist fuer alle gleich.', set()), ['Groesse', 'fuer'])
        self.assertEqual(self.umschreibungen('Die Größe ist für alle gleich, Aufloesungsstufe bleibt.', {'Aufloesungsstufe'}), [])


class WerkzeugeBildvergleichZahlenTest(SimpleTestCase):
    """Die Zahlen und Schwellen, die die Zeilen nennen, sind die Konstanten des Codes (gelesen am 03.10.2026)."""
    D = 'HumanBodyWeb/core/dienste/'
    P = '2d3DIterationen/iterationen2d3d/'

    def test_die_stufenregel_nennt_die_werte_der_aufloesungsstufe(self):
        d = self.D + 'aufloesungsstufe.py'
        self.assertEqual([konstante(d, 'Aufloesungsstufe', n) for n in ('START', 'FAKTOR', 'STILLSTAND')], [128, 2, 3])
        self.assertEqual(konstante(self.D + 'iterationsnote.py', 'Iterationsnote', 'FELDER'), (8, 12))
        self.assertEqual(konstante(self.D + 'iterationsbild.py', 'Iterationsbild', 'RAND'), 0.03)

    def test_die_optionen_der_stufen_haben_die_genannten_vorgaben_und_grenzen(self):
        baum = ast.parse((Path(settings.TOOLS_ROOT) / (self.D + 'iterationsoptionen.py')).read_text(encoding='utf-8'))
        klasse = next(k for k in baum.body if isinstance(k, ast.ClassDef) and k.name == 'Iterationsoptionen')
        katalog = next(m for m in klasse.body if isinstance(m, ast.Assign) and getattr(m.targets[0], 'id', '') == 'KATALOG')
        felder = {}
        for eintrag in katalog.value.elts:
            if not isinstance(eintrag, ast.Dict):
                continue                                                # `*Iterationsoptionenfoto.FOTOOPTIONEN` — ausgelagerte Einträge (08.10.2026)
            d = {k.value: v for k, v in zip(eintrag.keys, eintrag.values, strict=True) if isinstance(k, ast.Constant)}
            felder[ast.literal_eval(d['schluessel'])] = {x: ast.literal_eval(d[x]) for x in ('vorgabe', 'min', 'max')
                                                          if x in d and isinstance(d[x], (ast.Constant, ast.UnaryOp))}      # nur Zahlen (auch negative): Namen und Klassenkonstanten (`Haarlaenge.UNTEN_CM`, `GRENZE_CM[0]`) sind keine Literale
        self.assertEqual(felder['bildbreite'], {'vorgabe': 128, 'min': 96, 'max': 1024})
        self.assertEqual(felder['stufe_stillstand'], {'vorgabe': 3, 'min': 1, 'max': 100})
        self.assertEqual(felder['tafelbreite'], {'vorgabe': 384, 'min': 128, 'max': 1024})

    def test_die_schwellen_der_noten_und_der_messguete_sind_die_genannten(self):
        n = self.D + 'iterationsnetznote.py'
        self.assertEqual([konstante(n, 'Iterationsnetznote', k) for k in ('PROBEN', 'NAH_M', 'MASS_MM')], [60000, 0.015, 50.0])
        r = self.P + 'rundenauswahl.py'
        self.assertEqual([konstante(r, 'Rundenauswahl', k) for k in ('TOLERANZ', 'PROBE_RUNDEN', 'FARB_RAUSCHEN')], [0.002, 3, 0.0005])
        m = self.P + 'messpruefung.py'
        self.assertEqual([konstante(m, 'Messpruefung', k) for k in ('PROJEKTION_MIN', 'FOTO_MIN', 'TIEFE_MIN')], [0.95, 0.8, 30.0])
        self.assertEqual(konstante(self.P + 'gesamtnote.py', 'Gesamtnote', 'HAAR'), 0.25)
        self.assertEqual(konstante(self.D + 'begutachtungsrunde.py', 'Begutachtungsrunde', 'RUNDEN_HOECHSTENS'), 50)

    def test_die_rollen_und_ihre_winkel_sind_die_genannten(self):
        rollen = konstante(self.D + 'meshoptionen.py', 'Meshoptionen', 'ROLLEN')
        self.assertEqual([r[0] for r in rollen], ['auto', 'vorne', 'hinten', 'links', 'rechts', 'gesicht', 'detail', 'aus'])
        self.assertEqual(konstante(self.D + 'iterationsreferenz.py', 'Iterationsreferenz', 'ROLLEN'),
                         {'vorne': 0, 'links': 90, 'rechts': -90, 'hinten': 180})

    def test_die_schritte_des_laufs_sind_die_genannten(self):
        schritte = konstante(self.D + 'engine2d3dkleiderlauf.py', 'Engine2d3dKleiderlauf', 'SCHRITTE')
        # Stand 07.10.2026: davor `vorbereitung` (03.10.) und `segmentierung` (optional), danach `kleiderstuecke` vor den Iterationen, dazu `kopf` (der Kopf aus den drei Fotos, 07.10.) —
        # die Prüfung nannte noch die sieben von 02.10.2026.
        self.assertEqual(schritte, ('vorbereitung', 'netz', 'kopf', 'segmentierung', 'koerper', 'grundfigur', 'kleiderstuecke', 'iterationen', 'export', 'film', 'speichern'))

    def test_das_farbraster_waechst_wie_die_zeile_es_nennt(self):
        # Dieselbe Rechnung wie Iterationsnote.felder (Docstring: 2485 × 3728 → 155 × 233).
        from core.dienste.iterationsnote import Iterationsnote
        for (breite, hoehe), soll in (((128, 192), (8, 12)), ((256, 384), (16, 24)), ((512, 768), (32, 48)), ((2485, 3728), (155, 233))):
            self.assertEqual(Iterationsnote.felder(breite, hoehe), soll)
