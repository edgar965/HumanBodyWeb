# -*- coding: utf-8 -*-
"""Kleidermodellbau — ein `ModellMitKleidern` als Netze: Körper, Kleider, Haar (30.09.2026, „2D3D Kleider").

Gebaut wird über DENSELBEN Weg wie die Bühne: `G9garderobeapi._kleid` je Stück, `G9kleidmischbau` für die
Mischung der Kleider, `G9haarmischbau` für die des Haars — mit dem Rumpf, den der Browser schicken würde (die
Stellung als `regler`, die Werte des Sammeleintrags als `regler_stueck`, die getragenen Stücke als `getragen`).
Die rohen Netze fängt der Eingriff `vor_antwort` ab; was der Mischbau neu kodiert, wird aus den Netzfeldern
zurückgelesen. So sieht die Iteration genau das, was später auf der Bühne steht.

Ergebnis je Teil: `{punkte (N, 3), dreiecke (T, 3), farbe (3,), haut {knochen, index, gewicht}, art, sorte}` in der
Lage der Bühne (Meter, Y oben, Füße auf 0). Der Körper kommt als erstes Teil (Käfigstufe 0 an den UV-Nähten geteilt,
wie `G9figurrigglb`); seine Haut trägt die Daz-Knochen wie die der Stücke, damit `G9tanzhaut` alles gleich häutet.
Die Farbe eines Stücks ist das Mittel seiner Textur (`G9kleidfarbe.farben`), getönt mit der Umfärbung des Modells —
flach je Stück, weil die Note Farbflächen vergleicht (`Iterationsnote`). Kleidung und Haar kommen aus dem
`Teilevorrat`, solange ihr Bauplan gleich bleibt (eine Farbrunde baut nichts neu, 02.10.2026).

Läuft im Arbeitsprozess (python14 mit Django), nie im Server: Die Stufe wird hier auf den Käfig gesetzt
(`Netzstufenwahl`), sonst rechnete jede Runde die Unterteilung der Bühne mit.
"""

import logging

import numpy as np
from django.http import HttpResponse

from .koerperanhaenge import Koerperanhaenge
from .teilevorrat import Teilevorrat

logger = logging.getLogger('core')

__all__ = ['Kleidermodellbau']


