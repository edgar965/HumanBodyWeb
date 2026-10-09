# -*- coding: utf-8 -*-
"""Hilfe -> Recherche -> Human 3D, Urteile und drei Tabellen (09.10.2026).

Edgar: „die Teile, die wir eingebaut haben oder die sich nicht lohnen (weil veraltet oder schlecht), bitte in getrennte Tabellen unten“ —
das Urteil je Projekt (`Rechercheurteile`) gegen die ECHTE Datei, die Verteilung und die drei Tabellen gegen Kunstprojekte.
"""

from django.test import SimpleTestCase

from core.dienste.rechercheabschnitte import Rechercheabschnitte
from core.dienste.rechercheprojekte import Rechercheprojekte
from core.dienste.recherchetabelle import Recherchetabelle
from core.dienste.rechercheurteile import Rechercheurteile

from .test_recherche_human3d import _projekt, _zellen


class DieUrteile(SimpleTestCase):
    def test_jede_kennung_gehoert_zu_einem_projekt_und_jedes_projekt_hat_ein_urteil(self):
        ids = {p['id'] for p in Rechercheprojekte.projekte()}
        urteile = Rechercheurteile.urteile()
        self.assertEqual(set(urteile) - ids, set(), 'Urteil ohne Projekt')
        self.assertEqual(ids - set(urteile), set(), 'Projekt ohne Urteil')

    def test_jedes_urteil_hat_einen_grund_und_die_offenen_ein_bereich(self):
        for kennung, u in Rechercheurteile.urteile().items():
            self.assertTrue(u['grund'].strip(), f'{kennung}: Grund fehlt')
            if Rechercheurteile.abschnitt(u['urteil']) == Rechercheurteile.OFFEN:
                self.assertTrue(u['bereich'].strip(), f'{kennung}: Bereich fehlt')
            self.assertIn(u['aufwand'], ('', 'klein', 'mittel', 'groß'), kennung)

    def test_abgelegte_und_eingebaute_tragen_keinen_aufwand(self):
        for kennung, u in Rechercheurteile.urteile().items():
            if Rechercheurteile.abschnitt(u['urteil']) != Rechercheurteile.OFFEN:
                self.assertEqual(u['aufwand'], '', kennung)

    def test_eingebaut_ist_die_belegte_kurze_liste(self):
        """Nicht mehr als die am Code gesehenen: Ein Agent hielt einen C++-Port und eine ComfyUI-Hülle für „eingebaut“, weil das Modell dahinter bei uns läuft."""
        eingebaut = [k for k, u in Rechercheurteile.urteile().items() if u['urteil'] == 'eingebaut']
        self.assertNotIn('localai-org--gem-x.cpp', eingebaut)
        self.assertNotIn('PozzettiAndrea--ComfyUI-MotionCapture', eingebaut)
        self.assertIn('NVlabs--GEM-X', eingebaut)

    def test_verteilen_legt_jedes_projekt_in_genau_eine_tabelle(self):
        projekte = [_projekt(id='a'), _projekt(id='b'), _projekt(id='c'), _projekt(id='d')]
        urteile = {'a': {'urteil': 'eingebaut'}, 'b': {'urteil': 'veraltet'}, 'c': {'urteil': 'verbesserung'}}
        gruppen = Rechercheurteile.verteilen(projekte, urteile)
        self.assertEqual({k: [p['id'] for p in v] for k, v in gruppen.items()}, {'offen': ['c', 'd'], 'eingebaut': ['a'], 'abgelegt': ['b']})

    def test_ein_unbekanntes_urteil_zaehlt_nicht(self):
        self.assertEqual(Rechercheurteile.abschnitt('gibt_es_nicht'), Rechercheurteile.OFFEN)
        self.assertEqual(Rechercheurteile.rang(None), Rechercheurteile.OHNE[2])

    def test_jede_tabelle_hat_eigenen_schluessel_und_gleich_viele_zellen_wie_spalten(self):
        schluessel = set()
        for abschnitt in (Rechercheurteile.OFFEN, Rechercheurteile.EINGEBAUT, Rechercheurteile.ABGELEGT):
            tabelle = Recherchetabelle.bauen([_projekt()], None, {'a--b': {'urteil': 'veraltet', 'grund': 'alt', 'bereich': 'x'}}, abschnitt)
            schluessel.add(tabelle['key'])
            self.assertEqual(len(tabelle['zeilen'][0]['zellen']), len(tabelle['spalten']), abschnitt)
        self.assertEqual(len(schluessel), 3)
        self.assertEqual(Rechercheabschnitte.plan(Rechercheurteile.OFFEN)['key'], 'hilfe-recherche-human3d')   # Edgars gemerkte Spaltenbreiten hängen daran

    def test_die_prio_steht_nur_in_der_ersten_tabelle(self):
        for abschnitt in (Rechercheurteile.EINGEBAUT, Rechercheurteile.ABGELEGT):
            self.assertNotIn('prio', [s['key'] for s in Recherchetabelle.bauen([], None, None, abschnitt)['spalten']])

    def test_die_einschaetzung_maskiert_fremden_text_und_sortiert_verbesserung_vor_neu(self):
        u = {'urteil': 'verbesserung', 'grund': '<script>x</script>', 'bereich': '"><b>', 'aufwand': 'klein'}
        zelle = _zellen(Recherchetabelle.bauen([_projekt()], None, {'a--b': u}))['einschaetzung']
        self.assertNotIn('<script>', zelle['html'])
        self.assertNotIn('"><b>', zelle['html'])
        neu = _zellen(Recherchetabelle.bauen([_projekt()], None, {'a--b': {'urteil': 'neues_feature', 'aufwand': 'klein'}}))['einschaetzung']
        self.assertLess(zelle['sort'], neu['sort'])
        self.assertEqual(zelle['klasse'], 'rc-popupzelle')

    def test_das_fenster_zeigt_das_todo_nur_bei_offenen_projekten(self):
        offen = Recherchetabelle.popup([_projekt()], {'a--b': {'urteil': 'beobachten', 'grund': 'g', 'bereich': 'b', 'aufwand': 'mittel'}})['a--b']
        weg = Recherchetabelle.popup([_projekt()], {'a--b': {'urteil': 'veraltet', 'grund': 'g'}})['a--b']
        self.assertTrue(offen['todo_zeigen'])
        self.assertFalse(weg['todo_zeigen'])
        self.assertEqual(weg['urteil_label'], 'Veraltet')
        self.assertTrue(Recherchetabelle.popup([_projekt()])['a--b']['todo_zeigen'])
