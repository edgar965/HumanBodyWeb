"""„Kleidung – Generisch" (30.09.2026) — Sammeleintrag je Kategorie, Umleitung auf das gewählte Stück, gemeinsame
Passform.

Edgar: „OK, dann mach das ‚Kleidung Generisch' erstmal, nach dem Muster von Haar – Generisch."

Alles an einer erfundenen Garderobe (`mock.patch.object`), ohne Daz-Bibliothek, ohne Datenbank, ohne GPU: Die echte
Liste hängt daran, was auf dem Rechner installiert ist (und die Vorgabe je Eintrag kostet dort ~6 ms). """

import unittest
from unittest import mock

from Genesis9.dazkategorien import G9dazkategorien
from Genesis9.garderobe import G9garderobe
from Genesis9.garderobekategorien import G9garderobekategorien
from Genesis9.kleidgenerisch import G9kleidgenerisch

PASSFORM = [
    {'name': 'passform:laenge', 'anzeige': 'Länge (cm)', 'min': -20.0, 'max': 20.0, 'vorgabe': 0.0,
     'gruppe': 'Passform', 'einheit': 'cm', 'schritt': 0.5},
    {'name': 'passform:weite', 'anzeige': 'Weite (cm)', 'min': -3.0, 'max': 6.0, 'vorgabe': 0.0,
     'gruppe': 'Passform', 'einheit': 'cm', 'schritt': 0.1},
]
#: Drei Schuhe, wie sie in der Garderobenliste stehen — jeder trägt die Passform, der zweite dazu einen Daz-Morph.
SCHUHE = [
    {'id': 'stiefel_a', 'name': 'Stiefel A', 'art': 'kleidung', 'zeigbar': True, 'regler': list(PASSFORM)},
    {'id': 'stiefel_b', 'name': 'Stiefel B', 'art': 'kleidung', 'zeigbar': True,
     'regler': [{'name': 'Adj Inflate All', 'anzeige': 'Adj Inflate All', 'min': -1.0, 'max': 1.0, 'vorgabe': 0.0,
                 'gruppe': 'Adjustments'}] + list(PASSFORM)},
    {'id': 'stiefel_c', 'name': 'Stiefel C', 'art': 'kleidung', 'zeigbar': True, 'regler': list(PASSFORM)},
]