class Kleidermodellbau:
    """`teile(modell)` → Liste der Teile; `glb(teile, pfad)`."""

    #: Haut der Figur, wenn keine Kachel gelesen wird (sRGB 0…1) — wie `Genesishaarrender.HAUT`.
    HAUT = (0.82, 0.68, 0.60)
    STUFE = 0

    def __init__(self, stellung, drehung=None, stufe=STUFE, koerper=None, kacheln=None):
        """`drehung`: die Haltung (`ModellMitKleidern.drehung`; für den Film nicht, die Bewegung ist absolut).
        `koerper`: Genesis-Regler des Modells ÜBER der Stellung des Auftrags (sonst wirkte `IterationKoerper` nicht)."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.formung import G9formung
        from Genesis9.haut import G9haut

        from .netzstufenwahl import Netzstufenwahl
        Netzstufenwahl._gewaehlt.set(int(stufe))
        self.stellung = dict(stellung or {})
        self.stellung.update({str(k): v for k, v in (koerper or {}).items()})
        self.drehung = dict(drehung or {})
        self.formung = G9formung.aus_abfrage(self.stellung, self.drehung)
        self.boden = float(self.formung.boden())
        self._stufe = G9basisnetz.netzstufe(0)
        self._ursprung = np.asarray(self._stufe.ursprung, dtype=np.int64)
        self._haut = G9haut.holen().fuer(self._ursprung)
        self._koerper = None
        #: `{kachel: Pfad}` der gebackenen Haut (`Koerpertextur.kacheln`) — ohne: einfarbig `HAUT`.
        self.kacheln = dict(kacheln or {})

    # --------------------------------------------------------------- Körper

    def koerper(self):
        if self._koerper is None:
            from .koerpertextur import Koerpertextur
            punkte = np.asarray(self.formung.punkte(), dtype=np.float64) - np.array([0.0, self.boden, 0.0])
            self._koerper = Koerpertextur.teil(punkte[self._ursprung], self._stufe, self._haut, self.HAUT, self.kacheln)
        return self._koerper

    def formbezug(self, ordner, runde):
        """Den Daz-Käfig des Körpers DIESER Runde (25.182 Punkte, Lage der Bühne) als `runde_NNN_formbezug.npz` ablegen
        → Dateiname. Der Anker, mit dem der Form-Pinsel Striche auf dem Modell der Runde in die Lage der Grundfigur
        überträgt (`G9formpinsel.uebertragen`, `Engine2d3dKleiderformendpunkte`)."""
        name = 'runde_%03d_formbezug.npz' % int(runde)
        kaefig = np.asarray(self.formung.punkte(), dtype=np.float64) - np.array([0.0, self.boden, 0.0])
        np.savez_compressed(ordner / name, koerper=kaefig.astype(np.float32))
        return name

    # --------------------------------------------------------------- Stücke

    @staticmethod
    def _feld(wert, typ=None):
        """Ein Netzfeld (oder Liste) zurück zu NumPy."""
        roh = getattr(wert, 'rohdaten', None)
        if roh is not None:
            return np.frombuffer(roh, dtype=np.dtype(wert.typ))
        return np.asarray(wert, dtype=typ)

    @classmethod
    def _haut_aus(cls, teil):
        h = teil.get('hautgewichte')
        if not h or not h.get('knochen'):
            return None
        index = cls._feld(h['skin_indices']).reshape(-1, 4).astype(np.int64)
        gewicht = cls._feld(h['skin_weights']).reshape(-1, 4).astype(np.float64)
        if h.get('kodierung') == 'u16u8':
            gewicht = gewicht / 255.0
        return {'knochen': list(h['knochen']), 'index': index, 'gewicht': gewicht}

    @staticmethod
    def _farbe(netze, toenung):
        farben = []
        for netz in netze:
            try:
                farben.append(np.asarray(Teilevorrat.farben(netz), dtype=np.float64).mean(axis=0))
            except (OSError, ValueError, KeyError, TypeError) as fehler:   # ohne Textur: Haut
                logger.debug('Kleidermodellbau: Farbe nicht lesbar (%s)', fehler)
        grund = np.mean(farben, axis=0) if farben else np.asarray(Kleidermodellbau.HAUT)
        return np.clip(grund * 2.0 * np.asarray(toenung), 0.0, 1.0)

    def _rumpf(self, modell, kennung, werte, rang):
        """Der Rumpf wie vom Browser — die getragenen Stücke AUFGELÖST (das stärkste Stück je Sammeleintrag, die
        Hauptsorte des Haars): `G9lagenanfrage` kennt nur echte Stücke und lässt das eigene aus."""
        from Genesis9.haargenerisch import G9haargenerisch
        from Genesis9.kleidgenerisch import G9kleidgenerisch
        getragen = []
        for e in modell.getragene():
            if e['kennung'] == modell.HAAR:
                sorte, regler = G9haargenerisch.aufloesen(e['regler_stueck'])
                if sorte:
                    getragen.append({'kennung': sorte, 'stil': [], 'regler_stueck': regler})
            else:
                getragen += G9kleidgenerisch.getragene_aufloesen([e])
        return {'regler': self.stellung, 'drehung': self.drehung, 'regler_stueck': dict(werte),
                'getragen': getragen, 'rang': rang}

    def _kleidung(self, modell):
        from Genesis9.kleidgenerisch import G9kleidgenerisch
        from Genesis9.koerpernetz import G9koerpernetz
        from Genesis9.netzstufe import G9netzstufe

        from ..api.g9figur import G9figur
        from ..api.g9garderobe import G9garderobeapi
        from .g9kleidmischbau import G9kleidmischbau
        rumpf = self._rumpf(modell, modell.KLEIDUNG, modell.kleidung, 0)
        folge, uebergang = G9kleidgenerisch.mischung_aufloesen(modell.KLEIDUNG, rumpf['regler_stueck'])
        if not folge:
            return []
        roh = {}

        def kleid(kennung, eintrag, r, vor_antwort=None):
            def sammeln(nummer, netz):
                roh.setdefault(kennung, []).append(netz)
                return vor_antwort(nummer, netz) if vor_antwort else netz
            return G9garderobeapi._kleid(kennung, eintrag, r, vor_antwort=sammeln)

        if len(folge) > 1:
            rumpf = dict(rumpf, regler_stueck=G9kleidgenerisch.ohne_textur(rumpf['regler_stueck']))
            koerper = lambda: G9koerpernetz(G9figur.formung(rumpf, {}), stufen=G9netzstufe.browser()).bindungsflaeche()  # noqa: E731
            aus = Teilevorrat.antwort('kleidung', rumpf, lambda: G9kleidmischbau.antwort(
                rumpf, kleid, modell.KLEIDUNG, folge, uebergang, koerper), roh)
        else:
            kennung, _anteil, regler = folge[0]
            from Genesis9.garderobe import G9garderobe
            aus = Teilevorrat.antwort('kleidung', rumpf, lambda: kleid(
                kennung, G9garderobe.eintrag(kennung) or {}, dict(rumpf, regler_stueck=regler)), roh)
            if not isinstance(aus, HttpResponse):
                for teil in aus.get('teile') or []:
                    teil['sorte'] = kennung
        return self._teile(aus, roh, 'kleidung', modell)

    def _haar(self, modell):
        from ..api.g9garderobe import G9garderobeapi
        from .g9haarmischbau import G9haarmischbau
        if not modell.frisuren():
            return []
        rumpf = self._rumpf(modell, modell.HAAR, modell.haar, 1)
        roh = {}

        def kleid(kennung, eintrag, r, vor_antwort=None):
            def sammeln(nummer, netz):
                roh.setdefault(kennung, []).append(netz)
                return vor_antwort(nummer, netz) if vor_antwort else netz
            return G9garderobeapi._kleid(kennung, eintrag, r, vor_antwort=sammeln)

        aus = Teilevorrat.antwort('haar', rumpf, lambda: G9haarmischbau.antwort(rumpf, kleid), roh)
        return self._teile(aus, roh, 'haar', modell)

    def _teile(self, aus, roh, art, modell):
        if isinstance(aus, HttpResponse):
            raise RuntimeError('%s: %s' % (art, getattr(aus, 'content', b'')[:300].decode('utf-8', 'replace')))
        toenungen = {sorte: np.asarray(self._hex(modell.stueckfarbe(art, sorte))) for sorte in roh}
        grund = np.asarray(self._hex(modell.farben[art]))
        farben = {sorte: self._farbe(netze, toenungen[sorte]) for sorte, netze in roh.items()}
        teile = []
        for teil in aus.get('teile') or []:
            if teil is None or not teil.get('vertex_count'):
                continue
            punkte = self._feld(teil['vertices'], np.float32).reshape(-1, 3).astype(np.float64)
            dreiecke = self._feld(teil['faces'], np.uint32).reshape(-1, 3).astype(np.int64)
            if not len(dreiecke):
                continue
            sorte = teil.get('sorte') or art
            haut = self._haut_aus(teil)
            if teil.get('art') == 'strang':
                # Stranghaar: je Segment ein Band (`G9haarprofil`), Haut vom Strähnenpunkt; Mitsuba rendert die Strähnen
                # als Kurven (`kurven`), Masken, Netznote und GLB bleiben beim Band (01.10.2026).
                kurven = self._kurven(teil, punkte, dreiecke, modell, sorte, haut)
                punkte, dreiecke, haut = self._band(teil, punkte, dreiecke, haut, modell, sorte)
                teile.append({'punkte': punkte, 'dreiecke': dreiecke, 'farbe': farben.get(sorte, grund),
                              'haut': haut, 'art': art, 'sorte': sorte, 'uv': None, 'normalen': None, 'gruppen': [],
                              'toenung': toenungen.get(sorte, grund), 'textur': [], 'strang': True, 'kurven': kurven})
                continue
            # UV, Normalen und Materialgruppen (mit ihren Bildern, `G9kleidtexturen` schon eingerechnet) für den Render
            # mit Texturen und die Fotoprojektion (30.09.2026, nachts).
            uv = self._feld(teil['uvs'], np.float32).reshape(-1, 2).astype(np.float64) if teil.get('uvs') else None
            normalen = (self._feld(teil['normals'], np.float32).reshape(-1, 3).astype(np.float64)
                        if teil.get('normals') else None)
            gruppen = [dict(g) for g in (teil.get('gruppen') or []) if isinstance(g, dict)]
            toenung = toenungen.get(sorte, grund)
            teile.append({'punkte': punkte, 'dreiecke': dreiecke, 'farbe': farben.get(sorte, toenung),
                          'haut': self._haut_aus(teil), 'art': art, 'sorte': sorte, 'uv': uv, 'normalen': normalen,
                          'gruppen': gruppen, 'toenung': toenung,
                          'textur': self._textur(gruppen, {g['name']: g.get('bilder') or {} for g in gruppen}, toenung)})
        return teile

    @staticmethod
    def _band(teil, punkte, dreiecke, haut, modell, sorte):
        from Genesis9.haargenerisch import G9haargenerisch
        from Genesis9.haarprofil import G9haarprofil
        anteil = Kleidermodellbau._feld(teil['anteil'], np.float32) if teil.get('anteil') is not None else None
        wurzel, spitze = G9haarprofil.werte(G9haargenerisch.regler_von(sorte, modell.haar))
        neu, dreiecke_neu, quelle = G9haarprofil.bandnetz(punkte, dreiecke, anteil, wurzel, spitze)
        if haut is not None:
            haut = {'knochen': haut['knochen'], 'index': haut['index'][quelle], 'gewicht': haut['gewicht'][quelle]}
        return neu, dreiecke_neu, haut

    @staticmethod
    def _kurven(teil, punkte, dreiecke, modell, sorte, haut=None):
        """Strähnen als Mitsuba-Kurven: Punkte, Reihenfolge, Längen, Radius (m), Haut (für `G9haltungshaut`)."""
        from Genesis9.haargenerisch import G9haargenerisch
        from Genesis9.haarprofil import G9haarprofil
        from Genesis9.haarzusatz import G9haarzusatz
        ketten = [k for k in G9haarzusatz.ketten(G9haarprofil.segmente_aus(dreiecke), len(punkte)) if len(k) >= 2]
        if not ketten:
            return None
        anteil = (Kleidermodellbau._feld(teil['anteil'], np.float32).astype(np.float64) if teil.get('anteil') is not None
                  else np.zeros(len(punkte)))
        if len(anteil) != len(punkte):
            anteil = np.zeros(len(punkte))
        wurzel, spitze = G9haarprofil.werte(G9haargenerisch.regler_von(sorte, modell.haar))
        return {'punkte': np.asarray(punkte, dtype=np.float32), 'reihe': np.concatenate(ketten), 'haut': haut,
                'laengen': np.asarray([len(k) for k in ketten], dtype=np.int64),
                'radius': (0.5e-3 * (wurzel + (spitze - wurzel) * np.clip(anteil, 0.0, 1.0))).astype(np.float32)}

    @staticmethod
    def _textur(gruppen, bilder, toenung):
        u"""`[{ab, anzahl, albedo, normalen, faktor}]` je Materialgruppe (Dreiecke, Pfade, Farbfaktor = Daz-Farbe ×
        2 × Tönung) — leer, wenn keine Gruppe ein Bild trägt (dann bleibt der Render flach)."""
        from Genesis9.material import G9material
        aus = []
        for g in gruppen:
            b = bilder.get(g['name']) or {}
            albedo = G9material.datei(b['albedo']) if b.get('albedo') else None
            normalen, alpha = (G9material.datei(b[k]) if b.get(k) else None for k in ('normalen', 'alpha'))
            farbe = b.get('farbe')
            faktor = np.asarray(farbe[:3], dtype=np.float64) if isinstance(farbe, (list, tuple)) and len(farbe) >= 3 \
                else np.ones(3)
            aus.append({'ab': int(g['index_ab']) // 3, 'anzahl': int(g['index_anzahl']) // 3, 'albedo': albedo,
                        'normalen': normalen, 'alpha': alpha, 'opazitaet': b.get('opazitaet'), 'normalenachse': int(b.get('normalenachse') or 1),
                        'metall': b.get('metallgewicht'), 'rauheit': b.get('rauheitwert') if b.get('metallgewicht') else None,      # nur Metallstücke (Stiefel): sonst bleibt der Render matt
                        'faktor': np.clip(faktor * 2.0 * np.asarray(toenung), 0.0, 1.0)})
        return aus if any(t['albedo'] is not None or t['opazitaet'] is not None for t in aus) else []

    @classmethod
    def textur_auffrischen(cls, teile, modell, sorten):
        u"""Die Texturen der Teile dieser Sorten neu aus den Daz-Bildern und den Schichten komponieren — nach einer
        Fotoprojektion in der Runde, damit der Render derselben Runde die Schicht schon zeigt."""
        from Genesis9.garderobe import G9garderobe
        from Genesis9.haargenerisch import G9haargenerisch
        from Genesis9.kleidgenerischwahl import G9kleidgenerischwahl
        from Genesis9.kleidtexturen import G9kleidtexturen
        from Genesis9.kleidtransparenz import G9kleidtransparenz
        for t in teile:
            sorte = t.get('sorte')
            if sorte not in sorten or not t.get('gruppen'):
                continue
            regler = (G9haargenerisch.regler_von(sorte, modell.haar) if t['art'] == 'haar'
                      else G9kleidgenerischwahl.regler_von(sorte, modell.kleidung))
            bilder = G9kleidtransparenz.anwenden(sorte, G9kleidtexturen.anwenden(sorte, G9garderobe.bilder(sorte), regler), regler)
            t['textur'] = cls._textur(t['gruppen'], bilder, t['toenung'])

    @staticmethod
    def _hex(text):
        roh = str(text or '').lstrip('#')
        if len(roh) != 6:
            return (0.5, 0.5, 0.5)
        return tuple(int(roh[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    def teile(self, modell):
        """Körper (mit Augen, Mund, Wimpern, Brauen — `Koerperanhaenge`, 02.10.2026), Kleider, Haar."""
        return [self.koerper()] + Koerperanhaenge.teile(self, modell) + self._kleidung(modell) + self._haar(modell)

    # ------------------------------------------------------------------ GLB

    def glb(self, teile, pfad):
        """Alle Teile in der A-Pose als GLB mit Rig (`Rundenglb`, seit 01.10.2026; davor ohne Skelett)."""
        from .rundenglb import Rundenglb
        pfad.parent.mkdir(parents=True, exist_ok=True)
        Rundenglb(self.formung.skelett().bauen()['knochen']).alle(teile).schreiben(pfad)
        return pfad
