"""Meshgenesisnetznormalen — Normalen je Punkt für ein Anzeigenetz ohne mitgelieferte Normalen, in torch auf der
Karte (19.11.2026, Edgar: „optimiere die Ladezeit des Genesis figur. Bei Charakter geht das viel schneller“, „alles
auf torch auf diesen jobseiten“).

Gemessen an `goldprinzessin_mesh_genesis_47` im sichtbaren Tab der Foto-Genesis-Seite: das Kleiderfeld brauchte
4,9 s, davon das Haar (`ki_haar`, 1,64 Mio. Punkte) 3,0 s im Häuten — fast alles in
`Meshgenesisflaechennormalen.geschweisst` (JS: `computeVertexNormals`, dann jeder Punkt mit einem Text-Schlüssel in
eine `Map`), weil das Paket keine Normalen trug; Lage häuten 147 ms, Dreiecke sortieren 162 ms. Mit Normalen im Paket
dreht die Seite sie nur noch mit der Haltung (`Meshgenesisflaechennormalen.gehaeutet`): Haar 3.028 → 624 ms, der
lange Frame nach dem Netz 6,3 → 1,4 s. Gegen die alten Normalen der Seite (Haltung aus dem Netz): Winkel Median
0,84°, p90 12,6°, p99 80° (Strähnen, die nicht starr gedreht werden, und doppelseitige Karten — nicht weiter geprüft);
umgedreht fällt der Vergleich durch (99,2 % über 90°).

Dieselbe Regel wie `geschweisst`, aber in der Ruhelage: je Dreieck (C − B) × (A − B) an seine drei Punkte
(flächengewichtet wie three.js), je Punkt auf Länge 1; Punkte gleicher Lage (auf 1e-5 m gerundet) bekommen die Summe
ihrer Normalen, wieder auf Länge 1. Ausgabe int8 × 127 wie der Block `normalen` des Pakets, auf dem Gerät von `ruhe`.

    n = Meshgenesisnetznormalen.aus(ruhe, dreiecke)        # (V, 3) int8
"""
import torch

__all__ = ['Meshgenesisnetznormalen']


class Meshgenesisnetznormalen:
    RASTER = 1e5

    @staticmethod
    def _laenge_eins(n):
        laenge = n.norm(dim=1, keepdim=True)
        return n / torch.where(laenge > 0, laenge, torch.ones_like(laenge))

    @classmethod
    def aus(cls, ruhe, dreiecke):
        p = torch.as_tensor(ruhe, device='cuda').double()
        f = torch.as_tensor(dreiecke, device='cuda').long().reshape(-1, 3)
        a, b, c = p[f[:, 0]], p[f[:, 1]], p[f[:, 2]]
        fn = torch.linalg.cross(c - b, a - b, dim=1)
        n = torch.zeros_like(p)
        for ecke in range(3):
            n.index_add_(0, f[:, ecke], fn)
        n = cls._laenge_eins(n)
        lage, gruppe = torch.unique(torch.round(p * cls.RASTER).long(), dim=0, return_inverse=True)
        summe = torch.zeros((len(lage), 3), dtype=p.dtype, device='cuda').index_add_(0, gruppe, n)
        n = cls._laenge_eins(summe[gruppe])
        aus = torch.round(n * 127).clamp(-127, 127).to(torch.int8)
        return aus.to(ruhe.device) if torch.is_tensor(ruhe) else aus
