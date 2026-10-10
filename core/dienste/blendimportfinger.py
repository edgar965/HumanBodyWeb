# -*- coding: utf-8 -*-
"""Blendimportfinger — die Finger der Genesis-Figur an die Hände des Originals anpassen (Schritt „finger", 10.10.2026).

Anlass (Edgar mit Bild, Rosemary Winters: „Texturprobleme bei der Hand, und die Waffe geht durch die Hand hindurch"): „Mesh to 3D" kennt keine
Fingerknochen in der Haltung, die Figur hat immer die gestreckte Ruhehand. Das Original greift (Katana) oder liegt entspannt — Messung am
Import `2026.10.10.02.12.12`, Abstand Originalhand → Fläche der Figur in der Ruhelage: rechts Median 9,34 mm, p90 30,2, 56 % über 8 mm; die Kachel 1004
(Hände) zu 45 % und 52 % ohne Treffer, die Lücken füllte verwaschene Ersatzfarbe; das Katana lag in der gestreckten Hand statt in der Faust.
Gleiches Muster in allen gespeicherten Importen (Hände Median 3,9–9,3 mm, sonst Kopf und Rumpf 0,5–1,3 mm).

Was der Schritt tut (CPU, gemessen 371 s für zwei Hände bei 2 Rechenfäden):
  1. Die Originalpunkte jeder Hand (Teil `l_hand`/`r_hand` der Rückrechnung, `Blendimportlage.koerper_ruhelage`).
  2. `Blendimportfingersuche` stellt die 21 Fingerwinkel je Hand (`Blendimportfingermodell`) so, dass die Käfigflächen der Hand das Original
     treffen; eine Hand, die gestreckt schon passt, bleibt gestreckt.
  3. Ergebnis neben `posiert.npy` im Auftrag „Mesh to 3D": `finger.json` (die Winkel als Griff, Kennzahlen) und `finger_kaefig.npz` (um wie viel
     jeder Käfigpunkt der Hand in der Haltung anders liegt). `Blendimportlage` liest die zweite Datei und rechnet den Käfig der Haltung damit:
     das Original wird beim Entposen in die gestreckte Ruhehand zurückgeführt, die Haut passt dort, das Backen trifft.
  4. Das Requisit, das eine Hand trägt (Katana), bekommt die Winkel als `griff` in seine `.ersetzt.json`: die Figur schließt beim Tragen
     die Faust (wie bei den Absatzschuhen, `Blendimportfuss`).

Gemessen: Prototyp ohne Handgröße und ohne Ruhe-Probe (`ProjektTemp/_wegwerf/finger_ruhe_pruefung.py`): rechte Hand in Ruhe Median 9,34 → 2,77 mm.
Der Schritt selbst (10.10.2026, 23 Uhr, `schritte_nur.py … finger`, 371 s bei 2 Rechenfäden und niedriger Priorität): rechte Hand 9,34 → 4,74 mm,
p90 30,2 → 10,8, Handgröße −18 %; linke Hand (offen, entspannt) nur 4,79 → 3,38 / 11,5 → 10,3 — die Probe lässt sie gestreckt (Bild: die Passung
krümmte die Finger, um die kürzeren Finger der Originalhand auszugleichen). Der Größenunterschied der Finger gegenüber der Handfläche ist nicht
modelliert. Nicht berücksichtigt: Gelenkkorrekturen (JCM) der Finger.
"""

import json
import logging
import os

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Blendimportfinger']


