# -*- coding: utf-8 -*-
"""Bildmodellsilhouettenziel — das Zielnetz ohne 3D-Schätzer: Grundfigur → Umriss → Regler, in Runden.

Edgar (20.09.2026): „Soll ich von Null starten oder soll ich das GVHMR nutzen? …
4–5 Bilder einer Genesis-Person, daraus werden die Maße herausgenommen und
die Genesis-Schalter bedient, sodass eine Person herauskommt mit den gleichen
Maßen." — „mach das".

Gemessen (Ursula, Bilder aus der Figur selbst gerendert): SMPLest-X schätzt
alle Tiefen 3–5 cm zu klein (RMS 12,5 mm); was die Form wirklich brachte,
kam aus 2D — Fotomaße 11,5 mm, Umriss Zeile für Zeile 6,2 mm Flächenabstand.
Und das Modell folgt jedem Ziel auf unter 1 mm. Also formen hier die Bilder
die REGLER, nicht ein fremdes Netz — Analysis by Synthesis mit dem echten
parametrischen Modell:

    Runde k:  P = Käfig der Regler r(k−1)         (Start: Grundfigur)
              T = P auf die Körpergröße skaliert
              T = Umriss der Fotos auf T           (`Bildmodellumriss`, wie im Lauf)
              T = Kopfform vom Gesichtsschätzer     (PyMAF-X, wenn da; Lage aus T)
              G = Gelenkhöhen der Fotos              (`G9rigmasse`, geeicht; Option `gelenkhoehen`)
              T = Kopfmaße des Körperfotos + Eingaben des Popups (`G9proportionsformung`;
                  Option `kopfmasse`, eine Eingabe geht vor)
              r(k) = Regler, die T und G am nächsten kommen (`G9formanpassung`)

Mit jeder Runde stehen die Faktoren des Umrisses näher an 1 — der Umriss
formt einen Käfig, der der Person schon ähnelt. Das Zielnetz (`ziel.npz`) ist
am Ende der KÄFIG DER REGLER: glatt, weil Daz-Morphs glatt sind; die
Anpassung danach trägt nur noch den Rest (Umriss ein letztes Mal, Rest-
morph). Gliedlängen und Kopfmaße kommen aus dem Rig (`G9rigmasse`: Eichung an
Ursula je Ansicht, Kopfbreite aus den Ohren, Kopfhöhe aus dem openpifpaf-Kinn —
die Maskenoberkante ist bei echten Fotos das Haar). Option `weg` im Schritt „Zielnetz": `schaetzer` (bisher),
`silhouette` (Vorgabe; Kopf vom Gesichtsschätzer, wenn da), `silhouette_rein`.
Ohne neutral stehende Körperbilder (kein Umriss möglich) gibt `rechnen` None
zurück, und der Schätzerweg gilt.

GEMESSEN am Testfall Ursula (Bilder aus der Figur gerendert, `ProjektTemp/
silhouettenziel_messung.py`, `_lauf.py`): Zielschritt 14,5 s (3 Runden;
Umriss vorn 11,0 → 6,4 → 6,0 mm, Seite 18,5 → 11,7 → 11,0; Regler-Fit
3,8 → 3,3 → 3,4 mm); danach Anpassung 2,93 mm RMS (Schätzerweg 8,03),
Restmorph 0,49; Testfall Fläche 6,16 → 3,58 mm, RMS 11,32 → 6,10, max
32,5 → 17,3; 19 Proportionen auf ±0,6 cm bis auf Taille +1,3, Bauchtiefe
+1,8, Gesäßtiefe +1,1. Ursulas eigener Morph steckt im Satz `charaktere`
(auch beim Schätzerweg) — der Fit fand ihn zu 0,75.
"""

import logging
import time

import numpy as np

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellrigmasse import Bildmodellrigmasse
from .bildmodellumriss import Bildmodellumriss
from .bildmodellzielproportionen import Bildmodellzielproportionen

logger = logging.getLogger('core')

__all__ = ['Bildmodellsilhouettenziel']


