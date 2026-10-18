# -*- coding: utf-8 -*-
u"""Mhmorphplan — welche MakeHuman-Regler zu Genesis-Morphs werden und wie jeder berechnet wird (17.10.2026).

Ein Auftrag ist ein Regler in beiden Richtungen:

    {kennung, anzeige, kategorie, bereich, reihe, min, max, plus, minus}

`plus`/`minus` sagen, wie `Mhmorpheaufgenesis` die Stellung rechnet: `{'makro': {…}}` (Makrovariablen von `Mhformung`), `{'regler': {kennung: wert}}`
(ein Detailregler) oder `{'ziel': pfad}` (ein Ziel allein, Gewicht 1). `minus` fehlt bei Reglern mit einer Seite (min 0).

DREI QUELLEN
============
1. **Die 13 Makroregler**, von Hand (siehe `MAKRO`): Geschlecht, Alter in DREI Morphs (Baby, Kind, Alt), Rasse in drei, Muskeln, Gewicht, Groesse, Proportionen,
   Brustgroesse und -festigkeit zweiseitig. Das **Geschlecht** (`macro_Geschlecht`, 17.10.2026 auf Edgars Wunsch: „Genesis hat ja ein extra Teil fuer Geschlecht,
   kannst du ein zweites von MakeHuman einbauen?“) ist ein ZWEITES neben Genesis' eigenem (`BaseFeminine`/`BaseMasculine`): einseitig 0…1, Bezug die weibliche Vorgabe,
   +1 = MakeHumans Mann. Es ueberlagert das Genesis-Geschlecht (wer beide aufdreht, bekommt beide Wirkungen) und ist dafuer da, MakeHumans Form des Maennlichen
   zu haben — Schulter, Becken, Brustkorb, Gesicht, wie MakeHuman sie schneidet.
   ALTER: MakeHumans Kurve hat vier Stuetzstellen (1, 10, 25, 90 Jahre = 0 / 0,1875 / 0,5 / 1), die Zielgewichte laufen dazwischen linear. Gegen die Vorgabe
   (25 Jahre, `young` = 1) ist `F(Alter) − F(25)` darum die gewichtete Summe von (Baby − jung), (Kind − jung) und (Alt − jung) — drei Morphs, die zusammen die
   ganze Kurve tragen (`G9lebensalter` mischt sie nach Jahren).
2. **Die Detailregler** (`Mhmodifikatoren`, 258 ohne die Makros) in MakeHumans eigener Ordnung und mit seinen Beschriftungen (`Mhreglerplan` — Englisch,
   wie in MakeHuman; wer uebersetzt, findet sie in keiner Anleitung mehr).
3. **Die 22 Koerperformen** (`bodyshapes_sliders.json`, MakeHuman 1.3): Ziele ohne Modifier-Eintrag im Katalog, einseitig 0…1.
"""
import json
import os

__all__ = ['Mhmorphplan']


