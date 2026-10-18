# -*- coding: utf-8 -*-
"""G9bedlamhaut — die BEDLAM-Hauttexturen als Hautsätze von Genesis 9 (17.10.2026).

Edgar, 17.10.2026: „mach alles was offen ist" (Tabelle 12 in `genesis9-alter.md`). Die Texturen (100 Hautfotos, CC-BY-NC-4.0, nur nicht-kommerziell, `SMPL/HERKUNFT.md`) kommen aus dem Ordner, den die SMPL-X-Seite
schon nutzt (`Smplxbedlamdienst`: Fotobraue weg, damit Genesis' Brauen nicht doppelt stehen). Hier wird je Haut einmal je UDIM-Kachel ein Bild gerechnet — über die Abbildung Texel → SMPL-X-UV
(`G9bedlamabbildung`, einmal für alle 100) — und unter der EIGENEN Bibliothek abgelegt:

    <eigene Bibliothek>/Runtime/Textures/BEDLAM/<Schlüssel>/f<Fassung>_<Kachel>.jpg     (2048², JPEG 90)

Der Hautsatz ist der der Grundfigur (`G9 Feminine/Masculine Skin 01 MAT`: Normalen, Rauheit, Durchlicht, Details) mit der BEDLAM-Albedo statt der Daz-Albedo; seine Kennung ist `bedlam:<Schlüssel>`
(am Doppelpunkt erkennbar wie die Charakterhäute). Er steht in der Hautauswahl, in der Texturmischung und in gespeicherten Modellen wie jeder andere. Ohne die Abbildung (`bedlamabbildung_bauen`)
oder ohne den Texturordner erscheint er nicht.
"""
import copy
import logging
import os
import re

import numpy as np
from Genesis9.hautpresets import G9hautpresets

from .g9bedlamabbildung import G9bedlamabbildung

logger = logging.getLogger('core')

__all__ = ['G9bedlamhaut']


