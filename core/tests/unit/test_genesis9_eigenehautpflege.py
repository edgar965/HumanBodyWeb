# -*- coding: utf-8 -*-
u"""Eigene Häute umbenennen und löschen, Modellzeilen der Szene umbenennen (18.10.2026). Kunstdaten im Wegwerfordner, keine Daz-Bibliothek. Geschrieben, nicht gelaufen.

Edgar, 18.10.2026: „es sollen doch ALLE Assets umbenannt und gelöscht werden können?" — „mach beide" (eigene Häute und Modellzeilen der Szene).

1. Umbenennen ändert den Namen im Rezept, der Schlüssel (Dateiname, Kennung `eigen:<schluessel>`) bleibt; es gibt weiter genau eine Haut.
2. Eine andere Haut mit gleichem Namen (ohne Groß-/Kleinschreibung) → Fehler; derselbe Name in anderer Schreibung bei der Haut selbst ist erlaubt; leerer Name → Fehler.
3. Unbekannte Haut und Pfadzeichen im Schlüssel → `LookupError` — nichts wird angefasst.
4. Speichern unter dem NEUEN Namen überschreibt die umbenannte Haut, statt eine zweite mit gleichem Namen anzulegen.
5. Löschen legt das Rezept in `papierkorb/`; `praesets()` führt es nicht mehr, `rezept()` kennt es nicht; die Datei im Papierkorb ist lesbar.
6. Endpunkte: Umbenennen 200 / 400 (leer, doppelt) / 404; Löschen 200 / 404; GET → 405; beide Adressen im Router.
7. Browser (am Quelltext): „Meine Häute" im Popup der Haut mit Rechtsklick-Menü; Löschen einer getragenen Haut setzt den Grundsatz zurück; die Modellzeile hat „Umbenennen …"
   und „Aus der Szene entfernen", der Katalogschlüssel zieht beim Umbenennen mit.

Sabotage-Gegenprobe (nicht gefahren): in `speichern` `vorhandener` weglassen → Fall 4 rot; in `_rezept` die Schlüsselprüfung weglassen → Fall 3 rot (`../x`).
"""
import json
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from core.projekt_temp import ProjektTemp

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from core.api.g9eigenehautpflegeapi import G9eigenehautpflegeapi  # noqa: E402
from core.dienste.g9eigenehaut import G9eigenehaut  # noqa: E402
from core.dienste.g9eigenehautpflege import G9eigenehautpflege  # noqa: E402

GRUND = 'G9 Feminine Skin 01 MAT'


class Ablage:
    """Ein Wegwerfordner als Ablage der eigenen Häute."""

    def __init__(self):
        self._ordner = ProjektTemp.wegwerfordner(prefix='g9eigenehautpflege_')

    def __enter__(self):
        self.pfad = Path(self._ordner.__enter__())
        self._patch = mock.patch.object(G9eigenehaut, 'ordner', staticmethod(lambda: self.pfad))
        self._patch.start()
        return self.pfad

    def __exit__(self, *fehler):
        self._patch.stop()
        return self._ordner.__exit__(*fehler)


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer').joinpath(*teile).read_text(encoding='utf-8')


