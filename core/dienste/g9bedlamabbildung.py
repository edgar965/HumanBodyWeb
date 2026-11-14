# -*- coding: utf-8 -*-
"""G9bedlamabbildung — zu jedem Texel der Genesis-9-Kacheln die UV auf dem SMPL-X-Netz (17.10.2026), damit BEDLAM-Hauttexturen auf Genesis passen.

Edgar, 17.10.2026: „mach alles was offen ist" — dazu die BEDLAM-Häute (Tabelle 12 in `genesis9-alter.md`): 100 Hautfotos (50 weiblich/50 männlich, sieben Herkunftsgruppen, MPI/Meshcapade,
CC-BY-NC-4.0 — nur nicht-kommerziell) in der UV von SMPL (`SMPL/xbedlamhaut.py`: Hautbilder für SMPL-X-Figuren gibt es schon). Genesis hat eine andere UV; darum hier die Abbildung

    Texel der Kachel (`G9texturabtastung`: Dreieck + Anteile) → Lage auf dem Käfig → in dieselbe NORMIERTE Lage wie die Paarung (`G9netzpaarung._normiert`: Füße 0, Höhe 1, x um 0, z um
    das Becken) → nächster Punkt auf den SMPL-X-Dreiecken desselben oder eines Nachbarteils (`G9koerperteile.nachbarn`, Augäpfel ausgenommen) → UV der Ecken (`meshcapade_uv.npz`)

— derselbe Weg und dieselbe Suche (`Hbdreiecksuche`) wie bei der Hautverschiebung. Die Abbildung hängt nur an den Netzen, nicht an der Textur: EINMAL gerechnet für alle 100 Häute, abgelegt als
`Genesis9/ablage/bedlamuv_<Seite>_v<Fassung>.npz` (UV als uint16, 1/65535 genau — feiner als ein Pixel der 4096er Textur). Aufbau dauert gemessen siehe `bauen` (Kennzahlen im Bericht).

GENAUIGKEIT: die Paarung legt Genesis' Nasenspitze auf 3,0 mm und das Kinn auf 7,0 mm an SMPL-X' (`gesicht_sx.py`, 17.10.2026) — Lippen und Brauen des Fotos liegen so um höchstens rund 7 mm neben
denen von Genesis. Das Foto ist für SMPL gebaut (keine Augäpfel): Genesis' Lider holen ihre Farbe von der Haut daneben.
"""
import logging
import time

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch

logger = logging.getLogger('core')

__all__ = ['G9bedlamabbildung']


