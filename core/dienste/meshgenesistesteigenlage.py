# -*- coding: utf-8 -*-
"""Meshgenesistesteigenlage — die Ruhelage eines eigenen Stücks auf der Grundfigur, im Speicher gerechnet (25.11.2026, Edgar: „alles auf Karte, nichts auf CPU!“).

Bis dahin schrieb `Meshgenesistesteigenstueck` das Stück als OBJ, las es zurück, schrieb es als DSON in der Lage der vorhergesagten Figur, las es über die Garderobe (`G9gcfigurbau.folger`), rechnete
die Ruhelage, schrieb es noch einmal, las es noch einmal für die Prüfung und bei mehr als `NACHRECHNEN_MM` ein drittes Mal. Dieselben Rechnungen hier mit `G9eigenfolger`; geschrieben wird einmal, vom
Aufrufer. Gegen den alten Weg: `ProjektTemp/_wegwerf/tempo_kette/eigenlage_probe.py`.

    netz = Meshgenesistesteigenlage.netz(arbeit, punkte, dreiecke, uv_ecken)          # wie `G9objleser.lesen`, als Tensoren; legt `stueck.obj` in den Arbeitsordner
    ruhe, bericht, angezogen = Meshgenesistesteigenlage(netz, kennung, name, kategorie, art, knochen, gewichte, regler).rechnen(3.0)
"""
import json

import torch

__all__ = ['Meshgenesistesteigenlage']


class Meshgenesistesteigenlage:
    #: (Regler als Text, `G9formung`) des letzten Stücks — alle Stücke eines Laufs stehen auf derselben Figur
    _formung = (None, None)

    def __init__(self, netz, kennung, name, kategorie, art, knochen, gewichte, regler):
        """`gewichte`: Aufruf (Lage) → `{knochen: [[punkt, gewicht], …]}` oder None (dann `knochen` bzw. die drei nächsten Hautpunkte, wie `G9eigenstueck.schreiben`)."""
        from Genesis9.dsonschreiber import G9dsonschreiber
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.pfade import G9pfade
        self.netz, self.knochen, self.gewichte, self.regler = netz, knochen, gewichte, regler
        self.schreiber = G9dsonschreiber(G9pfade.eigene(), G9eigenstueck.HERSTELLER, name, kennung, art)
        self.koerper, _dreiecke, _normalen, self.baum, self.boden = G9eigenstueck.koerper()
        self.schuh = self._schuh(name, kategorie, art)

    @staticmethod
    def netz(arbeit, punkte, dreiecke, uv_ecken):
        """Punkte und UV wie in der OBJ-Datei auf sechs Stellen; eine UV je Ecke."""
        from KoerperKI_alle.objtext import Objtext
        roh, uv = (torch.round(x.to('cuda', torch.float64) * 1e6) / 1e6 for x in (punkte, uv_ecken.reshape(-1, 2)))
        dreiecke = dreiecke.to('cuda', torch.int64).reshape(-1, 3)
        ecken = torch.arange(3 * len(dreiecke), device='cuda').reshape(-1, 3)
        (arbeit / 'stueck.mtl').write_text('newmtl Stoff\nKd 1 1 1\n', encoding='utf-8')
        (arbeit / 'stueck.obj').write_bytes(Objtext.karte(roh, uv, dreiecke, 'mtllib stueck.mtl\nusemtl Stoff\n'))
        return {'punkte': roh, 'uvs': uv, 'flaechen': dreiecke, 'flaechen_uv': ecken, 'farbe': (1.0, 1.0, 1.0), 'bild': None}

    def _schuh(self, name, kategorie, art):
        """Ob die Garderobe das Stück unter „Schuhe“ führt (`G9garderobeteile`: starre Zehen) — Edgars Zuordnung, sonst die Vorgabe aus der Kategorie, die der Schreiber einträgt."""
        from Genesis9.dazkategorien import G9dazkategorien
        from Genesis9.garderobekategorien import G9garderobekategorien
        from Genesis9.garderobekennung import G9garderobekennung
        s = self.schreiber
        kennung = G9garderobekennung.fuer(s.duf)
        fest = G9garderobekategorien.laden()['zuordnung'].get(kennung)
        if fest is None:
            rel = s.duf.relative_to(s.wurzel)
            eintrag = {'id': kennung, 'name': name, 'art': 'haar' if art == 'Hair' else 'kleidung', 'wurzel': rel.parents[1].as_posix(), 'datei': '/'.join(rel.parts[-2:])}
            fest = G9dazkategorien.vorgabe(eintrag, {G9dazkategorien.schluessel(rel.as_posix()): (kategorie[0], [kategorie[1].removeprefix('/Default/')])})
        return fest == 'Schuhe'

    def formung(self):
        from Genesis9.gcfigurbau import G9gcfigurbau
        text = json.dumps(self.regler, sort_keys=True)
        if Meshgenesistesteigenlage._formung[0] != text:
            Meshgenesistesteigenlage._formung = (text, G9gcfigurbau.formung(self.regler))
        return Meshgenesistesteigenlage._formung[1]

    def folger(self, lage):
        from Genesis9.eigenfolger import G9eigenfolger
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.mbstuecke import G9mbstuecke
        from Genesis9.stueckersatz import G9stueckersatz
        g = self.gewichte(lage)
        if g is None and self.knochen is not None:
            G9eigenstueck.gewichte_auf(self.knochen, 0)          # unbekannter Knochen: ValueError wie beim Schreiben
            g = {self.knochen: torch.stack([torch.arange(len(lage), dtype=torch.float64, device='cuda'), torch.ones(len(lage), dtype=torch.float64, device='cuda')], 1)}
        elif g is None:
            g = G9mbstuecke.gewichte(lage, self.koerper, self.baum)
        return G9eigenfolger(self.schreiber.dsf, lage, self.boden, self.netz['flaechen'], g, self.schuh, not G9stueckersatz.eigene_gewichte(self.schreiber.duf))

    def rechnen(self, nachrechnen_mm=None):
        """→ (Ruhelage, Bericht, angezogen); folgt das Stück dem Ziel schlechter als `nachrechnen_mm` (p99), ein zweiter Durchgang, behalten, wenn er besser ist."""
        from Genesis9.gcfigurbau import G9gcfigurbau
        roh, formung, name = self.netz['punkte'], self.formung(), self.schreiber.kennung
        ruhe, bericht = G9gcfigurbau.ruhelage_mit(self.folger(roh), formung, roh, roh, name)
        folger = self.folger(ruhe)
        angezogen = G9gcfigurbau.pruefen_mit(folger, formung, roh)
        if nachrechnen_mm is not None and angezogen['p99_mm'] > nachrechnen_mm:
            ruhe2, bericht2 = G9gcfigurbau.ruhelage_mit(self.folger(ruhe), formung, roh, ruhe, name)
            angezogen2 = G9gcfigurbau.pruefen_mit(self.folger(ruhe2), formung, roh)
            if (angezogen2['p99_mm'], angezogen2['max_mm']) < (angezogen['p99_mm'], angezogen['max_mm']):
                return ruhe2, dict(bericht2, zweiter_durchgang=True), angezogen2
            bericht['zweiter_durchgang'] = 'verworfen'
        return ruhe, bericht, angezogen