class SammeleintragTest(unittest.TestCase):
    """Der Eintrag, den die Garderobenliste je Kategorie zusätzlich führt."""

    def setUp(self):
        gruppen = mock.patch.object(G9kleidgenerisch, 'gruppen', classmethod(lambda cls: [('Schuhe', SCHUHE)]))
        gruppen.start()
        self.addCleanup(gruppen.stop)

    def test_1_eintrag_sieht_aus_wie_ein_stueck(self):
        e = G9kleidgenerisch.eintraege()[0]
        self.assertEqual(e['id'], 'kleidung_generisch_schuhe')
        self.assertEqual(e['name'], 'Kleidung – Generisch: Schuhe')
        self.assertEqual(e['art'], 'kleidung')
        self.assertEqual(e['kategorie'], 'Schuhe')          # ein Eintrag ohne Datei hat keine Daz-Kategorie
        self.assertTrue(e['zeigbar'])
        self.assertTrue(e['generisch'])
        self.assertEqual(e['sorten'], 3)
        self.assertEqual((e['varianten'], e['stile'], e['datei']), ([], [], ''))

    def test_2_passform_steht_einmal_vorn_und_nicht_je_stueck(self):
        regler = G9kleidgenerisch.eintraege()[0]['regler']
        self.assertEqual([r['name'] for r in regler[:2]], ['passform:laenge', 'passform:weite'])
        self.assertEqual({r['gruppe'] for r in regler[:2]}, {'Passform'})
        self.assertEqual([r['einheit'] for r in regler[:2]], ['cm', 'cm'])   # der Browser zeigt sie in Zentimetern
        namen = [r['name'] for r in regler]
        self.assertEqual(namen.count('passform:laenge'), 1)
        self.assertFalse([n for n in namen if n.endswith('.passform:laenge')])

    def test_3_je_stueck_eine_gruppe_mit_anteil_und_echten_morphs(self):
        gruppen = {}
        for r in G9kleidgenerisch.eintraege()[0]['regler']:
            gruppen.setdefault(r['gruppe'], []).append(r['name'])
        self.assertEqual(set(gruppen), {'Passform', 'Mischung', 'Textur', 'Stiefel A', 'Stiefel B', 'Stiefel C'})
        # Jedes Stück trägt dazu die festen Regler „Form (Ort)" (`G9standardmorphe.KLEIDUNG`, 30.09.2026 nachts).
        from Genesis9.standardmorphe import G9standardmorphe
        feste = ['stiefel_b.eigen.' + n for n in G9standardmorphe.namen('kleidung')]
        self.assertEqual(gruppen['Stiefel B'], ['sorte.stiefel_b', 'stiefel_b.Adj Inflate All'] + feste)
        self.assertEqual(gruppen['Stiefel A'], ['sorte.stiefel_a'] + [n.replace('stiefel_b', 'stiefel_a') for n in feste])

    def test_4_das_erste_stueck_traegt_als_vorgabe(self):
        vorgaben = {r['name']: r['vorgabe'] for r in G9kleidgenerisch.eintraege()[0]['regler']
                    if r['name'].startswith('sorte.')}
        self.assertEqual(vorgaben, {'sorte.stiefel_a': 1.0, 'sorte.stiefel_b': 0.0, 'sorte.stiefel_c': 0.0})

    def test_5_kennungen_sind_ascii(self):
        self.assertEqual(G9kleidgenerisch.kennung('Röcke'), 'kleidung_generisch_roecke')
        self.assertEqual(G9kleidgenerisch.kennung('Unterwäsche'), 'kleidung_generisch_unterwaesche')
        self.assertEqual(G9kleidgenerisch.kennung('Rüstung'), 'kleidung_generisch_ruestung')
        self.assertEqual(G9kleidgenerisch.kennung('Meine Fantasy-Sachen'), 'kleidung_generisch_meine_fantasy_sachen')
        self.assertEqual(G9kleidgenerisch.kennung('???'), 'kleidung_generisch_sonstiges')

    def test_6_ist_generisch_nur_am_namen(self):
        self.assertTrue(G9kleidgenerisch.ist_generisch('kleidung_generisch_schuhe'))
        self.assertFalse(G9kleidgenerisch.ist_generisch('haar_generisch'))
        self.assertFalse(G9kleidgenerisch.ist_generisch('stiefel_a'))
        self.assertFalse(G9kleidgenerisch.ist_generisch(None))