class Mhmorphplan:
    u"""Die Auftragsliste fuer `Mhmorpheaufgenesis`."""

    #: Reiter von MakeHumans Seitenplan -> Bereich der Genesis-Morphs.
    BEREICH = {'Macro modelling': 'mh_makro', 'Gender': 'mh_koerper', 'Torso': 'mh_koerper', 'Arms and Legs': 'mh_koerper',
               'Face': 'mh_gesicht', 'Measure': 'mh_mass'}
    #: Die Makroregler von Hand — der Detailplan ueberspringt sie (`regler.makro`). (kennung, anzeige, plus, minus); minus None = einseitig 0…1.
    MAKRO = (
        ('macro_Geschlecht', u'Geschlecht (weiblich … männlich)', {'makro': {'gender': 1.0}}, None),
        ('macro_Alter_Baby', u'Alter: Baby (1 Jahr)', {'makro': {'age': 0.0}}, None),
        ('macro_Alter_Kind', u'Alter: Kind (10 Jahre)', {'makro': {'age': 0.1875}}, None),
        ('macro_Alter_Alt', u'Alter: Alt (90 Jahre)', {'makro': {'age': 1.0}}, None),
        ('macro_Rasse_Afrikanisch', u'Rasse: Afrikanisch', {'makro': {'african': 1.0}}, None),
        ('macro_Rasse_Asiatisch', u'Rasse: Asiatisch', {'makro': {'asian': 1.0}}, None),
        ('macro_Rasse_Kaukasisch', u'Rasse: Kaukasisch', {'makro': {'caucasian': 1.0}}, None),
        ('macro_Muskeln', u'Muskeln (schwach … stark)', {'makro': {'muscle': 1.0}}, {'makro': {'muscle': 0.0}}),
        ('macro_Gewicht', u'Gewicht (dünn … schwer)', {'makro': {'weight': 1.0}}, {'makro': {'weight': 0.0}}),
        ('macro_Groesse', u'Größe (klein … groß)', {'makro': {'height': 1.0}}, {'makro': {'height': 0.0}}),
        ('macro_Proportionen', u'Proportionen (ungewöhnlich … ideal)', {'makro': {'bodyproportions': 1.0}}, {'makro': {'bodyproportions': 0.0}}),
        ('macro_Brustgroesse', u'Brustgröße (klein … groß)', {'makro': {'breastsize': 1.0}}, {'makro': {'breastsize': 0.0}}),
        ('macro_Brustfestigkeit', u'Brustfestigkeit (weich … fest)', {'makro': {'breastfirmness': 1.0}}, {'makro': {'breastfirmness': 0.0}}),
    )

    @classmethod
    def auftraege(cls):
        u"""Alle Auftraege in der Reihenfolge, in der das Bedienfeld sie zeigt."""
        aus = []
        for kennung, anzeige, plus, minus in cls.MAKRO:
            aus.append(cls._auftrag(kennung, anzeige, u'Makro', 'mh_makro', len(aus), plus, minus))
        aus.extend(cls._details(len(aus)))
        aus.extend(cls._koerperformen(len(aus)))
        return aus

    @staticmethod
    def _auftrag(kennung, anzeige, kategorie, bereich, reihe, plus, minus):
        return {'kennung': kennung, 'anzeige': anzeige, 'kategorie': kategorie, 'bereich': bereich, 'reihe': reihe,
                'min': -1.0 if minus else 0.0, 'max': 1.0, 'plus': plus, 'minus': minus}

    @classmethod
    def _details(cls, ab):
        from MakeHuman.modifikatoren import Mhmodifikatoren
        from MakeHuman.reglerplan import Mhreglerplan
        katalog = Mhmodifikatoren.holen()
        aus = []
        for seite in Mhreglerplan.holen():
            bereich = cls.BEREICH.get(seite['name'], 'mh_koerper')
            for abschnitt in seite['abschnitte']:
                for zeile in abschnitt['regler']:
                    regler = katalog.regler.get(zeile['kennung'])
                    if regler is None or regler.makro:
                        continue
                    kennung = zeile['kennung'].replace('/', '_').replace('|', '_')
                    zweiseitig = bool(regler.links)
                    aus.append(cls._auftrag(kennung, u'%s: %s' % (abschnitt['name'].capitalize(), zeile['name']), abschnitt['name'], bereich,
                                            ab + len(aus), {'regler': {zeile['kennung']: 1.0}},
                                            {'regler': {zeile['kennung']: -1.0}} if zweiseitig else None))
        return aus

    @classmethod
    def _koerperformen(cls, ab):
        from MakeHuman.pfade import Mhpfade
        pfad = os.path.join(str(Mhpfade.modifikatoren()), 'bodyshapes_sliders.json')
        if not os.path.isfile(pfad):
            return []
        with open(pfad, encoding='utf-8') as f:
            daten = json.load(f)
        aus = []
        for seite in daten.values():
            for abschnitt, zeilen in seite.get('modifiers', {}).items():
                for zeile in zeilen:
                    ziel = zeile['mod']                       # `bodyshapes/bodyshapes-elvs-fem-apple`
                    kennung = ziel.replace('/', '_').replace('bodyshapes_bodyshapes-', 'bodyshapes_')
                    aus.append(cls._auftrag(kennung, u'%s: %s' % (abschnitt, zeile.get('label') or ziel), abschnitt, 'mh_formen',
                                            ab + len(aus), {'ziel': ziel}, None))
        return aus
