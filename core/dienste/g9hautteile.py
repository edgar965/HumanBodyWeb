# -*- coding: utf-8 -*-
"""G9hautteile — welcher Körperteil hinter jedem Texel der Genesis-9-Kacheln liegt, weich überblendet (25.10.2026).

Edgar, 25.10.2026: „bei den Reglern für die einzelnen Körperteile mach jeweils auch Regler für die Textur“ — Hautfarbe und Tattoo je Körperteil im Abschnitt „Eigen“
(`Genesis9hautteile` im Browser). Der Shader braucht dafür je Texel die Anteile der Teile; die stehen in dieser Karte.

TEILE (Kanal = Index, Browser gleich; seit Fassung 4 24 Teile in der Feinheit der Formregler — Edgar: „pro Körperteil brauche ich die Texturregler, z.B. Nase, Augen, Rumpf“):
kopfhaut, gesicht, mund, nase, auge_links, auge_rechts, braue_links, braue_rechts, ohr_links, ohr_rechts, hals, bauch_ruecken, brust_links, brust_rechts, gesaess_links,
gesaess_rechts, arm_links, arm_rechts, hand_links, hand_rechts, bein_links, bein_rechts, fuss_links, fuss_rechts. Je Käfigpunkt aus DENSELBEN Punktmengen wie die Formregler
(`G9eigenregler.morph('regler_<name>').merkmal`, `MERKMAL`): Augen, Brauen (Band über dem Auge), Ohren, Nase, Mund, Brust, Hüfte und Gesäß; der Rest aus Daz' Einteilung
(`G9reglerregionen`, `ORT_TEIL`; Gliedmaßen je Seite nach x, x > 0 = links der Figur). Überlappen sich Merkmale, gewinnt die spätere Zeile in `MERKMAL` (braue > auge > nase >
mund > ohr > gesicht > kopfhaut). Kleine Stücke eines Teils (< `INSEL_MAX` Punkte) gehen an den häufigsten Nachbarn. WEICH: je Teil der Weg über die Kanten des Netzes zum
nächsten Punkt des Teils (kürzeste Wege, nicht Luftlinie — sonst färbte das linke Bein am Schritt das rechte mit), Gewicht 1 − smoothstep(Weg / Halbbreite), je Punkt auf
Summe 1 — an der Grenze 50/50. Halbbreite `HALB_GESICHT_M` für die Teile des Kopfs (kopfhaut … ohr_rechts), sonst `HALB_M`. Beide GESETZT, nicht gemessen.

RECHNUNG mit torch (25.10.2026, Edgar: „alles soll auf GPU und RAM laufen“): auf der Karte, auch im Server-Faden (`G9eigenkarte`, dieselbe Ausnahme von `G9rechenkarte`
wie die Eigenregler: ein Bau dauert 0,6–3 s, die Warteschlange der GPU-Sperre wäre länger); ohne CUDA torch auf der CPU. Kürzeste Wege als Relaxation über alle Kanten (Bellman-Ford, bis nichts mehr kürzer wird; Wege über
`HALB_M` zählen nicht), Inseln per Etikettausbreitung, Rastern, Mitteln und Randfortsetzung als Feldrechnung. Nur das PNG schreibt die CPU; keine Zwischendateien.

BILD je Kachel (seit Fassung 4): RGBA 1536 × 1024, sechs 512er-Teilbilder in 3 Spalten × 2 Zeilen — obere Zeile Kanäle 0–3 | 4–7 | 8–11, untere 12–15 | 16–19 | 20–23
(Teilbild k: Spalte k % 3, Zeile k // 3). Aus der Texturabtastung 1024 (`G9texturabtastung`) per Baryzentrik gerastert und 2 × 2 gemittelt, Inselränder um `RAND_PX` nach
außen fortgesetzt (je Schritt das Mittel der belegten Nachbarn). Ein Sampler statt sechs (die Haut hat schon viele). Der Browser liest ohne Mip-Stufen und klemmt an den
Rändern jedes Teilbilds, sonst mischten die Nachbarteilbilder herein. Fassung 3 (12 Teile, 1536 × 512) bleibt in der Ablage liegen.

ABLAGE: `Genesis9/ablage/hautteile_<geschlecht>_v<FASSUNG>_<kachel>.png` und `….json` — die Gewichte hängen nicht am Geschlecht; gebaut wird trotzdem je Geschlecht, weil die
Ablage der Hautkarten so arbeitet (`G9hautfaltenablage`).

LESER außer dem Browser: die Haut-KI von Mesh3D-AI (Konzept `Docu/konzepte/2026-10-25_haut-ki-eingang-richtig-ablesen-konzept.md`, Fassung 2, Abschnitte 3 und 4: Ton-KI je Körperteil, Prüftöne und Training je
Körperteil) liest die Ablage bzw. `G9hautteile`. Ändern sich Format, `TEILE`-Reihenfolge oder `FASSUNG`: der Mesh3D-AI-Sitzung vorher Bescheid geben.
"""
import json
import logging
import time

