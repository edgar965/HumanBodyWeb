# -*- coding: utf-8 -*-
"""Mesh3daiwege — mehrere Wege zum Rig derselben Probe auf der Jobseite von Mesh3D-AI (16.10.2026, Job UrsulaSpagat).

Edgar zur Seite `/mesh-3D-AI/ursulaspagat/`: „ist ja noch sehr schlecht, sowohl das Rig bei dem Mesh ist falsch als das Ergebnis" — die Seite zeigte nur, was das Netz direkt auf der Spagat-Pose
liefert (280,5 mm), nicht die Vorstufe, die er vorgeschlagen hatte (Rig → Netz in die A-Pose → Netz). `ProjektTemp/_wegwerf/mesh3dai_spagat_wege.py` rechnet je Weg die 138 Gelenke und die
Drehungen der Daz-Winkel (dieselbe Anpassung wie beim Netz, damit die Seite die Figur wie das Ziel häuten kann) und legt sie in den Ordner DES LAUFS, dessen Netz sie benutzen:
    wege.npz   nr (P,), <schlüssel>_rig (P, 138, 3), <schlüssel>_dreh (P, 138, 3, 3)
    wege.json  {fassung, lauf, standard, ablage, wege: [{schluessel, name, text}], proben: {nr: {schlüssel: {mm, …}}}}
Jeder neue Lauf der Kette legt die vorige Fassung als `wege_vor_<Zeit>.json/.npz` daneben. Seit 18.10.2026 abends (Edgar: „mach das auswählbar …, über welche Methode das Aufrichten in A-Pose geht,
mit Mesh-3D oder MIA“) zeigt die Seite die jüngste Fassung DER Methode, die unter Einstellungen → Mesh3D-AI gewählt ist (`Mesh3daiaposewahl`: MeshToRigToPose_MIA oder MeshToRigToPose; welche
Methode rechnete, steht in `kette.json` der Ablage) — ohne neuen Lauf. Hat ein Job keinen Lauf der gewählten Methode, zeigt sie den jüngsten und sagt es (`fehlt`). Namen der Wege kommen aus der
Methode (ältere Dateien hießen bei beiden „Rig → A-Pose → Netz“).
Fehlt eine der Dateien, ist die Fassung eine andere oder passt die Form nicht, gibt es keine Wege (Warnung im Log) — die Seite zeigt dann den Lauf wie bisher.
"""

import json
import logging
from pathlib import Path

import numpy as np

from .mesh3daiaposewahl import Mesh3daiaposewahl

logger = logging.getLogger('core')

__all__ = ['Mesh3daiwege']


