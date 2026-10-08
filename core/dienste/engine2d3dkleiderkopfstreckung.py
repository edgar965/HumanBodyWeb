# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkopfstreckung — das Kopfnetz senkrecht strecken, bevor die Körper-Kette es einsetzt (08.10.2026, Option `koerper.kopfstreckung`).

Befund (`ProjektTemp/_wegwerf/edgar/kamera_anpassung.py`, Auftrag `…20.52.44`): Legt man die 3D-Landmarken des Hunyuan-Kopfnetzes mit einer schwach perspektivischen Kamera (Drehung frei, Maßstab,
Verschiebung) über die 2D-Landmarken des Fotos, erklärt es das Foto erst mit einer senkrechten Streckung von **1,111** (Rest-RMS 3,37 → 1,89 mm); die Figur braucht 1,115, das Körpernetz-Gesicht ohne
Kopfnetz nur 1,05. In Millimetern stimmen die Breiten (Augenabstand +0,5, Gesichtsbreite +1,3 mm), die Höhen sind zu kurz (Gesichtshöhe −15, Nase–Kinn −16 mm). Warum, ist nicht belegt (Vermutung: das
Vorderfoto sieht das Gesicht von unten, Hunyuan liest es als frontal).

Der Versuch am echten Lauf (Kopie `…10.57.00`, Kopfnetz um 11 % gestreckt, Körper bis Kleiderstücke): Profil-RMS gegen das Seitenfoto 7,49 → 1,72 mm (größte Abweichung 23 → 5 mm), IoU 0,923 → 0,946,
mittlerer Maßfehler gegen das Foto 9,47 → 7,18 %, Gesichtshöhe −9,0 → −1,4 %, Auge–Mund −10,4 → −1,6 %, Regler am Anschlag 10 → 9. Dagegen wurden die Breiten kleiner (Augenabstand −5,6, Gesichtsbreite
−5,7 mm): die Einpassung (`Meshfigurkopfabgleich`, Ähnlichkeit auf die Gesichtspunkte des Körpernetzes) wählt EINEN Maßstab für Breite und Höhe.

Die Streckung geschieht hier, an der Datei, nicht in der Einpassung — deren Code gehört der Registrierung (`Meshfigurkopfabgleich`, andere Sitzung). Aus `kopf/mesh.glb` entsteht `kopf/mesh_gestreckt_<Prozent>.glb`
(Fassung im Namen, `artefakte-benennen.md`); das Original bleibt, die Karte „Kopf" zeigt es weiter. Gestreckt wird um die Mitte der Netzhöhe — die Einpassung verschiebt danach ohnehin.
"""

import logging
import os
from pathlib import Path

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderkopfstreckung']


class Engine2d3dKleiderkopfstreckung:
    #: Mehr als ein Viertel Streckung ist kein Gesicht mehr (der gemessene Wert an Edgars Kopfnetz: 11 %).
    HOECHSTENS = 25.0

    @classmethod
    def faktor(cls, prozent):
        """1 + Prozent/100, begrenzt auf `0 … HOECHSTENS`; unlesbar oder ≤ 0 → 1,0 (keine Streckung)."""
        try:
            wert = float(prozent)
        except (TypeError, ValueError):
            return 1.0
        if not np.isfinite(wert) or wert <= 0:
            return 1.0
        return 1.0 + min(wert, cls.HOECHSTENS) / 100.0

    @classmethod
    def ziel(cls, quelle, prozent):
        """Der Pfad des gestreckten Netzes neben der Quelle: `<Name>_gestreckt_<Zehntelprozent>.glb`."""
        quelle = Path(quelle)
        zehntel = int(round(cls.faktor(prozent) * 1000 - 1000))
        return quelle.with_name('%s_gestreckt_%d.glb' % (quelle.stem, zehntel))

    @classmethod
    def gestreckt(cls, quelle, prozent):
        """Pfad des um `prozent` senkrecht gestreckten Kopfnetzes; ohne Streckung (≤ 0) die Quelle selbst. Ein vorhandenes gestrecktes Netz, das jünger ist als die Quelle, wird weiterverwendet."""
        faktor = cls.faktor(prozent)
        quelle = Path(quelle)
        if faktor == 1.0:
            return quelle
        ziel = cls.ziel(quelle, prozent)
        if ziel.is_file() and ziel.stat().st_mtime_ns >= quelle.stat().st_mtime_ns:
            return ziel
        import trimesh

        szene = trimesh.load(str(quelle), process=False)
        tief, hoch = szene.bounds
        matrix = np.eye(4)
        matrix[1, 1] = faktor
        matrix[1, 3] = float((tief[1] + hoch[1]) / 2) * (1.0 - faktor)
        szene.apply_transform(matrix)
        zwischen = ziel.with_name(ziel.name + '.tmp')
        szene.export(str(zwischen), file_type='glb')
        os.replace(zwischen, ziel)
        logger.info('Kopfnetz um %.1f %% gestreckt: %s → %s', (faktor - 1) * 100, quelle.name, ziel.name)
        return ziel