import numpy as np

from .g9hautfalten import G9hautfalten

logger = logging.getLogger('core')

__all__ = ['G9hautteile']


class G9hautteile(G9hautfalten):
    """`bauen()` rechnet alle Kacheln und schreibt sie in die Ablage."""

    #: 2: kleine Inseln umgeteilt; 3: Rechnung mit torch, Randfortsetzung als Nachbarmittel; 4: 24 Teile aus den Merkmalen der Formregler, 3 × 2 Teilbilder
    FASSUNG = 4
    TEILE = ('kopfhaut', 'gesicht', 'mund', 'nase', 'auge_links', 'auge_rechts', 'braue_links', 'braue_rechts', 'ohr_links', 'ohr_rechts', 'hals', 'bauch_ruecken',
             'brust_links', 'brust_rechts', 'gesaess_links', 'gesaess_rechts', 'arm_links', 'arm_rechts', 'hand_links', 'hand_rechts', 'bein_links', 'bein_rechts',
             'fuss_links', 'fuss_rechts')
    KANAELE = 24
    SPALTEN = 3
    #: Ort (`G9reglerregionen.ORTE`) → Teil; ohne Seite bekommen Gliedmaßen, Augen, Ohren, Brust und Hüfte die Seite nach x angehängt
    ORT_TEIL = {'kopfform': 'kopfhaut', 'gesicht': 'gesicht', 'augen': 'auge', 'ohren': 'ohr', 'nase': 'nase', 'mund': 'mund', 'hals': 'hals',
                'brust': 'brust', 'ruecken': 'bauch_ruecken', 'taille': 'bauch_ruecken', 'huefte': 'gesaess', 'arme': 'arm', 'haende': 'hand', 'beine': 'bein',
                'fuesse': 'fuss'}
    #: Merkmale der Formregler, die den Teil bestimmen — in aufsteigendem Vorrang (spätere Zeile gewinnt): ohr < mund < nase < auge < braue; Brust und Gesäß überlappen nicht
    MERKMAL = (('ohr_links', 'kopf_ohr_links'), ('ohr_rechts', 'kopf_ohr_rechts'), ('mund', 'kopf_mund'), ('nase', 'kopf_nase'),
               ('auge_links', 'kopf_auge_links'), ('auge_rechts', 'kopf_auge_rechts'), ('braue_links', 'kopf_braue_links'), ('braue_rechts', 'kopf_braue_rechts'),
               ('brust_links', 'rumpf_brust_links'), ('brust_rechts', 'rumpf_brust_rechts'), ('gesaess_links', 'rumpf_gesaess_links'),
               ('gesaess_rechts', 'rumpf_gesaess_rechts'))
    #: Halbe Breite des Übergangs zwischen zwei Teilen (m, über die Kanten) — gesetzt; im Kopf schmaler (Nase, Augen, Brauen liegen Millimeter auseinander)
    HALB_M = 0.01
    HALB_GESICHT_M = 0.004
    GESICHT_BIS = 'ohr_rechts'
    #: Ein Stück eines Teils mit weniger Punkten ist eine Insel im Nachbarn — gesetzt
    INSEL_MAX = 40
    #: Abtastung (Texel je Kachel) und Bildseite
    SEITE = 1024
    BILD = 512
    RAND_PX = 4

    @classmethod
    def stamm(cls, geschlecht):
        from Genesis9.pfade import G9pfade
        return G9pfade.ablage() / ('hautteile_%s_v%d' % (geschlecht, cls.FASSUNG))

    @staticmethod
    def geraet():
        """(torch, Gerät) — die Karte wie bei den Eigenreglern (`G9eigenkarte`, auch im Server-Faden; ohne CUDA die CPU)."""
        import torch
        from Genesis9.eigenkarte import G9eigenkarte
        return torch, G9eigenkarte.geraet()

    # ------------------------------------------------------------- Punkte

    @classmethod
    def punktteile(cls, punkte):
        """(Teil je Käfigpunkt (N,) int64 — Index in `TEILE`, vor dem Umteilen der Inseln; {Teil: Punkte im Merkmal des Formreglers})."""
        from Genesis9.eigenregler import G9eigenregler
        from Genesis9.reglerregionen import G9reglerregionen
        region = np.asarray(G9reglerregionen.holen())
        nummer = {t: i for i, t in enumerate(cls.TEILE)}
        aus = np.zeros(len(region), dtype=np.int64)
        links = punkte[:, 0] > 0
        for i, ort in enumerate(G9reglerregionen.ORTE):
            teil, m = cls.ORT_TEIL[ort], region == i
            if teil in nummer:
                aus[m] = nummer[teil]
            else:
                aus[m & links] = nummer[teil + '_links']
                aus[m & ~links] = nummer[teil + '_rechts']
        zahl = {}
        for teil, regler in cls.MERKMAL:                       # aufsteigender Vorrang: die spätere Zeile überschreibt
            merkmal = np.asarray(G9eigenregler.morph(G9eigenregler.PRAEFIX + regler).merkmal, dtype=np.int64)
            aus[merkmal] = nummer[teil]
            zahl[teil] = int(len(merkmal))
        return aus, zahl

    @staticmethod
    def kanten(torch, g, ecken, punkte):
        """(von, nach, Länge) — jede Kante des Netzes in beiden Richtungen, auf dem Gerät."""
        e = torch.as_tensor(np.asarray(ecken), device=g)
        k = torch.cat([e[:, [0, 1]], e[:, [1, 2]], e[:, [2, 0]]])
        k = torch.unique(torch.sort(k, dim=1).values, dim=0)
        k = k[k[:, 0] != k[:, 1]]
        p = torch.as_tensor(punkte, device=g, dtype=torch.float64)
        laenge = torch.linalg.norm(p[k[:, 0]] - p[k[:, 1]], dim=1).clamp_min(1e-7)
        return torch.cat([k[:, 0], k[:, 1]]), torch.cat([k[:, 1], k[:, 0]]), torch.cat([laenge, laenge])

    @classmethod
    def inseln(cls, torch, teil, von, nach):
        """Kleine Stücke eines Teils (zusammenhängend über Kanten, < `INSEL_MAX` Punkte) → häufigster Teil ihrer Nachbarn. → (Teil, umgeteilte Punkte, Inseln)."""
        n = len(teil)
        gleich = teil[von] == teil[nach]
        etikett = torch.arange(n, device=teil.device)
        for _ in range(n):                                     # Etikett = kleinster Index im Stück; Zeigersprung beschleunigt
            neu = etikett.scatter_reduce(0, nach[gleich], etikett[von[gleich]], 'amin', include_self=True)
            neu = neu[neu]
            if torch.equal(neu, etikett):
                break
            etikett = neu
        groesse = torch.bincount(etikett, minlength=n)[etikett]
        # das größte Stück eines Teils bleibt immer — ein kleines Teil (Braue) darf nicht als Insel im Gesicht verschwinden
        groesstes = torch.zeros(cls.KANAELE, device=teil.device, dtype=groesse.dtype).scatter_reduce(0, teil, groesse, 'amax', include_self=True)
        klein = (groesse < cls.INSEL_MAX) & (groesse < groesstes[teil])
        rand = klein[nach] & ~gleich                           # Kanten aus einer kleinen Insel in einen anderen Teil
        if not bool(rand.any()):
            return teil, 0, 0
        stimmen = torch.bincount(etikett[nach[rand]] * cls.KANAELE + teil[von[rand]], minlength=n * cls.KANAELE).view(n, cls.KANAELE)
        hat = stimmen.sum(1) > 0
        ziel = stimmen.argmax(1)
        wechsel = klein & hat[etikett]
        aus = torch.where(wechsel, ziel[etikett], teil)
        return aus, int(wechsel.sum()), int(torch.unique(etikett[wechsel]).numel())

    @classmethod
    def gewichte(cls, torch, teil, von, nach, laenge):
        """(N, KANAELE) float64 — weiche Anteile je Käfigpunkt, Summe 1 (kürzeste Wege über die Kanten, Relaxation bis zur Ruhe)."""
        n, t_n = len(teil), len(cls.TEILE)
        gesicht = cls.TEILE.index(cls.GESICHT_BIS)
        halb = torch.tensor([cls.HALB_GESICHT_M if i <= gesicht else cls.HALB_M for i in range(t_n)], device=teil.device, dtype=torch.float64)
        weit = 2.0 * cls.HALB_M
        d = torch.full((n, t_n), weit, device=teil.device, dtype=torch.float64)
        d[torch.arange(n, device=teil.device), teil] = 0.0
        index = nach[:, None].expand(-1, t_n)
        for _ in range(n):
            neu = d.scatter_reduce(0, index, (d[von] + laenge[:, None]).clamp_max(weit), 'amin', include_self=True)
            if torch.equal(neu, d):
                break
            d = neu
        t = (d / halb).clamp(0.0, 1.0)
        w = torch.zeros((n, cls.KANAELE), device=teil.device, dtype=torch.float64)
        w[:, :t_n] = 1.0 - t * t * (3.0 - 2.0 * t)
        return w / w.sum(1, keepdim=True).clamp_min(1e-9)

    # ------------------------------------------------------------- Kacheln

    @classmethod
    def kachel(cls, torch, g, abtastung, nummer, w):
        """`(bild (Zeilen·BILD, SPALTEN·BILD, 4) uint8 numpy, anteile {teil: Anteil}, texel)` einer Kachel."""
        import torch.nn.functional as F

        drin_np, ecken, anteile = abtastung.stellen(nummer)
        s, b, c = abtastung.seite, cls.BILD, cls.KANAELE
        f = s // b
        drin = torch.as_tensor(drin_np, device=g)
        feld = torch.zeros((s, s, c), device=g, dtype=torch.float32)
        e = torch.as_tensor(ecken, device=g)
        a = torch.as_tensor(anteile, device=g, dtype=torch.float32)
        feld[drin] = torch.einsum('nk,nkc->nc', a, w[e].float())
        zahl = drin.view(b, f, b, f).sum((1, 3)).float()
        klein = feld.view(b, f, b, f, c).sum((1, 3)) / zahl.clamp_min(1)[..., None]
        belegt = zahl > 0
        texel = int(belegt.sum())
        summe = klein[belegt].sum(0)
        x, m = klein.permute(2, 0, 1)[None], belegt[None, None].float()
        for _ in range(cls.RAND_PX):                           # Rand: je Schritt das Mittel der belegten Nachbarn (3 × 3)
            wert = F.avg_pool2d(x * m, 3, 1, 1, count_include_pad=False)
            anzahl = F.avg_pool2d(m, 3, 1, 1, count_include_pad=False)
            neu = (m == 0) & (anzahl > 0)
            x = torch.where(neu, wert / anzahl.clamp_min(1e-9), x)
            m = torch.where(neu, torch.ones_like(m), m)
        x = x * m
        bild = (x[0].permute(1, 2, 0) * 255.0 + 0.5).clamp(0, 255).to(torch.uint8)
        sp = cls.SPALTEN                                       # Teilbild k: Spalte k % SPALTEN, Zeile k // SPALTEN (oben 0)
        bild = torch.cat([torch.cat([bild[..., 4 * (z * sp + s_):4 * (z * sp + s_) + 4] for s_ in range(sp)], dim=1) for z in range(c // (4 * sp))], dim=0)
        anteile_teil = {t: round(float(summe[i] / summe.sum().clamp_min(1e-9)), 4) for i, t in enumerate(cls.TEILE) if float(summe[i]) > 0}
        return bild.cpu().numpy(), anteile_teil, texel

    def bauen(self):
        """Alle Kacheln in die Ablage; → die Liste (`{kachel: {anteile, texel}}`, `sekunden`, `geraet`)."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.texturabtastung import G9texturabtastung
        from PIL import Image

        t0 = time.perf_counter()
        torch, g = self.geraet()
        abtastung = G9texturabtastung.holen(self.SEITE)
        punkte = np.asarray(G9basisnetz.holen().punkte, dtype=np.float64)
        von, nach, laenge = self.kanten(torch, g, abtastung.ecken, punkte)
        roh, merkmale = self.punktteile(punkte)
        teil, umgeteilt, inseln = self.inseln(torch, torch.as_tensor(roh, device=g), von, nach)
        w = self.gewichte(torch, teil, von, nach, laenge)
        punkte_je_teil = {t: int(n) for t, n in zip(self.TEILE, torch.bincount(teil, minlength=len(self.TEILE)).tolist(), strict=True)}
        logger.info('Hautteile %s auf %s: %d Punkte, Merkmale der Formregler %s, je Teil %s, %d in %d Inseln umgeteilt, Übergang %.1f %% der Punkte (%.1f s)',
                    self.geschlecht, g, len(punkte), merkmale, punkte_je_teil, umgeteilt, inseln, float((w.max(1).values < 0.99).double().mean() * 100),
                    time.perf_counter() - t0)
        kacheln = {}
        for nummer in abtastung.kacheln:
            bild, anteile, texel = self.kachel(torch, g, abtastung, nummer, w)
            Image.fromarray(bild, 'RGBA').save(self.bildpfad(self.geschlecht, nummer), 'PNG')
            kacheln[str(nummer)] = {'anteile': anteile, 'texel': texel}
            logger.info('Hautteile %s Kachel %d: %s (%.1f s)', self.geschlecht, nummer, anteile, time.perf_counter() - t0)
        liste = {'geschlecht': self.geschlecht, 'fassung': self.FASSUNG, 'seite': self.BILD, 'spalten': self.SPALTEN, 'teile': list(self.TEILE),
                 'punkte_je_teil': punkte_je_teil, 'kacheln': kacheln, 'geraet': str(g), 'sekunden': round(time.perf_counter() - t0, 1)}
        ziel = self.listenpfad(self.geschlecht)
        vorlaeufig = ziel.with_suffix('.neu')
        vorlaeufig.write_text(json.dumps(liste), encoding='utf-8')
        vorlaeufig.replace(ziel)                    # die Liste kommt zuletzt: sie sagt „fertig"
        return liste
