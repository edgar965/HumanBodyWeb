# -*- coding: utf-8 -*-
"""Die Tabelle „Wie liefe das mit Blender“ im Reiter „Tools“ der Seite Hilfe → Architektur → 2D3D (03.10.2026): die Datenmodule `blendervergleich<name>.py`.

WARUM: Die Tabelle sagt anderen Sessions, welches Blender-Werkzeug eine Aufgabe löst und was das Projekt stattdessen tut. Eine lokale Klasse, die es nicht gibt, ein unbekannter
Stand oder eine Zeile „gemessen“ ohne Quelle wäre genau die unbelegte Behauptung, die die Seite verhindern soll. Diese Tests lesen die Datenmodule (kein Blender, kein Rechnen) und halten fest:
das Schema stimmt, jede lokale Klasse steht im Code, jeder Stand ist bekannt, `genutzt` und `gemessen` nennen eine Quelle, die Pflichtaufgaben des Auftrags sind da."""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.architektur2d3dblender import Architektur2d3dblender
from core.dienste.architektur2d3dklassen import Architektur2d3dklassen

#: Umschreibungen, die in sichtbaren Texten nichts zu suchen haben (echte Umlaute, `~/.claude/CLAUDE.md`). Nur Prosa wird geprüft, nie Bezeichner und Aufrufe.
UMSCHREIBUNG = re.compile(r'\b(fuer|ueber|Ueber|Faelle|Koerper|Staerke|Ruecken|moeglich|waehrend|waehlen|zurueck|loeschen|aendern|Aenderung|aehnlich|'
                          r'Groesse|groesse|Hoehe|hoehe|Naehte|naehte|Schluessel|Uebersicht|oeffnen)\b')
#: Eine Fundstelle: ein Dateiname mit Punkt (`.py`, `.md`, `.json`) oder das README des Stoffsolvers.
QUELLE = re.compile(r'\.(py|md|json|blend)\b|README')
#: Aufgaben, die der Auftrag mindestens verlangt (Stichwort im Namen der Aufgabe).
PFLICHT = ['Mensch-Figur erzeugen', 'Körperform', 'Gesicht', 'Haut und Textur aus Fotos', 'Rig und Skinning', 'Retarget', 'Pose', 'Kleidung aus Schnittmuster',
           'Passform', 'Stoffsimulation', 'Kollision', 'Haar erzeugen', 'Haar-Dynamik', 'UV abwickeln', 'UV packen', 'Texturen backen', 'Rendern', 'Bildvergleich',
           'Export', 'Automatisierung']


def abschnitte():
    """`[(stem, klasse)]` aller Dateien `blendervergleich*.py` — ein Ladefehler ist selbst ein Befund."""
    return [(stem, klasse, fehler) for stem, klasse, fehler in Architektur2d3dblender.abschnittsklassen()]


def zeilen():
    """`[(kennung, zeile)]` über alle Abschnitte (rohe Tupel, wie sie in `ZEILEN` stehen)."""
    return [(k.KENNUNG, z) for _stem, k, _fehler in abschnitte() if k is not None for z in k.ZEILEN]


def prosa(kennung, z):
    """Die Felder, die ein Mensch liest: Aufgabe, lokales Werkzeug, Blender-Werkzeug, Unterschied — ohne die Stellen in Rückwärtsstrichen (Bezeichner, Dateien, Aufrufe)."""
    aufgabe, lokal, _lokal_aufruf, _klassen, blender, _blender_aufruf, _stand, unterschied = z
    return re.sub(r'`[^`]*`', ' ', ' '.join([aufgabe, lokal, blender, unterschied]))