class Mesh3daiwege:
    NPZ = 'wege.npz'
    JSON = 'wege.json'
    #: Fassung der Ablage; eine andere wird nicht gezeigt (`artefakte-benennen.md`).
    FASSUNG = 1

    @staticmethod
    def _json(pfad):
        try:
            return json.loads(Path(pfad).read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            return None

    @classmethod
    def fassungen(cls, lauf):
        """[(JSON-Datei, kette)] des Laufs, jüngste zuerst: `wege.json`, dann die Sicherungen nach der Zeit im Namen — nur mit passender `.npz` daneben."""
        lauf = Path(lauf)
        dateien = [lauf / cls.JSON] + sorted(lauf.glob('wege_vor_*.json'), key=lambda p: p.name, reverse=True)
        aus = []
        for datei in dateien:
            if not datei.is_file() or not datei.with_suffix('.npz').is_file():
                continue
            ablage = (cls._json(datei) or {}).get('ablage')
            aus.append((datei, (cls._json(Path(ablage) / 'kette.json') if ablage else None) or {}))
        return aus

    @classmethod
    def gewaehlt(cls, lauf):
        """(JSON-Datei, kette, fehlt) — die jüngste Fassung der eingestellten Methode; bei „aus“ die jüngste überhaupt; ohne Lauf der Methode die jüngste mit `fehlt` True. None ohne Wege."""
        alle = cls.fassungen(lauf)
        if not alle:
            return None
        wahl = Mesh3daiaposewahl.gewaehlt()
        if wahl == 'aus':
            return (*alle[0], False)
        for datei, kette in alle:
            if Mesh3daiaposewahl.passt(wahl, kette):
                return datei, kette, False
        logger.warning('Mesh3daiwege: %s hat keinen Lauf von %s — gezeigt wird der jüngste (%s)', lauf, Mesh3daiaposewahl.NAMEN[wahl], alle[0][0].name)
        return (*alle[0], True)

    @classmethod
    def stand(cls, lauf):
        """Stempel der gezeigten Fassung und der Einstellung „Zwischenschritt A-Pose“ (für die Ablage von `Mesh3daidaten`) — None ohne Wege."""
        g = cls.gewaehlt(lauf)
        if g is None:
            return None
        try:
            return (g[0].name, g[0].stat().st_mtime_ns, g[0].with_suffix('.npz').stat().st_mtime_ns, Mesh3daiaposewahl.gewaehlt())
        except OSError:
            return None

    @classmethod
    def _benennen(cls, w, kette):
        """Name und Text eines Wegs nach der Methode, die ihn rechnete."""
        name = Mesh3daiaposewahl.name_des_laufs(kette)
        if w['schluessel'] == 'vorstufe':
            text = w.get('text', '')
            # Seit 18.10.2026 abends nennt die Kette die Methode selbst im Text (`mesh3dai_vorstufe.py`, `wege`); ältere Texte bekommen sie vorangestellt.
            return '%s → Netz' % name, text if Mesh3daiaposewahl.NAMEN[Mesh3daiaposewahl.methode(kette)] in text else '%s. %s' % (name, text)
        if w['schluessel'] == 'rig':
            return 'Rig allein (%s)' % Mesh3daiaposewahl.NAMEN[Mesh3daiaposewahl.methode(kette)], w.get('text', '')
        return w.get('name', w['schluessel']), w.get('text', '')

    @classmethod
    def lesen(cls, lauf, knochen):
        """`{standard, methode, fehlt, datei, wege: [{schluessel, name, text}], proben: {nr: {schluessel: (rig (138, 3), dreh (138, 3, 3))}}}` oder None."""
        g = cls.gewaehlt(lauf)
        if g is None:
            return None
        datei, kette, fehlt = g
        try:
            bericht = json.loads(datei.read_text(encoding='utf-8'))
            if int(bericht.get('fassung', 0)) != cls.FASSUNG:
                logger.warning('Mesh3daiwege: %s hat Fassung %s statt %s — keine Wege', datei, bericht.get('fassung'), cls.FASSUNG)
                return None
            wege = [w for w in bericht['wege'] if w.get('schluessel')]
            proben = {}
            with np.load(datei.with_suffix('.npz')) as d:
                nummern = [int(x) for x in d['nr']]
                for w in wege:
                    rig, dreh = d['%s_rig' % w['schluessel']], d['%s_dreh' % w['schluessel']]
                    if rig.shape != (len(nummern), knochen, 3) or dreh.shape != (len(nummern), knochen, 3, 3):
                        logger.warning('Mesh3daiwege: %s, Weg %s hat die Form %s / %s — keine Wege', datei.with_suffix('.npz'), w['schluessel'], rig.shape, dreh.shape)
                        return None
                    for i, nr in enumerate(nummern):
                        proben.setdefault(nr, {})[w['schluessel']] = (rig[i].astype(float), dreh[i].astype(float))
            standard = bericht.get('standard') if bericht.get('standard') in {w['schluessel'] for w in wege} else wege[0]['schluessel']
            # 18.10.2026: Einstellungen → Mesh3D-AI, „Zwischenschritt A-Pose“ = aus → zuerst das Netz direkt auf der Pose (`Mesh3daiaposewahl`).
            if Mesh3daiaposewahl.gewaehlt() == 'aus' and any(w['schluessel'] == 'direkt' for w in wege):
                standard = 'direkt'
        except (OSError, KeyError, ValueError, IndexError) as fehler:
            logger.warning('Mesh3daiwege: %s nicht lesbar (%s) — keine Wege', datei, fehler)
            return None
        benannt = []
        for w in wege:
            name, text = cls._benennen(w, kette)
            benannt.append({'schluessel': w['schluessel'], 'name': name, 'text': text})
        return {'standard': standard, 'methode': Mesh3daiaposewahl.name_des_laufs(kette), 'fehlt': fehlt, 'datei': datei.name, 'wege': benannt, 'proben': proben}
