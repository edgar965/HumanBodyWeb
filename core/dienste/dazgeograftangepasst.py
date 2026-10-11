# -*- coding: utf-8 -*-
"""Dazgeograftangepasst — das Daz-Geograft als Stück „<Modell> Daz Scham": angepasst an die Scham eines Blender-Imports (10.10.2026).

Edgar: „im Blender-File war die Scham ja vorgegeben, die sollst du mit Hilfe der Scham aus Genesis nachbauen". Der Weg ist der von `Dazgeograft` (Käfig → Stufe 1 → Loch → Naht →
Stück), nur mit drei Änderungen an den Haken dort:

    figur        die Figur des gespeicherten Modells (`figur.regler` in `data/models/<Modell>.json`) statt der Grundfigur — das Loch und der Ring liegen auf IHRER Haut
    angleichen   das Geograft wird in den Raum dieser Figur verlegt und auf die Original-Scham angepasst (`Dazgeograftanpassung`)
    backen       Farbe, Rauheit und Normalen der Original-Scham werden auf das Geograft übertragen (`Dazgeograftbacken`); die UV des Geografts bleibt die von Daz
Die Daz-Formmorphe (`Dazgeograftmorphe`, Realism, Vorhaut) und die Charakter-Varianten gehören zur Grundform und entfallen hier; die Regler `sch_*` rechnen aus der Form des Stücks.
"""
import json
import logging
import re

from .dazgeograft import Dazgeograft

logger = logging.getLogger('core')

__all__ = ['Dazgeograftangepasst']