class AufloesenTest(unittest.TestCase):
    """Welches Stück gemeint ist, und welche Regler es bekommt."""

    KENNUNG = 'kleidung_generisch_schuhe'

    def setUp(self):
        gruppen = mock.patch.object(G9kleidgenerisch, 'gruppen', classmethod(lambda cls: [('Schuhe', SCHUHE)]))
        gruppen.start()
        self.addCleanup(gruppen.stop)

    def test_1_ohne_angabe_gilt_das_erste(self):
        self.assertEqual(G9kleidgenerisch.aufloesen(self.KENNUNG, {}), ('stiefel_a', {}))
        self.assertEqual(G9kleidgenerisch.aufloesen(self.KENNUNG, None), ('stiefel_a', {}))

    def test_2_der_groesste_anteil_gewinnt_und_seine_regler_verlieren_das_praefix(self):
        # 1,0 wie die getragene Grundsorte: Sie verliert den Gleichstand (test_4), sonst bliebe sie bei 0,8 des anderen.
        kennung, regler = G9kleidgenerisch.aufloesen(self.KENNUNG, {
            'sorte.stiefel_b': 1.0, 'stiefel_b.Adj Inflate All': 0.4, 'stiefel_c.Adj Inflate All': 0.9})
        self.assertEqual(kennung, 'stiefel_b')
        self.assertEqual(regler, {'Adj Inflate All': 0.4})      # der Regler des anderen Stücks bleibt draußen

    def test_3_die_gemeinsame_passform_geht_an_jedes_gewaehlte_stueck(self):
        for wahl in ('stiefel_a', 'stiefel_c'):
            kennung, regler = G9kleidgenerisch.aufloesen(self.KENNUNG, {
                'sorte.' + wahl: 1.0, 'passform:laenge': 4.0, 'passform:weite': -1.5})
            self.assertEqual(kennung, wahl)
            self.assertEqual(regler, {'passform:laenge': 4.0, 'passform:weite': -1.5})

    def test_4_die_grundsorte_verliert_jeden_gleichstand(self):
        # Wie bei „Haar – Generisch": Wer eine andere Sorte auf 100 % zieht, meint die andere.
        kennung, _ = G9kleidgenerisch.aufloesen(self.KENNUNG, {'sorte.stiefel_a': 1.0, 'sorte.stiefel_c': 1.0})
        self.assertEqual(kennung, 'stiefel_c')

    def test_5_unter_gleich_hohen_entscheidet_die_zuletzt_bewegte(self):
        kennung, _ = G9kleidgenerisch.aufloesen(self.KENNUNG, {
            'sorte.stiefel_b': 1.0, 'sorte.stiefel_c': 1.0, 'sorte_zuletzt': 'stiefel_b'})
        self.assertEqual(kennung, 'stiefel_b')

    def test_6_die_grundsorte_auf_null_gibt_nach(self):
        kennung, _ = G9kleidgenerisch.aufloesen(self.KENNUNG, {'sorte.stiefel_a': 0.0, 'sorte.stiefel_b': 0.2})
        self.assertEqual(kennung, 'stiefel_b')

    def test_7_ein_unbekannter_sortenname_wird_ignoriert(self):
        self.assertEqual(G9kleidgenerisch.aufloesen(self.KENNUNG, {'sorte.weg_damit': 1.0})[0], 'stiefel_a')

    def test_8_unbekannte_kategorie_liefert_nichts(self):
        self.assertEqual(G9kleidgenerisch.aufloesen('kleidung_generisch_gibtsnicht', {}), (None, {}))

    def test_9_getragene_stuecke_werden_aufgeloest(self):
        roh = [{'kennung': self.KENNUNG, 'stil': 'x', 'regler_stueck': {'sorte.stiefel_c': 1.0, 'passform:weite': 2.0}},
               {'kennung': 'kin_hair', 'regler_stueck': {}}]
        aus = G9kleidgenerisch.getragene_aufloesen(roh)
        self.assertEqual(aus[0], {'kennung': 'stiefel_c', 'stil': 'x', 'regler_stueck': {'passform:weite': 2.0}})
        self.assertEqual(aus[1], roh[1])                        # ein gewöhnliches Stück bleibt, wie es ist
        self.assertEqual(roh[0]['kennung'], self.KENNUNG)       # die Eingabe wird nicht verändert

    def test_10_ein_getragener_sammeleintrag_ohne_stuecke_faellt_weg(self):
        roh = [{'kennung': 'kleidung_generisch_gibtsnicht'}, {'kennung': 'kin_hair'}]
        self.assertEqual(G9kleidgenerisch.getragene_aufloesen(roh), [{'kennung': 'kin_hair'}])
        self.assertIsNone(G9kleidgenerisch.getragene_aufloesen(None))


OBERTEIL = {'id': 'shirt_1', 'name': 'Shirt 1', 'art': 'kleidung', 'zeigbar': True, 'regler': list(PASSFORM)}
KLEID = {'id': 'kleid_1', 'name': 'Kleid 1', 'art': 'kleidung', 'zeigbar': True, 'regler': list(PASSFORM)}
FUENF = [dict(SCHUHE[0], id='s%d' % i, name='Schuh %d' % i) for i in range(5)]


