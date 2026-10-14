# -*- coding: utf-8 -*-
"""Mesh3dmesswerte — die Messwerte eines Mesh-3D-Auftrags für die Prüfreihe, gelesen aus dem, was der Lauf abgelegt hat (13.10.2026).

Edgar: „Kannst du dir Testcases bauen, die checken, dass an den Jobs im ‚Test‘-Bereich nichts kaputt geht bei Änderungen, die du an der Pipeline machst?" — Anlass: an seinem Job „Edgar“ waren Hand, Hosensaum und Uhr kaputt gegangen, ohne dass es eine Messung gab, die es meldete
(die Hand durch die Mindestluft unter dem Stoff, die ich für die Ballerina eingeführt hatte).

Hier steht NUR das Messen (ohne Grafikkarte, ohne etwas zu rechnen): `Mesh3dmesswerte(kennung).alle()` → `{name: Zahl, Text oder None}`. Die Sollwerte und der Vergleich stehen in `Mesh3dpruefreihe`. Gemessen wird am Auftrag „Mesh to 3D“ des Imports
(`stand.ergebnis.figur`), an seiner Datenbankzeile (`ergebnis`) und an seinen Dateien:

    allgemein   status, fehler (Abschnitte des Ergebnisses mit einem Fehlerfeld), hoehe_cm, figur_netz_mm, netz_figur_mm
    hand        hand_verformung_mm (Verformung der Hand durch den Eigenmorph ohne den starren Anteil, größter RMS beider Hände),
                hand_untergrenze (Handpunkte mit Untergrenze unter Stoff: soll 0 sein — die Hand liegt nie unter Stoff)
    kleidung    kleidung_flaechen, kleidung_unterkante_m (1. Perzentil der Höhe: der Saum), zubehoer_flaechen (Uhr, Schmuck), hautband_art
    haar        haar_flaechen
    bestandteile teile (Namen, sortiert)
    animation   animation_gewaehlt, animation_spitzen, animation_max_dehnung (`Meshfigurtanzpruefung`), animation_wahl_beste (hat jedes Objekt die Kandidaten mit den wenigsten Spitzen gewählt?)
    griff       griff_seiten (Hände, deren Finger sich um einen Gegenstand schließen)
    abnahme     abnahme_doppelt (Flächen in zwei Objekten; müsste 0 sein)

Ein Wert, der sich nicht messen lässt (der Lauf ist älter als die Messung, die Datei fehlt), ist `None` — die Prüfreihe meldet „nicht gemessen“, nie „in Ordnung“.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Mesh3dmesswerte']


class Mesh3dmesswerte:
    #: Körperteile der Hände im Käfig (`G9koerperteile.TEILE`: l_hand 7, r_hand 11 — Finger gehören dazu).
    HAENDE = (7, 11)

    def __init__(self, kennung):
        from ..daten.blendimportablage import Blendimportablage

        self.kennung = kennung
        self.ablage = Blendimportablage(kennung)
        self.stand = self.ablage.stand() or {}
        self.job = None
        self.ordner = None
        figur = (self.stand.get('ergebnis') or {}).get('figur') or {}
        if figur.get('id'):
            from ..daten.meshfigurablage import Meshfigurablage
            from ..models import Meshfigurauftrag

            self.job = Meshfigurauftrag.objects.filter(pk=figur['id']).first()
            if self.job is not None:
                self.ordner = Meshfigurablage(self.job.kennung)

    # ------------------------------------------------------------------ Einstieg

    def alle(self):
        """Alle Messwerte; ein Fehler beim Messen einer Gruppe lässt ihre Werte `None` und steht im Log."""
        aus = {'status': self.stand.get('status'), 'figur_auftrag': getattr(self.job, 'kennung', None)}
        if self.job is None:
            return aus
        for gruppe in (self._allgemein, self._hand, self._kleidung, self._haar_teile, self._animation, self._griff, self._abnahme):
            try:
                aus.update(gruppe())
            except Exception:  # noqa: BLE001 — eine Messung darf die anderen nicht verhindern
                logger.exception('Prüfreihe %s: Messung %s gescheitert', self.kennung, gruppe.__name__)
        return aus

    @property
    def _e(self):
        return self.job.ergebnis or {}

    # ------------------------------------------------------------------ Gruppen

    def _allgemein(self):
        e = self._e
        abstand = ((e.get('vorschau') or {}).get('abstand')) or {}
        fehler = [k for k, v in e.items() if isinstance(v, dict) and (v.get('fehler') or (isinstance(v.get('objekt'), dict) and v['objekt'].get('fehler')))]
        return {'hoehe_cm': (e.get('vorschau') or {}).get('hoehe_cm'), 'figur_netz_mm': abstand.get('figur_netz_rms_mm'),
                'netz_figur_mm': abstand.get('netz_figur_rms_mm'), 'fehler': sorted(fehler)}

    def _hand(self):
        """Die Hand ist kaputt, wenn der Eigenmorph (`rest.npz`) sie verformt statt nur zu verschieben, oder wenn Punkte der Hand eine Untergrenze unter Stoff tragen (`mindest`)."""
        rest_datei, ende = self.ordner.arbeit('rest.npz'), self.ordner.arbeit('genesis_ende.npz')
        if not (rest_datei.is_file() and ende.is_file()):
            return {'hand_verformung_mm': None, 'hand_untergrenze': None}
        with np.load(rest_datei) as r, np.load(ende) as g:
            teil = g['teil']
            rest = r['rest'].astype(np.float64)
            mindest = r['mindest'].astype(np.float64) if 'mindest' in r.files else None
        rms = []
        for nr in self.HAENDE:
            v = rest[teil == nr]
            if len(v):
                rms.append(float(np.sqrt((np.linalg.norm(v - v.mean(axis=0), axis=1) ** 2).mean())) * 1000.0)
        hand = np.isin(teil, self.HAENDE)
        untergrenze = 0 if mindest is None else int((np.linalg.norm(mindest[hand], axis=1) > 0).sum())
        return {'hand_verformung_mm': round(max(rms), 2) if rms else None, 'hand_untergrenze': untergrenze}

    def _kleidung(self):
        k = self._e.get('kleidung') or {}
        objekt = k.get('objekt') or {}
        zubehoer = next((s for s in (k.get('stuecke') or []) if s.get('name') == 'Zubehör'), None)
        werte = {'kleidung_flaechen': objekt.get('flaechen'), 'zubehoer_flaechen': zubehoer.get('flaechen') if zubehoer else 0,
                 'hautband_art': (k.get('objekt_hautrand') or {}).get('art') or ('entfernen' if k.get('objekt_hautrand') else None), 'kleidung_unterkante_m': None}
        datei = self.ordner.ergebnis(objekt['datei']) if objekt.get('datei') else None
        if datei is not None and datei.is_file():
            import trimesh

            szene = trimesh.load(str(datei), process=False)
            netze = list(szene.geometry.values()) if hasattr(szene, 'geometry') else [szene]
            y = np.concatenate([np.asarray(n.vertices)[:, 1] for n in netze])
            werte['kleidung_unterkante_m'] = round(float(np.quantile(y, 0.01)), 4)
        return werte

    def _haar_teile(self):
        e = self._e
        teile = sorted(t.get('name') for t in (e.get('teile') or []) if t.get('name'))
        return {'haar_flaechen': (e.get('haar') or {}).get('flaechen'), 'teile': teile if 'teile' in e else None}

    def _animation(self):
        a = (self._e.get('animation') or {}).get('objekte') or {}
        k = a.get('kleidung') or {}
        gewaehlt = k.get('gewaehlt')
        zahlen = (k.get('kandidaten') or {}).get(gewaehlt) or {}
        return {'animation_gewaehlt': gewaehlt, 'animation_spitzen': zahlen.get('spitzen'), 'animation_max_dehnung': zahlen.get('max'),
                'animation_wahl_beste': self.wahl_beste(a)}

    @staticmethod
    def wahl_beste(objekte):
        """`True`, wenn bei JEDEM Objekt der Animationsprüfung die gewählten Gewichte nicht mehr `spitzen` haben als ein anderer Kandidat (so wählt `Meshfigurtanzpruefung`; ein Rückfall auf `basis` mit Grund zählt nicht
        als Fehler). `None` ohne Prüfung im Ergebnis — Aufträge von vor der Option.

        Die Gewebe-Regel (`Meshfigurtanzpruefung._gewebe`, 14.10.2026) trägt sich als Kandidat `gewebe` ein, auch wenn sie verworfen wurde (Zauberer: mehr Armgewicht in der Robe). Angenommen, ist SIE die Wahl (Ballerina `…14.11.28.16`: `weich_0.5` 0,0007, `gewebe` 0,0001 —
        die Reihe meldete „nicht die beste Wahl“, obwohl die Regel die bessere Wahl getroffen hatte); verworfen, zählt sie nicht als Kandidat."""
        if not objekte:
            return None
        for bericht in objekte.values():
            bericht = bericht or {}
            kandidaten = dict(bericht.get('kandidaten') or {})
            gewaehlt = bericht.get('gewaehlt')
            if (bericht.get('gewebe') or {}).get('angewandt') and 'gewebe' in kandidaten:
                gewaehlt = 'gewebe'
            else:
                kandidaten.pop('gewebe', None)
            if gewaehlt not in kandidaten:
                continue
            werte = [k.get('spitzen') for k in kandidaten.values() if isinstance(k.get('spitzen'), (int, float))]
            eigen = kandidaten[gewaehlt].get('spitzen')
            if werte and isinstance(eigen, (int, float)) and eigen > min(werte) + 1e-12:
                return False
        return True

    def _griff(self):
        """Die Seiten, deren Finger sich um einen Gegenstand schließen (`ergebnis.griff.seiten.<r|l>.uebernommen`, `Meshfigurgriff`); `[]` heißt: gerechnet, keine Hand angenommen, `None`: Lauf von vor dem Griff."""
        griff = self._e.get('griff')
        if not isinstance(griff, dict) or 'fassung' not in griff:
            return {'griff_seiten': None}
        return {'griff_seiten': sorted(s for s, v in (griff.get('seiten') or {}).items() if isinstance(v, dict) and v.get('uebernommen') and not v.get('leer'))}      # leere Hände (Finger-Pose) zählen nicht als Griff

    def _abnahme(self):
        """Doppelte Flächen aus der Abnahme des Laufs (`ergebnis.abnahme.objekte.doppelt`; müsste 0 sein) — `None` bei Läufen von vor der Abnahme."""
        objekte = (self._e.get('abnahme') or {}).get('objekte') or {}
        doppelt = objekte.get('doppelt')
        return {'abnahme_doppelt': doppelt if isinstance(doppelt, int) else None}