class EigeneHautPflegeTest(SimpleTestCase):
    databases = set()

    def test_1_umbenennen_aendert_den_namen_und_nicht_den_schluessel(self):
        with Ablage() as ordner:
            G9eigenehaut.speichern('Sommer', GRUND, {'sommer': 10})
            eintrag = G9eigenehautpflege.umbenennen('sommer', 'Winterhaut')
            self.assertEqual(eintrag['id'], 'eigen:sommer')
            self.assertEqual(eintrag['name'], 'Eigene Haut · Winterhaut')
            self.assertEqual(G9eigenehaut.rezept('eigen:sommer')['name'], 'Winterhaut')
            self.assertEqual(G9eigenehaut.rezept('eigen:sommer')['hautebenen'], {'sommer': 10}, 'der Rest des Rezepts bleibt')
            self.assertEqual(sorted(p.name for p in ordner.glob('*.json')), ['sommer.json'])
            self.assertEqual([e['id'] for e in G9eigenehaut.praesets()], ['eigen:sommer'])

    def test_2_doppelte_und_leere_namen(self):
        with Ablage():
            G9eigenehaut.speichern('Sommer', GRUND)
            G9eigenehaut.speichern('Winter', GRUND)
            with self.assertRaises(ValueError):
                G9eigenehautpflege.umbenennen('sommer', 'WINTER')
            with self.assertRaises(ValueError):
                G9eigenehautpflege.umbenennen('sommer', '   ')
            self.assertEqual(G9eigenehautpflege.umbenennen('sommer', 'SOMMER')['name'], 'Eigene Haut · SOMMER', 'die eigene Schreibung ändern ist kein Doppelgänger')

    def test_3_unbekannt_und_pfadzeichen(self):
        with Ablage() as ordner:
            G9eigenehaut.speichern('Sommer', GRUND)
            for schluessel in ('gibtsnicht', '../sommer', '', 'Sommer'):
                with self.assertRaises(LookupError, msg=schluessel):
                    G9eigenehautpflege.umbenennen(schluessel, 'Neu')
                with self.assertRaises(LookupError, msg=schluessel):
                    G9eigenehautpflege.loeschen(schluessel)
            self.assertEqual(sorted(p.name for p in ordner.glob('*.json')), ['sommer.json'])

    def test_4_speichern_unter_dem_neuen_namen_ueberschreibt(self):
        with Ablage() as ordner:
            G9eigenehaut.speichern('Sommer', GRUND, {'a': 1})
            G9eigenehautpflege.umbenennen('sommer', 'Winterhaut')
            _eintrag, ueberschrieben = G9eigenehaut.speichern('winterhaut', GRUND, {'a': 2})
            self.assertTrue(ueberschrieben)
            self.assertEqual(sorted(p.name for p in ordner.glob('*.json')), ['sommer.json'], 'keine zweite Haut mit gleichem Namen')
            self.assertEqual(G9eigenehaut.rezept('eigen:sommer')['hautebenen'], {'a': 2})

    def test_5_loeschen_geht_in_den_papierkorb(self):
        with Ablage() as ordner:
            G9eigenehaut.speichern('Sommer', GRUND, {'a': 1})
            ziel = G9eigenehautpflege.loeschen('sommer')
            self.assertEqual(ziel.parent, ordner / 'papierkorb')
            self.assertTrue(ziel.name.endswith('_sommer.json'))
            self.assertEqual(json.loads(ziel.read_text(encoding='utf-8'))['name'], 'Sommer', 'das Rezept bleibt lesbar (zurückholen = Datei zurückkopieren)')
            self.assertEqual(G9eigenehaut.praesets(), [])
            self.assertIsNone(G9eigenehaut.rezept('eigen:sommer'))
            with self.assertRaises(LookupError):
                G9eigenehautpflege.loeschen('sommer')

    def test_6_endpunkte(self):
        fabrik = RequestFactory()
        adresse = '/api/character/genesis9-figur/eigenehaut/sommer/'
        self.assertEqual(reverse('g9_figur_eigenehaut_umbenennen', args=['sommer']), adresse + 'umbenennen/')
        self.assertEqual(reverse('g9_figur_eigenehaut_loeschen', args=['sommer']), adresse + 'loeschen/')
        with Ablage():
            G9eigenehaut.speichern('Sommer', GRUND)
            G9eigenehaut.speichern('Winter', GRUND)

            def senden(aufruf, schluessel, nutzlast):
                return aufruf(fabrik.post(adresse, json.dumps(nutzlast), content_type='application/json'), schluessel)

            antwort = senden(G9eigenehautpflegeapi.umbenennen, 'sommer', {'name': 'Frühling'})
            self.assertEqual(antwort.status_code, 200)
            self.assertEqual(json.loads(antwort.content)['eintrag']['name'], 'Eigene Haut · Frühling')
            self.assertEqual(senden(G9eigenehautpflegeapi.umbenennen, 'sommer', {'name': ''}).status_code, 400)
            self.assertEqual(senden(G9eigenehautpflegeapi.umbenennen, 'sommer', {'name': 'winter'}).status_code, 400, 'doppelter Name')
            self.assertEqual(senden(G9eigenehautpflegeapi.umbenennen, 'gibtsnicht', {'name': 'X'}).status_code, 404)
            self.assertEqual(senden(G9eigenehautpflegeapi.loeschen, 'gibtsnicht', {}).status_code, 404)
            geloescht = senden(G9eigenehautpflegeapi.loeschen, 'sommer', {})
            self.assertEqual(geloescht.status_code, 200)
            self.assertTrue(json.loads(geloescht.content)['ok'])
            self.assertEqual(G9eigenehautpflegeapi.loeschen(fabrik.get(adresse), 'winter').status_code, 405)


class PflegeImBrowserTest(SimpleTestCase):
    databases = set()

    def test_7a_meine_haeute_im_popup(self):
        pflege = quelltext('charakter', 'genesis9', 'genesis9eigenehautpflege.js')
        self.assertIn('Kontextmenue.binden(zeile, () => Genesis9eigenehautpflege.eintraege(inst, plan, haut, danach));', pflege)
        self.assertIn("text: 'Umbenennen …'", pflege)
        self.assertIn("text: 'Löschen'", pflege)
        self.assertIn("adresse(haut, 'umbenennen')", pflege)
        self.assertIn("adresse(haut, 'loeschen')", pflege)
        self.assertIn('zeile.textContent = haut.rezept?.name || haut.id;', pflege, 'Namen des Nutzers als TEXT, nie als HTML')
        block = quelltext('charakter', 'genesis9', 'genesis9hautdialogblock.js')
        self.assertIn('Genesis9eigenehautpflege.liste(inst, plan, nachSpeichern)', block)
        self.assertIn('liste.neu()', block, 'eine neu gespeicherte Haut steht sofort in der Liste')

    def test_7b_getragene_haut_geht_auf_den_grundsatz_zurueck(self):
        pflege = quelltext('charakter', 'genesis9', 'genesis9eigenehautpflege.js')
        self.assertIn('if (inst.haut === haut.id)', pflege)
        self.assertIn("await inst.hautSetzen(haut.rezept?.grund || '');", pflege)
        # Erst der Server, dann die Figur: scheitert das Löschen, bleibt die Figur wie sie ist.
        self.assertLess(pflege.index("adresse(haut, 'loeschen')"), pflege.index('inst.hautSetzen('))

    def test_7c_modellzeile_umbenennen_und_entfernen(self):
        menue = quelltext('charakter', 'speichernmenue.js')
        self.assertIn('Figurumbenennen.umbenennen(charId)', menue)
        self.assertIn("text: 'Aus der Szene entfernen'", menue)
        self.assertIn('fn.deleteCharacter(charId)', menue)
        figur = quelltext('charakter', 'figurumbenennen.js')
        self.assertIn('inst.presetName = name;', figur)
        self.assertIn('if (inst.presetKey) inst.presetKey = name;', figur, 'beim Laden einer Szene kommt der Name aus dem Schlüssel')
        self.assertIn('markDirty()', figur)
