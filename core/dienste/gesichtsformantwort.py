# -*- coding: utf-8 -*-
"""Gesichtsformantwort — was die Seite „Gesichtsform" zu einer Figur bekommt (Millimeter im Rahmen).

    ist        die Figur OHNE ihren Kopf-Eigen-Morph (Schnitte, Konturpunkte) — Rahmen `rahmen`
    ergebnis   die Figur MIT ihm, falls es ihn gibt — in ihrem eigenen Rahmen `ergebnis.rahmen`
    ziel       Zielkurven: die zuletzt gerechneten (Steckbrief des Morphs), sonst aus dem Netz des
               Auftrags (`Gesichtsformziel`), sonst keine (dann wird gemalt, Ausgang = Ist)
    guete      je Schnitt und Kontur, aus der letzten Rechnung

Die Figur der 3D-Ansicht ist `stellung` samt Kopf-Eigen (Wert `wert`), mit den Kacheln `fototextur`.
"""

import numpy as np

__all__ = ['Gesichtsformantwort']


class Gesichtsformantwort:
    def __init__(self, quelle, waagerecht=7, senkrecht=7, ziel_neu=False):
        self.quelle = quelle
        self.waagerecht = max(3, min(12, int(waagerecht or 7)))
        self.senkrecht = max(3, min(12, int(senkrecht or 7)))
        self.ziel_neu = bool(ziel_neu)

    def bauen(self):
        from Genesis9.gesichtsrahmen import G9gesichtsrahmen
        from Genesis9.gesichtsschnitte import G9gesichtsschnitte as S
        from Genesis9.schnittmorph import G9schnittmorph

        from .gesichtsformziel import Gesichtsformziel

        name, stellung = self.quelle.name(), self.quelle.stellung()
        if not stellung:
            raise ValueError('Die Figur hat noch keine Regler — erst die Anpassung rechnen')
        morph = G9schnittmorph(stellung, name)
        kaefig = morph.figur()
        brief = G9schnittmorph.steckbrief(name)
        ziel, zielquelle = None, None
        if brief.get('ziel', {}).get('schnitte') and not self.ziel_neu:
            ziel, zielquelle = G9schnittmorph.ziel_aus_seite(brief['ziel']), 'gespeichert'
            lagen = G9schnittmorph.lagen_von(ziel)
        else:
            lagen = S(morph.rahmen).lagen(self.waagerecht, self.senkrecht)
            job = self.quelle.zielauftrag()
            if job is not None and Gesichtsformziel(job).vorhanden():
                ziel, zielquelle = Gesichtsformziel(job).ziel(lagen, morph.rahmen), 'netz'
        vorhanden = bool(brief)
        wert = float(stellung.get(morph.regler, 1.0 if vorhanden else 0.0))
        figur = dict(morph.stellung)
        if vorhanden and wert > 0:
            figur[morph.regler] = wert
        return {
            'name': name,
            'titel': self.quelle.titel(),
            'regler': morph.regler,
            'vorhanden': vorhanden,
            'wert': wert,
            'stellung': figur,
            'fototextur': self.quelle.fototextur(),
            'konturen': {k: list(v) for k, v in G9gesichtsrahmen.KONTUREN.items()},
            'lagen': {k: [round(w * 1000, 2) for w in v] for k, v in lagen.items()},
            'rahmen': morph.rahmen.als_dict(),
            'ist': self._block(morph.messen(kaefig, lagen, augen=True), morph.rahmen),
            'ergebnis': self._ergebnis(figur, name, lagen, morph.rahmen) if vorhanden and wert > 0 else None,
            'ziel': self._ziel(ziel) if ziel else None,
            'zielquelle': zielquelle,
            'guete': brief.get('guete'),
            'max_mm': brief.get('max_mm'),
        }

    @staticmethod
    def _punkte(landmarken):
        from Genesis9.gesichtsrahmen import G9gesichtsrahmen

        aus = {}
        for k in G9gesichtsrahmen.KONTUREN:
            for j in G9gesichtsrahmen.KONTUREN[k]:
                if np.isfinite(landmarken[j]).all():
                    aus[str(j)] = np.round(landmarken[j][:2] * 1000, 2).tolist()
        return aus

    def _block(self, messung, rahmen):
        from Genesis9.gesichtsschnitte import G9gesichtsschnitte as S

        return {'schnitte': S.als_liste(messung['schnitte']), 'punkte': self._punkte(messung['landmarken']),
                'rahmen': {'ursprung': rahmen.ursprung.tolist(), 'achsen': rahmen.achsen.tolist()}}

    def _ergebnis(self, figur, name, lagen, rahmen):
        """Die Figur mit dem Morph — im Rahmen der Figur OHNE ihn: ein fester Rahmen für Ist, Ergebnis und
        Ziel (die Landmarken wandern mit dem Morph; ein eigener Rahmen verdrehte den Vergleich)."""
        from Genesis9.schnittmorph import G9schnittmorph

        mit = G9schnittmorph(figur, name + ' ·')  # anderer Name: der eigene Morph bleibt in der Stellung
        kaefig = mit.figur()
        mit.rahmen = rahmen
        return self._block(mit.messen(kaefig, lagen, augen=True), rahmen)

    def _ziel(self, ziel):
        from Genesis9.gesichtsschnitte import G9gesichtsschnitte as S

        punkte = {str(j): np.round(np.asarray(v[:2]) * 1000, 2).tolist() for j, v in ziel['punkte'].items()}
        return {'schnitte': S.als_liste(ziel['schnitte']), 'punkte': punkte}
