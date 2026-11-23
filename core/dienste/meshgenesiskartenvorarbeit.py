# -*- coding: utf-8 -*-
"""Meshgenesiskartenvorarbeit — was die Seite zum Häuten eines Anzeigenetzes auf der Grafikkarte (`Meshgenesiskartenhaut`) sonst selbst über alle Punkte rechnet, einmal beim Bau
des Pakets in den Kopf (24.11.2026, Edgar „fixe“ — lange Bilder beim Laden von /foto-genesis/test/iphone_mit_lidar_dycheck_space_out/).

Gemessen im Chrome (Haar, 2,1 Mio. Punkte, je Laden einmal und darum unoptimiert im Hauptfaden): Prüfung der Gewichtssummen 10,7–36 ms, Läufe gleichen Materials 11–15,5 ms, Kästen je
Knochen für die Hülle 15,8–18,4 ms. Das Paket baut der Server einmal je Stand (`Netzpackung`).

    Meshgenesiskartenvorarbeit.kopf(d) -> dict      {summe255, laeufe, laeufe_letzter, huelle, huelle_probe}

- `summe255`: vier Plätze je Punkt und jede Gewichtssumme genau 255 — dann nimmt die Seite die Felder des Pakets selbst.
- `laeufe` [[erstes Dreieck, Ende, Material], …]: die Dreiecke liegen nach Material (−1 = das Material nach den Bildmaterialien, `laeufe_letzter`), nichts verborgen; sonst None.
- `huelle` [[Knochen, min x, y, z, max x, y, z], …]: Kasten der Ruhepunkte je Knochen über jeden `huelle_probe`-ten Punkt, Knochen −1 = Punkte ohne Gewicht (der Einheitsknochen der
  Seite). Werte sind die float32 der Ruhelage — min und max sind exakt, JSON trägt sie ohne Rundung: dieselben Kästen wie die Schleife der Seite.
"""
import torch

__all__ = ['Meshgenesiskartenvorarbeit']

KARTE = 'cuda'


class Meshgenesiskartenvorarbeit:
    PROBE = 16                       # wie `Meshgenesiskartenhaut.PROBE`

    @classmethod
    def kopf(cls, d):
        aus = {'summe255': cls._summe255(d['gewicht']), 'laeufe': None, 'laeufe_letzter': len(d['materialien'])}
        if not len(d.get('verborgen', ())):
            aus['laeufe'] = cls._laeufe(d['material'], aus['laeufe_letzter'])
        if 'ruhe' in d and 1 <= int(d['knochen'].shape[1]) <= 4:
            aus['huelle'], aus['huelle_probe'] = cls._huelle(d['ruhe'], d['knochen'], d['gewicht']), cls.PROBE
        return aus

    @staticmethod
    def _summe255(gewicht):
        g = torch.as_tensor(gewicht, device=KARTE)
        return int(g.shape[1]) == 4 and bool((g.to(torch.int32).sum(dim=1) == 255).all())

    @staticmethod
    def _laeufe(material, letzter):
        m = torch.as_tensor(material, device=KARTE).to(torch.int64)
        if not len(m):
            return []
        m = torch.where(m < 0, torch.full_like(m, letzter), m)
        if not bool((m[1:] >= m[:-1]).all()):
            return None
        wechsel = (torch.nonzero(m[1:] != m[:-1], as_tuple=True)[0] + 1).tolist()
        anfang, ende = [0] + wechsel, wechsel + [len(m)]
        werte = m[torch.as_tensor(anfang, device=m.device)].tolist()
        return [[a, e, w] for a, e, w in zip(anfang, ende, werte, strict=True)]

    @classmethod
    def _huelle(cls, ruhe, knochen, gewicht):
        p = torch.as_tensor(ruhe, device=KARTE)[::cls.PROBE].to(torch.float64)
        kn = torch.as_tensor(knochen, device=KARTE)[::cls.PROBE].to(torch.int64)
        w = torch.as_tensor(gewicht, device=KARTE)[::cls.PROBE] > 0
        frei = ~w.any(dim=1)                                           # ohne Gewicht: am Einheitsknochen
        nummer = torch.cat([kn[w], torch.full((int(frei.sum()),), -1, dtype=torch.int64, device=kn.device)])
        punkte = torch.cat([p.unsqueeze(1).expand(-1, kn.shape[1], -1)[w], p[frei]])
        if not len(nummer):
            return []
        platz = nummer + 1                                             # −1 → Platz 0
        zahl = int(platz.max()) + 1
        index = platz[:, None].expand(-1, 3)
        unten = torch.full((zahl, 3), float('inf'), dtype=torch.float64, device=p.device).scatter_reduce(0, index, punkte, 'amin')
        oben = torch.full((zahl, 3), float('-inf'), dtype=torch.float64, device=p.device).scatter_reduce(0, index, punkte, 'amax')
        j = torch.nonzero(torch.bincount(platz, minlength=zahl) > 0, as_tuple=True)[0]
        return [[k - 1, *u, *o] for k, u, o in zip(j.tolist(), unten[j].tolist(), oben[j].tolist(), strict=True)]