class BlendervergleichSchemaTest(SimpleTestCase):
    def test_jede_datei_laedt_und_traegt_die_klasse_mit_kennung_titel_einleitung_und_zeilen(self):
        gefunden = abschnitte()
        self.assertGreater(len(gefunden), 0, 'keine Datei blendervergleich*.py')
        for stem, klasse, fehler in gefunden:
            self.assertIsNotNone(klasse, '%s: %s' % (stem, fehler))
            self.assertTrue(klasse.KENNUNG.strip() and klasse.TITEL.strip() and klasse.EINLEITUNG.strip(), stem)
            self.assertGreater(len(klasse.ZEILEN), 0, stem)

    def test_die_kennungen_der_abschnitte_sind_eindeutig_weil_sie_die_anker_der_seite_sind(self):
        kennungen = [k.KENNUNG for _stem, k, _fehler in abschnitte() if k is not None]
        self.assertEqual(len(kennungen), len(set(kennungen)))
        for kennung in kennungen:
            self.assertRegex(kennung, r'^[a-z0-9-]+$', 'KENNUNG nur ASCII, Kleinbuchstaben und Bindestrich')

    def test_jede_zeile_hat_die_acht_felder_des_schemas_und_keine_leeren_texte(self):
        for kennung, z in zeilen():
            self.assertEqual(len(z), 8, '%s / %s' % (kennung, z[0]))
            aufgabe, lokal, lokal_aufruf, klassen, blender, blender_aufruf, stand, unterschied = z
            stelle = '%s / %s' % (kennung, aufgabe)
            for name, text in (('aufgabe', aufgabe), ('lokal', lokal), ('lokal_aufruf', lokal_aufruf), ('blender', blender),
                               ('blender_aufruf', blender_aufruf), ('stand', stand), ('unterschied', unterschied)):
                self.assertTrue(str(text).strip(), '%s: %s ist leer' % (stelle, name))
            self.assertIsInstance(klassen, list, stelle)

    def test_eine_zeile_ohne_lokale_klasse_sagt_im_aufruf_dass_es_kein_lokales_werkzeug_gibt(self):
        for kennung, z in zeilen():
            if not z[3]:
                self.assertTrue(z[2].lstrip().startswith('—') or 'kein' in z[2].lower(), '%s / %s: leere Klassenliste ohne Erklärung' % (kennung, z[0]))

    def test_jeder_stand_ist_einer_der_fuenf_bekannten(self):
        for kennung, z in zeilen():
            self.assertIn(z[6], Architektur2d3dblender.STAENDE, '%s / %s: Stand „%s“' % (kennung, z[0], z[6]))

    def test_jede_aufgabe_steht_je_abschnitt_nur_einmal(self):
        for _stem, k, _fehler in abschnitte():
            if k is None:
                continue
            aufgaben = [z[0] for z in k.ZEILEN]
            self.assertEqual(len(aufgaben), len(set(aufgaben)), k.KENNUNG)

    def test_die_sichtbaren_texte_enthalten_keine_ae_oe_ue_umschreibungen(self):
        for _stem, k, _fehler in abschnitte():
            if k is None:
                continue
            self.assertIsNone(UMSCHREIBUNG.search(re.sub(r'`[^`]*`', ' ', k.TITEL + ' ' + k.EINLEITUNG)), k.KENNUNG)
        for kennung, z in zeilen():
            treffer = UMSCHREIBUNG.search(prosa(kennung, z))
            self.assertIsNone(treffer, '%s / %s: „%s“' % (kennung, z[0], treffer.group(0) if treffer else ''))

    def test_genutzt_und_gemessen_nennen_eine_fundstelle_im_unterschied(self):
        for kennung, z in zeilen():
            if z[6] in ('genutzt', 'gemessen'):
                self.assertRegex(z[7], QUELLE, '%s / %s: Stand „%s“ ohne Datei oder README' % (kennung, z[0], z[6]))

    def test_vorhanden_und_keins_nennen_den_beleg_der_introspektion_oder_eine_quelle(self):
        for kennung, z in zeilen():
            if z[6] in ('vorhanden', 'keins', 'addon'):
                self.assertRegex(z[7], r'Introspektion|ergebnis_introspektion|operatoren\.txt|Konzept|Manifest|bl_info|\.md|\.py|README',
                                 '%s / %s: Stand „%s“ ohne Beleg' % (kennung, z[0], z[6]))

    def test_die_pflichtaufgaben_des_auftrags_stehen_in_der_tabelle(self):
        aufgaben = [z[0] for _kennung, z in zeilen()]
        for stichwort in PFLICHT:
            self.assertTrue(any(stichwort in a for a in aufgaben), 'Aufgabe „%s“ fehlt' % stichwort)


class BlendervergleichKlassenTest(SimpleTestCase):
    def test_jede_lokale_klasse_der_zeilen_steht_im_code(self):
        geprueft = {}
        for kennung, z in zeilen():
            for eintrag in z[3]:
                datei, klasse = tuple(eintrag)
                if (datei, klasse) not in geprueft:
                    geprueft[(datei, klasse)] = Architektur2d3dklassen.zeile(datei, klasse)
                self.assertEqual(geprueft[(datei, klasse)]['fehlt'], '', '%s / %s: %s in %s' % (kennung, z[0], klasse, datei))

    def test_die_seite_meldet_fuer_den_vergleich_keinen_befund(self):
        kontext = Architektur2d3dblender.kontext()
        self.assertEqual(kontext['befunde'], [])
        self.assertEqual(kontext['zeilen'], len(zeilen()))
        self.assertEqual(sum(s['anzahl'] for s in kontext['zaehlung']), kontext['zeilen'])

    def test_jede_rezeptzeile_nennt_eine_methode_die_es_im_code_gibt(self):
        wurzel = Path(settings.TOOLS_ROOT)
        quellen = ''
        for ordner in ('Genesis9', '2d3DIterationen', 'HumanBodyWeb/core/dienste'):
            for datei in (wurzel / ordner).rglob('*.py'):
                quellen += datei.read_text(encoding='utf-8', errors='replace')
        for kennung, z in zeilen():
            for aufruf in (z[2], z[5]):
                for name in re.findall(r'\bm\.([a-z_0-9]+)\(', aufruf):
                    self.assertIn('def %s(' % name, quellen, '%s / %s: m.%s gibt es nicht' % (kennung, z[0], name))
