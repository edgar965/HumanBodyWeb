# -*- coding: utf-8 -*-
u"""G9koerperkoordinaten — wo auf dem Körper jeder Texel der Genesis-9-Kacheln liegt: Kette, Anteil entlang der Kette, Rumpfhöhe, Umfangswinkel (25.10.2026, Stufe K2a).

WOFÜR (Konzept `Docu/konzepte/2026-10-25_eigene-kleider-konzept.md`, Abschnitt 3): Ein eigenes Stück (Oberteil, Hose) ist eine Schale über der Haut DERSELBEN Körpergeometrie.
Der Vertex-Shader im Browser (`Eigenkleidshader`) liest diese Karte an der UV jedes Punkts und rechnet daraus Sitz (Abstand zur Haut) und Säume — kein Neubau beim Reglerzug.
Die Karte hängt nur am Netz (Genesis-9-Käfig, UV-Satz), gilt also für alle Figuren.

KETTEN (`KETTEN`, Nummer = Index) je Käfigpunkt aus dem führenden Knochen (`G9koerperteile.genesis_punkte`, größtes Hautgewicht von `G9haut`): Rumpf = Wirbelsäule,
Brust, Becken, Schlüsselbeine; Arm = Ober- und Unterarm; Bein = Ober- und Unterschenkel; Hals, Kopf (mit Augen), Hand, Fuß als eigene Kennung ohne Säume. Kleine Stücke
einer Kette gehen an den häufigsten Nachbarn (`G9hautteile.inseln`, dieselbe Regel wie bei den Hautteilen).

ANTEIL entlang der Glieder, aus dem Skelett der Grundfigur in Ruhelage (`G9skelett`, Gelenkzentren `center_point`), UNGEKLEMMT (Bild `ANTEIL_BEREICH`):
  Arm    Projektion auf Schulter (`upperarm`) → Ellbogen (`forearm`) → Handgelenk (`hand`): Bogenlänge ÷ Gesamtlänge, nächstes Teilstück; vor der Schulter negativ.
  Bein   ebenso Hüfte (`thigh`) → Knie (`shin`) → Knöchel (`foot`); über der Hüfte (Gesäß) negativ.
  Rumpf  Punkte bis SCHULTER_M um das Schultergelenk ihrer Seite (und über der halben Rumpfhöhe): derselbe ARMANTEIL — so laufen Arm- und Rumpfpunkte an der Schulter
         stetig ineinander, und ein ärmelloses Oberteil schneidet als glatte Ebene durch das Gelenk statt entlang der Kettengrenze. Sonst `OHNE` (−0,5, nie geschnitten).
HÖHE: Rumpfhöhe für JEDEN Punkt, 0 = Halsansatz (Gelenk `neck1`) … 1 = Schritt (tiefster Rumpfpunkt mit |x| < SCHRITT_BREITE_M), ungeklemmt (Bild `HOEHE_BEREICH`) —
waagrecht, damit Saum und Bund waagrecht laufen; ein langes Oberteil deckt auch die Beinpunkte über seinem Saum (Gesäß), am Hals ist sie negativ.
WINKEL um die Achse der Kette, 0 = vorn (+z), 0,25 = links der Figur (+x): Rumpf UND Hals um die Mitte des Rumpfquerschnitts in dieser Höhe (`RUMPF_SCHEIBEN`; der
Hals um die oberste Scheibe — der Halsausschnitt braucht vorn/hinten auch dort), Glieder um Schulter→Handgelenk bzw. Hüfte→Knöchel.

BILD: je Kachel mit Rumpf-, Arm- oder Beinpunkten (`kacheln`) eine Zeile aus zwei SEITE²-Teilbildern, die Kacheln untereinander:
  links   R = Kette × STUFE, G/B = Anteil (16 Bit über ANTEIL_BEREICH, hoch/tief), A = 255
  rechts  R/G = Höhe (16 Bit über HOEHE_BEREICH), B = Winkel (8 Bit), A = 255
Fassung 2 (25.10.2026 spät, Edgar: Halsrand „zackig ausgefranst“): Anteil vorzeichenbehaftet, Armanteil am Rumpf, Winkel am Hals.
Je Texel gilt die Kette der Ecke mit dem größten baryzentrischen Anteil; Anteil und Winkel werden nur über die Ecken DIESER Kette gemittelt (die Höhe über alle drei) —
an einer Kettengrenze entsteht so kein erfundener Zwischenwert. Der Browser liest punktgenau (`texelFetch`), deshalb ist auch die Randfortsetzung (`RAND_PX`) eine Kopie des
Nachbarn und kein Mittel. Gerastert aus der Texturabtastung 1024 (`G9texturabtastung`, liegt für die Hautteile schon) und je 2 × 2 auf SEITE ausgedünnt.

RECHNUNG mit torch auf der Karte (`G9eigenkarte`, dieselbe Ausnahme wie `G9hautteile`), EINMAL je Prozess und nur im Speicher — keine Ablage. `holen()` liefert
(PNG-Bytes, Marke, Angaben); die Marke (SHA-1 der Bytes) ist das ETag der Antwort (`G9koerperkoordinatenapi`).
"""
import hashlib
import io
import logging
import math
import threading
import time

