# -*- coding: utf-8 -*-
"""Bildmodellschaetzung — Schritt 2: SMPL-X-Parameter je Hauptbild, gemischt.

Körper: alle Ausschnitte der Kategorie `koerper` mit Gewicht > 0 und
Nutzung „Form" (`Bildmodellbildtypen.fuer_form`) gehen an den gewählten
Schätzer — dazu, nur für das posierte Netz der Fotofarbe, die Bilder mit
Nutzung „nur Textur" und die Nebenbilder mit Körperteil (`nur_haut`), die
in der Mischung nichts zählen — SMPLest-X und PyMAF-X in EINEM python10-Prozess
(`Bildmodellmehrbild`, Modell einmal geladen), die anderen über
`photo_analyzer.analyze` je Bild (HMR 2.0 in python10, MediaPipe im
Prozess). Je Bild bleibt die Rohantwort am Eintrag (`schaetzung`), damit
ein neuer Lauf ab „ziel" nichts neu rechnen muss.

Gesicht: mit `pymafx_flame` laufen die Kopf- UND Körperbilder durch
PyMAF-X; der neutrale FLAME-Kopf (5.023 × 3) des Bildes mit dem größten
Gesicht wird das Kopfziel (`schaetzung/<stamm>_flame.npy`).

Mischung der Körperparameter: Median (Vorgabe), gewichtetes Mittel oder
das beste Bild — und das Geschlecht aus dem Schulter-Hüft-Verhältnis der
Sichtung, wenn die Grundfigur „auto" steht.
"""

import logging
import os
import shutil

import numpy as np

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellbildtypen import Bildmodellbildtypen
from .bildmodellmehrbild import Bildmodellmehrbild
from .bildmodellsilhouette import Bildmodellsilhouette
from .bildmodellvideo import Bildmodellvideo

logger = logging.getLogger('core')

__all__ = ['Bildmodellschaetzung']


