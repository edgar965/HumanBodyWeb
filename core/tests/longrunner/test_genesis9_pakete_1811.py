# -*- coding: utf-8 -*-
u"""Die Zips aus `3DObjects/DAZ/n` vom 18.11.2026 gegen die installierte Bibliothek.

Edgar: „hier sind neue Modell, importiere sie und baue die um auf Genesis9“. Drei neue Bauarten für
Genesis 9, eine für Genesis 8:

1. JamesF G9 (Pekmez): Preset vom Typ `scene_subset` statt `character` (`G9charakterpresets`).
2. Luna for G9 (al5929): `scene_subset` mit eingebettetem Face-Transfer-Morph `Luna-g9`
   (`G9eingebettetemorphe`, Wert aus der eigenen `modifier_library`).
3. Seratin for G9 (SAP3D): nur Apply-Sätze (`G9charakterapply`), Haut `Materials/Seratin Skin.duf`.
4. Dante DMC5 (InTheFlesh, G8M): Zip mit nur einem Formmorph (`G8charakterquellen._aus_paketen`).

Was NICHT dazukommen darf (Katalogvergleich 18.11.2026, `_wegwerf/daz_n_katalog_stand.py`): die
Apply-Sätze von MB Olesia, NW Damira und P3D Ursula HD als eigene Einträge.

LongRunner, ohne die Pakete übersprungen. Sabotage: `G9charakterpresets._TYP` nur `character` →
Fall 1 und 2 rot; `_mit_gesteuerten` gibt `gesetzt` zurück → Fall 5 rot (mb_olesia, damira);
`_morphordner` gibt '' → Fall 5 rot (p3d_ursula_hd).
"""
import unittest

from django.test import SimpleTestCase
from Genesis9.charaktere import G9charaktere
from Genesis9.morphablage import G9morphablage
from Genesis9.pfade import G9pfade

from core.dienste.g8charakterquellen import G8charakterquellen


def pakete_da():
    if not G9pfade.vorhanden():
        return False
    figuren = G9pfade.people() / 'Characters'
    return ((figuren / 'JamesF G9.duf').is_file() and (figuren / 'al5929' / 'Luna-g9.duf').is_file()
            and (figuren / 'SAP3D' / 'Seratin' / 'Seratin Body Apply.duf').is_file())


@unittest.skipUnless(pakete_da(), 'JamesF G9, Luna for G9 oder Seratin fehlen')
class Pakete1811Test(SimpleTestCase):
    databases = set()

    def test_1_jamesf_aus_scene_subset(self):
        e = G9charaktere.eintrag('jamesf_g9')
        self.assertIsNotNone(e)
        self.assertEqual(e['geschlecht'], u'männlich')
        self.assertEqual(e['regler'], {'James G9 Body-0xa4ac60d': 1.0, 'JamesF Head G9-0xa49de46': 1.0,
                                       'BaseMasculine_figure_ctrl_Character': 1.0})
        self.assertTrue((e.get('bilder') or {}).get('Head', {}).get('albedo'))

    def test_2_luna_mit_eingebettetem_morph(self):
        kanal = G9morphablage.holen().kanaele.get('Luna-g9')
        self.assertIsNotNone(kanal)
        self.assertTrue(kanal.get('eingebettet'))
        self.assertEqual(kanal['vorgabe'], 0.0)                 # sonst trüge jede Figur Lunas Gesicht
        self.assertEqual(kanal['deltas'], 5397)                 # gelesen `_wegwerf/daz_n_inline.py`
        self.assertNotIn('Luna-g9-2', G9morphablage.holen().kanaele)   # Augen-Netz, nicht der Körper
        e = G9charaktere.eintrag('luna_g9')
        self.assertIsNotNone(e)
        self.assertEqual(e['regler'].get('Luna-g9'), 1.0)
        self.assertEqual(e['geschlecht'], u'weiblich')

    def test_3_seratin_aus_apply_saetzen(self):
        e = G9charaktere.eintrag('seratin')
        self.assertIsNotNone(e)
        self.assertEqual(e['regler'], {'Seratin Body-0xaaa5e94': 1.0, 'Seratin Head-0xaaa5d72': 1.0})
        self.assertEqual(e['datei'].replace('\\', '/'), 'Characters/SAP3D/Seratin/Materials/Seratin Skin.duf')

    def test_4_dante_als_g8_morphpaket(self):
        auftraege = {a['kennung']: a for a in G8charakterquellen.auftraege(['Dante DMC5'])}
        self.assertEqual(list(auftraege), ['Dante_DMC5'])
        a = auftraege['Dante_DMC5']
        self.assertEqual(a['klon'], 'CloneGenesis8Male')
        verweise = [(p.name, w) for p, w, _b in G8charakterquellen.verweise(a)]
        self.assertEqual(verweise, [('Dante DMC5.dsf', 1.0)])
        self.assertIsNone(G8charakterquellen.hautquelle(a))

    def test_5_keine_zweiteintraege_bekannter_charaktere(self):
        namen = set(G9charaktere.namen())
        self.assertTrue({'mb_olesia_hd', 'nw_damira_8k', 'p3d_ursula'} <= namen)
        self.assertFalse({'mb_olesia', 'damira', 'damira_full', 'p3d_ursula_hd'} & namen)
