# -*- coding: utf-8 -*-
"""Meshfigurvorschau — Schritt „vorschau" von „Mesh to 3D": Bilder, Abstände, Testfall.

* Bilder der Figur (`G9vorschaubild`, Käfig der Endstellung samt Eigenmorph): Icon für die
  Tabelle, vorn, seitlich, hinten, Kopf.
* Abstände zum Netz und das Vergleichsbild (Netz · Figur · Tiefenvergleich) aus dem Runner
  (`bewertung`: die ECHT gerechnete Endfigur in der Haltung des Netzes).
* Testfall: mit Referenzfigur (Option `referenz`, eine Figur der Genesis-Bibliothek) wird das
  Ergebnis Punkt für Punkt und Fläche gegen Fläche gemessen — dieselbe Rechnung wie im Reiter
  „3D" (`Bildmodelltestfall`), dazu nach Procrustes mit Maßstab, weil ein Netz aus dem Reiter
  „Mesh" seine Größe nicht kennt (dort auf 170 cm samt Haar gebracht).
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurvorschau']


class Meshfigurvorschau:
    BILDER = {'vorn': 'vorschau_vorn.png', 'seite': 'vorschau_seite.png', 'hinten': 'vorschau_hinten.png'}

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = lauf.optionen

    def ausfuehren(self):
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung
        from Genesis9.vorschaubild import G9vorschaubild

        from .meshfigurgenesis import Meshfigurgenesis

        stellung = self.job.stellung()
        if not stellung:
            raise RuntimeError('Regler fehlen — Schritte „koerper"/„gesicht" zuerst')
        punkte, _, _ = G9reglerableitung.lage(G9formung(stellung))
        bild = G9vorschaubild(punkte, kacheln=self.kacheln())
        dateien = {'icon': 'icon.png'}
        # Von vorn wie das Vorlagebild daneben (`Meshfigurlauf.vorlage`), nicht dreiviertel.
        bild.speichern(self.ablage.ergebnis('icon.png'), 'vorn', 256, 256)
        for ansicht, name in self.BILDER.items():
            bild.speichern(self.ablage.ergebnis(name), ansicht)
            dateien[ansicht] = name
        bild.speichern(
            self.ablage.ergebnis('vorschau_kopf.png'),
            'vorn',
            600,
            600,
            (float(punkte[:, 1].max()) - 0.28, float(punkte[:, 1].max()) + 0.02),
        )
        dateien['kopf'] = 'vorschau_kopf.png'
        self.lauf.melden(0.2, 'Endfigur am Netz messen')
        haltung = (self.job.ergebnis.get('koerper') or {}).get('haltung') or {}
        Meshfigurgenesis(stellung, haltung).speichern(self.ablage.arbeit('genesis_ende.npz'))
        e = self.lauf.runner('bewertung', von=0.25, bis=0.85)
        dateien['vergleich'] = e.get('bild')
        verlauf = e.get('verlauf') or [{}]
        self.job.ergebnis['vorschau'] = {
            'dateien': dateien,
            'hoehe_cm': round(float(punkte[:, 1].max()) * 100, 1),
            'abstand': verlauf[-1],
            'haut': e.get('haut'),
        }
        self.lauf.melden(0.87, 'Haar als Objekt')
        self.haarobjekt()
        self.lauf.melden(0.88, 'Kleidung als Objekt')
        self.kleidungsobjekt()
        self.lauf.melden(0.9, 'Testfall')
        self.job.ergebnis['testfall'] = self.testfall(stellung, punkte)

    def kleidungsobjekt(self):
        """Die Kleidung aus Schritt „kleidung" als Objekt auf der Figur (`Meshfigurkleidung.objekt`) — wie das Haar
        erst jetzt, wenn `genesis_ende.npz` und `posiert.npy` zur Figur gehören (das Netz steht in der Haltung der
        Person, die Bühne zeigt die Figur in Ruhe). Scheitert es, steht der Grund in `ergebnis.kleidung.objekt`;
        die Vorschau selbst ist davon unberührt."""
        from .meshfigurkleidung import Meshfigurkleidung

        try:
            Meshfigurkleidung(self.lauf).objekt()
        except Exception as fehler:  # noqa: BLE001 — sichtbar im Ergebnis und im Log, der Lauf geht weiter
            logger.exception('Mesh to 3D %s: Kleidungsobjekt gescheitert', self.job.kennung)
            if self.job.ergebnis.get('kleidung'):
                self.job.ergebnis['kleidung']['objekt'] = {'fehler': str(fehler)[:300]}

    def haarobjekt(self):
        """Das Haar aus Schritt „haar" als Objekt auf der Figur (`Meshfigurhaar.objekt`) — hier, weil erst
        jetzt `genesis_ende.npz` zur Figur gehört. Scheitert es, steht der Grund in `ergebnis.haar.objekt`;
        die Vorschau selbst ist davon unberührt."""
        from .meshfigurhaar import Meshfigurhaar

        try:
            Meshfigurhaar(self.lauf).objekt()
        except Exception as fehler:  # noqa: BLE001 — sichtbar im Ergebnis und im Log, der Lauf geht weiter
            logger.exception('Mesh to 3D %s: Haarobjekt gescheitert', self.job.kennung)
            if self.job.ergebnis.get('haar'):
                self.job.ergebnis['haar']['objekt'] = {'fehler': str(fehler)[:300]}

    def kacheln(self):
        """Die Kacheln aus Schritt „textur" (`{kachel: Pfad}`) — die Bilder zeigen die Figur mit
        der Haut, die Szene und Export tragen (27.09.2026). Leer ohne Fototextur."""
        f = self.job.ergebnis.get('fototextur') or {}
        pfade = {k: self.ablage.ergebnis(n) for k, n in (f.get('kacheln') or {}).items()}
        return {k: p for k, p in pfade.items() if p.is_file()}

    # -------------------------------------------------------------- Testfall

    def testfall(self, stellung, punkte):
        """Gegen die Referenzfigur (Genesis-Käfig gegen Genesis-Käfig) — None ohne Referenz."""
        from Genesis9.charaktere import G9charaktere
        from Genesis9.netzbereiche import G9netzbereiche

        from .bildmodelltestfall import Bildmodelltestfall

        name = self.optionen.get('referenz')
        if not name:
            return None
        eintrag = G9charaktere.eintrag(name)
        if eintrag is None:
            return {'fehler': 'Referenz %s nicht im Katalog' % name}
        ref, _ = Bildmodelltestfall.kaefig(eintrag['regler'])
        mod = np.asarray(punkte, float)
        # Gemessen wird die ganze Haut samt Zehen (Bereich 6 seit 27.09.2026) — ohne Finger und Innenräume.
        haut = np.isin(G9netzbereiche.bereiche(), (0, 1, 5, 6))
        mm = lambda a: round(float(np.sqrt((a[haut] ** 2).mean())) * 1000.0, 2)  # noqa: E731
        punkt, flaeche, s = self._vergleich(mod, ref, haut)
        e_regler = self.job.ergebnis.get('regler') or {}
        nur, _ = Bildmodelltestfall.kaefig(dict(e_regler.get('stellung') or {}))
        grund, _ = Bildmodelltestfall.kaefig(dict(e_regler.get('grund') or {}))
        _, nur_flaeche, _ = self._vergleich(nur, ref, haut)
        _, grund_flaeche, _ = self._vergleich(grund, ref, haut)
        return {
            'flaeche_je_teil_mm': self.je_teil(flaeche, haut),
            'figur': eintrag['name'],
            'anzeige': eintrag.get('anzeige') or eintrag['name'],
            'blind': self.optionen.get('blind') == 'an',
            'hoehe_cm': {
                'referenz': round(float(ref[:, 1].max()) * 100, 1),
                'modell': round(float(mod[:, 1].max()) * 100, 1),
            },
            'punkt_mm': mm(np.linalg.norm(mod - ref, axis=1)),
            'procrustes_massstab': round(float(s), 4),
            'punkt_ausgerichtet_mm': mm(punkt),
            'flaeche_ausgerichtet_mm': mm(flaeche),
            # Dieselbe Messung nur mit den Reglern (ohne Eigenmorph) und für die Grundfigur: zeigt, ob
            # der Eigenmorph zur Referenz hin oder nur zum Netz hin führt (das Netz ist nicht die Wahrheit).
            'nur_regler_flaeche_mm': mm(nur_flaeche),
            'grundfigur_flaeche_mm': mm(grund_flaeche),
        }

    @staticmethod
    def _vergleich(mod, ref, haut):
        """`(punktabstand, flächenabstand, maßstab)` nach Procrustes MIT Maßstab (ein Netz aus dem
        Reiter „Mesh" kennt seine Größe nicht) — je Käfigpunkt, Meter."""
        from Genesis9.zielnetz import G9zielnetz

        from .bildmodelltestfall import Bildmodelltestfall

        r, s, t = G9zielnetz.procrustes(mod[haut], ref[haut])
        ausgerichtet = s * mod @ r.T + t
        return (
            np.linalg.norm(ausgerichtet - ref, axis=1),
            Bildmodelltestfall.flaechenabstand(ausgerichtet, ref),
            s,
        )

    @staticmethod
    def je_teil(abstand, haut):
        """RMS in mm je Körperteil, nur über Hautpunkte (Innenräume und Finger verwässern sonst)."""
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile

        teil = G9koerperteile.genesis_punkte(G9haut.holen())
        aus = {}
        for i, name in enumerate(G9koerperteile.TEILE):
            drin = haut & (teil == i)
            if drin.any():
                aus[name] = round(float(np.sqrt((abstand[drin] ** 2).mean())) * 1000.0, 2)
        return aus