class Bildmodellschaetzung:
    #: Detektorschwelle für SMPLest-X. Die Sichtung hat auf jedem Hauptbild
    #: schon eine Person mit ≥ 85 % der Landmarken bestätigt; SMPLest-Xs 0,5
    #: verwarf trotzdem Damiras Vorderansicht (YOLOv8x 0,38 bei 640 — die
    #: anderen Hauptbilder 0,56 und 0,92; bei 1280 alle unter 0,2).
    ZUVERSICHT = 0.2
    #: Schulter zu Hüfte (Bildbreite der Landmarken) — darüber „masculine".
    MASKULIN_AB = 1.25

    def __init__(self, job, ablage, optionen):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen

    # --------------------------------------------------------------- Lauf

    def nur_haut(self):
        """Bilder, die nur ihr posiertes Netz für die Fotofarbe brauchen (Textur „foto"):
        Körperbilder mit Nutzung „nur Textur" und Nebenbilder mit Körperteil."""
        if self.optionen.get('textur', 'hautton') != 'foto':
            return []
        aus = []
        for b in self.job.bilder:
            if not Bildmodellbildtypen.fuer_textur(b) or Bildmodellbildtypen.fuer_form(b):
                continue
            if b.get('kategorie') == 'koerper' or Bildmodellbildtypen.textur_teile(b):
                aus.append(b)
        return aus

    def ausfuehren(self, melder=None):
        form = [b for b in self.job.bilder if Bildmodellbildtypen.fuer_form(b)]
        koerper = [b for b in form if b.get('kategorie') == 'koerper']
        koepfe = [b for b in form if b.get('kategorie') == 'kopf']
        haut = self.nur_haut()
        backend = self.optionen.get('koerper', 'smplest_x')
        # Nur, was noch keine Antwort DIESES Schätzers hat: ein zweiter Lauf
        # ab „schaetzung" (andere Mischung, andere Grundfigur) lädt das
        # 8-GB-Modell nicht noch einmal; ein anderer Schätzer rechnet neu.
        offen = [
            b
            for b in koerper + haut
            if (b.get('schaetzung') or {}).get('backend') != backend
            or (b.get('schaetzung') or {}).get('fehler')
            # Eine SMPLest-X-Antwort ohne Pose stammt von vor dem 19.09.2026 —
            # der Silhouettenabgleich braucht sie; einmal neu rechnen.
            or (backend == 'smplest_x' and not (b.get('schaetzung') or {}).get('pose'))
        ]
        if backend != 'keiner' and offen:
            self._schaetzen(offen, backend, melder)
        wahl = self.optionen.get('silhouette', 'aus')
        Bildmodellsilhouette.zuruecksetzen(koerper)
        if wahl in ('an', 'messen'):
            Bildmodellsilhouette(self.ablage).ausfuehren(
                Bildmodellsilhouette.offen(koerper), melder, ersetzen=(wahl == 'an')
            )
        if self.optionen.get('gesicht') == 'pymafx_flame':
            self._schaetzen(
                [b for b in koepfe + koerper if not (b.get('gesichtsschaetzung') or {}).get('face_shape')],
                'pymafx',
                melder,
                'gesicht',
            )
        videos = [b for b in self.job.bilder if b.get('video') and Bildmodellbildtypen.fuer_form(b)]
        if self.optionen.get('video', 'gvhmr') == 'gvhmr':
            self._videos(videos, melder)
            # Ein Drehvideo zählt in der Mischung wie ein Hauptbild.
            koerper = koerper + [b for b in videos if (b.get('schaetzung') or {}).get('betas')]
        self.job.ergebnis = dict(self.job.ergebnis or {})
        self.job.ergebnis['schaetzung'] = self.mischen(koerper, koepfe)
        self.job.save(update_fields=['bilder', 'ergebnis', 'updated_at'])
        return self.job.ergebnis['schaetzung']

    # ------------------------------------------------------------- Videos

    def _videos(self, videos, melder):
        lauf = Bildmodellvideo(self.ablage)
        for b in videos:
            s = b.get('schaetzung') or {}
            if s.get('backend') == 'gvhmr' and s.get('betas'):
                continue
            self._eintragen(b, lauf.schaetzen(b, melder), 'gvhmr')

    # --------------------------------------------------------- schätzen

    def _schaetzen(self, bilder, backend, melder, zweck='koerper'):
        if not bilder:
            return
        feld = 'gesichtsschaetzung' if zweck == 'gesicht' else 'schaetzung'
        if Bildmodellmehrbild.kann(backend):
            self._mehrbild(bilder, backend, melder, feld)
        else:
            self._einzeln(bilder, backend, melder, feld)

    def _mehrbild(self, bilder, backend, melder, feld):
        argumente = ['--zuversicht', str(self.ZUVERSICHT)] if backend == 'smplest_x' else []
        lauf = Bildmodellmehrbild(backend, argumente)
        nach_datei = lauf.ausfuehren([self.ablage.zuschnitt() / b['datei'] for b in bilder], melder)
        for i, b in enumerate(bilder, 1):
            self._eintragen(b, nach_datei.get(b['datei']), backend, feld)
            if melder:
                melder(0.1 + 0.8 * i / len(bilder), '%s %d / %d' % (lauf.name, i, len(bilder)))

    # --------------------------------------------------------- einzeln

    def _einzeln(self, bilder, backend, melder, feld):
        # Der Wrapperpfad bleibt für die ganze Schleife eingehängt:
        # `analyze` lädt das Backend-Modul erst beim ersten Aufruf — mit
        # dem Pfad nur um den Import stand jedes Kopfbild auf „the 'package'
        # argument is required for '.pymafx_photo'" (19.09.2026).
        with Wrapperpfad():
            from photo_analyzer import analyze

            for i, b in enumerate(bilder, 1):
                if melder:
                    melder(0.1 + 0.8 * i / max(1, len(bilder)), '%s %d / %d' % (backend, i, len(bilder)))
                pfad = str(self.ablage.zuschnitt() / b['datei'])
                try:
                    roh = analyze(pfad, backend=backend)
                except Exception as fehler:  # noqa: BLE001
                    roh = {'error': str(fehler)}
                # `gesicht` ist der Gesichtskasten der Sichtung — die Schätzung
                # des Gesichts heißt deshalb `gesichtsschaetzung`.
                self._eintragen(b, roh, backend, feld)

    # --------------------------------------------------------- eintragen

    def _eintragen(self, bild, roh, backend, feld='schaetzung'):
        if not roh:
            roh = {'error': 'keine Antwort'}
        stamm = os.path.splitext(bild['datei'])[0]
        eintrag = {'backend': backend}
        if 'error' in roh:
            eintrag['fehler'] = str(roh['error'])
        else:
            for k in (
                'betas',
                'betas_std',
                'frames',
                'expression',
                'confidence',
                'gender',
                'jaw_pose',
                'pose',
                'face_shape',
                'bbox_xyxy',
                'cam_trans',
                'cam_focal',
                'cam_princpt',
                'processed_bbox',
                'input_body_shape',
                'pred_cam',
                'image_width',
                'image_height',
            ):
                if k in roh and roh[k] is not None:
                    eintrag[k] = roh[k]
            for quelle, name in (
                ('posed_vertices_path', '_posed.npy'),
                ('flame_vertices_path', '_flame.npy'),
            ):
                p = roh.get(quelle)
                if p and os.path.isfile(p):
                    ziel = self.ablage.schaetzung() / (stamm + name)
                    shutil.move(p, ziel)
                    eintrag[quelle] = ziel.name
        bild[feld] = eintrag

    # ----------------------------------------------------------- mischen

    def mischen(self, koerper, koepfe):
        art = self.optionen.get('mischung', 'median')
        reihen, gewichte, quellen = [], [], []
        for b in koerper:
            s = b.get('schaetzung') or {}
            if s.get('betas'):
                reihen.append(np.asarray(s['betas'], dtype=float)[:10])
                gewichte.append(float(b.get('gewicht') or 0) * float(s.get('confidence') or 1.0))
                quellen.append(b['datei'])
        betas = None
        if reihen:
            m = np.array([np.pad(r, (0, 10 - len(r))) for r in reihen])
            w = np.array(gewichte)
            if art == 'bestes':
                betas = m[int(w.argmax())]
            elif art == 'mittel' and w.sum() > 0:
                betas = (m * w[:, None]).sum(0) / w.sum()
            else:
                betas = np.median(m, axis=0)
        kopf = self._kopf(koepfe + koerper)
        return {
            'betas': [round(float(v), 5) for v in betas] if betas is not None else None,
            'bilder': quellen,
            'mischung': art,
            'anzahl': len(reihen),
            'kopf': kopf,
            'geschlecht': self.geschlecht(betas, koerper),
        }

    def _kopf(self, bilder):
        """Der FLAME-Kopf des Bildes mit dem größten Gesicht — Dateiname oder None."""
        beste, groesse = None, 0.0
        for b in bilder:
            p = (b.get('gesichtsschaetzung') or {}).get('flame_vertices_path') or (
                b.get('schaetzung') or {}
            ).get('flame_vertices_path')
            if not p:
                continue
            kasten = b.get('gesicht') or {}
            h = float(kasten.get('hoehe') or 0.1) * float(b.get('gewicht') or 0)
            if h > groesse:
                beste, groesse = p, h
        return beste

    def geschlecht(self, betas, koerper):
        """`feminine`/`masculine` — aus den SMPL-X-Parametern
        (`Morphzuordnung.geschlecht_schaetzen`: welchem Grundkörper die
        Gestalt näher liegt), sonst aus dem Schulter-Hüft-Verhältnis der
        Landmarken (über 1,25 masculine).

        Erst Landmarken allein: Damira (Frau) kam auf 1,3 — MediaPipes
        Hüftpunkte sind die Gelenke, nicht die Hüftbreite (19.09.2026).
        """
        if betas is not None:
            try:
                with Wrapperpfad():
                    from morphzuordnung import Morphzuordnung

                    return (
                        'masculine'
                        if Morphzuordnung.geschlecht_schaetzen([float(b) for b in betas]) == 'male'
                        else 'feminine'
                    )
            except Exception as fehler:  # noqa: BLE001
                logger.warning('Geschlecht aus Betas nicht schätzbar: %s', fehler)
        werte = []
        for b in koerper:
            lm = b.get('landmarken')
            if not lm or len(lm) < 29:
                continue
            schulter = abs(lm[11][0] - lm[12][0])
            huefte = abs(lm[23][0] - lm[24][0])
            if huefte > 1e-6 and b.get('ansicht') in ('vorne', 'hinten'):
                werte.append(schulter / huefte)
        if not werte:
            return 'feminine'
        return 'masculine' if float(np.median(werte)) > self.MASKULIN_AB else 'feminine'
