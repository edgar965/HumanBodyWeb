# -*- coding: utf-8 -*-
"""Bildmodellflame — der FLAME-Kopf EINES Kopfbilds: rechnen, als Bild ablegen, fürs 3D-Fenster.

Edgar (20.09.2026): „warum gibt es beim Kopf keine Button zum Lauf und Erzeugung eines
3D-Modells?" — das Gegenstück zu `Bildmodellgvhmr` für Kopfbilder. GVHMR erfindet auf einem
Kopfausschnitt einen Körper; der Kopf kommt aus PyMAF-X/FLAME (`Bildmodellschaetzung._schaetzen`
mit Zweck `gesicht`: `<stamm>_gesicht_flame.npy`, 5.023 Punkte, Kopf im Ursprung, y oben).
Der Einzelschritt `flame` (`Bildmodelllauf._flame`, Bild in `optionen.gvhmr_bild` wie beim
SMPL-Knopf) rechnet die Schätzung für genau dieses Bild (neu), rendert `ergebnis/flame_<stamm>.png`
(`Bildmodellgvhmrbild` ohne Rig, Bild im Seitenverhältnis des Ausschnitts) und schreibt das Feld
`flame` an den Eintrag: `{netz, punkte, dreiecke, bild, bild_breite, bild_hoehe, dauer_s, stand,
fehler?}`. Danach folgt die Kette wie nach `gvhmr` (Schätzung → Ziel → Kopf-Fit → Vorschau).

Die Dreiecke des FLAME-Kopfs sind die SMPL-X-Dreiecke, deren drei Ecken im Kopf liegen
(`G9zielnetz.flame_nummern`, FLAME-Reihenfolge) — einmal berechnet, `schaetzung/flame_dreiecke.npy`.
"""

import base64
import logging
import os
import time

import numpy as np
from django.utils import timezone

logger = logging.getLogger('core')

__all__ = ['Bildmodellflame']


