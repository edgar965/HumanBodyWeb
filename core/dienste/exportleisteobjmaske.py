# -*- coding: utf-8 -*-
"""Exportleisteobjmaske — die OBJ der Exportleiste ohne die Haut unter den Stücken, mit derselben Maske wie GLB, .blend und Render (`Exportleistehautmaske`; 31.10.2026, offen war
„Der OBJ-Export behält wie bisher die ganze Haut“, Edgar: „mach alles was offen ist“).

Die OBJ schreibt der Browser (`Modellexport._obj`, Three.js `OBJExporter`): je Netz `o <Name>`, darunter `v`/`vt`/`vn` und Flächen `f a/b/c` mit Nummern über die ganze Datei,
in Weltlage (Pose des Exports; ohne laufende Animation die Ruhelage). Netze mit mehreren Materialzonen kommen zerlegt als `<Name>_<Zone>` mit eigenen Punkten (`Gruppennetze`):
Der Körper steht in mehreren Teilen, deren Ränder auf denselben Lagen liegen; `Exportleistehautmaske.maske` verschweißt sie wieder (sonst wäre jede kleine Zone eine freie Insel,
Test `test_eine_kleine_zone_ohne_stoff_bleibt`). Weg fällt eine Fläche des Körpers, deren Ecken alle verdeckt sind; ihre Punkte bleiben stehen (OBJ erlaubt unbenutzte Punkte). Welche Stücke decken, sagt die Seite
(`haut_deckt`, `Exportleistefigur.hautDeckt`; ein zerlegtes Stück zählt mit allen Zonen). Ohne Angabe deckt keins.

    text, bericht = Exportleisteobjmaske.text(text, deckend)
"""

import re

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from .exportleistehautmaske import Exportleistehautmaske

__all__ = ['Exportleisteobjmaske']


class Exportleisteobjmaske:
    #: Zonennummer, die `Gruppennetze.zerlegen` an den Namen hängt
    ZONE = re.compile(r'_\d+$')

    @classmethod
    def text(cls, text, deckend):
        """OBJ-Text → (Text ohne die verdeckten Körperflächen, Bericht `{stuecke, punkte_verdeckt, dreiecke_weg, dreiecke}`)."""
        zeilen = text.split('\n')
        punkte, flaechen = cls._lesen(zeilen)
        deckend = set(deckend or ())
        koerper = [f for name, fl in flaechen.items() if Exportleistehautmaske.KOERPER.match(name) for f in fl]
        stuecke = [cls._netz(punkte, fl) for name, fl in flaechen.items() if name in deckend or cls.ZONE.sub('', name) in deckend]
        bericht = {'stuecke': len(stuecke), 'punkte_verdeckt': 0, 'dreiecke_weg': 0, 'dreiecke': len(koerper)}
        if not koerper or not stuecke:
            return text, bericht
        verdeckt = cls._verdeckt(punkte, [e for _, e in koerper], stuecke)
        weg = [i for i, e in koerper if verdeckt[e].all()]
        bericht.update(punkte_verdeckt=int(verdeckt.sum()), dreiecke_weg=len(weg))
        if not weg:
            return text, bericht
        bleibt = torch.ones(len(zeilen), dtype=torch.bool, device='cuda')
        bleibt[weg] = False
        return '\n'.join(z for z, b in zip(zeilen, bleibt.tolist(), strict=True) if b), bericht

    @staticmethod
    def _lesen(zeilen):
        """→ (Punkte (N, 3), `{Netzname: [(Zeile, Ecken als Nummern ab 0)]}`)."""
        punkte, flaechen, objekt = [], {}, ''
        for i, z in enumerate(zeilen):
            art = z[:2]
            if art == 'v ':
                punkte.append(z[2:].split()[:3])
            elif art == 'f ':
                ecken = [int(t.split('/', 1)[0]) for t in z[2:].split()]
                flaechen.setdefault(objekt, []).append((i, Torchfeld.feld([n - 1 if n > 0 else len(punkte) + n for n in ecken], dtype=torch.int64)))
            elif art == 'o ':
                objekt = z[2:].strip()
        return Torchfeld.feld(punkte, dtype=torch.float64).reshape(-1, 3), flaechen

    @staticmethod
    def _dreiecke(ecken):
        """Flächen (Listen von Nummern) als Fächer zu Dreiecken (N, 3)."""
        return Torchfeld.feld([(e[0], e[k], e[k + 1]) for e in ecken for k in range(1, len(e) - 1)], dtype=torch.int64).reshape(-1, 3)

    @classmethod
    def _netz(cls, punkte, flaechen):
        """Ein Stück als (Punkte, Dreiecke) nur mit seinen Punkten."""
        t = cls._dreiecke([e for _, e in flaechen])
        genutzt, neu = Torchfeld.unique(t, return_inverse=True)
        return punkte[genutzt], neu.reshape(-1, 3)

    @classmethod
    def _verdeckt(cls, punkte, ecken, stuecke):
        """Bool je Punkt der Datei: verdeckt (nur Körperpunkte können es sein)."""
        genutzt, t = Torchfeld.unique(cls._dreiecke(ecken), return_inverse=True)
        verdeckt = torch.zeros(len(punkte), dtype=torch.bool, device='cuda')
        verdeckt[genutzt] = Exportleistehautmaske.maske(punkte[genutzt], t.reshape(-1, 3), stuecke)
        return verdeckt