class MischenTest(unittest.TestCase):
    """Mischen (30.09.2026): Anteile ohne feste Summe, die Reihenfolge nach Anteil, Übergang und Textur-Regler."""

    def test_1_nicht_gestellte_stuecke_stehen_auf_ihrer_vorgabe(self):
        self.assertEqual(G9kleidgenerisch.anteile(SCHUHE, {}), {'stiefel_a': 1.0})

    def test_2_die_anteile_muessen_nicht_hundert_prozent_ergeben(self):
        anteile = G9kleidgenerisch.anteile(SCHUHE, {'sorte.stiefel_b': 0.3})
        self.assertEqual(anteile, {'stiefel_a': 1.0, 'stiefel_b': 0.3})          # Summe 1,3 — keine Normierung

    def test_3_null_prozent_heisst_das_stueck_fehlt(self):
        werte = {'sorte.stiefel_a': 0.0, 'sorte.stiefel_b': 0.5, 'sorte.stiefel_c': 0.0}
        anteile = G9kleidgenerisch.anteile(SCHUHE, werte)
        self.assertEqual(anteile, {'stiefel_b': 0.5})

    def test_4_stehen_alle_auf_null_gilt_die_grundsorte(self):
        anteile = G9kleidgenerisch.anteile(SCHUHE, {'sorte.stiefel_a': 0.0, 'sorte.stiefel_b': 0.0})
        self.assertEqual(anteile, {'stiefel_a': 1.0})

    def test_5_ein_winziger_anteil_faellt_weg(self):
        self.assertEqual(G9kleidgenerisch.anteile(SCHUHE, {'sorte.stiefel_b': 0.001}), {'stiefel_a': 1.0})

    def test_6_die_reihenfolge_geht_nach_anteil_und_traegt_die_regler_des_stuecks(self):
        folge = G9kleidgenerisch.mischung(SCHUHE, {
            'sorte.stiefel_a': 0.4, 'sorte.stiefel_b': 1.0, 'stiefel_b.Adj Inflate All': 0.7, 'passform:weite': 2.0})
        self.assertEqual([k for k, _a, _r in folge], ['stiefel_b', 'stiefel_a'])
        self.assertEqual([a for _k, a, _r in folge], [1.0, 0.4])
        self.assertEqual(folge[0][2], {'Adj Inflate All': 0.7, 'passform:weite': 2.0})
        self.assertEqual(folge[1][2], {'passform:weite': 2.0})           # die Passform gilt für jedes Stück

    def test_7_bei_gleichstand_geht_die_grundsorte_zuletzt_und_die_zuletzt_bewegte_zuerst(self):
        werte = {'sorte.stiefel_b': 1.0, 'sorte.stiefel_c': 1.0, 'sorte_zuletzt': 'stiefel_b'}
        folge = G9kleidgenerisch.mischung(SCHUHE, werte)
        self.assertEqual([k for k, _a, _r in folge], ['stiefel_b', 'stiefel_c', 'stiefel_a'])

    def test_8_alle_getragenen_stuecke_werden_gemischt_ohne_grenze(self):
        werte = {'sorte.s%d' % i: 1.0 - i * 0.1 for i in range(5)}
        folge = G9kleidgenerisch.mischung(FUENF, werte)
        self.assertEqual([k for k, _a, _r in folge], ['s0', 's1', 's2', 's3', 's4'])   # Edgar, 03.10.2026: unbegrenzt

    def test_9_sorte_ist_das_staerkste_stueck(self):
        self.assertEqual(G9kleidgenerisch.sorte(SCHUHE, {'sorte.stiefel_c': 0.6, 'sorte.stiefel_a': 0.2}), 'stiefel_c')

    def test_10_uebergang_kommt_in_zentimetern_und_geht_in_metern(self):
        self.assertAlmostEqual(G9kleidgenerisch.uebergang({}), 0.03)
        self.assertAlmostEqual(G9kleidgenerisch.uebergang({'mischung:uebergang': 5.0}), 0.05)
        self.assertAlmostEqual(G9kleidgenerisch.uebergang({'mischung:uebergang': 99}), 0.10)       # Obergrenze 10 cm
        self.assertAlmostEqual(G9kleidgenerisch.uebergang({'mischung:uebergang': 0}), 0.005)       # Untergrenze 5 mm
        self.assertAlmostEqual(G9kleidgenerisch.uebergang({'mischung:uebergang': 'kaputt'}), 0.03)

    def test_11_der_uebergang_geht_nicht_an_die_stuecke(self):
        folge = G9kleidgenerisch.mischung(SCHUHE, {'sorte.stiefel_b': 0.5, 'mischung:uebergang': 6.0, 'textur:2': 0.5})
        for _k, _a, regler in folge:
            self.assertNotIn('mischung:uebergang', regler)
            self.assertNotIn('textur:2', regler)

    def test_12_textur_regler_stehen_nur_im_browser_und_nicht_im_schluessel(self):
        werte = {'sorte.stiefel_b': 0.5, 'textur:2': 0.5, 'textur:3': 1.0, 'passform:weite': 1.0}
        self.assertEqual(G9kleidgenerisch.ohne_textur(werte), {'sorte.stiefel_b': 0.5, 'passform:weite': 1.0})
        self.assertEqual(G9kleidgenerisch.ohne_textur(None), {})
        self.assertEqual(werte['textur:2'], 0.5)                        # die Eingabe bleibt

    def test_13_mischung_und_textur_gruppen_gibt_es_nur_mit_mehreren_stuecken(self):
        mehrere = {r['name']: r for r in G9kleidgenerisch.regler(SCHUHE)}
        self.assertEqual([n for n in mehrere if n.startswith('textur:')], ['textur:2', 'textur:3', 'textur:4'])
        self.assertEqual({mehrere[n]['gruppe'] for n in mehrere if n.startswith('textur:')}, {'Textur'})
        self.assertEqual(mehrere['mischung:uebergang']['einheit'], 'cm')
        self.assertEqual(mehrere['mischung:uebergang']['vorgabe'], 3.0)
        einzeln = [r['name'] for r in G9kleidgenerisch.regler(SCHUHE[:1])]
        self.assertNotIn('mischung:uebergang', einzeln)
        self.assertFalse([n for n in einzeln if n.startswith('textur:')])

    def test_14_der_anteil_erklaert_sich_am_regler(self):
        regler = {r['name']: r for r in G9kleidgenerisch.regler(SCHUHE)}
        self.assertIn('überdecken', regler['sorte.stiefel_b']['hinweis'])
        self.assertIn('nicht 100', regler['sorte.stiefel_b']['hinweis'])
        self.assertIn('2. Stücks', regler['textur:2']['hinweis'])


