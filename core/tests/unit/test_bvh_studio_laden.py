# -*- coding: utf-8 -*-
u"""BVH Studio: drei Befunde vom 11.09.2026 (Edgar), alle still.

1. „kamera spur gelöscht - Undo funktioniert nicht": Die Tastenkürzel
   prüften `ereignis.code` — die PHYSISCHE Taste in US-Lage. Auf einer
   deutschen Tastatur liegt das Z, wo im US-Layout Y ist: Strg+Z meldete
   `code = 'KeyY'` und löste REDO aus. Jetzt `key`, die Taste auf der Kappe.
2. „Lichtkegel (aus) gesetzt und projekt gespeichert, beim neu laden war der
   alte Status": `Projektdaten._lichter` schrieb `coneVisible`,
   `Szenenlichter._spurwerte` las nur `visible` und `muted`.
3. „auch boden größe wird nicht gespeichert": gespeichert ja, gelesen nur
   beim Seitenstart (`createFloorTrack`). Zur Laufzeit (Datei → Laden,
   Rückgängig) bleibt der Boden stehen (Szenen-Element, nicht löschbar), und
   niemand legte die Werte darauf. Jetzt `applyFloorOverride` nach dem
   Wiederherstellen.

Dazu: Sprungknöpfe Anfang/Ende in der Abspielleiste (Pos1/Ende).
Geprüft am Quelltext; Sabotage: `taste === 'z'` zurück auf `code` → 1 rot.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

WURZEL = Path(settings.BASE_DIR)
STUDIO = WURZEL / 'static' / 'viewer' / 'bvh_studio'


def _studio(name):
    return (STUDIO / name).read_text(encoding='utf-8')


class TastenTest(SimpleTestCase):

    databases = set()

    def test_undo_und_redo_gehen_ueber_key_nicht_code(self):
        index = _studio('index.js')
        tasten = index[index.index("window.addEventListener('keydown'"):]
        tasten = tasten[:tasten.index('}, true);')]
        self.assertIn("String(ereignis.key || '').toLowerCase()", tasten)
        self.assertIn("taste === 'z'", tasten)
        self.assertIn("taste === 'y'", tasten)
        self.assertIn("taste === 'u'", tasten)
        # Die Verwechslung darf nicht zurückkommen.
        self.assertNotIn("ereignis.code === 'KeyZ'", tasten)
        self.assertNotIn("ereignis.code === 'KeyY'", tasten)

    def test_sprungtasten_und_knoepfe(self):
        abspiel = _studio('playback.js')
        self.assertIn("getElementById('pb-start')", abspiel)
        self.assertIn("getElementById('pb-end')", abspiel)
        self.assertIn("e.code === 'Home'", abspiel)
        self.assertIn("e.code === 'End'", abspiel)
        self.assertIn('springen(abspielende())', abspiel)
        html = (WURZEL / 'templates' / 'bvh_studio.html').read_text(encoding='utf-8')
        self.assertIn('id="pb-start"', html)
        self.assertIn('id="pb-end"', html)


class LadenTest(SimpleTestCase):

    databases = set()

    def test_lichtkegel_der_szenenlichter_wird_gelesen(self):
        daten = _studio('projekt_daten.js')
        self.assertIn('coneVisible: t.coneVisible !== false', daten)
        lichter = _studio('szenenlichter.js')
        spurwerte = lichter[lichter.index('static _spurwerte(spur, werte)'):]
        spurwerte = spurwerte[:spurwerte.index('static _clips') if 'static _clips' in spurwerte else len(spurwerte)]
        self.assertIn('spur.coneVisible = werte.coneVisible ?? true', spurwerte)

    def test_bodenwerte_gelten_auch_beim_laden_zur_laufzeit(self):
        boden = _studio('spur_boden.js')
        self.assertIn('export function applyFloorOverride(override)', boden)
        self.assertIn('fn.applyFloorOverride = applyFloorOverride', boden)
        fuer = boden[boden.index('export function applyFloorOverride'):]
        fuer = fuer[:fuer.index('export function updateFloorMaterial')]
        for feld in ('override.width', 'override.length', 'override.centerX', 'override.color',
                     'override.roughness', 'override.metalness', 'override.gridVisible', 'override.texture'):
            self.assertIn(feld, fuer, feld)
        laden = _studio('projekt_wiederherstellung.js')
        nach = laden.index('fn.applyFloorOverride?.(data.sceneFloor)')
        self.assertGreater(nach, laden.index('Projektwiederherstellung._modellspurenVerlinken();'),
                           'der Boden wird NACH den Spuren belegt')


class LinealTest(SimpleTestCase):
    u"""Das Lineal bleibt beim Blättern sichtbar (Edgar, 11.09.2026: „diese
    Spaltenüberschrift soll immer sichtbar bleiben, auch beim blättern")."""

    databases = set()

    def test_lineal_haengt_am_sichtbaren_rand_und_liegt_ueber_den_reihen(self):
        zeichnen = _studio('zeitleiste_zeichnen.js')
        reihen = zeichnen.index('_reihen(breite, pps);')
        lineal = zeichnen.index('Zeitleistenlineal.zeichnen(breite, pps, oben)')
        self.assertLess(reihen, lineal, 'das Lineal muss NACH den Reihen gezeichnet werden')
        self.assertIn('Abspielkopf.zeichnen(hoehe, pps, oben)', zeichnen)
        self.assertIn('static get oben()', _studio('zeitleiste_flaeche.js'))
        self.assertIn('ctx.translate(0, oben)', _studio('zeitleiste_lineal.js'))
        self.assertIn("addEventListener('scroll', () => renderTimeline())", _studio('timeline.js'))

    def test_treffer_im_lineal_rechnen_mit_dem_geblaetterten_anteil(self):
        ziehen = _studio('zeitleiste_ziehen.js')
        self.assertIn('my - Zeitleistenflaeche.oben <= RULER_HEIGHT', ziehen)
        self.assertNotIn('if (my <= RULER_HEIGHT)', ziehen)
        self.assertIn('my - Zeitleistenflaeche.oben <= RULER_HEIGHT', _studio('zeitleiste_menue.js'))
        self.assertIn('position:sticky;top:0', _studio('zeitleiste_kopfspalte.js'))
