# -*- coding: utf-8 -*-
"""Mesh3dairig — das volle Genesis-9-Skelett von Ursula1 in echten Posen, für die Seite „Mesh3D-AI" (14.10.2026).

Edgar: „ich möchte das volle Skelett mit allen Gesichts- und Handknochen" und „Rig soll ein Toggle-Button sein für alle Ansichten". Das Ziel des Netzes ist ein Genesis-Rig; hier steht es mit seinen 138 Knochen
(Becken bis Zehen, 76 Finger-, 47 Gesichtsknochen mit Kiefer, Lippen, Brauen, Lidern, Augen; ohne die Endpunkte) in echten Posen: `Retargetdaten` (BVH → Genesis 9, derselbe Kern wie Studio und Mesh-3D) und `G9tanzhaut`
(Weltmatrizen der Knochen aus Bauplan und Bewegungsspuren) auf der Stellung von `Ursula1` (`figur.regler`). Gemessen am 14.10.2026: Retarget einer Bewegung 0,7 s, 125 Bilder Matrizen 0,4 s.

Aus den Knochenpunkten leitet die Seite ihre Dummy-Flächen ab: 22 Gelenke für die Kapseln (`ZUORDNUNG`), Drehungen für Gesicht, Hände und Füße (Kopf aus der echten Knochendrehung, Hand und Fuß aus Punkten), und die
Rig-Punkte je Zeile (`zeilen`: Gesicht auf die Kopfmitte, Hände und Füße in ihre Ausschnitte, die übrigen in der Weltlage). Die „Ausgabe des Netzes" ist weiter Soll plus Rauschen — nichts ist trainiert.

    Mesh3dairig.beschreibung()                  -> {modell, knochen: [{name, eltern, gruppe}], zeilen: {schluessel: [Index…]}}
    Mesh3dairig.ruhe()                          -> Pose der A-Haltung (Genesis-Ruhelage)
    Mesh3dairig.bewegung(datei)                 -> Bewegung (Anzahl Bilder, `pose(bild)`) — Retarget einmal je Datei
    Mesh3dairig.ausrichten(pose, …)             -> Pose mit Blick nach +Z, in der Mitte, Füße auf dem Boden
"""

import math
from pathlib import Path

import numpy as np

from .mesh3daigeruest import Mesh3daigeruest

__all__ = ['Mesh3dairig']


