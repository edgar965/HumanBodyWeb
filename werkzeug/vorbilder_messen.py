# -*- coding: utf-8 -*-
u"""Die Kleiderbibliothek einmal vermessen und als Voreinstellungen ablegen.

    python werkzeug/vorbilder_messen.py

Jedes Stueck geht durch `Stueckmasse` und `Schnittdeutung`; das Ergebnis
landet als `Assets/GarmentCode/vorbilder.json`, gebuendelt nach
Katalogstueck. Der GarmentCode-Reiter zeigt sie dann als Voreinstellungen
unter „Eng anliegend" — Klick setzt die Regler, gebaut wird wie immer.

WARUM EINMAL MESSEN UND NICHT BEI JEDEM KLICK (Edgar, 09.09.2026): Ein
Vorbild ist ein Satz Reglerwerte, und der aendert sich nicht. Gemessen
(09.09.2026): 181 Stuecke in 10 s, davon 121 gedeutet und 60 abgelehnt.
Zehn Sekunden will niemand im Reiter warten, und eine Datei laesst sich
ansehen; eine Rechnung im Hintergrund nicht.

DIE WERTE SIND RELATIV, DESHALB GELTEN SIE FUER JEDE FIGUR. `length` ist
der Anteil der Beinlaenge, `suns` faellt aus dem Verhaeltnis Saum zu
Taille. Gemessen wird an der Vorgabefigur, angewandt auf die, die gerade
in der Szene steht.
"""
import json
import os
import sys
import time

import django
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ui.settings')
django.setup()


class Vorbilderlauf:
    u"""Alle Bibliotheksstuecke deuten und als Preset-Datei schreiben."""

    def __init__(self, ziel=''):
        from GarmentCode.vorbildpresets import Vorbildpresets
        self.ziel = ziel or Vorbildpresets.DATEI
        self.gebuendelt = {}
        self.abgelehnt = []

    def laufen(self):
        from core.dienste.charakterdaten import Charakterdaten
        from core.dienste.kleiderbibliothek import Kleiderbibliothek
        from GarmentCode.dienst import GarmentcodeDienst

        koerper = Charakterdaten.koerper_aus({})
        if koerper.vertices is None:
            print('Kein Koerpernetz - Abbruch')
            return 1
        masse, _ = GarmentcodeDienst.masse('female')
        bestand = getattr(Kleiderbibliothek.holen(), 'catalog', None) or []
        print('%d Stueck werden vermessen …\n' % len(bestand))

        begonnen = time.time()
        for eintrag in bestand:
            self._eines(eintrag, koerper, masse)
        self._schreiben()
        print('\n%d Vorbilder in %d Katalogstuecken, %d abgelehnt, %.0f s'
              % (sum(len(v) for v in self.gebuendelt.values()),
                 len(self.gebuendelt), len(self.abgelehnt),
                 time.time() - begonnen))
        for stueck in sorted(self.gebuendelt):
            print('  %-18s %3d' % (stueck, len(self.gebuendelt[stueck])))
        return 0

    def _eines(self, eintrag, koerper, masse):
        from core.dienste.stueckueberfuehrung import Stueckueberfuehrung

        kennung = (eintrag.get('id') if isinstance(eintrag, dict)
                   else getattr(eintrag, 'garment_id', None))
        if not kennung:
            return
        titel = (eintrag.get('name') if isinstance(eintrag, dict)
                 else getattr(eintrag, 'name', '')) or kennung.split('/')[-1]
        try:
            deutung, grund = Stueckueberfuehrung.deuten(kennung, koerper, masse)
        except Exception as fehler:                             # noqa: BLE001
            self.abgelehnt.append((kennung, str(fehler)[:70]))
            return
        if deutung is None:
            self.abgelehnt.append((kennung, grund))
            return
        self.gebuendelt.setdefault(deutung['vorlage'], []).append({
            'kennung': kennung,
            'titel': titel,
            'hinweis': self._hinweis(titel, deutung),
            'werte': deutung['regler'],
            # Farbe und Glanz aus der `.mhmat` des Stuecks (Edgar, 09.09.2026:
            # „soll auch die Farbe, Roughness ... vom Garment Fit
            # herueberkommen"). Die Farbe in `garment.json` taugt dafuer
            # nicht - sie steht bei allen 181 Stuecken auf [0.3, 0.35, 0.5].
            'material': self._material(kennung),
            # Ob es ein Vorschaubild gibt - der Reiter zeigt dasselbe wie die
            # Asset-Liste (`/api/character/garment/thumb/<id>/`). Die Angabe
            # steht im Katalog-dict, nicht am Template.
            'bild': bool(eintrag.get('has_thumb')
                         if isinstance(eintrag, dict)
                         else getattr(eintrag, 'has_thumb', False)),
        })

    @staticmethod
    def _material(kennung):
        u"""Farbe und Glanz aus der Materialdatei neben dem Netz.

        Den ORDNER kennt nur das Template - der Katalog fuehrt dicts ohne
        Pfad (`name`, `id`, `category`, `has_thumb`, ...). Das Template ist
        zu diesem Zeitpunkt ohnehin geladen, die Deutung hat es gebraucht.
        """
        from core.dienste.kleiderbibliothek import Kleiderbibliothek
        from GarmentCode.vorbildmaterial import Vorbildmaterial
        vorlage = Kleiderbibliothek.holen().get_template(kennung)
        return Vorbildmaterial.lesen(getattr(vorlage, 'dir', '') or '')

    @staticmethod
    def _hinweis(titel, deutung):
        u"""Was gemessen wurde — ohne Zahl waere das Preset eine Behauptung.

        Dieselbe Regel wie bei den Passform-Presets: `test_passform.py`
        verlangt in jedem Hinweis eine Zahl.
        """
        masse = deutung['bericht']['stueck']
        teile = [u'Nach dem Bibliotheksstück „%s".' % titel,
                 u'Gemessen: Netz %.0f–%.0f cm über dem Boden'
                 % (masse['unten_cm'], masse['oben_cm'])]
        if masse.get('saum_umfang_cm'):
            teile.append(u'Saumumfang %.0f cm' % masse['saum_umfang_cm'])
        if masse.get('armstoff_cm'):
            teile.append(u'Ärmelstoff %.0f cm' % masse['armstoff_cm'])
        teile.append(u'Übernommen wird die Silhouette, nicht Muster '
                     u'und Rüschen.')
        return ' · '.join(teile[:1] + [', '.join(teile[1:-1])] + teile[-1:])

    def _schreiben(self):
        for liste in self.gebuendelt.values():
            liste.sort(key=lambda e: e['titel'].lower())
        with open(self.ziel, 'w', encoding='utf-8') as datei:
            json.dump(self.gebuendelt, datei, indent=1, ensure_ascii=False)
        print('-> %s' % self.ziel)
        if not self.abgelehnt:
            return
        gruende = {}
        for _, grund in self.abgelehnt:
            kurz = (grund or '').split('—')[-1].strip()[:60]
            gruende[kurz] = gruende.get(kurz, 0) + 1
        print('\nAbgelehnt (der Schnittkatalog kann sie nicht):')
        for grund, anzahl in sorted(gruende.items(), key=lambda p: -p[1]):
            print('  %3d x  %s' % (anzahl, grund))


if __name__ == '__main__':
    raise SystemExit(Vorbilderlauf().laufen())