class AlleKategorienTest(unittest.TestCase):
    """Der Eintrag über alle Kategorien: T-Shirt plus Kleid (Edgars Beispiel) sind zwei verschiedene Kategorien."""

    GRUPPEN = [('Oberteile', [OBERTEIL]), ('Kleider', [KLEID]), ('Schuhe', SCHUHE)]

    def setUp(self):
        gruppen = mock.patch.object(G9kleidgenerisch, 'gruppen', classmethod(lambda cls: self.GRUPPEN))
        gruppen.start()
        self.addCleanup(gruppen.stop)

    def test_1_der_eintrag_steht_hinter_den_kategorien_und_hat_alle_stuecke(self):
        eintraege = G9kleidgenerisch.eintraege()
        self.assertEqual([e['id'] for e in eintraege], ['kleidung_generisch_oberteile', 'kleidung_generisch_kleider',
                                                       'kleidung_generisch_schuhe', 'kleidung_generisch_alle'])
        alle = eintraege[-1]
        self.assertEqual(alle['name'], 'Kleidung – Generisch: Alle Kategorien')
        self.assertEqual(alle['kategorie'], 'Mischung')
        self.assertEqual(alle['sorten'], 5)
        self.assertTrue(alle['generisch'])

    def test_2_nur_der_anteil_je_stueck_gruppiert_nach_kategorie(self):
        regler = G9kleidgenerisch.eintraege()[-1]['regler']
        sorten = [r for r in regler if r['name'].startswith('sorte.')]
        self.assertEqual([(r['name'], r['gruppe']) for r in sorten], [
            ('sorte.shirt_1', 'Oberteile'), ('sorte.kleid_1', 'Kleider'), ('sorte.stiefel_a', 'Schuhe'),
            ('sorte.stiefel_b', 'Schuhe'), ('sorte.stiefel_c', 'Schuhe')])
        morphs = [r for r in regler if '.' in r['name'] and not r['name'].startswith('sorte.')]
        self.assertFalse(morphs)                                             # keine Morphs im Sammeleintrag

    def test_3_die_grundsorte_ist_das_erste_stueck_der_ersten_kategorie(self):
        vorgaben = {r['name']: r['vorgabe'] for r in G9kleidgenerisch.eintraege()[-1]['regler']
                    if r['name'].startswith('sorte.')}
        self.assertEqual(vorgaben['sorte.shirt_1'], 1.0)
        self.assertEqual(sum(vorgaben.values()), 1.0)

    def test_4_t_shirt_und_kleid_lassen_sich_mischen(self):
        folge, uebergang = G9kleidgenerisch.mischung_aufloesen('kleidung_generisch_alle', {
            'sorte.kleid_1': 0.3, 'mischung:uebergang': 4.0, 'passform:weite': 1.0})
        self.assertEqual([(k, a) for k, a, _r in folge], [('shirt_1', 1.0), ('kleid_1', 0.3)])
        self.assertAlmostEqual(uebergang, 0.04)
        self.assertEqual(folge[0][2], {'passform:weite': 1.0})

    def test_5_eine_kategorie_mischt_nur_ihre_eigenen_stuecke(self):
        folge, _u = G9kleidgenerisch.mischung_aufloesen('kleidung_generisch_schuhe', {
            'sorte.stiefel_b': 0.5, 'sorte.kleid_1': 1.0})
        self.assertEqual([k for k, _a, _r in folge], ['stiefel_a', 'stiefel_b'])         # das Kleid gehört nicht dazu

    def test_6_eine_unbekannte_kategorie_mischt_nichts(self):
        folge, uebergang = G9kleidgenerisch.mischung_aufloesen('kleidung_generisch_gibtsnicht', {})
        self.assertEqual(folge, [])
        self.assertAlmostEqual(uebergang, 0.03)

    def test_7_ein_getragener_mischeintrag_wird_zum_staerksten_stueck(self):
        roh = [{'kennung': 'kleidung_generisch_alle', 'regler_stueck': {'sorte.kleid_1': 2.0}}]
        aus = G9kleidgenerisch.getragene_aufloesen(roh)
        self.assertEqual(aus[0]['kennung'], 'kleid_1')

    def test_8_nur_der_eintrag_ueber_alle_kategorien_steht_oben(self):
        u"""Edgar, 30.09.2026: „Kleidung – Generisch" direkt unter der Überschrift „Genesis", in keiner Kategorie.
        Der Browser zeichnet `oben` vor den Kategorien (`Genesis9garderobe.fuellen`)."""
        eintraege = G9kleidgenerisch.eintraege()
        self.assertEqual([e['id'] for e in eintraege if e['oben']], ['kleidung_generisch_alle'])
        self.assertTrue(all(e['oben'] is False for e in eintraege[:-1]))


