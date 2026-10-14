# -*- coding: utf-8 -*-
"""Meshfighaltung — die Figur in der Haltung des Netzes statt der Stoff in der Ruhelage der Figur (13.10.2026).

Anlass (Edgar, Zauberer): die Robe sieht in der A-Pose fächerförmig verzerrt aus. Ursache: `Meshfigurkleidungsruhelage` rechnet jeden Stoffpunkt über die Käfigpunkte in seiner Nähe zurück in die Ruhelage; das setzt voraus, dass der Stoff dem
Körper folgt — lose Kleidung (Robe, Umhang) tut es nicht (Literatur und Messung: `mesh-3d-bestandteile.md`). Der andere Weg, hier gebaut: nichts zurückrechnen. Die Figur selbst steht in der Haltung des Netzes, und der Stoff, die Bestandteile und das
Haar aus dem Netz bleiben, wie sie sind — nur in den Raum der gebackenen Figur verschoben (eine starre Bewegung).

Der Server backt eine Haltung, wenn der Rumpf der Netzanfrage `drehung` trägt (`G9figur.formung`: `{knochen: {'rotation/x': Grad, …}}`, dieselbe Form wie ein Posenpreset). WELCHE Haltung: die der Anpassung, gelesen aus `arbeit/zustand.npz`
(`theta` je freiem Knochen), NICHT `ergebnis.koerper.haltung` — die steht nach der Körper- und Gesichtskette und ist nicht die, mit der `posiert.npy` entstand: die Nachhaltung in „bewertung" passt die Winkel an die Endfigur an (am Zauberer bis 47,8°
Unterschied; Rest zu `posiert.npy` 29,0 mm RMS mit `ergebnis.koerper.haltung`, 2,3 mm RMS mit `zustand.npz`, Median 0,02 mm; `ProjektTemp/_wegwerf/mesh3d/haltung_probe2.py`).

Die gebackene Figur steht mit den Füßen auf 0 und ohne Lage der Registrierung (`rg`, `tg`); `posiert.npy` hat sie. Die starre Bewegung dazwischen (Kabsch, ohne Maßstab, die schlechtesten 20 % der Punkte aus dem Rest — Finger, Gelenkkorrekturen) liegt in
`arbeit/haltung_lage.npz` (`r`, `t`: Netz ≈ gebacken @ r.T + t), `punkte` bringt Netzpunkte in den Raum der gebackenen Figur: `(p − t) @ r`. Gilt nur, wenn der Rest klein ist (`MAX_RMS_MM`); sonst steht der Grund in `ergebnis.haltung` und die Bühne
bietet den Schalter nicht an. Ergebnis: `ergebnis.haltung = {gueltig, drehung, rest_rms_mm, …}`.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfighaltung']


class Meshfighaltung:
    DATEI = 'haltung_lage.npz'
    #: Setzung (nicht gemessen als Grenze): ab diesem Rest in mm RMS passen gebackene Figur und Netz nicht mehr zusammen — der Zauberer liegt bei 2,3.
    MAX_RMS_MM = 10.0
    #: Ausrichtung: Anteil der Punkte mit dem kleinsten Rest, der die späteren Durchgänge bestimmt, und Zahl der Durchgänge.
    ANTEIL = 0.8
    DURCHGAENGE = 3

    def __init__(self, r, t):
        """`r` (3, 3), `t` (3,): Netz ≈ gebackene Figur @ r.T + t."""
        self.r = np.asarray(r, dtype=np.float64)
        self.t = np.asarray(t, dtype=np.float64)

    def punkte(self, netz):
        """(M, 3) — Punkte des Netzes (Lage der Erkennung, Meter) im Raum der gebackenen Figur."""
        return (np.asarray(netz, dtype=np.float64) - self.t) @ self.r

    # ------------------------------------------------------------- Rechnung

    @staticmethod
    def drehung_aus(theta, frei, namen):
        """`{knochen: {'rotation/x': Grad, …}}` aus den Winkeln der Anpassung (`theta` (K, 3) Grad je freiem Knochen, `frei` (K,) Knochennummern, `namen` Knochennamen) — wie `Meshfigurregistrierungruhe.haltung`."""
        aus = {}
        for i, nummer in enumerate(frei):
            werte = {'rotation/%s' % achse: round(float(theta[i, k]), 3) for k, achse in enumerate('xyz') if abs(theta[i, k]) > 1e-3}
            if werte:
                aus[str(namen[int(nummer)])] = werte
        return aus

    @staticmethod
    def _kabsch(quelle, ziel):
        mq, mz = quelle.mean(0), ziel.mean(0)
        u, _, vt = np.linalg.svd((quelle - mq).T @ (ziel - mz))
        vorzeichen = np.sign(np.linalg.det(vt.T @ u.T))
        r = vt.T @ np.diag([1.0, 1.0, vorzeichen]) @ u.T
        return r, mz - mq @ r.T

    @classmethod
    def ausrichten(cls, quelle, ziel):
        """`(r, t, abstand)` — starr, ohne Maßstab: `ziel ≈ quelle @ r.T + t`; `abstand` (N,) in Metern über ALLE Punkte. Der erste Durchgang nimmt alle Punkte, die weiteren nur die `ANTEIL` besten (Finger und Gelenkkorrekturen ziehen sonst an der Lage)."""
        quelle, ziel = np.asarray(quelle, dtype=np.float64), np.asarray(ziel, dtype=np.float64)
        r, t = cls._kabsch(quelle, ziel)
        for _ in range(cls.DURCHGAENGE - 1):
            abstand = np.linalg.norm(quelle @ r.T + t - ziel, axis=1)
            gut = abstand <= np.quantile(abstand, cls.ANTEIL)
            r, t = cls._kabsch(quelle[gut], ziel[gut])
        return r, t, np.linalg.norm(quelle @ r.T + t - ziel, axis=1)

    @classmethod
    def rechnen(cls, lauf):
        """Die Haltung dieses Laufs bestimmen und `ergebnis.haltung` + `arbeit/haltung_lage.npz` schreiben; gibt das Ergebnis-Dict zurück. Erst im Schritt „vorschau": dann gehören `zustand.npz`, `genesis_ende.npz` und `posiert.npy` zur aktuellen Figur."""
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung

        job, ablage = lauf.job, lauf.ablage
        zustand, ende, posiert = ablage.arbeit('zustand.npz'), ablage.arbeit('genesis_ende.npz'), ablage.arbeit('posiert.npy')
        stellung = job.stellung()
        if not (zustand.is_file() and ende.is_file() and posiert.is_file() and stellung):
            job.ergebnis['haltung'] = {'gueltig': False, 'grund': 'Zustand der Anpassung, Figur oder Regler fehlen'}
            return job.ergebnis['haltung']
        with np.load(zustand) as z:
            theta = np.asarray(z['theta'], dtype=np.float64)
        with np.load(ende) as d:
            frei, namen = np.asarray(d['frei']), [str(n) for n in d['knochen']]
        if len(theta) != len(frei):
            job.ergebnis['haltung'] = {'gueltig': False, 'grund': 'Zustand (%d Knochen) und Figur (%d freie Knochen) passen nicht zusammen' % (len(theta), len(frei))}
            return job.ergebnis['haltung']
        drehung = cls.drehung_aus(theta, frei, namen)
        # Genau der Weg der Netzanfrage des Browsers (`G9figur.formung` → `G9koerpernetz`): Regler begrenzt, Haltung gebacken, Füße auf 0.
        punkte, _, _ = G9reglerableitung.lage(G9formung.aus_abfrage(dict(stellung), drehung))
        r, t, abstand = cls.ausrichten(punkte, np.load(posiert))
        mm = abstand * 1000.0
        rms = float(np.sqrt((mm ** 2).mean()))
        gueltig = rms <= cls.MAX_RMS_MM
        np.savez(ablage.arbeit(cls.DATEI), r=r, t=t)
        job.ergebnis['haltung'] = {
            'gueltig': bool(gueltig),
            'quelle': 'zustand.npz',
            'drehung': drehung,
            'knochen': len(drehung),
            'rest_rms_mm': round(rms, 2),
            'rest_p95_mm': round(float(np.quantile(mm, 0.95)), 2),
            'rest_max_mm': round(float(mm.max()), 1),
            'verschiebung_m': [round(float(x), 4) for x in t],
            'drehwinkel_grad': round(float(np.degrees(np.arccos(np.clip((np.trace(r) - 1.0) / 2.0, -1.0, 1.0)))), 2),
        }
        if not gueltig:
            job.ergebnis['haltung']['grund'] = 'Die gebackene Figur liegt %.1f mm RMS neben der angepassten (Grenze %.0f mm)' % (rms, cls.MAX_RMS_MM)
            logger.warning('Mesh to 3D %s: Haltung des Netzes nicht angeboten — %s', job.kennung, job.ergebnis['haltung']['grund'])
        return job.ergebnis['haltung']

    @classmethod
    def holen(cls, lauf):
        """Die Bewegung Netz → gebackene Figur dieses Laufs, oder None (keine gültige Haltung)."""
        if not (lauf.job.ergebnis.get('haltung') or {}).get('gueltig'):
            return None
        pfad = lauf.ablage.arbeit(cls.DATEI)
        if not pfad.is_file():
            return None
        with np.load(pfad) as d:
            return cls(d['r'], d['t'])