class Bildmodellsilhouettenziel:
    OPTION = 'weg'
    WEGE = ('silhouette', 'silhouette_rein')
    RUNDEN = 3

    def __init__(self, job, ablage, optionen, anpassung):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen or {}
        self.anpassung = anpassung

    @classmethod
    def an(cls, optionen):
        return (optionen or {}).get(cls.OPTION, 'silhouette') in cls.WEGE

    def fotos(self):
        """Die neutral stehenden Körperbilder mit Profil — ohne sie gibt es keinen Umriss."""
        return Bildmodellumriss(self.job, self.optionen).bilder(('vorne', 'hinten', 'seite'))

    # ------------------------------------------------------------ Eingaben

    def person(self):
        p = self.optionen.get('person')
        return p if isinstance(p, dict) else {}

    def hoehe_cm(self):
        """Körpergröße: Personenangabe, sonst Feld „Größe cm", sonst die Grundfigur."""
        person = self.person()
        if person.get('groesse_cm'):
            return float(person['groesse_cm'])
        if self.optionen.get('groesse') == 'cm' and self.optionen.get('groesse_cm'):
            return float(self.optionen['groesse_cm'])
        from Genesis9.netzpaarung import G9netzpaarung

        return G9netzpaarung.holen().hoehe_basis * 100.0

    def kopf_ziel(self, hoehe_cm):
        """`(punkte, maske)` — Kopfpunkte des Gesichtsschätzers auf dem Käfig; None ohne Kopf."""
        if self.optionen.get(self.OPTION) == 'silhouette_rein':
            return None
        s = self.job.ergebnis.get('schaetzung') or {}
        if not s.get('kopf'):
            return None
        pfad = self.ablage.schaetzung() / s['kopf']
        if not pfad.is_file():
            return None
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile
        from Genesis9.netzpaarung import G9netzpaarung
        from Genesis9.zielnetz import G9zielnetz

        symmetrisch = self.optionen.get('symmetrie', 'an') == 'an'
        zielnetz = G9zielnetz.aus(None, np.load(pfad), symmetrisch=symmetrisch)
        punkte, gewicht = G9netzpaarung.holen().zielpunkte(zielnetz, hoehe_cm)
        with Wrapperpfad():
            teil = np.asarray(G9koerperteile.genesis_punkte(G9haut.holen()))
        maske = (np.asarray(gewicht) > 0) & (teil == G9koerperteile.NUMMER['kopf'])
        if not maske.any():
            return None
        return np.asarray(punkte, float), maske

    # -------------------------------------------------------------- Runden

    def _kaefig(self, stellung):
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung

        p, gk, knochen = G9reglerableitung.lage(G9formung(stellung))
        return np.asarray(p, float), {n: np.asarray(gk[i], float) for i, n in enumerate(knochen)}

    def _zielen(self, stellung, hoehe_cm, kopf):
        """Das Ziel dieser Runde: Käfig skaliert, Umriss, Kopf, Eingaben — `(T, gelenke, bericht)`."""
        p, gelenke = self._kaefig(stellung)
        f = hoehe_cm / 100.0 / float(p[:, 1].max())
        t = p * f
        gelenke = {k: v * f for k, v in gelenke.items()}
        self.job.ergebnis['ziel'] = {'hoehe_ziel_cm': round(hoehe_cm, 1)}  # der Umriss liest die Höhe hier
        t, gelenke, umriss = Bildmodellumriss(self.job, self.optionen).formen(t, gelenke)
        t = np.asarray(t, float)
        if kopf is not None:
            t = self.kopf_einsetzen(t, *kopf)
        bericht = {}
        for seite in ('vorn', 'seite'):
            if isinstance((umriss or {}).get(seite), dict):
                bericht[seite] = {k: umriss[seite].get(k) for k in ('vorher_mm', 'nachher_mm', 'bilder')}
        # Gliedlängen: die Gelenkhöhen der Fotos (geeicht, `G9rigmasse`) als Zielgelenke — x, z bleiben.
        rig = Bildmodellrigmasse(self.job, self.optionen)
        if self.optionen.get('gelenkhoehen', 'an') == 'an':
            gelenke, bericht['gelenke_cm'] = rig.gelenke(gelenke, hoehe_cm / 100.0)
        ziele = Bildmodellzielproportionen(self.job, self.ablage, self.optionen).eingaben_m()
        if self.optionen.get('kopfmasse', 'an') == 'an':
            kopfmasse = rig.kopfmasse(hoehe_cm / 100.0)
            for k, v in kopfmasse.items():
                ziele.setdefault(k, v)  # eine Eingabe im Popup geht vor
            bericht['kopf_cm'] = {k: round(v * 100, 1) for k, v in kopfmasse.items()}
        if ziele:
            from Genesis9.proportionsformung import G9proportionsformung

            t, gelenke, _ = G9proportionsformung().formen(t, gelenke, ziele, np.ones(len(t), bool))
        return np.asarray(t, float), gelenke, bericht

    def _melder(self, melder, runde):
        """Fortschritt einer Runde: `(anteil 0..1 innerhalb der Runde, text)` → Band 0,05–0,95."""
        def melden(x, text):
            if melder:
                melder(0.05 + 0.9 * (runde - 1 + x) / self.RUNDEN, text)
        return melden

    @staticmethod
    def kopf_einsetzen(t, kp, maske):
        """Die Kopfform des Schätzers an der Stelle des Kopfes im Ziel (Schwerpunkt auf Schwerpunkt) —
        der Schätzer liefert die FORM, die Größe kommt aus der Paarung auf die Körperhöhe."""
        aus = np.array(t, float)
        aus[maske] = kp[maske] - kp[maske].mean(0) + t[maske].mean(0)
        return aus

    def rechnen(self, melder=None):
        from Genesis9.formanpassung import G9formanpassung
        from Genesis9.reglerableitung import G9reglerableitung

        from .bildmodelloptionen import Bildmodelloptionen

        if not self.fotos():
            logger.info('Bildmodell %s: Silhouettenziel ohne neutrale Körperbilder — Zielnetz vom Schätzer',
                        self.job.kennung)
            return None
        grund, wahl = self.anpassung.grund()
        satz = self.optionen.get('reglersatz', 'charaktere')
        if melder:
            melder(0.02, 'Reglerableitung %s' % satz)
        ableitung = G9reglerableitung.holen(satz, grund)
        fest = self.anpassung._festgehalten(ableitung)
        hoehe = self.hoehe_cm()
        kopf = self.kopf_ziel(hoehe)
        stellung = dict(grund)
        runden = []
        for runde in range(1, self.RUNDEN + 1):
            t0 = time.perf_counter()
            melden = self._melder(melder, runde)
            melden(0.0, 'Runde %d/%d: Umriss der Fotos' % (runde, self.RUNDEN))
            ziel, gelenke, umriss = self._zielen(stellung, hoehe, kopf)
            fit = G9formanpassung(
                ableitung, ziel, np.ones(len(ziel)),
                gelenke if self.optionen.get('gelenke', 'an') == 'an' else None,
                daempfung=Bildmodelloptionen.DAEMPFUNG.get(self.optionen.get('daempfung'), 0.02), fest=fest,
            )
            e = fit.anpassen(lambda d, n, z, melden=melden, runde=runde: melden(
                0.3 + 0.6 * d / n,
                'Runde %d/%d, Durchgang %d/%d: %.2f mm' % (runde, self.RUNDEN, d, n, z['rms_mm'])))
            stellung = e['regler']
            runden.append({'runde': runde, 'umriss': umriss, 'rms_mm': e['punkte_rms_mm'],
                           'gelenke_mm': e['gelenke_mm'], 'regler': len(stellung),
                           'sekunden': round(time.perf_counter() - t0, 1)})
            logger.info('Bildmodell %s: Silhouettenziel Runde %d: %s', self.job.kennung, runde, runden[-1])
        return self._ablegen(stellung, hoehe, wahl, kopf is not None, runden)

    def _ablegen(self, stellung, hoehe, wahl, mit_kopf, runden):
        p, gelenke = self._kaefig(stellung)
        self.ablage.ergebnis().mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            self.ablage.ergebnis() / self.anpassung.ZIEL,
            punkte=p.astype(np.float32),
            gewicht=np.ones(len(p), dtype=np.float32),
            gelenknamen=np.array(list(gelenke)),
            gelenke=np.array([gelenke[k] for k in gelenke], dtype=np.float32),
        )
        self.job.ergebnis['ziel'] = {
            'weg': self.optionen.get(self.OPTION),
            'quelle': 'silhouette',
            'hoehe_ziel_cm': round(float(p[:, 1].max() - p[:, 1].min()) * 100, 1),
            'hoehe_soll_cm': round(hoehe, 1),
            'basis': wahl,
            'kopf': 'schaetzer' if mit_kopf else 'keine',
            'runden': runden,
            'regler': stellung,
            'person': self.person(),
        }
        self.anpassung._sichern('ergebnis')
        return self.job.ergebnis['ziel']