class G9bedlamabbildung:
    """`holen()` → `{kachel: (S, S, 2) float32 UV}` oder None; `bauen()` rechnet und legt ab."""

    SEITE = 2048
    FASSUNG = 1
    _gemerkt = None

    @classmethod
    def pfad(cls):
        from Genesis9.pfade import G9pfade
        return G9pfade.ablage() / ('bedlamuv_%d_v%d.npz' % (cls.SEITE, cls.FASSUNG))

    @classmethod
    def vorhanden(cls):
        return Npztorch.da(cls.pfad())

    @classmethod
    def holen(cls):
        if cls._gemerkt is None and cls.vorhanden():
            try:
                with Npztorch.lesen(cls.pfad()) as d:
                    cls._gemerkt = {int(k): Torchfeld.astype(d['uv_%d' % k], torch.float32) / 65535.0 for k in d['kacheln']}
            except (OSError, KeyError, ValueError) as fehler:
                logger.warning('BEDLAM-Abbildung %s unlesbar (%s)', cls.pfad(), fehler)
        return cls._gemerkt

    @classmethod
    def vergessen(cls):
        cls._gemerkt = None

    # -------------------------------------------------------------- Bauen

    @classmethod
    def bauen(cls):
        """Alle Kacheln rechnen und ablegen → `{kachel: Texel}`."""
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile
        from Genesis9.netzpaarung import G9netzpaarung
        from Genesis9.texturabtastung import G9texturabtastung
        from Genesis9.zielnetz import G9zielnetz

        from .hbdreiecksuche import Hbdreiecksuche

        t0 = time.perf_counter()
        paarung = G9netzpaarung.holen()
        teil_g = G9koerperteile.genesis_punkte(G9haut.holen())
        kaefig, _h = G9netzpaarung._normiert(paarung.basis, teil_g)
        smplx, _h2 = G9netzpaarung._normiert(paarung.neutral.punkte, paarung.neutral.teil)
        faces = Torchfeld.feld(G9zielnetz.koerper().faces, dtype=torch.int64)
        vt, ft = cls._uv()
        if ft.shape != faces.shape:
            raise ValueError('UV-Dreiecke (%s) passen nicht zu den SMPL-X-Dreiecken (%s)' % (ft.shape, faces.shape))
        uvs = vt[ft]
        teil_dreieck = Torchfeld.feld(paarung.neutral.teil)[faces[:, 0]]
        auge = G9koerperteile.NUMMER['auge']
        erlaubt = G9koerperteile.nachbarn()
        suchen = {}

        def suche(teil):
            if teil not in suchen:
                m = torch.isin(teil_dreieck, Torchfeld.feld(list(erlaubt.get(teil, ())) if teil >= 0 else list(range(len(G9koerperteile.TEILE))))) & (teil_dreieck != auge)
                suchen[teil] = Hbdreiecksuche(smplx, faces[m], uvs[m]) if m.sum() >= 4 else None
            return suchen[teil]

        abtastung = G9texturabtastung.holen(cls.SEITE)
        aus, zahlen = {}, {}
        for kachel in abtastung.kacheln:
            drin, ecken, anteile = abtastung.stellen(kachel)
            lage = Torchfeld.einsum('nk,nkc->nc', anteile, kaefig[ecken])
            teil = teil_g[ecken[Torchfeld.arange(len(ecken)), anteile.argmax(1)]]
            uv = torch.zeros((len(lage), 2), dtype=torch.float64, device='cuda')
            for t in Torchfeld.liste(Torchfeld.unique(teil)):
                s = suche(int(t))
                m = teil == t
                if s is not None:
                    uv[m], _abstand = s.uv(lage[m])
            bild = torch.zeros((cls.SEITE, cls.SEITE, 2), dtype=torch.uint16, device='cuda')
            bild[drin] = Torchfeld.astype(Torchfeld.clip(uv * 65535.0 + 0.5, 0, 65535), torch.uint16)
            aus['uv_%d' % kachel] = bild
            zahlen[int(kachel)] = int(drin.sum())
            logger.info('BEDLAM-Abbildung Kachel %d: %d Texel (%.0f s)', kachel, zahlen[int(kachel)], time.perf_counter() - t0)
        ziel = cls.pfad()
        vorlaeufig = ziel.with_suffix('.neu.npz')
        Npztorch.speichern(vorlaeufig, kacheln=Torchfeld.feld(abtastung.kacheln, dtype=torch.int64), **aus, komprimiert=True)
        Npztorch.ersetzen(vorlaeufig, ziel)
        cls.vergessen()
        return zahlen

    @staticmethod
    def _uv():
        """`(vt, ft)` der Meshcapade-UV — dieselbe Datei wie `SMPL/xuv.py` (`BEVORZUGT`), ohne Django."""
        from Genesis9.pfade import G9pfade
        for name in ('meshcapade_uv.npz', 'smplx_uv.npz'):
            pfad = G9pfade.smplx() / name
            if Npztorch.da(pfad):
                with Npztorch.lesen(pfad) as d:
                    return Torchfeld.feld(d['vt'], dtype=torch.float64), Torchfeld.feld(d['ft'], dtype=torch.int64)
        raise FileNotFoundError('meshcapade_uv.npz fehlt in %s' % G9pfade.smplx())