class Blendimportfinger:
    DATEI = 'finger.json'
    KAEFIG = 'finger_kaefig.npz'
    FASSUNG = 1
    #: Weniger Originalpunkte hat eine Hand nie (eine vollständige hat 3.000–17.000): dann gibt es nichts zu messen.
    MINDEST_PUNKTE = 500

    def __init__(self, ablage, job, inventar, rollen, zusatz=None, melden=None):
        """`ablage`: `Blendimportablage` des Imports; `job`: der Auftrag „Mesh to 3D"; `zusatz`: die Regler der Nachformung."""
        self.ablage = ablage
        self.job = job
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen
        self.zusatz = dict(zusatz or {})
        self.melden = melden or (lambda anteil, text: None)

    # ------------------------------------------------------------------ Rechnen

    def rechnen(self):
        """Beide Hände anpassen und ablegen; der Bericht für den Stand (`ergebnis.finger`)."""
        from Genesis9.koerperteile import G9koerperteile

        from .blendimportfingermodell import Blendimportfingermodell
        from .blendimportfingersuche import Blendimportfingersuche
        from .blendimporthaltung import Blendimporthaltung
        from .blendimportlage import Blendimportlage

        # Ohne den Käfig-Zusatz eines früheren Laufs: die Rechnung beginnt bei der gestreckten Hand.
        lage = Blendimportlage(self.job, self.zusatz, finger=False)
        halt = Blendimporthaltung(lage)
        if halt.vorbereiten() is None:
            return self._nichts('Der Auftrag führt keine Haltung')
        koerper = next((r for r in self.rollen if r['rolle'] == 'koerper'), None)
        if koerper is None:
            return self._nichts('Kein Körper')
        with np.load(self.ablage.export(self.inventar[koerper['name']]['datei'])) as d:
            punkte, dreiecke = np.asarray(d['punkte'], dtype=np.float64), np.asarray(d['dreiecke'], dtype=np.int64)
        self.melden(0.05, 'Finger: Hände des Originals')
        _, teile = lage.koerper_ruhelage(punkte, dreiecke, mit_teilen=True)
        netz = lage.ins_netz(punkte)
        masken = {s: teile == G9koerperteile.NUMMER[s + '_hand'] for s in ('r', 'l')}
        figur = lage.genesis()
        ruhe0 = self._ruhe(lage, punkte, dreiecke, figur, masken)
        bericht, idx_liste, delta_liste, haltung = {}, [], [], {}
        for nr, seite in enumerate(('r', 'l')):
            ziel = netz[masken[seite]]
            if len(ziel) < self.MINDEST_PUNKTE:
                bericht[seite] = {'uebernommen': False, 'grund': 'nur %d Originalpunkte an dieser Hand' % len(ziel)}
                continue
            modell = Blendimportfingermodell(halt, seite, ziel)
            erg = Blendimportfingersuche(modell, lambda text, nr=nr: self.melden(0.1 + 0.4 * nr, text)).suchen()
            griff = modell.als_griff(erg['phi']) if erg['uebernommen'] else {}
            bericht[seite] = {'uebernommen': False, 'original_punkte': int(len(ziel)), 'vorher': erg['vorher'], 'nachher': erg['nachher'],
                              'start': erg['start'], 'sekunden': erg['sekunden'], 'auswertungen': erg['auswertungen'], 'griff': {}}
            if griff:
                # Der Käfig bekommt genau die gerundeten Winkel, die auch als Griff gespeichert werden.
                idx, delta = modell.kaefig(modell.vektor(griff))
                lage.kaefig_posiert[idx] += delta
                lage._entposen = None
                probe = self._probe(ruhe0[seite], self._ruhe(lage, punkte, dreiecke, figur, masken)[seite])
                bericht[seite]['ruhe'] = probe
                if probe['gilt']:
                    bericht[seite].update(uebernommen=True, griff=griff)
                    idx_liste.append(idx)
                    delta_liste.append(delta)
                    haltung.update(griff)
                else:
                    lage.kaefig_posiert[idx] -= delta
                    lage._entposen = None
            logger.info('Blender-Import %s: Finger %s %s', self.ablage.kennung, seite, {k: v for k, v in bericht[seite].items() if k != 'griff'})
        self._ablegen(bericht, idx_liste, delta_liste)
        return {'seiten': bericht, 'aus': not haltung}

    #: Die Winkel gelten nur, wenn die Originalhand danach in der RUHELAGE im Median UND im p90 höchstens diesen Anteil des früheren Abstands zur
    #: Fläche der Figur hat — das Maß, das später das Backen und das Entposen der Kleider entscheidet, nicht das Maß der Suche. Gemessen
    #: (23.10 Uhr, Lauf auf Rosemary Winters): rechte Hand Median 9,34 → 4,74, p90 30,2 → 10,8 (Griff um das Katana, gilt); linke Hand 4,79 → 3,38
    #: und 11,5 → 10,3 (offene Hand, Faust im Bild falsch, gilt nicht). Der Wert 0,8 ist eine Setzung an diesen zwei Händen eines Modells.
    RUHE_VORTEIL = 0.8

    @staticmethod
    def _ruhe(lage, punkte, dreiecke, figur, masken):
        """`{seite: Abstand der Originalpunkte der Hand zur Fläche der Figur in der Ruhelage (mm)}` mit dem Käfig der Haltung, wie er jetzt ist."""
        from .flaechenabstand import Flaechenabstand

        ruhe = lage.koerper_ruhelage(punkte, dreiecke)
        return {s: Flaechenabstand.abstand(ruhe[m], figur['punkte'], figur['dreiecke']) * 1000.0 for s, m in masken.items()}

    def _probe(self, vorher, nachher):
        """`{vorher_median_mm, nachher_median_mm, vorher_p90_mm, nachher_p90_mm, gilt}` der Ruhelage-Probe: Median UND p90 müssen um `RUHE_VORTEIL`
        besser werden. Nur der Median genügt nicht — gemessen an der linken Hand von Rosemary (offene, entspannte Hand): Median 4,79 → 3,38 (0,71),
        p90 11,5 → 10,3 (0,89); das Bild zeigte eine zusammengekrümmte Faust, die die zu langen Genesis-Finger auf die Länge der Originalhand
        kürzt. Die rechte Hand (echter Griff): Median 0,51, p90 0,36."""
        v50, n50 = float(np.median(vorher)), float(np.median(nachher))
        v90, n90 = float(np.percentile(vorher, 90)), float(np.percentile(nachher, 90))
        return {'vorher_median_mm': round(v50, 2), 'nachher_median_mm': round(n50, 2), 'vorher_p90_mm': round(v90, 2), 'nachher_p90_mm': round(n90, 2),
                'gilt': bool(n50 < self.RUHE_VORTEIL * v50 and n90 < self.RUHE_VORTEIL * v90)}

    @staticmethod
    def _nichts(grund):
        return {'aus': True, 'grund': grund}

    def _ablegen(self, bericht, idx_liste, delta_liste):
        """Beide Dateien neben `posiert.npy` — erst die Käfigdatei (ohne Hand keine), dann die Winkel."""
        from ..atomic_write import AtomarSchreiber

        arbeit = self.job_ablage().arbeit
        kaefig = arbeit(self.KAEFIG)
        if idx_liste:
            idx = np.concatenate(idx_liste).astype(np.int32)
            delta = np.concatenate(delta_liste).astype(np.float32)
            gesamt = {}
            for i, d in zip(idx, delta, strict=True):
                gesamt[int(i)] = gesamt.get(int(i), 0.0) + d            # ein Punkt, den beide Hände bewegen (Handgelenk), bekommt die Summe
            neben = kaefig.with_name(kaefig.stem + '.neu.npz')
            np.savez(neben, idx=np.array(sorted(gesamt), dtype=np.int32), delta=np.array([gesamt[k] for k in sorted(gesamt)], dtype=np.float32))
            os.replace(neben, kaefig)
        elif kaefig.is_file():
            kaefig.unlink()
        AtomarSchreiber.json_schreiben(arbeit(self.DATEI), {'fassung': self.FASSUNG, 'seiten': bericht})

    def job_ablage(self):
        from ..daten.meshfigurablage import Meshfigurablage

        return Meshfigurablage(self.job.kennung)

    # ------------------------------------------------------------------- Lesen

    @classmethod
    def kaefig(cls, meshablage):
        """`(idx, delta)` der Käfigkorrektur im Auftrag „Mesh to 3D" — `None` ohne Datei (Imports vor dem 10.10.2026, Hände gestreckt)."""
        pfad = meshablage.arbeit(cls.KAEFIG)
        if not pfad.is_file():
            return None
        with np.load(pfad) as d:
            return np.asarray(d['idx'], dtype=np.int64), np.asarray(d['delta'], dtype=np.float64)

    @classmethod
    def _lesen(cls, meshablage):
        try:
            daten = json.loads(meshablage.arbeit(cls.DATEI).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}
        seiten = daten.get('seiten') if isinstance(daten, dict) else None
        return seiten if isinstance(seiten, dict) else {}

    @classmethod
    def haltung(cls, meshablage):
        """`{knochen: {kanal: Grad}}` der Finger beider Hände (nur angenommene), die im Käfig der Haltung stecken — leer ohne Datei."""
        aus = {}
        for seite in cls._lesen(meshablage).values():
            if isinstance(seite, dict) and seite.get('uebernommen'):
                aus.update(seite.get('griff') or {})
        return aus

    @classmethod
    def griff(cls, meshablage, teil):
        """Die Fingerwinkel der Hand `teil` (`r_hand`/`l_hand`) als Griff für ein Requisit — leer, wenn `teil` keine Hand ist oder die Hand gestreckt blieb."""
        if teil not in ('r_hand', 'l_hand'):
            return {}
        seite = cls._lesen(meshablage).get(teil[0])
        return dict(seite.get('griff') or {}) if isinstance(seite, dict) and seite.get('uebernommen') else {}

    @classmethod
    def requisit_griff(cls, meshablage, duf, teil):
        """Das Requisit in der Hand `teil` bekommt die Fingerwinkel als `griff` in `<stück>.ersetzt.json`: die Figur schließt beim Tragen die Faust
        (`G9stueckersatz.griff`, wie bei den Absatzschuhen). Die Datei kommt NACH der `.duf` (Stückstand im Antwortvorrat) und auch ohne Winkel
        — sonst bliebe der Griff eines früheren Laufs stehen. Ein Requisit an anderer Stelle (Helm, Rücken) bekommt keine. `{seite, knochen}` oder None."""
        from Genesis9.stueckersatz import G9stueckersatz

        if teil not in ('r_hand', 'l_hand'):
            return None
        griff = cls.griff(meshablage, teil)
        G9stueckersatz.schreiben(duf, [], griff=griff or None)
        return {'seite': teil[0], 'knochen': len(griff)}
