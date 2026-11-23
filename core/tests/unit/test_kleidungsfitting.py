"""Hilfe → Kleidung → Fitting (22.11.2026): `Kleidungsfitting` bereitet `meshgenesis/kleidmethoden.json` für die Seite auf — Methoden mit Ablauf je Gruppe, Verlauf mit einer
Zelle je Methode, Urteile mit Anzeige. Ohne Datenbank, ohne Karte. Noch nicht gelaufen (Tests nur auf Ansage)."""
import unittest

from kleidung.fitting import Kleidungsfitting


class KleidungsfittingTest(unittest.TestCase):
    databases = []

    def test_verlauf_nennt_nur_methoden_der_gruppe(self):
        # eine Zelle für eine Methode, die es in der Gruppe nicht gibt, fiele auf der Seite still weg
        d = Kleidungsfitting.daten()
        for g in d['gruppen']:
            kennungen = {m['kennung'] for m in d['methoden'] if m['gruppe'] == g['kennung']}
            for z in g.get('verlauf', []):
                self.assertLessEqual(set(z.get('zellen', {})), kennungen, '%s / %s' % (g['kennung'], z['schritt']))

    def test_eine_zelle_je_methode_mit_ablauf(self):
        for g in Kleidungsfitting.gruppen():
            for z in g['verlauf']:
                self.assertEqual(len(z['zellen']), len(g['methoden']), '%s / %s' % (g['kennung'], z['schritt']))
                for c in z['zellen']:
                    self.assertIn('text', c)
                    self.assertIn('zeit', c)

    def test_vier_kleidermethoden(self):
        kleider = next(g for g in Kleidungsfitting.gruppen() if g['kennung'] == 'kleider')
        self.assertEqual([m['kennung'] for m in kleider['methoden']], ['bibliothek', 'eigen', 'drapieren', 'passend'])

    def test_urteile_sind_bekannt(self):
        # das Urteil ist zugleich CSS-Klasse `fit-<urteil>` (`static/css/hilfe_fitting.css`)
        for g in Kleidungsfitting.gruppen():
            for m in g['methoden']:
                for q in m['qualitaet']:
                    self.assertIn(q['urteil'], Kleidungsfitting.URTEILE, m['kennung'])
                    self.assertNotIn('ue', q['name'])

    def test_konzept_urteile_und_gruppen(self):
        # Konzeptteil (`Assets/kleidung/fitting_konzept.json`): jedes Urteil ist eine CSS-Klasse, Übernahmen nach Gruppe zusammengefasst
        from kleidung.fittingkonzept import Kleidungsfittingkonzept
        k = Kleidungsfittingkonzept.kontext()
        befunde = k['drapieren']['befund'] + [q for a in k['haut']['aufgaben'] for q in a['befund']]
        for q in befunde:
            self.assertIn(q['urteil'], Kleidungsfitting.URTEILE, q['text'])
        gruppen = [g['gruppe'] for g in k['uebernehmen']]
        self.assertEqual(len(gruppen), len(set(gruppen)), 'Gruppe zerrissen: Zeilen einer Gruppe stehen nicht beieinander')
        for g in k['uebernehmen']:
            for z in g['zeilen']:
                self.assertIn(z['urteil'], Kleidungsfitting.URTEILE, z['was'])
                self.assertNotEqual(z['nach'], z['von'])

    def test_einstellungen_brauchen_was_gut_offen(self):
        # Einstellungen → Kleider (`settings_kleider_methoden.html`) liest dieselben Methoden
        for m in Kleidungsfitting.daten()['methoden']:
            for feld in ('name', 'weg', 'wahl', 'was', 'quelle', 'gut', 'offen'):
                self.assertIn(feld, m, m['kennung'])


if __name__ == '__main__':
    unittest.main()
