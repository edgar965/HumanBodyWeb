# -*- coding: utf-8 -*-
"""Retargetvorrat — der Retarget eines Auftrags, gerechnet bevor er „fertig" ist.

Edgar, 16.09.2026: „keine Animation zu sehen … erst jetzt, nach ca. 1 Minute"
→ „Mach retarget neben BVH". Der erste Abruf eines Ergebnisses im Studio
oder auf der Ergebnisseite rechnete den Retarget (43 s bei 7.538 Bildern) —
je BVH-Datei, je Ort: das BVH im Auftragsordner und seine Kopie in der
Bibliothek (`A_Results`) haben je eine eigene Ablage
(`<stamm>_retarget_<hash>.json`, `Retargetdaten.ablage`).

Hier rechnet der Auftragsprozess (`auftrag_fahren`, ohnehin abgekoppelt vom
Server) den Retarget für die VORGABEHÖHE — die Studio und Ergebnisseite ohne
eigene Figurhöhe nehmen — als letzten Schritt für jedes BVH des Auftrags
(Körper, Gesicht, Hände, weitere Personen) und legt die Ablage neben das BVH
UND neben seine Bibliothekskopie (gleicher Hash, der Name hängt nur am Stamm).
Der Auftrag meldet solange „Bewegung wird umgesetzt …" und steht erst danach
auf „Complete". Scheitert die Rechnung, bleibt der Auftrag trotzdem fertig —
dann rechnet wie früher der erste Abruf.
"""

import logging
import os
import shutil
from pathlib import Path

logger = logging.getLogger('core')


class Retargetvorrat:
    @staticmethod
    def hoehe():
        from ..api.retarget import Retargetendpunkte

        return Retargetendpunkte.VORGABE_GROESSE

    @classmethod
    def dateien(cls, job):
        """`[(bvh_pfad, kennung_der_kopie)]` — Körper, Gesicht, Hände, Personen."""
        from ..pipelines.personenergebnisse import Personenergebnisse

        paare = [
            (job.bvh_file, job.pipeline),
            (job.bvh_file_face, job.pipeline + '_face'),
            (job.bvh_file_hands, job.pipeline + '_hands'),
        ]
        for pfad in job.bvh_file_personen or []:
            paare.append((pfad, '%s_p%d' % (job.pipeline, Personenergebnisse.nummer(pfad))))
        return [(pfad, kopie) for pfad, kopie in paare if pfad and os.path.isfile(pfad)]

    @classmethod
    def anlegen(cls, job, melden=None):
        """Den Retarget je BVH rechnen und ablegen; Rückgabe: die Ablagen.

        `melden(text)` zeigt den Zwischenstand (Auftrag: `progress_detail`).
        """
        from .ergebnisablage import Ergebnisablage
        from .retargetdaten import Retargetdaten

        hoehe = cls.hoehe()
        abgelegt = []
        for pfad, kennung in cls.dateien(job):
            if melden:
                melden('Bewegung wird umgesetzt (%s) …' % os.path.basename(pfad))
            try:
                daten = Retargetdaten(pfad, hoehe)
                ergebnis = daten.holen()
                abgelegt.append(daten.ablage)
                kopie = Ergebnisablage.pfad(job.name, kennung)
                if kopie.is_file():
                    ziel = Retargetdaten(str(kopie), hoehe).ablage
                    if not os.path.isfile(ziel):
                        shutil.copy2(daten.ablage, ziel)
                    abgelegt.append(ziel)
                logger.info(
                    'Retargetvorrat %s: %s (%s Bilder) -> %d Ablage(n)',
                    job.kennung,
                    os.path.basename(pfad),
                    # `holen()` liefert `Bewegungsspuren`, kein Dictionary mehr — das
                    # `.get` warf nach der fertigen Ablage und meldete „nicht gerechnet"
                    # (Auftrag 2026.09.24.13.39.32, 24.09.2026).
                    ergebnis.frame_count,
                    len(abgelegt),
                )
            except Exception:  # noqa: BLE001
                logger.warning(
                    'Retargetvorrat %s: %s nicht gerechnet — der erste Abruf rechnet',
                    job.kennung,
                    pfad,
                    exc_info=True,
                )
        return [Path(p) for p in abgelegt]