class Mesh3dairig:
    MODELL = 'Ursula1'
    #: Modelldatei statt `HUMANBODY_MODELS_DIR/<MODELL>.json` (16.10.2026: Formvarianten des Mesh3D-AI-Trainings liegen als `3DObjects/mesh3dai/<Form…>/modell.json`, nie in HumanBody/data).
    #: Nur die Datenskripte setzen sie; der Server rechnet weiter mit `MODELL`.
    MODELL_DATEI = None
    #: Körperhöhe für den Retarget (m): Kopfknochen der Ruhelage 1,52 m + Kopf; nicht gemessen an einer Figur, nur gesetzt.
    HOEHE_M = 1.73
    #: Gelenk des Dummy-Gerüsts → Knochen des Genesis-Skeletts. „Scheitel" fehlt (Kopf + `SCHEITEL_M` in Richtung Hals → Kopf).
    ZUORDNUNG = {
        'Becken': 'hip', 'Bauch': 'spine2', 'Brust': 'spine4', 'Hals': 'neck1', 'Kopf': 'head',
        'Schulter L': 'l_upperarm', 'Ellbogen L': 'l_forearm', 'Handgelenk L': 'l_hand', 'Hand L': 'l_mid1',
        'Schulter R': 'r_upperarm', 'Ellbogen R': 'r_forearm', 'Handgelenk R': 'r_hand', 'Hand R': 'r_mid1',
        'Hüfte L': 'l_thigh', 'Knie L': 'l_shin', 'Knöchel L': 'l_foot', 'Fuß L': 'l_toes',
        'Hüfte R': 'r_thigh', 'Knie R': 'r_shin', 'Knöchel R': 'r_foot', 'Fuß R': 'r_toes',
    }
    SCHEITEL_M = 0.21
    #: Mitte des Kopfes über dem Kopfknochen (m, im Rahmen des Kopfes) — die Mitte des Kopf-Ellipsoids der Gesichtszeile.
    KOPFMITTE_M = (0.0, 0.09, 0.0)
    #: Gruppen je Knochen (Namensregeln, Reihenfolge zählt).
    #: Das Gesicht steht VOR den Fingern („liplowermiddle" enthält „mid") und das Ohr heißt `_ear` („forearm" enthält „ear") — an den 138 Namen geprüft (`gruppen_zaehlen`).
    GRUPPEN = (
        ('zehen', ('toe',)), ('gesicht', ('teeth', 'jaw', 'facerig', 'lip', 'cheek', 'chin', 'brow', 'eyelid', 'squint', 'nostril', 'infraorbital', 'eye', '_ear')),
        ('finger', ('thumb', 'index', 'mid', 'ring', 'pinky')), ('hand', ('_hand',)), ('fuss', ('_foot', 'metatarsal')), ('arm', ('shoulder', 'arm')), ('bein', ('thigh', 'shin')),
        ('kopf', ('neck', 'head')), ('rumpf', ('hip', 'pelvis', 'spine', 'pectoral')),
    )
    #: Welche Gruppen welche Zeile zeigt (`None` = alle). Gesicht und Hände/Füße werden in ihren Ausschnitt gerückt (`zeilen`).
    ZEILEN = {
        'koerper': None, 'koerper_nackt': None, 'kleider': ('rumpf', 'arm', 'bein', 'kopf'),
        'gesicht': ('kopf', 'gesicht'), 'haende': ('hand', 'finger', 'fuss', 'zehen'),
    }
    #: Rauschen der Ausgabe je Gruppe, als Faktor auf den Pegel der Zeile (Finger, Zehen und Hände streuen mehr, das Gesicht weniger).
    RAUSCHFAKTOR = {'rumpf': 1.0, 'kopf': 1.0, 'gesicht': 0.5, 'arm': 1.6, 'hand': 2.2, 'finger': 2.2, 'bein': 1.5, 'fuss': 2.0, 'zehen': 2.0}
    #: Rot ab so viel mm Fehler (Rig).
    FEHLER_ROT_MM = 30
    _speicher = {}

    # ------------------------------------------------------------------ Skelett

    @classmethod
    def _gruppe(cls, name):
        n = name.lower()
        for gruppe, worte in cls.GRUPPEN:
            if any(w in n for w in worte):
                return gruppe
        return 'rumpf'

    @classmethod
    def _modell(cls):
        """`(Bauplan der Knochen ohne Endpunkte, G9tanzhaut, Formung)` — einmal je Prozess."""
        if 'modell' not in cls._speicher:
            import json

            from django.conf import settings
            from Genesis9.formung import G9formung
            from Genesis9.tanzhaut import G9tanzhaut

            datei = Path(cls.MODELL_DATEI) if cls.MODELL_DATEI else Path(settings.HUMANBODY_MODELS_DIR) / ('%s.json' % cls.MODELL)
            regler = json.loads(datei.read_text(encoding='utf-8'))['figur']['regler']
            formung = G9formung(regler)
            bauplan = formung.skelett().kette().bauplan()
            cls._speicher['modell'] = (G9tanzhaut(bauplan), formung)
        return cls._speicher['modell']

    @classmethod
    def namen(cls):
        return [k['name'] for k in cls._modell()[0].knochen]

    @classmethod
    def beschreibung(cls):
        if 'beschreibung' not in cls._speicher:
            tanz, _f = cls._modell()
            index = {k['name']: i for i, k in enumerate(tanz.knochen)}
            knochen = [{'name': k['name'], 'eltern': index.get(k.get('eltern'), -1), 'gruppe': cls._gruppe(k['name'])} for k in tanz.knochen]
            zeilen = {s: [i for i, k in enumerate(knochen) if g is None or k['gruppe'] in g] for s, g in cls.ZEILEN.items()}
            cls._speicher['beschreibung'] = {'modell': cls.MODELL, 'knochen': knochen, 'zeilen': zeilen, 'fehler_rot_mm': cls.FEHLER_ROT_MM}
        return cls._speicher['beschreibung']

    # ------------------------------------------------------------------ Posen

    @classmethod
    def _pose(cls, matrizen):
        tanz, _f = cls._modell()
        pos = np.array([matrizen[k['name']][:3, 3] for k in tanz.knochen], dtype=float)
        kopf = matrizen['head'][:3, :3] @ tanz.ruhe['head'][:3, :3].T            # Drehung des Kopfes gegen die Ruhelage (Weltraum)
        return {'pos': pos, 'kopf': kopf}

    @classmethod
    def ruhe(cls):
        return cls._pose(cls._modell()[0].ruhe)

    @classmethod
    def bewegung(cls, datei):
        """`(anzahl, pose)` — `pose(bild)` liefert die Rohpose (Weltraum der Retarget-Rechnung); der Retarget läuft einmal je Datei."""
        schluessel = ('bewegung', str(datei))
        if schluessel not in cls._speicher:
            from .retargetdaten import Retargetdaten

            tanz, formung = cls._modell()
            spuren = Retargetdaten(str(datei), body_height=cls.HOEHE_M, ziel=Retargetdaten.ZIEL_G9, formung=formung).holen()
            cls._speicher[schluessel] = (int(spuren.frame_count), lambda bild: cls._pose(tanz.matrizen(spuren, int(bild))))
        return cls._speicher[schluessel]

    @classmethod
    def ausrichten(cls, pose, heading=None, zentrum=None, boden=None):
        """Die Pose mit Blick nach +Z (die linke Seite bei +X), die Hüfte in der Mitte und den Füßen auf dem Boden der Ruhelage. Wer mehrere Bilder zusammen ausrichtet (Bewegung), gibt `heading`, `zentrum`
        (x, z) und `boden` vor (aus Bild 0 bzw. dem Mittel/Minimum der Bewegung); sonst gelten die Werte dieser Pose. Rückgabe `(pose, {heading, zentrum, boden})`."""
        n = cls.namen()
        ix = {k: n.index(k) for k in ('l_thigh', 'r_thigh', 'hip')}
        pos = pose['pos']
        if heading is None:
            links = pos[ix['l_thigh']] - pos[ix['r_thigh']]
            heading = math.atan2(links[2], links[0])
        c, s = math.cos(heading), math.sin(heading)
        r = np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])
        neu = pos @ r.T
        if zentrum is None:
            zentrum = (neu[ix['hip'], 0], neu[ix['hip'], 2])
        neu[:, 0] -= zentrum[0]
        neu[:, 2] -= zentrum[1]
        fuss = cls._fussknochen()
        if boden is None:
            boden = float(neu[fuss, 1].min())
        neu[:, 1] += cls._ruhehoehe() - boden
        return {'pos': neu, 'kopf': r @ pose['kopf']}, {'heading': heading, 'zentrum': zentrum, 'boden': boden}

    @classmethod
    def _fussknochen(cls):
        """Die Knochen von Fuß und Zehen — der tiefste von ihnen steht auf dem Boden (nur die Knöchel zu nehmen ließ Zehen bis 7 cm unter den Boden)."""
        return [i for i, k in enumerate(cls.beschreibung()['knochen']) if k['gruppe'] in ('fuss', 'zehen')]

    @classmethod
    def _ruhehoehe(cls):
        """Höhe des tiefsten Fußknochens in der Ruhelage."""
        if 'ruhehoehe' not in cls._speicher:
            cls._speicher['ruhehoehe'] = float(cls.ruhe()['pos'][cls._fussknochen(), 1].min())
        return cls._speicher['ruhehoehe']

    # ------------------------------------------------------------------ Ableitungen für die Dummy-Flächen

    @classmethod
    def lagen(cls, pose):
        """Die 22 Gelenke des Dummy-Gerüsts (`Mesh3daigeruest.GELENKE`) aus den Knochenpunkten — Scheitel = Kopf + `SCHEITEL_M` in Richtung Hals → Kopf."""
        n = cls.namen()
        pos = pose['pos']
        lagen = np.zeros((len(Mesh3daigeruest.GELENKE), 3))
        for i, (name, _e, _v, _g) in enumerate(Mesh3daigeruest.GELENKE):
            if name in cls.ZUORDNUNG:
                lagen[i] = pos[n.index(cls.ZUORDNUNG[name])]
        kopf, hals, scheitel = (Mesh3daigeruest.index(x) for x in ('Kopf', 'Hals', 'Scheitel'))
        achse = lagen[kopf] - lagen[hals]
        lagen[scheitel] = lagen[kopf] + cls.SCHEITEL_M * achse / max(float(np.linalg.norm(achse)), 1e-9)
        return lagen

    @staticmethod
    def _norm(v):
        return v / max(float(np.linalg.norm(v)), 1e-9)

    @classmethod
    def _senkrecht(cls, richtung, bezug, ersatz):
        r = bezug - np.dot(bezug, richtung) * richtung
        if np.linalg.norm(r) < 1e-3:
            r = ersatz - np.dot(ersatz, richtung) * richtung
        return cls._norm(r)

    @staticmethod
    def _zeilen(spalten):
        return tuple(tuple(float(w) for w in zeile) for zeile in np.stack(spalten, axis=1))

    @classmethod
    def drehungen(cls, lagen, kopf):
        """Die Drehungen von Kopf, Handgelenken und Knöcheln (alle anderen Einheit), wie `Mesh3daigesicht` und `Mesh3daihaende` sie brauchen. Der Kopf ist die echte Drehung des Kopfknochens gegen die
        Ruhelage; Hand und Fuß folgen den Punkten (Unterarm bzw. Schienbein, dazu der Körperblick), nicht den Knochenachsen — die Dummy-Hand hat ihre eigene Achsenwahl."""
        ix = Mesh3daigeruest.index
        punkt = lambda name: np.asarray(lagen[ix(name)], dtype=float)  # noqa: E731
        einheit = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
        r = [einheit] * len(Mesh3daigeruest.GELENKE)
        oben = np.array([0.0, 1.0, 0.0])
        rumpf_hoch = cls._norm(punkt('Brust') - punkt('Becken'))
        rumpf_links = cls._senkrecht(rumpf_hoch, punkt('Hüfte L') - punkt('Hüfte R'), np.array([1.0, 0.0, 0.0]))
        blick = np.cross(rumpf_links, rumpf_hoch)
        r[ix('Kopf')] = tuple(tuple(float(w) for w in zeile) for zeile in kopf)
        for seite, vorzeichen in (('L', 1.0), ('R', -1.0)):
            x = vorzeichen * cls._norm(punkt('Handgelenk ' + seite) - punkt('Ellbogen ' + seite))
            y = cls._senkrecht(x, oben, blick)
            r[ix('Handgelenk ' + seite)] = cls._zeilen([x, y, np.cross(x, y)])
            h = cls._norm(punkt('Knie ' + seite) - punkt('Knöchel ' + seite))
            z = cls._senkrecht(h, blick, rumpf_links)
            r[ix('Knöchel ' + seite)] = cls._zeilen([np.cross(h, z), h, z])
        return r

    @classmethod
    def zeilen(cls, pose):
        """`{Zeile: (n, 3)}` — die Rig-Punkte jeder Zeile in ihrem Koordinatensystem: Körper und Kleider in der Weltlage, das Gesicht um die Kopfmitte, Hände und Füße je um ihren Mittelpunkt in ihrem Ausschnitt."""
        from .mesh3daihaende import Mesh3daihaende

        beschr = cls.beschreibung()
        n = cls.namen()
        pos = pose['pos']
        aus = {}
        for schluessel, indizes in beschr['zeilen'].items():
            p = pos[indizes].copy()
            if schluessel == 'gesicht':
                mitte = pos[n.index('head')] + pose['kopf'] @ np.array(cls.KOPFMITTE_M)
                p = p - mitte
            elif schluessel == 'haende':
                gruppen = {'Hand L': 'l_', 'Hand R': 'r_'}
                teile = [(name, lambda k, s=seite: k.startswith(s) and beschr['knochen'][n.index(k)]['gruppe'] in ('hand', 'finger')) for name, seite in gruppen.items()]
                teile += [('Fuß L', lambda k: k.startswith('l_') and beschr['knochen'][n.index(k)]['gruppe'] in ('fuss', 'zehen')),
                          ('Fuß R', lambda k: k.startswith('r_') and beschr['knochen'][n.index(k)]['gruppe'] in ('fuss', 'zehen'))]
                for name, passt in teile:
                    zeilen = [j for j, i in enumerate(indizes) if passt(n[i])]
                    mitte = p[zeilen].mean(axis=0)
                    platz = Mesh3daihaende.PLAETZE[name]
                    p[zeilen] = p[zeilen] - mitte + np.array([platz[0], platz[1], 0.0])
            aus[schluessel] = p
        return aus
