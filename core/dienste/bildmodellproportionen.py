# -*- coding: utf-8 -*-
"""Bildmodellproportionen — Vorher/Nachher-Bilder mit Maßlinien je Ansicht.

Edgar (19.09.2026): „alle Ansichten aus der zweiten Zeile in jeweils einer
Zeile einbringen. Vorher und nachher Bild. … in jedem Bild die Körper-
proportionen zeigen … Ich brauche dann ein Bild wie ich das eingestellt
habe und eines wie das aus dem Modell kommt."

VORHER ist das Zielnetz — mit Edgars Eingaben geformt („wie ich das
eingestellt habe", `Bildmodellzielproportionen`) —, NACHHER das Modell
(Regler plus Restmorph). Beide sind Genesis-Käfige, beide werden mit
derselben orthografischen Kamera gerendert (`G9proportionenbild`) und mit
derselben Messfunktion gemessen (`G9proportionen`); die Endpunkte jeder
Linie kommen als Pixel mit, der Browser zeichnet sie als SVG über das
Bild. Ungepaarte Punkte des Ziels (Mundhöhle, Fingerkuppen) nehmen für
das Bild die Lage des Modells — sonst stünden dort die Rohpositionen.

Läuft im Schritt „vorschau", Ergebnis in `ergebnis.proportionen`.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Bildmodellproportionen']


class Bildmodellproportionen:
    """Maße und Bilder für die Proportionszeilen der Auftragsseite."""

    ANSICHTEN = ('vorn', 'seite', 'hinten', 'kopf')
    #: Welche Maße in welcher Ansicht gezeichnet werden (hinten: die Breiten von vorn).
    GEZEICHNET = {'vorn': ('vorn',), 'seite': ('seite',), 'hinten': ('vorn',), 'kopf': ('kopf',)}

    def __init__(self, job, ablage, stellung, ziel_laden):
        self.job = job
        self.ablage = ablage
        self.stellung = stellung
        self._ziel_laden = ziel_laden

    def modell(self):
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung

        f = G9formung(self.stellung)
        p, _, _ = G9reglerableitung.lage(f)
        gelenke = {e['name']: np.asarray(e['kopf'], float) for e in f.skelett().gelenkknochen()}
        return np.asarray(p, float), gelenke

    def alle(self, melder=None):
        from Genesis9.proportionen import G9proportionen
        from Genesis9.proportionenbild import G9proportionenbild

        pr = G9proportionen()
        ziel_p, gewicht, ziel_g = self._ziel_laden()
        modell_p, modell_g = self.modell()
        ok = gewicht > 0
        ziel = pr.messen(ziel_p, ziel_g, ok)
        modell = pr.messen(modell_p, modell_g)
        # Ungepaarte Zielpunkte fürs Bild aus dem Modell.
        bild_p = np.where(ok[:, None], ziel_p, modell_p)
        bilder = {'ziel': G9proportionenbild(bild_p), 'modell': G9proportionenbild(modell_p)}
        befunde = {'ziel': ziel, 'modell': modell}
        ordner = self.ablage.ergebnis()
        # `nur_ansicht` (Knopf „Bild neu" je Zeile, 20.09.2026): nur diese Ansicht rendern,
        # die anderen Einträge bleiben aus dem letzten Ergebnis stehen.
        nur = (self.job.optionen or {}).get('nur_ansicht')
        alt = ((self.job.ergebnis.get('proportionen') or {}).get('ansichten') or {}) if nur else {}
        ansichten = {k: v for k, v in alt.items() if k in self.ANSICHTEN}
        for i, ansicht in enumerate(self.ANSICHTEN):
            if nur and ansicht != nur:
                continue
            if melder:
                melder(0.1 + 0.8 * i / len(self.ANSICHTEN), 'Proportionen: Ansicht %s' % ansicht)
            eintrag = {'linien': {}, 'bild': {}}
            for wer, bild in bilder.items():
                name = 'prop_%s_%s.png' % (ansicht, wer)
                bild.speichern_ortho(ordner / name, ansicht)
                eintrag['bild'][wer] = name
                linien = {}
                for k, e in befunde[wer].items():
                    if G9proportionen.ANSICHT[k] not in self.GEZEICHNET[ansicht]:
                        continue
                    uv = bild.projizieren(ansicht, [e['a'], e['b']])
                    linien[k] = [[round(float(u), 1), round(float(v), 1)] for u, v in uv]
                eintrag['linien'][wer] = linien
            breite, hoehe = G9proportionenbild.GROESSE[ansicht]
            eintrag.update(breite=breite, hoehe=hoehe,
                           px_je_m={wer: round(float(b.px_je_m(ansicht)), 2) for wer, b in bilder.items()})
            ansichten[ansicht] = eintrag
        anpassung = self.job.ergebnis.get('anpassung') or {}
        return {
            'masse': G9proportionen.katalog(),
            'ziel': G9proportionen.in_cm(ziel),
            'modell': G9proportionen.in_cm(modell),
            'formung': anpassung.get('proportionen'),
            'ansichten': ansichten,
        }