class GruppenTest(unittest.TestCase):
    """Die wirksame Kategorie: Edgars Zuordnung vor der Vorgabe aus Daz' Metadaten."""

    LISTE = [
        {'id': 'schuh_1', 'name': 'Schuh 1', 'art': 'kleidung', 'zeigbar': True},
        {'id': 'kleid_1', 'name': 'Kleid 1', 'art': 'kleidung', 'zeigbar': True},
        {'id': 'schuh_2', 'name': 'Schuh 2', 'art': 'kleidung', 'zeigbar': True},
        {'id': 'kaputt', 'name': 'Kaputt', 'art': 'kleidung', 'zeigbar': False},
        {'id': 'kin_hair', 'name': 'Kin Hair', 'art': 'haar', 'zeigbar': True},
        {'id': 'dolch', 'name': 'Dolch', 'art': 'requisit', 'zeigbar': True},
    ]
    VORGABEN = {'schuh_1': 'Schuhe', 'kleid_1': 'Kleider', 'schuh_2': 'Schuhe', 'kaputt': 'Schuhe'}

    def _gruppen(self, zuordnung):
        stand = {'kategorien': ['Kleider', 'Schuhe', 'Fantasy'], 'zuordnung': zuordnung}
        with mock.patch.object(G9garderobe, 'liste', classmethod(lambda cls: self.LISTE)), \
                mock.patch.object(G9garderobekategorien, 'laden', classmethod(lambda cls: stand)), \
                mock.patch.object(G9dazkategorien, 'tabelle', classmethod(lambda cls: {})), \
                mock.patch.object(G9garderobekategorien, 'vorgabe',
                                  classmethod(lambda cls, e, tabelle=None: self.VORGABEN[e['id']])), \
                mock.patch.object(G9kleidgenerisch, '_vorgaben_stand', (None, {})):
            return [(k, [e['id'] for e in stuecke]) for k, stuecke in G9kleidgenerisch.gruppen()]

    def test_1_nur_zeigbare_kleidung_je_kategorie_in_der_reihenfolge_der_einteilung(self):
        self.assertEqual(self._gruppen({}), [('Kleider', ['kleid_1']), ('Schuhe', ['schuh_1', 'schuh_2'])])

    def test_2_haar_und_requisiten_gehoeren_nicht_dazu(self):
        ids = [i for _k, stuecke in self._gruppen({}) for i in stuecke]
        self.assertNotIn('kin_hair', ids)
        self.assertNotIn('dolch', ids)
        self.assertNotIn('kaputt', ids)

    def test_3_ein_verschobenes_stueck_wandert_mit(self):
        self.assertEqual(self._gruppen({'schuh_2': 'Fantasy'}),
                         [('Kleider', ['kleid_1']), ('Schuhe', ['schuh_1']), ('Fantasy', ['schuh_2'])])

    def test_4_eine_leere_kategorie_hat_keinen_eintrag(self):
        self.assertEqual(self._gruppen({'schuh_1': 'Kleider', 'schuh_2': 'Kleider'}),
                         [('Kleider', ['schuh_1', 'kleid_1', 'schuh_2'])])   # Reihenfolge der Liste
