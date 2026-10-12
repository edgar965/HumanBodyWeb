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
from .dazgeograftumriss import Dazgeograftumriss

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
    #: Unterteilungsstufe des angepassten Stücks (seit 11.10.2026 Stufe 2 ≈ 2 mm Punktabstand, Frau 16.741 Punkte vor der Naht; das Basis-Stück „Daz Anatomie Frau" bleibt auf Stufe 1). Gemessen am Probebau
    #: „cute girl Daz2" (`Schammessung`, gegen Stufe 1): Form Original → Modell Median 0,32 / p90 1,73 mm (0,63 / 2,19), Stück → Original 0,09 / 1,04 (0,28 / 1,60), Tiefenkarte p90 1,15 (2,31),
    #: Knick über die Naht größter 49,2° (56,6°), keine Kante über 60°; Regler-Übernahme von der alten Scham Masse 1,00 (0,83). Die Regler am Basis-Stück: `Dazgeograftstufenzuordnung`.
    STUFE = 2
    #: Vorgabe für ALLE Modelle (11.10.2026, Edgar: „sodass sie standardmäßig bei allen Modellen angewandt wird"): das Stück hat den Umriss und das Loch des Blender-Stücks (`Dazgeograftumriss`),
    #: sein Rand läuft wie dort über 12 mm auf die Haut (`Blendimportscham.angleichen`). Gemessen an „cute girl": Blender-Stück 72 × 43 mm, Daz-Geograft 120 × 74 mm. `False` = das Loch des Geografts
    #: (Stand bis 11.10.2026, Modelle „cute girl Daz", „Daz1", „Daz2").
    UMRISS = True
    #: Randband des zugeschnittenen Stücks (mm): Breite und höchster Weg zur Haut, `None` = wie beim Blender-Stück (`Blendimportscham.BAND_MM`, `ANGLEICH_MAX_MM`: 12 / 8); `RAND_MAX_MM` 0 = kein Band.
    #: Gemessen 11.10.2026 (Probebau ohne Schreiben, `ProjektTemp/_wegwerf/umriss_reihe.py`, Stufe 2, „cute girl", Umriss; Band 12 mm, Höchstweg wechselnd).
    #: Edgar, 11.10.2026: „mach das wie Blender mit 8 mm" — gewählt ist die Blender-Vorgabe (12 / 8):
    #:   Höchstweg   Form Median / p90   Erhebung links / rechts   Knick über die Naht p90 / größter / Kanten über 60°   Rand → Ring p90 / größter
    #:   0           0,39 / 2,66 mm      0,87 / 0,84               45,2° / 62,5° / 1                                       16,4 / 20,4 mm
    #:   2           0,40 / 2,69         0,82 / 0,77               43,1° / 62,7° / 1                                       14,4 / 18,4
    #:   3           0,42 / 2,77         0,78 / 0,74               41,0° / 60,8° / 1                                       13,4 / 17,4
    #:   4           0,45 / 2,78         0,75 / 0,71               38,7° / 58,7° / 0                                       12,5 / 16,4
    #:   8 (gewählt) 0,48 / 2,85         0,62 / 0,61               30,1° / 48,6° / 0                                        8,8 / 12,7
    #: Das Band zieht den Rand zur Haut (kein Absatz, keine Naht-Kante über 60°) und kostet Erhebung der Lippenflanken; im Randstreifen liegen mit dem Band 707 statt 905 von 2.507 Punkten mehr als 3 mm unter der Haut
    #: (`ProjektTemp/_wegwerf/randband_bild.py`). Die Stufe am Ring (gültige Ringpunkte, `Schammessungansichten`) ist in allen Fällen klein (größte 1,7–4,1 mm).
    RAND_BAND_MM, RAND_MAX_MM = None, None
    #: Woran das Randband den Rand zieht: `haut` (die Figurfläche, wie beim Blender-Stück — Stand bis 11.10.2026) oder `stueck` (die Scham des Blender-Imports, auf die sich das Geograft legt: der Rand folgt dann dem Original statt der Hautebene).
    RAND_ZIEL = 'haut'
    #: Anzeigename eines anderen Blender-Stücks, dessen Loch (Umriss) gilt statt dem von `scham` — z. B. das größere Loch eines Stücks mit höherem Kasten (`None` = das von `scham`). Die Anpassung zielt weiter auf `scham`.
    UMRISS_VON = None

    def __init__(self, modell, scham, name=None, aufloesung=1024, steifigkeit=None, nachformung=None, stufe=None, umriss=None):
        """`modell`: Name des gespeicherten Modells (`cute girl`); `scham`: Anzeigename des Scham-Stücks seines Imports (`cute girl Scham`); `name`: des neuen Stücks;
        `nachformung`: Wert der Nachformung der Figur am Becken (`eigen:…_scham`, `Blendimportnachformung`), wo es sie für das Modell gibt (Vorgabe `NACHFORMUNG`) — 0 schaltet sie aus;
        `stufe`: Unterteilungsstufe des Geografts (Vorgabe `STUFE` = 2: ≈ 2 mm Punktabstand, 1 ≈ 4 mm — Maße der Anpassung: `Dazgeograftanpassung.STUFE_STEIF`);
        `umriss`: Umriss und Loch des Blender-Stücks `scham` statt des Geografts (Vorgabe `UMRISS`).

        Ohne Nachformung steht die Haut der Figur am Becken 10–25 mm vor dem Original, und der Ring des Lochs sitzt auf dieser Haut: das Stück kann das Original dort kaum erreichen
        (gemessen am ersten Stand ohne Glättung: Original → Modell Median 2,64 mm, p90 8,85 mm, 30 % innerhalb 1 mm; mit Nachformung 1 damals 0,95 mm, p90 4,98 mm, 51 %)."""
        from django.conf import settings

        super().__init__('frau')
        if stufe is not None:
            self.STUFE = int(stufe)
        self.modell, self.scham, self.aufloesung, self.steifigkeit = modell, scham, int(aufloesung), steifigkeit
        daten = json.loads((settings.HUMANBODY_MODELS_DIR / (modell + '.json')).read_text(encoding='utf-8'))
        self.regler = dict((daten.get('figur') or {}).get('regler') or {})
        #: Das Loch des Blender-Stücks (bool je Dreieck der Haut) — oder `None`, dann gilt das Loch des Geografts. Ohne Loch beim Blender-Stück (gebaut ohne Naht) fällt der Bau darauf zurück, mit Warnung.
        #: Die Nachformung braucht es schon jetzt: das Unterkleid der Figur lässt die Haut IM Loch aus (`Dazgeograftnachformung`).
        self.umriss_loch = self._umriss_loch(self.UMRISS if umriss is None else bool(umriss))
        #: `herkunft` je Punkt des zugeschnittenen Stücks (Nummer vor dem Schnitt, −1 neu), sonst `None` (`Dazgeograftumriss.zuschneiden`).
        self.herkunft = None
        #: Die Regler, die dieser Bau auf die Figur legt (`{eigen:…_scham: Wert, eigen:…_unterkleid_daz: 1}`) und die des Imports, die er weglässt (`…_unterkleid`) — das Modell, das das Stück
        #: trägt, braucht dieselben (`modell_abgleichen`).
        self.nachformung, self.entfernen = {}, []
        wert = self.NACHFORMUNG if nachformung is None else float(nachformung)
        if wert:
            # Der Import lässt die Nachformung bei `scham = objekt` weg, ein Neuimport ersetzt den Körpermorph, und sein Unterkleid ist ohne sie gerechnet und zählt das Loch mit: fehlende Morphe
            # werden hier aus dem Import des Modells gerechnet (`Dazgeograftnachformung`).
            from .dazgeograftnachformung import Dazgeograftnachformung

            fremd = self.stueck_id(self.UMRISS_VON) if self.UMRISS_VON and self.umriss_loch is not None else None
            self.nachformung, self.entfernen = Dazgeograftnachformung.sichern(daten, wert, self.umriss_loch, fremd)
        self.regler.update(self.nachformung)
        for schluessel in self.entfernen:
            self.regler.pop(schluessel, None)
        if wert and not self.nachformung:
            # Gesehen 11.10.2026: ein Neuimport des Modells ersetzte den Körpermorph (`…_193211` → `…_084515`), und zu dem gibt es keinen `…_scham`-Morph — der Bau lief ohne Nachformung weiter,
            # ohne ein Wort (Form Original → Modell Median 0,80 / p90 3,69 statt 0,76 / 2,92 mm, Naht über 60°: 4 Kanten statt 0).
            logger.warning('Daz-Geograft für %s: kein Nachformungs-Morph (`eigen:…_scham`) zu den Körper-Reglern des Modells — Bau OHNE Nachformung (Wert %s)', modell, wert)
        self.haut_ordner = settings.HUMANBODY_MODELS_DIR / 'Texturen' / modell
        self.anzeige = name or '%s Daz Scham' % modell
        self.gruppe = 'Genitalia %s' % modell
        self._anpassung = None

    def figur(self):
        from .dazgeografthaut import Dazgeografthaut

        return Dazgeografthaut.grundfigur(self.regler)

    def falten(self, punkte, dreiecke, loch, bericht):
        """Die Anpassung erzeugt Haarnadel-Falten im Innern (225 neue Kanten über 90°, 2,28 % statt 1,71 % des rohen Geografts): sie werden begrenzt geglättet (`Schamfaltenglaetter`)."""
        from .schamfaltenglaetter import Schamfaltenglaetter

        neu, zahlen = Schamfaltenglaetter.glaetten(punkte, dreiecke, loch['ring'])
        bericht['falten'] = zahlen
        return neu

    @staticmethod
    def stueck_id(anzeige):
        """So heißt das Stück „cute girl Scham" in der Garderobe und im Modell (`kleidung`): kleingeschrieben, Sonderzeichen zu `_` (`cute_girl_scham`) — nicht die Netzkennung `EIGEN_…`."""
        from Genesis9.eigenstueck import G9eigenstueck

        return re.sub(r'[^a-z0-9]+', '_', G9eigenstueck.kennung_und_name(anzeige)[1].lower()).strip('_')

    def modell_ableiten(self, ziel):
        """Das Modell `ziel` (z. B. „cute girl Daz") frisch aus dem Modell des Imports ableiten: Kopie mit neuem Namen, das Blender-Scham-Stück (`self.scham`) durch dieses Stück ersetzt, alles andere
        (Regler, Kleidung, Hautkacheln, Herkunft) wie im Import. Vorher war „cute girl Daz" eine Kopie von Hand und blieb nach dem Neuimport beim alten Körpermorph (`…_193211`) stehen, während
        „cute girl" auf `…_084515` lief. → `True`, wenn geschrieben (die Regler des Baus legt danach `modell_abgleichen` darauf)."""
        import copy

        from django.conf import settings

        quelle = json.loads((settings.HUMANBODY_MODELS_DIR / (self.modell + '.json')).read_text(encoding='utf-8'))
        neu = copy.deepcopy(quelle)
        neu['name'] = ziel
        kleidung = neu.setdefault('figur', {}).setdefault('kleidung', {})
        eintrag = kleidung.pop(self.stueck_id(self.scham), None)
        kleidung[self.stueck_id(self.anzeige)] = eintrag if eintrag is not None else {}
        # Das Stück gehört diesem Modell: beim Löschen des Modells geht es in den Papierkorb der Garderobe (`Modellstuecke`; Edgar, 11.10.2026: „warum liegen die noch in der Bibliothek?").
        herkunft = neu['figur'].get('herkunft')
        if not isinstance(herkunft, dict):
            herkunft = neu['figur']['herkunft'] = {}
        herkunft['daz_stuecke'] = [self.stueck_id(self.anzeige)]
        (settings.HUMANBODY_MODELS_DIR / (ziel + '.json')).write_text(json.dumps(neu, ensure_ascii=False, indent=2), encoding='utf-8')
        logger.info('Daz-Geograft: Modell %s aus %s abgeleitet (Stück %s statt %s)', ziel, self.modell, self.anzeige, self.scham)
        return True

    def modell_abgleichen(self, name):
        """Das Modell `name`, das dieses Stück trägt, bekommt die Regler des Baus (Nachformung, Unterkleid der Daz-Figur) und verliert die des Imports, die er weglässt — sonst säße der Ring auf einer
        anderen Haut als der, die der Browser zeigt. → die geänderten Regler (entfernte mit `None`; leer: nichts zu tun oder das Modell gibt es nicht)."""
        from django.conf import settings

        pfad = settings.HUMANBODY_MODELS_DIR / (name + '.json')
        if not (self.nachformung or self.entfernen) or not pfad.is_file():
            return {}
        daten = json.loads(pfad.read_text(encoding='utf-8'))
        regler = daten.setdefault('figur', {}).setdefault('regler', {})
        geaendert = {k: v for k, v in self.nachformung.items() if regler.get(k) != v}
        entfernt = [k for k in self.entfernen if k in regler]
        if geaendert or entfernt:
            regler.update(geaendert)
            for k in entfernt:
                regler.pop(k)
            pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding='utf-8')
            logger.info('Daz-Geograft: Modell %s bekommt %s und verliert %s', name, geaendert, entfernt)
        return {**geaendert, **{k: None for k in entfernt}}

    def _umriss_loch(self, an):
        """Das Loch des Blender-Stücks `self.scham` (oder von `UMRISS_VON`, ein anderes Stück derselben Haut), wenn `an` — sonst, und wenn das Stück keines nennt (Warnung), `None`."""
        if not an:
            return None
        try:
            return Dazgeograftumriss.loch(self.stueck_id(self.UMRISS_VON or self.scham))
        except ValueError as fehler:
            logger.warning('Daz-Geograft für %s: kein Umriss des Blender-Stücks, es gilt das Loch des Geografts: %s', self.modell, fehler)
            return None

    def loch_maske(self, figur, quelle):
        """Das Loch des Blender-Stücks (`Dazgeograftumriss`) — oder das des Geografts (`UMRISS` aus)."""
        if self.umriss_loch is None:
            return super().loch_maske(figur, quelle)
        if len(self.umriss_loch) != len(figur['dreiecke']):
            raise ValueError('das Loch des Blender-Stücks gilt für %d Dreiecke der Haut, die Figur hat %d' % (len(self.umriss_loch), len(figur['dreiecke'])))
        return self.umriss_loch, {'umriss': self.stueck_id(self.scham), 'dreiecke': int(self.umriss_loch.sum())}

    def angleichen(self, punkte, dreiecke, uv_ecken, figur, maske, bericht):
        """verlegen → (am Umriss zuschneiden) → anpassen → (Randband auf die Haut) — das Geograft in den Raum der Figur und auf die Scham des Imports."""
        import trimesh

        from .blendimportscham import Blendimportscham
        from .blendimportschamloch import Blendimportschamloch
        from .dazgeograftanpassung import Dazgeograftanpassung
        from .dazgeografthaut import Dazgeografthaut
        from .dazgeograftziel import Dazgeograftziel

        haut = Blendimportschamloch(figur['punkte'], figur['dreiecke'])
        ring = haut.ring(maske)
        ring_punkte = haut.ringpunkte(ring)
        anpassung = Dazgeograftanpassung(Dazgeografthaut.grundfigur(), figur, ring_punkte, Dazgeograftziel(self.scham), stufe=self.STUFE)
        verlegt = anpassung.verlegen(punkte, dreiecke)
        zugeschnitten = self.umriss_loch is not None
        flaeche = trimesh.Trimesh(figur['punkte'], figur['dreiecke'], process=False)
        if zugeschnitten:        # am Rand des Lochs (ungeglättet: die Linie, auf der die Haut wirklich endet) — die Naht rastet den Rand danach auf den geglätteten Ring
            verlegt, dreiecke, uv_ecken, self.herkunft, bericht['umriss'] = Dazgeograftumriss.zuschneiden(verlegt, dreiecke, uv_ecken, flaeche, maske, haut.lage(ring))
        angepasst = anpassung.anpassen(verlegt, dreiecke, self.steifigkeit, fest=not zugeschnitten)
        if zugeschnitten and self.RAND_MAX_MM != 0:        # wie beim Blender-Stück: der Rand läuft über `BAND_MM` auf die Haut, höchstens `ANGLEICH_MAX_MM`
            ziel = flaeche if self.RAND_ZIEL == 'haut' else trimesh.Trimesh(anpassung.ziel.punkte, anpassung.ziel.dreiecke, process=False)
            angepasst, bericht['rand'] = Blendimportscham.angleichen(angepasst, dreiecke, ziel, self.RAND_BAND_MM, self.RAND_MAX_MM)
        bericht['anpassung'] = anpassung.bericht
        bericht['nachformung'] = self.nachformung
        self._anpassung = anpassung
        return angepasst, dreiecke, uv_ecken

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
        from Genesis9.standardmorphe import G9standardmorphe

        from .dazgeograftmorphuebertrag import Dazgeograftmorphuebertrag

        namen = [e[0] for e in G9anatomien.fuer(self.NAMEN[self.geschlecht][1]).eintraege()]
        # Kennung des alten Stücks in der Garderobe: Dateiname in Kleinbuchstaben (`G9eigenstueck.schreiben`, Schlüssel `stueck`), nicht die Dateikennung `EIGEN_…`.
        alt = self.stueck_id(self.scham)
        bericht = bilanz['bericht']
        # Welche Punkte des Geografts das zugeschnittene Stück noch trägt — `Dazgeograftmorphbasis` braucht es für die Regler des Basis-Stücks (ohne Zuschnitt: `null`, damit eine ältere Datei nicht weiter gilt).
        Dazgeograftumriss.herkunft_ablegen(bilanz['duf'], self.STUFE, self.nahtfrei_punkte, self.herkunft)
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
