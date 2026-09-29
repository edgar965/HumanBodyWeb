# -*- coding: utf-8 -*-
"""Meshfigurkette — die Schritte „koerper" und „gesicht" von „Mesh to 3D" auf der python14-Seite.

Je Runde: Genesis für die aktuelle Reglerstellung ECHT rechnen und ablegen (`Meshfigurgenesis`:
Käfig, Skelett, Haut, Landmarken, Gelenkkorrekturen der letzten Haltung), dazu die Begleitdaten
der Reglerableitung (`Meshfigurregler`: aktueller Wert, Stufe, Grenzen); der Runner stellt die
Regler auf der Karte; hier wird daraus die neue Stellung (Paare, Grenzen, Kleinstwerte 0).

Vorgabe „Körpergröße": nach der ersten Runde ist die Figur ohne Haar gemessen — ihr Scheitel ist
die Größe der Person. Das Netz wird dann um den Faktor Vorgabe / Figur um den Boden gestreckt
(Runner-Schritt `skalieren`), und die folgenden Runden passen die Regler daran an.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Meshfigurkette']


class Meshfigurkette:
    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = lauf.optionen

    def _regler(self):
        from .meshfigurregler import Meshfigurregler

        grund = Meshfigurregler.GRUNDFIGUREN.get(
            self.optionen['basis'], Meshfigurregler.GRUNDFIGUREN['feminine']
        )
        gesperrt = []
        if self.optionen.get('referenz') and self.optionen.get('blind') == 'an':
            from Genesis9.charaktere import G9charaktere

            eintrag = G9charaktere.eintrag(self.optionen['referenz']) or {}
            gesperrt = Meshfigurregler.sperrmarken(eintrag.get('regler') or {})
        return Meshfigurregler(grund, gesperrt)

    def _genesis(self, name, stellung, haltung):
        from .meshfigurgenesis import Meshfigurgenesis

        return Meshfigurgenesis(stellung, haltung).speichern(self.ablage.arbeit(name))

    @staticmethod
    def hoehe(stellung):
        """Scheitelhöhe (m) der Figur dieser Stellung, Füße auf 0."""
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung

        punkte, _, _ = G9reglerableitung.lage(G9formung(stellung))
        return float(punkte[:, 1].max())

    # -------------------------------------------------------------- Körper

    def koerper(self):
        regler = self._regler()
        # Feste Werte (Genitalbereich der männlichen Grundfigur) stehen von Anfang an in der Stellung; die Kette
        # darf sie nicht ändern (`Meshfigurregler.AUS`) — sie stellte den Regler sonst auf 100 %.
        stellung, haltung = {**regler.grund, **regler.festwerte(self.optionen)}, {}
        # Frisch beginnen: die Haltung eines früheren Laufs (`arbeit/zustand.npz`) wäre ein Warmstart,
        # der zwei Läufe mit denselben Optionen verschieden rechnen ließe.
        self.ablage.arbeit('zustand.npz').unlink(missing_ok=True)
        runden = int(self.optionen.get('runden') or 2)
        verlauf = []
        for runde in range(1, runden + 1):
            anteil = (runde - 1) / runden
            self.lauf.melden(anteil, 'Runde %d/%d: Genesis rechnen' % (runde, runden))
            self._genesis('genesis_koerper_%d.npz' % runde, stellung, haltung)
            stufen = regler.speichern(
                self.ablage.arbeit('regler_koerper_%d.npz' % runde), 'koerper', stellung
            )
            e = self.lauf.runner('koerper', runde, von=anteil + 0.02 / runden, bis=anteil + 0.95 / runden)
            stellung = regler.stellung('koerper', e['werte'], stellung)
            haltung = e['haltung']
            verlauf.append(
                {
                    'runde': runde,
                    'verlauf': e['verlauf'],
                    'haut': e.get('haut'),
                    'lage': e.get('lage'),
                    'landmarken_flaeche': e.get('landmarken_flaeche'),
                    'sekunden': e.get('sekunden'),
                    'stufen': stufen,
                    'hoehe_cm': round(self.hoehe(stellung) * 100, 1),
                }
            )
            if runde == 1 and float(self.optionen.get('hoehe_cm') or 0) > 0:
                self._skalieren(stellung, verlauf[-1])
        # `stellung`/`haltung_koerper` bleiben als Ergebnis DER KÖRPERKETTE stehen: ein Neustart ab
        # „gesicht" beginnt dort und nicht bei den Kopfreglern eines früheren Gesichtslaufs.
        self.job.ergebnis['koerper'] = {'runden': verlauf, 'haltung': haltung, 'stellung': stellung,
                                        'haltung_koerper': haltung}
        self.job.ergebnis['regler'] = {
            'stellung': stellung,
            'grund': regler.grund,
            'geaendert': regler.geaendert(stellung),
        }
        self.job.ergebnis.pop('gesicht', None)
        self.job.ergebnis.pop('rest', None)

    def _skalieren(self, stellung, eintrag):
        ziel = float(self.optionen['hoehe_cm']) / 100.0
        ist = self.hoehe(stellung)
        faktor = ziel / ist if ist > 0 else 1.0
        self.lauf.zusatz['skalierung'] = faktor
        self.lauf.runner('skalieren')
        self.lauf.zusatz.pop('skalierung', None)
        eintrag['skalierung'] = {
            'figur_cm': round(ist * 100, 1),
            'ziel_cm': round(ziel * 100, 1),
            'faktor': round(faktor, 5),
        }
        self.job.ergebnis.setdefault('erkennung', {})['skalierung'] = eintrag['skalierung']

    # ------------------------------------------------------------- Gesicht

    def gesicht(self):
        if self.optionen.get('gesicht') != 'an':
            self.job.ergebnis['gesicht'] = {'aus': True}
            return
        e_regler = self.job.ergebnis.get('regler') or {}
        koerper = self.job.ergebnis.get('koerper') or {}
        stellung = dict(koerper.get('stellung') or e_regler.get('stellung') or {})
        if not stellung:
            raise RuntimeError('Körperkette fehlt — Schritt „koerper" zuerst')
        haltung = koerper.get('haltung_koerper') or koerper.get('haltung') or {}
        regler = self._regler()
        self.lauf.melden(0.02, 'Genesis rechnen')
        self._genesis('genesis_gesicht.npz', stellung, haltung)
        stufen = regler.speichern(self.ablage.arbeit('regler_kopf.npz'), 'kopf', stellung)
        e = self.lauf.runner('gesicht', von=0.05, bis=0.98)
        stellung = regler.stellung('kopf', e['werte'], stellung)
        self.job.ergebnis['gesicht'] = {
            'verlauf': e['verlauf'],
            'stufen': stufen,
            'sekunden': e.get('sekunden'),
            'haltung': e['haltung'],
            'landmarken_flaeche': e.get('landmarken_flaeche'),
        }
        self.job.ergebnis['koerper']['haltung'] = e['haltung']
        e_regler['stellung'] = stellung
        e_regler['geaendert'] = regler.geaendert(stellung)
        self.job.ergebnis['regler'] = e_regler
        self.job.ergebnis.pop('rest', None)
