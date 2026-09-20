# -*- coding: utf-8 -*-
u"""Die Kategorie eines Daz-Stuecks aus Daz' Metadaten (`G9dazkategorien`).

Edgar (20.09.2026, nachts): „ich hatte auch in Auftrag gegeben, dass die
Genesis Assets in Kategorien erscheinen, kategorien so wie die bei Garment
Code. warum wurde das nicht gemacht???" Die Vorgabe kannte bis dahin nur die
drei Bibliotheksordner. Daz liefert je Produkt `Runtime/Support/*.dsx` mit
`<Asset VALUE="…duf"><ContentType …/><Categories><Category VALUE="/Default/
Wardrobe/Shirts"/>`; gemessen an Edgars Bibliothek haben alle 121 Stuecke
einen Eintrag. Hier eine kleine Bibliothek im Wegwerfordner. Zusagen:

1. Die Daz-KATEGORIE zaehlt vor dem ContentType (Boxers: `Pant`, aber
   `Underwear/Bottoms` -> Unterwaesche); Shirts -> Oberteile, Pants -> Hosen,
   Footwear -> Schuhe, Hair -> Haare, Props -> Requisiten, Wearables-Preset
   -> Outfits, Accessories -> Zubehoer.
2. Daz kennt keine Shorts und nennt die Base Clothing „Underwear": der Name
   entscheidet — „… Shorts" wird Shorts, ein „Shirt"/„Tank Top" in der
   Unterwaesche wird Oberteil, Bra und Panties bleiben.
3. Ohne Eintrag entscheidet die Art; ohne Kategorie der ContentType.
4. Ein neues Produkt (neue .dsx) faellt beim naechsten Lesen auf.

Sabotage: Reihenfolge in `NACH_PFAD` (Underwear hinter Pants) -> Fall 1 rot;
`SHORTS` weg -> Fall 2 rot; `_dateien`-Vergleich weg -> Fall 4 rot.
"""
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.dazkategorien import G9dazkategorien
from Genesis9.pfade import G9pfade

DSX = u"""<?xml version="1.0" encoding="UTF-8"?>
<ContentDBInstall VERSION="1.0">
 <Assets>
  <Asset VALUE="People/Genesis 9/Clothing/Daz Originals/Base Clothing/G9 Base Shirt.duf">
   <ContentType VALUE="Follower/Wardrobe/Shirt"/>
   <Categories><Category VALUE="/Default/Wardrobe/Shirts"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Clothing/Basic Wear/Boxers.duf">
   <ContentType VALUE="Follower/Wardrobe/Pant"/>
   <Categories><Category VALUE="/Default/Wardrobe/Underwear/Bottoms"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Clothing/Magus/Magus Shorts.duf">
   <ContentType VALUE="Follower/Wardrobe/Pant"/>
   <Categories><Category VALUE="/Default/Wardrobe/Pants"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Clothing/Angie/Angie Sneakers.duf">
   <ContentType VALUE="Follower/Wardrobe/Footwear"/>
   <Categories><Category VALUE="/Default/Wardrobe/Footwear"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Clothing/Worker/Worker Uniform 00 Outfit.duf">
   <ContentType VALUE="Preset/Wearables"/>
   <Categories><Category VALUE="/Default/Wardrobe/Outfits"/>
   <Category VALUE="/Default/Saved Files/Preset/Wearables"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Clothing/JS/JS Sash.duf">
   <ContentType VALUE="Follower/Accessory/Waist"/>
   <Categories><Category VALUE="/Default/Accessories/Waist"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Hair/Toulouse Hair.duf">
   <ContentType VALUE="Follower/Hair"/>
   <Categories><Category VALUE="/Default/Hair/Short"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Props/Tubal/Tubal Sword Base LT.duf">
   <ContentType VALUE="Prop/Arm/Left/Hand"/>
   <Categories><Category VALUE="/Default/Props/Weapons/Blades"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Clothing/Daz Originals/Base Clothing/G9 Base Shirt U.duf">
   <ContentType VALUE="Follower/Wardrobe/Underwear/Top"/>
   <Categories><Category VALUE="/Default/Wardrobe/Underwear/Tops"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Clothing/Daz Originals/Base Clothing/G9 Base Shorts U.duf">
   <ContentType VALUE="Follower/Wardrobe/Underwear/Bottom"/>
   <Categories><Category VALUE="/Default/Wardrobe/Underwear/Bottoms"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Clothing/Basic Wear/Sports Bra.duf">
   <ContentType VALUE="Follower/Wardrobe/Underwear/Top"/>
   <Categories><Category VALUE="/Default/Wardrobe/Underwear/Tops"/></Categories>
  </Asset>
  <Asset VALUE="People/Genesis 9/Clothing/Nur Typ/Kleid.duf">
   <ContentType VALUE="Follower/Wardrobe/Dress"/>
   <Categories></Categories>
  </Asset>
 </Assets>
</ContentDBInstall>
"""


def _eintrag(wurzel, datei, art='kleidung', name=None):
    return {'id': datei.lower(), 'art': art, 'datei': datei + '.duf', 'wurzel': wurzel,
            'name': name or datei.split('/')[-1]}


class DazkategorienTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.bib = Path(self.ordner.name)
        self.support = self.bib / 'Runtime' / 'Support'
        self.support.mkdir(parents=True)
        (self.support / 'DAZ_3D_1_Probe.dsx').write_text(DSX, encoding='utf-8')
        self._bib = mock.patch.object(G9pfade, 'bibliothek', classmethod(lambda cls: self.bib))
        self._da = mock.patch.object(G9pfade, 'vorhanden', classmethod(lambda cls: True))
        self._bib.start()
        self._da.start()
        G9dazkategorien.vergessen()

    def tearDown(self):
        G9dazkategorien.vergessen()
        self._da.stop()
        self._bib.stop()
        self.ordner.cleanup()

    def test_1_kategorie_vor_contenttype(self):
        k = 'People/Genesis 9/Clothing'
        faelle = [
            (_eintrag(k, 'Daz Originals/Base Clothing/G9 Base Shirt'), u'Oberteile'),
            (_eintrag(k, 'Basic Wear/Boxers'), u'Unterwäsche'),
            (_eintrag(k, 'Angie/Angie Sneakers'), u'Schuhe'),
            (_eintrag(k, 'Worker/Worker Uniform 00 Outfit'), u'Outfits'),
            (_eintrag(k, 'JS/JS Sash'), u'Zubehör'),
            (_eintrag('People/Genesis 9/Hair', 'Toulouse Hair', 'haar'), u'Haare'),
            (_eintrag('People/Genesis 9/Props', 'Tubal/Tubal Sword Base LT', 'requisit'),
             u'Requisiten'),
        ]
        for eintrag, soll in faelle:
            self.assertEqual(G9dazkategorien.vorgabe(eintrag), soll, eintrag['datei'])
        # Gross/klein und Backslash im Pfad sind egal (Windows-Bibliothek).
        schraeg = _eintrag(k, 'Basic Wear\\BOXERS')
        self.assertEqual(G9dazkategorien.vorgabe(schraeg), u'Unterwäsche')

    def test_2_shorts_ueber_den_namen(self):
        eintrag = _eintrag('People/Genesis 9/Clothing', 'Magus/Magus Shorts')
        self.assertEqual(G9dazkategorien.vorgabe(eintrag), u'Shorts')
        # Nur „Shorts" als Wort — „Shortcut Pants" bleibt Hose.
        eintrag['name'] = 'Shortcut Pants'
        self.assertEqual(G9dazkategorien.vorgabe(eintrag), u'Hosen')
        k = 'People/Genesis 9/Clothing'
        self.assertEqual(G9dazkategorien.vorgabe(
            _eintrag(k, 'Daz Originals/Base Clothing/G9 Base Shirt U')), u'Oberteile')
        self.assertEqual(G9dazkategorien.vorgabe(
            _eintrag(k, 'Daz Originals/Base Clothing/G9 Base Shorts U')), u'Shorts')
        self.assertEqual(G9dazkategorien.vorgabe(_eintrag(k, 'Basic Wear/Sports Bra')),
                         u'Unterwäsche')

    def test_3_ohne_eintrag_die_art_ohne_kategorie_der_typ(self):
        k = 'People/Genesis 9/Clothing'
        self.assertEqual(G9dazkategorien.vorgabe(_eintrag(k, 'Fehlt/Fehlt')), u'Oberteile')
        self.assertEqual(G9dazkategorien.vorgabe(_eintrag(k, 'Fehlt/Fehlt', 'haar')), u'Haare')
        self.assertEqual(G9dazkategorien.vorgabe(_eintrag(k, 'Fehlt/Fehlt', 'requisit')),
                         u'Requisiten')
        self.assertEqual(G9dazkategorien.vorgabe(_eintrag(k, 'Nur Typ/Kleid')), u'Kleider')

    def test_4_neues_produkt_faellt_auf(self):
        k = 'People/Genesis 9/Clothing'
        eintrag = _eintrag(k, 'Neu/Bardot Skirt')
        self.assertEqual(G9dazkategorien.vorgabe(eintrag), u'Oberteile', 'noch unbekannt')
        (self.support / 'DAZ_3D_2_Neu.dsx').write_text(u"""<Assets>
  <Asset VALUE="People/Genesis 9/Clothing/Neu/Bardot Skirt.duf">
   <ContentType VALUE="Follower/Wardrobe/Skirt"/>
   <Categories><Category VALUE="/Default/Wardrobe/Skirts"/></Categories>
  </Asset></Assets>""", encoding='utf-8')
        self.assertEqual(G9dazkategorien.vorgabe(eintrag), u'Röcke')
        self.assertEqual(len(G9dazkategorien.tabelle()), 13)

    def test_5_reihenfolge_traegt_alle_namen(self):
        namen = set(G9dazkategorien.REIHENFOLGE)
        for _pfad, name in G9dazkategorien.NACH_PFAD + G9dazkategorien.NACH_TYP:
            self.assertIn(name, namen)
        self.assertIn(u'Shorts', namen)
        for name in G9dazkategorien.NACH_ART.values():
            self.assertIn(name, namen)