class Bildmodellflame:
    FELD = 'flame'
    BILD = 'flame_%s.png'
    HOEHE = 640
    DREIECKE = 'flame_dreiecke.npy'

    def __init__(self, job, ablage, optionen=None):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen if optionen is not None else (job.optionen or {})

    # ------------------------------------------------------------ Rechnen

    def ausfuehren(self, datei, melder=None, neu=False):
        """FLAME für das Kopfbild `datei`; schreibt `flame` an den Eintrag und gibt es zurück."""
        from .bildmodellschaetzung import Bildmodellschaetzung

        eintrag = self.job.bild(datei) if datei else None
        if eintrag is None:
            raise ValueError('Kein Bild %s' % datei)
        if eintrag.get('kategorie') != 'kopf':
            raise ValueError('%s ist kein Kopfbild — für den Körper „SMPL (GVHMR)"' % datei)
        if melder:
            melder(0.05, 'FLAME (PyMAF-X): %s' % datei)
        start = time.monotonic()
        g = eintrag.get('gesichtsschaetzung') or {}
        if neu or not (g.get('flame_vertices_path') and self._netzpfad(eintrag).is_file()):
            Bildmodellschaetzung(self.job, self.ablage, self.optionen)._schaetzen(
                [eintrag], 'pymafx', melder, 'gesicht')
        ergebnis = self.eintrag(eintrag, time.monotonic() - start)
        # Die Seite kann derweil Häkchen und Typen geändert haben: frisch lesen, dann schreiben.
        self.job.refresh_from_db(fields=['bilder'])
        frisch = self.job.bild(datei)
        if frisch is None:
            raise ValueError('Bild %s wurde während des Laufs entfernt' % datei)
        frisch['gesichtsschaetzung'] = eintrag.get('gesichtsschaetzung')
        frisch[self.FELD] = ergebnis
        if ergebnis.get('netz'):
            if melder:
                melder(0.9, 'FLAME: Kopf rendern')
            self.bild_rendern(frisch)
        self.job.save(update_fields=['bilder', 'updated_at'])
        if melder:
            melder(1.0, ergebnis.get('fehler') or 'FLAME: %s fertig' % datei)
        return ergebnis

    def _netzpfad(self, eintrag):
        g = eintrag.get('gesichtsschaetzung') or {}
        return self.ablage.schaetzung() / os.path.basename(g.get('flame_vertices_path') or '-')

    def eintrag(self, eintrag, dauer_s=0.0):
        """Das Feld `flame` aus der Gesichtsschätzung des Eintrags."""
        aus = {'stand': timezone.now().isoformat(), 'dauer_s': round(float(dauer_s), 1)}
        g = eintrag.get('gesichtsschaetzung') or {}
        pfad = self._netzpfad(eintrag)
        if g.get('fehler') or not pfad.is_file():
            aus['fehler'] = str(g.get('fehler') or 'PyMAF-X hat keinen FLAME-Kopf abgelegt')[:400]
            return aus
        punkte = np.load(pfad)
        aus.update(netz=pfad.name, punkte=int(punkte.shape[0]), dreiecke=self.DREIECKE,
                   confidence=g.get('confidence'), expression=g.get('expression'))
        return aus

    # ------------------------------------------------------------ Dreiecke

    def dreiecke(self):
        """Die Dreiecke des FLAME-Kopfs (uint32, FLAME-Nummern) — aus dem SMPL-X-Netz, abgelegt."""
        pfad = self.ablage.schaetzung() / self.DREIECKE
        if pfad.is_file():
            return np.load(pfad)
        from Genesis9.zielnetz import G9zielnetz
        from SMPL.xkoerper import Smplxkoerper

        from ..daten.wrapperpfad import Wrapperpfad

        with Wrapperpfad():
            from baum import Baum

            koerper = Smplxkoerper.laden('neutral', Baum.SMPLX)
        nummern = G9zielnetz.flame_nummern()
        umkehr = np.full(len(koerper.v_template), -1, dtype=np.int64)
        umkehr[nummern] = np.arange(len(nummern))
        f = umkehr[np.asarray(koerper.faces, dtype=np.int64)]
        aus = f[(f >= 0).all(axis=1)].astype(np.uint32)
        pfad.parent.mkdir(parents=True, exist_ok=True)
        np.save(pfad, aus)
        return aus

    # ------------------------------------------------------------ Standbild

    def bild_rendern(self, eintrag):
        """Der FLAME-Kopf von vorn als PNG nach `ergebnis/`, im Seitenverhältnis des Ausschnitts."""
        from .bildmodellgvhmrbild import Bildmodellgvhmrbild

        g = eintrag.get(self.FELD) or {}
        stamm = os.path.splitext(eintrag.get('datei') or '')[0]
        try:
            punkte = np.load(self.ablage.schaetzung() / os.path.basename(g['netz']))
            s = eintrag.get('gesichtsschaetzung') or {}
            seitig = float(s.get('image_width') or 3) / float(s.get('image_height') or 4)
            breite, hoehe = int(round(self.HOEHE * seitig)), self.HOEHE
            self.ablage.ergebnis().mkdir(parents=True, exist_ok=True)
            name = self.BILD % stamm
            Bildmodellgvhmrbild(punkte, self.dreiecke()).speichern(
                self.ablage.ergebnis() / name, 'vorn', breite, hoehe)
            g.update(bild=name, bild_breite=breite, bild_hoehe=hoehe)
            g.pop('bild_fehler', None)
        except Exception as fehler:  # noqa: BLE001
            logger.warning('Bildmodell %s: FLAME-Bild %s nicht gerendert: %s',
                           self.job.kennung, stamm, fehler)
            g['bild_fehler'] = str(fehler)[:200]
        eintrag[self.FELD] = g
        return g.get('bild')

    # ------------------------------------------------------------ Anzeigen

    def netz3d(self, eintrag):
        """Punkte (base64 float32 N×3, Meter, y oben) und Dreiecke (base64 uint32) des FLAME-Kopfs."""
        g = (eintrag or {}).get(self.FELD) or {}
        if not g.get('netz'):
            raise FileNotFoundError(g.get('fehler') or 'FLAME für dieses Bild noch nicht gerechnet')
        punkte = np.load(self.ablage.schaetzung() / os.path.basename(g['netz']))
        return {
            'ok': True, 'datei': eintrag.get('datei'), 'anzahl': int(punkte.shape[0]),
            'punkte': self._b64(punkte, np.float32), 'dreiecke': self._b64(self.dreiecke(), np.uint32),
            'hoehe_cm': round(float(punkte[:, 1].max() - punkte[:, 1].min()) * 100.0, 1),
            'confidence': g.get('confidence'), 'stand': g.get('stand'),
        }

    @staticmethod
    def _b64(feld, art):
        return base64.b64encode(np.ascontiguousarray(feld, dtype=art).tobytes()).decode('ascii')