class Dazgeograftangepasst(Dazgeograft):
    #: Vorgabe der Nachformung der Figur am Becken (`eigen:…_scham`): gemessen 10.10.2026 mit `Schammessung` am Verlauf 0 … 1 (cute girl, Glättung und Randband an) —
    #:   Nachformung   Form Median / p90 / ≤ 2 mm     Normalen am Ring Median / p90 / umgekehrt
    #:   0,0           0,84 / 4,53 mm / 69 %          10,8° / 30,1° / 2 %
    #:   0,2           0,80 / 3,79 mm / 79 %           8,9° / 27,8° / 2 %
    #:   0,5           0,70 / 2,49 mm / 85 %          14,8° / 52,6° / 7 %
    #:   1,0           0,67 / 2,63 mm / 85 %          17,1° / 62,2° / 8 %
    #: Je stärker die Nachformung, desto besser die Form und desto knickiger der Ring (die Haut um das Loch wird dort von der Käfigverschiebung unruhig).
    #: Neu gemessen am 11.10.2026 mit allem, was seither dazukam (Tangentenraum, Randseite; Probebau ohne Schreiben, `ProjektTemp/_wegwerf/bau_probe.py`), diesmal mit dem Knick über die Naht
    #: je Ringkante (`Schammessungknick`) statt der Punktnormalen, die Falten wegmitteln — Form Median / p90 | Zone „Lippen seitlich" Median | Knick Median / p90 / größter, Kanten über 30°:
    #:   0,2   0,80 / 3,81 mm | 5,35 mm | 10,9° / 36,1° / 55,0°, 13        0,35  0,83 / 3,29 | 3,41 | 11,5° / 30,2° / 52,6°, 10
    #:   0,3   0,87 / 3,76    | 5,14    |  8,9° / 33,8° / 53,8°, 13        **0,4   0,76 / 2,92 | 2,77 | 10,2° / 32,6° / 51,3°, 13**
    #:   0,45  0,78 / 2,84    | 2,47    | 11,7° / 33,9° / 50,2°, 18        0,5   0,70 / 2,49 | 1,85 | 12,4° / 38,2° / 56,8°, 23
    #:   0,6   0,75 / 2,87    | 2,02    | 13,0° / 41,5° / 59,2°, 26        1,0   0,67 / 2,63 | 1,17 | 13,9° / 50,4° / 167°, 33 (5 Kanten über 60°)
    #: 0,4 ist besser als 0,2 in jeder Spalte (Form p90 unter der Schwelle 3,0 von `Schammessung`, die seitlichen Lippen halb so weit weg, der Knick nicht größer); die Werte sind an EINEM Modell
    #: gemessen und nicht gleichmäßig (0,35 hat die wenigsten Kanten über 30°) — ein anderes Modell braucht eine eigene Reihe (`--nachformung`).
    NACHFORMUNG = 0.4

    def __init__(self, modell, scham, name=None, aufloesung=1024, steifigkeit=None, nachformung=None):
        """`modell`: Name des gespeicherten Modells (`cute girl`); `scham`: Anzeigename des Scham-Stücks seines Imports (`cute girl Scham`); `name`: des neuen Stücks;
        `nachformung`: Wert der Nachformung der Figur am Becken (`eigen:…_scham`, `Blendimportnachformung`), wo es sie für das Modell gibt (Vorgabe `NACHFORMUNG`) — 0 schaltet sie aus.

        Ohne Nachformung steht die Haut der Figur am Becken 10–25 mm vor dem Original, und der Ring des Lochs sitzt auf dieser Haut: das Stück kann das Original dort kaum erreichen
        (gemessen am ersten Stand ohne Glättung: Original → Modell Median 2,64 mm, p90 8,85 mm, 30 % innerhalb 1 mm; mit Nachformung 1 damals 0,95 mm, p90 4,98 mm, 51 %)."""
        from django.conf import settings
        from Genesis9.eigenmorphe import G9eigenmorphe

        super().__init__('frau')
        self.modell, self.scham, self.aufloesung, self.steifigkeit = modell, scham, int(aufloesung), steifigkeit
        daten = json.loads((settings.HUMANBODY_MODELS_DIR / (modell + '.json')).read_text(encoding='utf-8'))
        self.regler = dict((daten.get('figur') or {}).get('regler') or {})
        #: Die Regler der Nachformung, die dieser Bau auf die Figur legt (`{eigen:…_scham: Wert}`) — das Modell, das das Stück trägt, braucht dieselben (`modell_abgleichen`).
        self.nachformung = {}
        wert = self.NACHFORMUNG if nachformung is None else float(nachformung)
        for schluessel in [k for k in self.regler if k.startswith(G9eigenmorphe.PRAEFIX) and not k.endswith('_scham')]:
            if G9eigenmorphe.vorhanden(schluessel + '_scham'):
                self.nachformung[schluessel + '_scham'] = wert
        self.regler.update(self.nachformung)
        self.haut_ordner = settings.HUMANBODY_MODELS_DIR / 'Texturen' / modell
        self.anzeige = name or '%s Daz Scham' % modell
        self.gruppe = 'Genitalia %s' % modell
        self._anpassung = None

    def figur(self):
        from .dazgeografthaut import Dazgeografthaut

        return Dazgeografthaut.grundfigur(self.regler)

    def modell_abgleichen(self, name):
        """Das Modell `name`, das dieses Stück trägt, bekommt die Regler der Nachformung des Baus — sonst säße der Ring auf einer anderen Haut als der, die der Browser zeigt.
        → die geänderten Regler (leer: nichts zu tun oder das Modell gibt es nicht)."""
        from django.conf import settings

        pfad = settings.HUMANBODY_MODELS_DIR / (name + '.json')
        if not self.nachformung or not pfad.is_file():
            return {}
        daten = json.loads(pfad.read_text(encoding='utf-8'))
        regler = daten.setdefault('figur', {}).setdefault('regler', {})
        geaendert = {k: v for k, v in self.nachformung.items() if regler.get(k) != v}
        if geaendert:
            regler.update(geaendert)
            pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding='utf-8')
            logger.info('Daz-Geograft: Modell %s bekommt %s', name, geaendert)
        return geaendert

    def angleichen(self, punkte, dreiecke, figur, maske, bericht):
        from .blendimportschamloch import Blendimportschamloch
        from .dazgeograftanpassung import Dazgeograftanpassung
        from .dazgeografthaut import Dazgeografthaut
        from .dazgeograftziel import Dazgeograftziel

        haut = Blendimportschamloch(figur['punkte'], figur['dreiecke'])
        ring_punkte = haut.ringpunkte(haut.ring(maske))
        anpassung = Dazgeograftanpassung(Dazgeografthaut.grundfigur(), figur, ring_punkte, Dazgeograftziel(self.scham))
        verlegt = anpassung.verlegen(punkte, dreiecke)
        angepasst = anpassung.anpassen(verlegt, dreiecke, self.steifigkeit)
        bericht['anpassung'] = anpassung.bericht
        bericht['nachformung'] = self.nachformung
        self._anpassung = anpassung
        return angepasst

    def backen(self, punkte, dreiecke, uv_ecken, figur, bericht):
        from Genesis9.eigenstueck import G9eigenstueck

        from .dazgeograftbacken import Dazgeograftbacken

        kennung, _anzeige = G9eigenstueck.kennung_und_name(self.anzeige)
        ausgabe = G9eigenstueck.arbeitsordner(kennung) / 'gebacken'
        dateien, zahlen = Dazgeograftbacken(self._anpassung.ziel, figur, self.haut_ordner, self.aufloesung).backen(punkte, dreiecke, uv_ecken, ausgabe)
        bericht['bake'] = zahlen
        return dateien

    def vorgabe(self):
        """Die Original-Scham des Imports (nur der Teil, den die Figur nicht trägt) mit ihrer Atlasfarbe."""
        ziel = self._anpassung.ziel
        return {'punkte': ziel.punkte, 'dreiecke': ziel.dreiecke, 'farbe_an': ziel.farbe_an, 'teil': True}

    def kachelbild(self):
        return lambda kachel: self.haut_ordner / ('haut_%d_farbe.klein.jpg' % kachel)

    def zusaetze(self, quelle, _kaefig, bilanz):
        """Die Regler des Katalogs (`sch_*`) kommen aus der alten Scham: `Dazgeograftmorphuebertrag` überträgt ihre fertigen Deltas auf dieses Stück (gemessen: die Zonen aus der Form des
        Daz-Stücks lagen daneben). Regler, die sich nicht übertragen lassen (alter Regler fehlt, altes Stück nicht in der Garderobe), rechnet der Katalog aus der Form des neuen Stücks."""
        from Genesis9.anatomien import G9anatomien
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.standardmorphe import G9standardmorphe

        from .dazgeograftmorphuebertrag import Dazgeograftmorphuebertrag

        namen = [e[0] for e in G9anatomien.fuer(self.NAMEN[self.geschlecht][1]).eintraege()]
        # Kennung des alten Stücks in der Garderobe: Dateiname in Kleinbuchstaben (`G9eigenstueck.schreiben`, Schlüssel `stueck`), nicht die Dateikennung `EIGEN_…`.
        alt = re.sub(r'[^a-z0-9]+', '_', G9eigenstueck.kennung_und_name(self.scham)[1].lower()).strip('_')
        bericht = bilanz['bericht']
        uebernommen, offen = [], {n: 'nicht versucht' for n in namen}
        try:
            uebertrag = Dazgeograftmorphuebertrag(alt, bilanz['stueck'])
            uebernommen, offen = uebertrag.alle(namen)
            bericht['regler_uebertrag'] = {'von': alt, 'uebernommen': len(uebernommen), 'pruefung': uebertrag.pruefen(uebernommen)}
            for zeile in Dazgeograftmorphuebertrag.zeilen(bericht['regler_uebertrag']['pruefung']):
                logger.info('Regler-Übernahme: %s', zeile)
        except (ValueError, OSError, KeyError, IndexError) as fehler:
            logger.warning('Regler-Übernahme von %s gescheitert: %s', alt, fehler)
            bericht['regler_uebertrag'] = {'von': alt, 'fehler': str(fehler)[:200]}
        selbst = []
        for name in (offen if isinstance(offen, dict) else {}):
            try:
                G9standardmorphe.bauen(bilanz['stueck'], name)
                selbst.append(name)
            except (ValueError, OSError, KeyError, IndexError) as fehler:
                logger.warning('Daz-Geograft %s: Regler %s nicht gebaut: %s', bilanz['stueck'], name, fehler)
        bericht['regler_gebaut'], bericht['regler_aus_form'] = len(uebernommen) + len(selbst), selbst
        logger.info('Daz-Geograft angepasst an %s: %d Regler (%d übernommen, %d aus der Form)', self.scham, len(uebernommen) + len(selbst), len(uebernommen), len(selbst))