import numpy as np

from .g9hautteile import G9hautteile

logger = logging.getLogger('core')

__all__ = ['G9koerperkoordinaten']


class G9koerperkoordinaten:
    """`holen()` → (png, marke, angaben), einmal je Prozess gerechnet."""

    #: 2: Anteil vorzeichenbehaftet, Armanteil an der Schulter, Winkel am Hals (25.10.2026 spät)
    FASSUNG = 2
    KETTEN = ('keine', 'rumpf', 'arm_links', 'arm_rechts', 'bein_links', 'bein_rechts', 'hals', 'kopf', 'hand_links', 'hand_rechts', 'fuss_links', 'fuss_rechts')
    #: Teil (`G9koerperteile.TEILE`) → Kette; fehlt ein Teil, ist es `keine`
    TEIL_KETTE = {'rumpf': 'rumpf', 'becken': 'rumpf', 'l_schulter': 'rumpf', 'r_schulter': 'rumpf',
                  'l_oberarm': 'arm_links', 'l_unterarm': 'arm_links', 'r_oberarm': 'arm_rechts', 'r_unterarm': 'arm_rechts',
                  'l_oberschenkel': 'bein_links', 'l_unterschenkel': 'bein_links', 'r_oberschenkel': 'bein_rechts', 'r_unterschenkel': 'bein_rechts',
                  'hals': 'hals', 'kopf': 'kopf', 'auge': 'kopf', 'l_hand': 'hand_links', 'r_hand': 'hand_rechts', 'l_fuss': 'fuss_links', 'r_fuss': 'fuss_rechts'}
    #: Gelenke je Glied: Anfang, Mitte, Ende (Daz-Knochen, deren `center_point`)
    GLIEDER = {'arm_links': ('l_upperarm', 'l_forearm', 'l_hand'), 'arm_rechts': ('r_upperarm', 'r_forearm', 'r_hand'),
               'bein_links': ('l_thigh', 'l_shin', 'l_foot'), 'bein_rechts': ('r_thigh', 'r_shin', 'r_foot')}
    HALS = 'neck1'
    #: Halbe Breite des Streifens um die Mitte, in dem der Schritt gesucht wird (m) — gesetzt
    SCHRITT_BREITE_M = 0.015
    STUFE = 20
    HOEHE_BEREICH = (-0.5, 1.5)
    ANTEIL_BEREICH = (-0.5, 1.5)
    #: Anteil eines Punkts ohne Glied (Rumpf fern der Schulter, Hals, Kopf …) — ein Ärmel schneidet ihn nie
    OHNE = -0.5
    #: Radius um das Schultergelenk, in dem Rumpfpunkte den Armanteil bekommen (m) — gesetzt (reicht über die Achsel, nicht bis zur Brustmitte)
    SCHULTER_M = 0.15
    SEITE = 512
    ABTASTUNG = 1024
    RAND_PX = 4
    RUMPF_SCHEIBEN = 40
    #: Abstand zum mittleren Gelenk, in dem der Anteil zur Probe gemittelt wird (m) — größer als der Gliedradius (bei 3 cm lag am Ellbogen kein Hautpunkt darin)
    PROBE_M = 0.06
    RICHTUNGEN = ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1))

    _stand = None
    _schloss = threading.Lock()

    @classmethod
    def holen(cls):
        if cls._stand is None:
            with cls._schloss:
                if cls._stand is None:
                    cls._stand = cls.bauen()
        return cls._stand

    @classmethod
    def nummer(cls, kette):
        return cls.KETTEN.index(kette)

    # ------------------------------------------------------------- Punkte

    @classmethod
    def ketten(cls, torch, g, ecken, punkte):
        """(Kette je Käfigpunkt (N,) int64 auf der Karte, umgeteilte Punkte, Inseln)."""
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile
        haut = G9haut.holen()
        if len(haut.index) != len(punkte):
            raise ValueError('Hautgewichte für %d Punkte, Käfig hat %d' % (len(haut.index), len(punkte)))
        teil = G9koerperteile.genesis_punkte(haut)
        je_teil = np.array([cls.nummer(cls.TEIL_KETTE.get(t, 'keine')) for t in G9koerperteile.TEILE] + [0], dtype=np.int64)   # Teil −1 → letzte Zeile = keine
        von, nach, _laenge = G9hautteile.kanten(torch, g, ecken, punkte)
        return G9hautteile.inseln(torch, torch.as_tensor(je_teil[teil], device=g), von, nach)

    @staticmethod
    def gelenke():
        from Genesis9.skelett import G9skelett
        return {k['name']: np.asarray(k['kopf'], dtype=np.float64) for k in G9skelett().gelenkknochen()}

    @staticmethod
    def glied(torch, p, a, b, c):
        """(Anteil, Winkel) je Punkt für die Kette a → b → c (Gelenke als Tensoren (3,)). Das nächste Teilstück wählt der geklemmte Abstand; der Anteil selbst ist
        an den Enden UNGEKLEMMT (vor a negativ, hinter c über 1) — stetig in den Rumpf hinein."""
        l1, l2 = torch.linalg.norm(b - a), torch.linalg.norm(c - b)

        def stueck(s, e):
            d = e - s
            u = (p - s) @ d / (d @ d)
            return u, torch.linalg.norm(p - (s + u.clamp(0.0, 1.0)[:, None] * d), dim=1)

        u1, d1 = stueck(a, b)
        u2, d2 = stueck(b, c)
        anteil = torch.where(d1 <= d2, u1.clamp(max=1.0) * l1, l1 + u2.clamp(min=0.0) * l2) / (l1 + l2)
        achse = (c - a) / torch.linalg.norm(c - a)
        z = torch.tensor([0.0, 0.0, 1.0], device=p.device, dtype=p.dtype)
        vorn = z - (z @ achse) * achse
        vorn = vorn / torch.linalg.norm(vorn)
        seite = torch.linalg.cross(vorn, achse)
        r = p - a
        r = r - (r @ achse)[:, None] * achse
        return anteil, torch.remainder(torch.atan2(r @ seite, r @ vorn) / (2 * math.pi), 1.0)

    @classmethod
    def punktwerte(cls, torch, g, punkte, kette):
        """`{anteil, hoehe, winkel}` je Käfigpunkt (float64 auf der Karte) und die Proben für die Angaben."""
        p = torch.as_tensor(punkte, device=g, dtype=torch.float64)
        gelenk = {k: torch.as_tensor(v, device=g) for k, v in cls.gelenke().items()}
        rumpf = kette == cls.nummer('rumpf')
        mitte = rumpf & (p[:, 0].abs() < cls.SCHRITT_BREITE_M)
        y0, y1 = float(gelenk[cls.HALS][1]), float(p[mitte, 1].min())
        hoehe = (y0 - p[:, 1]) / (y0 - y1)
        anteil = torch.full_like(hoehe, cls.OHNE)
        winkel = torch.zeros_like(hoehe)
        rumpfhals = rumpf | (kette == cls.nummer('hals'))
        winkel[rumpfhals] = cls.rumpfwinkel(torch, g, p, hoehe, rumpf, rumpfhals)
        proben = {}
        for name, (a, b, c) in cls.GLIEDER.items():
            m = kette == cls.nummer(name)
            anteil[m], winkel[m] = cls.glied(torch, p[m], gelenk[a], gelenk[b], gelenk[c])
            if name.startswith('arm'):        # Rumpfpunkte an der Schulter dieser Seite: derselbe Armanteil (siehe Kopf)
                seite = (p[:, 0] > 0) if name.endswith('links') else (p[:, 0] <= 0)
                nah = rumpf & seite & (hoehe < 0.5) & (torch.linalg.norm(p - gelenk[a], dim=1) < cls.SCHULTER_M)
                anteil[nah] = cls.glied(torch, p[nah], gelenk[a], gelenk[b], gelenk[c])[0]
            nah = m & (torch.linalg.norm(p - gelenk[b], dim=1) < cls.PROBE_M)
            l1, l2 = float(torch.linalg.norm(gelenk[b] - gelenk[a])), float(torch.linalg.norm(gelenk[c] - gelenk[b]))
            proben[name] = {'gelenk_soll': round(l1 / (l1 + l2), 3), 'am_gelenk': round(float(anteil[nah].mean()), 3) if bool(nah.any()) else None,
                            'punkte_am_gelenk': int(nah.sum()), 'laenge_m': round(l1 + l2, 3), 'anfang_x': round(float(gelenk[a][0]), 3)}
        proben['rumpf'] = {'halsansatz_y': round(y0, 4), 'schritt_y': round(y1, 4), 'laenge_m': round(y0 - y1, 3),
                           'schulterpunkte': int(((anteil > cls.OHNE) & rumpf).sum())}
        return {'anteil': anteil.clamp(*cls.ANTEIL_BEREICH), 'hoehe': hoehe, 'winkel': winkel}, proben

    @classmethod
    def rumpfwinkel(cls, torch, g, p, hoehe, rumpf, ziel):
        """Winkel der Punkte `ziel` um die Mitte des Rumpfquerschnitts (Scheiben über die Rumpfhöhe; Arme gehören nicht zum Rumpf, verschieben die Mitte also nicht;
        der Hals nimmt die oberste Scheibe)."""
        from Genesis9.eigenkarte import G9eigenkarte
        n = cls.RUMPF_SCHEIBEN
        scheibe = (hoehe[rumpf].clamp(0.0, 1.0) * (n - 1)).round().long()
        mitten = []
        for achse in (0, 2):
            unten = torch.full((n,), float('inf'), device=g, dtype=torch.float64).scatter_reduce(0, scheibe, p[rumpf, achse], 'amin')
            oben = torch.full((n,), float('-inf'), device=g, dtype=torch.float64).scatter_reduce(0, scheibe, p[rumpf, achse], 'amax')
            mitten.append((unten + oben) / 2)
        gut = torch.isfinite(mitten[0]) & torch.isfinite(mitten[1])
        stellen = (torch.arange(n, device=g, dtype=torch.float64)[gut] / (n - 1)).float()
        h = hoehe[ziel].clamp(0.0, 1.0).float()
        cx = G9eigenkarte.interp(h, stellen, mitten[0][gut].float()).double()
        cz = G9eigenkarte.interp(h, stellen, mitten[1][gut].float()).double()
        return torch.remainder(torch.atan2(p[ziel, 0] - cx, p[ziel, 2] - cz) / (2 * math.pi), 1.0)

    # ------------------------------------------------------------- Kacheln

    @classmethod
    def kachel(cls, torch, g, abtastung, nummer, kette, werte):
        """(4, SEITE, SEITE) float32 — Kette, Anteil, Höhe, Winkel je Texel; Rand fortgesetzt; Texel außerhalb: Kette 0."""
        drin_np, ecken_np, anteile_np = abtastung.stellen(nummer)
        s, b = abtastung.seite, cls.SEITE
        e = torch.as_tensor(ecken_np, device=g)
        a = torch.as_tensor(anteile_np, device=g, dtype=torch.float64)
        ke = kette[e]
        k = ke.gather(1, a.argmax(1, keepdim=True)).squeeze(1)       # Kette der stärksten Ecke
        w = a * (ke == k[:, None])
        w = w / w.sum(1, keepdim=True).clamp_min(1e-12)
        phi = 2 * math.pi * werte['winkel'][e]
        texel = torch.stack([k.double(), (w * werte['anteil'][e]).sum(1), (a * werte['hoehe'][e]).sum(1),
                             torch.remainder(torch.atan2((w * phi.sin()).sum(1), (w * phi.cos()).sum(1)) / (2 * math.pi), 1.0)])
        drin = torch.as_tensor(drin_np, device=g)
        feld = torch.zeros((4, s, s), device=g, dtype=torch.float64)
        feld[:, drin] = texel
        f = s // b                                                    # 2 × 2 ausdünnen: je Block der erste belegte Texel
        d4 = drin.view(b, f, b, f).permute(0, 2, 1, 3).reshape(b, b, f * f)
        wahl = d4.float().argmax(-1, keepdim=True)
        belegt = d4.any(-1)
        feld = feld.view(4, b, f, b, f).permute(0, 1, 3, 2, 4).reshape(4, b, b, f * f).gather(-1, wahl[None].expand(4, -1, -1, -1)).squeeze(-1)
        feld = feld * belegt
        for _ in range(cls.RAND_PX):                                  # Rand: Kopie des ersten belegten Nachbarn (kein Mittel — der Browser liest punktgenau)
            neu_m, neu_f = belegt.clone(), feld.clone()
            for dy, dx in cls.RICHTUNGEN:
                q_m, q_f = cls._schieben(belegt, dy, dx), cls._schieben(feld, dy, dx)
                nimm = ~neu_m & q_m
                neu_f = torch.where(nimm[None], q_f, neu_f)
                neu_m = neu_m | nimm
            belegt, feld = neu_m, neu_f
        return feld.float(), int(belegt.sum())

    @staticmethod
    def _schieben(x, dy, dx):
        """x[y + dy, x + dx] an (y, x), außerhalb 0/False."""
        import torch
        aus = torch.zeros_like(x)
        h, w = x.shape[-2:]
        aus[..., max(-dy, 0):h - max(dy, 0), max(-dx, 0):w - max(dx, 0)] = x[..., max(dy, 0):h - max(-dy, 0), max(dx, 0):w - max(-dx, 0)]
        return aus

    @classmethod
    def kodieren(cls, torch, feld):
        """(SEITE, 2·SEITE, 4) uint8 — die zwei Teilbilder einer Kachel (siehe Kopf)."""
        k, anteil, hoehe, winkel = feld
        a0, a1 = cls.ANTEIL_BEREICH
        qa = ((anteil - a0) / (a1 - a0)).clamp(0, 1).mul(65535).round().long()
        lo, hi = cls.HOEHE_BEREICH
        qh = ((hoehe - lo) / (hi - lo)).clamp(0, 1).mul(65535).round().long()
        voll = torch.full_like(qa, 255)
        links = torch.stack([(k * cls.STUFE).round().long().clamp(0, 255), qa // 256, qa % 256, voll], -1)
        rechts = torch.stack([qh // 256, qh % 256, (winkel * 256).round().long() % 256, voll], -1)
        return torch.cat([links, rechts], 1).to(torch.uint8)

    @classmethod
    def bauen(cls):
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.texturabtastung import G9texturabtastung
        from PIL import Image

        t0 = time.perf_counter()
        torch, g = G9hautteile.geraet()
        abtastung = G9texturabtastung.holen(cls.ABTASTUNG)
        punkte = np.asarray(G9basisnetz.holen().punkte, dtype=np.float64)
        kette, umgeteilt, inseln = cls.ketten(torch, g, abtastung.ecken, punkte)
        werte, proben = cls.punktwerte(torch, g, punkte, kette)
        glied = {cls.nummer(k) for k in ('rumpf', 'arm_links', 'arm_rechts', 'bein_links', 'bein_rechts')}
        zeilen, kacheln, texel_je_kette = [], [], {}
        for nummer in abtastung.kacheln:
            feld, belegt = cls.kachel(torch, g, abtastung, nummer, kette, werte)
            je = torch.bincount(feld[0].round().long().flatten(), minlength=len(cls.KETTEN)).tolist()
            if not any(je[i] for i in glied):
                continue
            kacheln.append(int(nummer))
            zeilen.append(cls.kodieren(torch, feld).cpu().numpy())
            texel_je_kette[str(nummer)] = {cls.KETTEN[i]: int(n) for i, n in enumerate(je) if n and i}
        puffer = io.BytesIO()
        Image.fromarray(np.concatenate(zeilen, 0), 'RGBA').save(puffer, 'PNG')
        png = puffer.getvalue()
        angaben = {'fassung': cls.FASSUNG, 'seite': cls.SEITE, 'kacheln': kacheln, 'ketten': list(cls.KETTEN), 'stufe': cls.STUFE,
                   'hoehe_bereich': list(cls.HOEHE_BEREICH), 'anteil_bereich': list(cls.ANTEIL_BEREICH), 'bytes': len(png), 'geraet': str(g),
                   'punkte_je_kette': {cls.KETTEN[i]: int(n) for i, n in enumerate(torch.bincount(kette, minlength=len(cls.KETTEN)).tolist())},
                   'umgeteilt': umgeteilt, 'inseln': inseln, 'texel_je_kette': texel_je_kette, 'proben': proben,
                   'sekunden': round(time.perf_counter() - t0, 2)}
        logger.info('Körperkoordinaten auf %s: Kacheln %s, Punkte je Kette %s, %d Punkte in %d Inseln umgeteilt, Proben %s, %d Bytes (%.1f s)', g, kacheln,
                    angaben['punkte_je_kette'], umgeteilt, inseln, proben, len(png), angaben['sekunden'])
        return png, hashlib.sha1(png).hexdigest()[:24], angaben