class G9bedlamhaut:
    """Anbieter von Hautsätzen für `G9hautpresets` (`anbieten`)."""

    PRAEFIX = 'bedlam:'
    #: 2: ohne die aufgemalte Unterwäsche (17.10.2026); 3: Regel für das Olivgrün nach der Messung der Farbe; 4: auch die graue Boxershorts der Männer, erkannt an den fertigen Körperkacheln.
    FASSUNG = 4
    QUALITAET = 90
    #: Materialgruppen der Haut; ihre Kachel steht im Netz (`gruppen[*].kachel`).
    GRUPPEN = ('Head', 'Body', 'Arms', 'Legs')
    GRUND = {'female': 'G9 Feminine Skin 01 MAT', 'male': 'G9 Masculine Skin 01 MAT'}
    _SCHLUESSEL = re.compile(r'^skin_(f|m)_[a-z]+_\d+_ALB$')

    # ------------------------------------------------------------- Quellen

    @staticmethod
    def _basis():
        from django.conf import settings
        return str(settings.SMPLX_BEDLAM_DIR)

    @classmethod
    def verfuegbar(cls):
        """Gibt es Abbildung UND Texturordner?"""
        return G9bedlamabbildung.vorhanden() and os.path.isdir(cls._basis())

    @classmethod
    def gehoert(cls, preset):
        return str(preset or '').startswith(cls.PRAEFIX)

    @staticmethod
    def _geschlecht(schluessel):
        return 'male' if schluessel.startswith('skin_m_') else 'female'

    @classmethod
    def praesets(cls):
        """`[{id, name, geschlecht, vorschau}]` für die Hautauswahl — leer ohne Abbildung/Ordner."""
        if not cls.verfuegbar():
            return []
        from SMPL.xbedlamhaut import Smplxbedlamhaut
        aus = []
        for geschlecht, anzeige in (('female', 'weiblich'), ('male', 'männlich')):
            for e in Smplxbedlamhaut.liste(cls._basis(), geschlecht):
                aus.append({'id': cls.PRAEFIX + e['schluessel'], 'name': 'BEDLAM · %s (%s)' % (e['name'], anzeige), 'geschlecht': anzeige, 'vorschau': False})
        return aus

    # ---------------------------------------------------------------- Bilder

    @classmethod
    def bilder(cls, preset):
        """Die Bilder des Hautsatzes je Gruppe (wie `G9hautpresets.haut`) — oder {}."""
        schluessel = str(preset)[len(cls.PRAEFIX):]
        if not cls.verfuegbar() or not cls._SCHLUESSEL.match(schluessel):
            return {}
        geschlecht = cls._geschlecht(schluessel)
        kacheln = cls.kacheln(geschlecht, schluessel)
        if not kacheln:
            return {}
        aus = copy.deepcopy(G9hautpresets.haut(cls.GRUND[geschlecht]))
        for gruppe, kachel in cls._kachel_je_gruppe().items():
            if gruppe in aus and kachel in kacheln:
                aus[gruppe]['albedo'] = kacheln[kachel]
        return aus

    @classmethod
    def _kachel_je_gruppe(cls):
        from Genesis9.basisnetz import G9basisnetz
        return {g['name']: int(g['kachel']) for g in G9basisnetz.netzstufe(0).gruppen if g.get('name') in cls.GRUPPEN}

    @classmethod
    def _ordner(cls, schluessel):
        from Genesis9.pfade import G9pfade
        return G9pfade.eigene() / 'Runtime' / 'Textures' / 'BEDLAM' / schluessel

    @classmethod
    def kacheln(cls, geschlecht, schluessel):
        """`{kachel: Pfad relativ zur eigenen Bibliothek}` — baut fehlende Kacheln (einmal je Haut, ~10 s)."""
        ordner = cls._ordner(schluessel)
        namen = {k: ordner / ('f%d_%d.jpg' % (cls.FASSUNG, k)) for k in set(cls._kachel_je_gruppe().values())}
        if not all(p.is_file() for p in namen.values()):
            try:
                cls._bauen(geschlecht, schluessel, namen)
            except Exception:                                           # noqa: BLE001 — eine Haut, die nicht geht, darf die Auswahl nicht sprengen
                logger.exception('BEDLAM-Haut %s nicht gebaut', schluessel)
                return {}
        return {k: 'Runtime/Textures/BEDLAM/%s/%s' % (schluessel, p.name) for k, p in namen.items()}

    @classmethod
    def _quelle(cls, geschlecht, schluessel):
        """Die Textur in SMPL-UV, Fotobraue weg (wie bei SMPL-X) — sonst das Rohfoto."""
        from SMPL.xbedlamhaut import Smplxbedlamhaut
        try:
            from .smplxbedlamdienst import Smplxbedlamdienst
            pfad = Smplxbedlamdienst.textur_pfad(geschlecht, schluessel)
            if pfad:
                return pfad
        except Exception:                                               # noqa: BLE001 — ohne eigenes Foto/Modell geht der Weg nicht, das Rohfoto bleibt
            logger.warning('BEDLAM-Haut %s: Fotobraue nicht entfernt (Rohfoto)', schluessel, exc_info=True)
        return Smplxbedlamhaut.pfad(cls._basis(), geschlecht, schluessel)

    #: Die Fotos tragen eine aufgemalte olivgrüne Unterwäsche (BEDLAM-Körper sind nie nackt, gesehen 17.10.2026 an `skin_f_white_01`: Farbe (123, 117, 77), 8 % des Fotos; Haut hat Rot
    #: mindestens 40 über Grün, Haar auch). Olivgrün heißt: Rot höchstens `ROT_UEBER_GRUEN` über Grün und Blau mehr als `BLAU_UNTER_GRUEN` unter Grün. Maske samt Rand (`RAND`),
    #: gefüllt aus der Umgebung (Telea, auf `KLEIN` Pixel gerechnet — in einem grossen Loch zählt nur der Farbverlauf, kein Detail).
    ROT_UEBER_GRUEN = 12
    BLAU_UNTER_GRUEN = 25
    #: Die männlichen Fotos tragen eine GRAUE Boxershorts mit Schriftzug (gesehen 17.10.2026 am Genesis-Körper, `skin_m_white_01`): kaum Buntheit — Haut hat zwischen größtem und kleinstem
    #: Kanal mindestens 40 (hellste Haut 239/196/162: 77).
    GRAU_BUNTHEIT = 30
    RAND = 4
    KLEIN = 1024
    #: Nur Kopf (1001) behält sein Foto: dort stehen Augen, Zähne, Brauen und das aufgemalte Haar, die „grau" aussehen und bleiben sollen.
    KOPFKACHEL = 1001

    @classmethod
    def ohne_unterwaesche(cls, foto):
        """Das Bild (H, W, 3) uint8 ohne die aufgemalte Unterwäsche (olivgrün bei den Frauen, grau bei den Männern); ohne solche Pixel unverändert."""
        import cv2
        g = foto.astype(np.int16)
        olive = (g[..., 0] - g[..., 1] < cls.ROT_UEBER_GRUEN) & (g[..., 1] - g[..., 2] > cls.BLAU_UNTER_GRUEN)
        grau = (g.max(axis=2) - g.min(axis=2)) < cls.GRAU_BUNTHEIT
        maske = (olive | grau).astype(np.uint8) * 255
        if not maske.any():
            return foto
        maske = cv2.morphologyEx(maske, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        maske = cv2.dilate(maske, np.ones((5, 5), np.uint8), iterations=cls.RAND)
        h, b = foto.shape[:2]
        klein = cv2.resize(foto, (cls.KLEIN, cls.KLEIN), interpolation=cv2.INTER_AREA)
        mklein = cv2.resize(maske, (cls.KLEIN, cls.KLEIN), interpolation=cv2.INTER_NEAREST)
        gefuellt = cv2.resize(cv2.inpaint(klein, mklein, 8, cv2.INPAINT_TELEA), (b, h), interpolation=cv2.INTER_CUBIC)
        a = (cv2.GaussianBlur(maske, (0, 0), 3).astype(np.float32) / 255.0)[..., None]
        return np.clip(foto * (1.0 - a) + gefuellt * a + 0.5, 0, 255).astype(np.uint8)

    @classmethod
    def _bauen(cls, geschlecht, schluessel, namen):
        from PIL import Image
        from scipy import ndimage

        abbildung = G9bedlamabbildung.holen()
        quelle = cls._quelle(geschlecht, schluessel)
        if not abbildung or not quelle:
            raise FileNotFoundError('BEDLAM-Abbildung oder Textur fehlt')
        foto = np.asarray(Image.open(quelle).convert('RGB'), dtype=np.float32)
        h, b = foto.shape[:2]
        from Genesis9.texturabtastung import G9texturabtastung
        abtastung = G9texturabtastung.holen(G9bedlamabbildung.SEITE)
        os.makedirs(cls._ordner(schluessel), exist_ok=True)
        for kachel, ziel in namen.items():
            drin = abtastung.dreieck[kachel] >= 0
            uv = abbildung[kachel][drin]
            y = (1.0 - uv[:, 1]) * (h - 1)
            x = uv[:, 0] * (b - 1)
            bild = np.zeros(drin.shape + (3,), dtype=np.float32)
            for k in range(3):
                bild[drin, k] = ndimage.map_coordinates(foto[..., k], [y, x], order=1, mode='nearest')
            _w, (iy, ix) = ndimage.distance_transform_edt(~drin, return_indices=True)
            bild = np.clip(bild[iy, ix] + 0.5, 0, 255).astype(np.uint8)  # außerhalb der Inseln die Farbe des nächsten Texels — das Filtern zieht kein Schwarz herein
            if kachel != cls.KOPFKACHEL:
                bild = cls.ohne_unterwaesche(bild)
            neu = ziel.with_name(ziel.stem + '.neu.jpg')
            Image.fromarray(bild).save(neu, quality=cls.QUALITAET)
            os.replace(neu, ziel)
            logger.info('BEDLAM-Haut %s Kachel %d gebaut: %s', schluessel, kachel, ziel)


G9hautpresets.anbieten(G9bedlamhaut)         # beim ersten Import als Anbieter von Hautsätzen eintragen
