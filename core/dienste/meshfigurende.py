# -*- coding: utf-8 -*-
"""Meshfigurende — die Schritte „rest" und „textur" von „Mesh to 3D" auf der python14-Seite.

REST → EIGENMORPH: Was die Regler nicht erreichen, liefert der Runner je Käfigpunkt in der
Ruhelage (über die Hautmischung zurückgerechnet, einseitige Punkte unter Haar nur nach innen).
Auf Wunsch symmetrisch (Daz-Figuren sind es, ein Netz aus Fotos nie ganz): je Punkt der
Mittelwert mit seinem Spiegelpunkt (`G9netzbereiche.spiegel`), wo nur eine Seite getroffen ist,
deren gespiegelter Wert. Dann dieselbe Glättung wie im Reiter „3D" (`G9restmorph`: Lücken aus
den Nachbarn, 6 Laplace-Schritte) und als `eigen:<kennung>` abgelegt. Die Augenpartie (Lider und
Körpernachbarn des Augapfels) ist dabei Lücke (`Meshfiguraugenhoehle`): sonst zog der Rest sie in
die Augenmulde des Netzes, und der Augapfel stach durch die Lider.

TEXTUR: Der Runner liefert je Texel der fünf Kacheln die Farbe des Netzes (`meshtextur.npz`,
Format wie `_run_fotofarben.py`); gebacken wird mit `G9texturbacken` — Daz-Albedo auf den
Hautton des Netzes getönt, darüber die Netzfarbe. Ergebnis wie beim Reiter „3D" unter
`ergebnis.fototextur` (die Seite legt die Kacheln mit `Texturauflage` auf). Dazu das Daz-Augenbild
in der Irisfarbe des Netzes (`Meshfiguraugenbild`, `fototextur.augen`).
"""

import logging
import time

import numpy as np

from .meshfiguraugenbild import Meshfiguraugenbild
from .meshfiguraugenhoehle import Meshfiguraugenhoehle

logger = logging.getLogger('core')

__all__ = ['Meshfigurende']


class Meshfigurende:
    PRAEFIX = 'meshfigur'

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = lauf.optionen

    def _haltung(self):
        return (self.job.ergebnis.get('koerper') or {}).get('haltung') or {}

    def _genesis(self, stellung):
        from .meshfigurgenesis import Meshfigurgenesis

        return Meshfigurgenesis(stellung, self._haltung()).speichern(self.ablage.arbeit('genesis_ende.npz'))

    # ---------------------------------------------------------------- Rest

    def rest(self):
        from Genesis9.restmorph import G9restmorph

        if self.optionen.get('eigenmorph') != 'an':
            self.job.ergebnis['rest'] = {'aus': True}
            return
        stellung = dict((self.job.ergebnis.get('regler') or {}).get('stellung') or {})
        if not stellung:
            raise RuntimeError('Regler fehlen — Schritte „koerper"/„gesicht" zuerst')
        self._genesis(stellung)
        e = self.lauf.runner('rest', von=0.05, bis=0.85)
        with np.load(self.ablage.arbeit('rest.npz')) as d:
            rest, gewicht = d['rest'].astype(float), d['gewicht'].astype(float)
            # Option `kleidungsluft_mm`: Punkte, die durch Stoff ragen, behalten nach dem Spiegeln und Glätten mindestens ihren Weg (`G9restmorph.untergrenze`, 07.10.2026).
            mindest = d['mindest'].astype(float) if 'mindest' in d.files else None
        # Augenpartie aus der Umgebung füllen — nicht in die Augenmulde des Netzes ziehen.
        rest, gewicht, augen = Meshfiguraugenhoehle.luecke(rest, gewicht)
        if self.optionen.get('symmetrie') == 'an':
            rest, gewicht = self.symmetrisch(rest, gewicht)
        self.lauf.melden(0.9, 'Eigenmorph glätten')
        name = '%s Mesh %s' % (self.job.name, self.job.kennung[-8:].replace('.', ''))
        regler, zahlen = G9restmorph.ablegen(
            name, rest, gewicht, {'quelle': 'mesh to 3d', 'auftrag': self.job.kennung}, mindest=mindest
        )
        self.job.ergebnis['rest'] = {
            'regler': regler,
            **zahlen,
            'rest_rms_mm': e.get('rest_rms_mm'),
            'getroffen': e.get('rest_punkte'),
            'augenpartie_luecke': augen,
            'verlauf': e.get('verlauf'),
            # Augen-, Mund- und Nasenmorph aus den Landmarken (nur „2D3D Kleider", Option `koerper.landmarkmorphe`; leer sonst)
            'landmarkmorphe': self._landmarkmorphe(rest, gewicht, name, stellung),
        }
        self.kopfeigen_nachziehen()

    def _landmarkmorphe(self, rest, gewicht, name, stellung):
        """`{bereich: {regler, …}}` aus `lauf.landmarkmorphe` (07.10.2026) — „Mesh to 3D" hat die Methode nicht und bekommt `{}`. Ein Fehler hält den Lauf nicht auf: die Figur bleibt, wie sie war."""
        bauer = getattr(self.lauf, 'landmarkmorphe', None)
        if bauer is None:
            return {}
        try:
            return bauer(rest, gewicht, name, stellung)
        except Exception:  # noqa: BLE001 — ohne die Morphe fehlen nur die Feinheiten an Augen, Mund und Nase
            logger.exception('%s: Landmarkmorphe nicht gebaut', self.job.kennung)
            return {'fehler': 'siehe Log'}

    def kopfeigen_nachziehen(self):
        """„Kopf-Eigen" (Seite „Gesichtsform") mit seinen gespeicherten Zielkurven auf die NEUE Figur
        rechnen — sonst trüge die Figur den Morph einer anderen Reglerstellung."""
        from Genesis9.schnittmorph import G9schnittmorph

        from .gesichtsformquelle import Gesichtsformquelle

        kopf = self.job.ergebnis.get('kopfeigen') or {}
        name = Gesichtsformquelle.auftragsname(self.job)
        ziel = (G9schnittmorph.steckbrief(name).get('ziel') or {}) if kopf.get('regler') else {}
        if not ziel.get('schnitte') and not ziel.get('punkte'):
            return
        self.lauf.melden(0.95, 'Kopf-Eigen nachziehen')
        morph = G9schnittmorph(self.job.stellung(), name)
        e = morph.rechnen(G9schnittmorph.ziel_aus_seite(ziel), 'nachgezogen')
        self.job.ergebnis['kopfeigen'] = {
            **kopf,
            'regler': e['regler'],
            'guete': e['guete'],
            'max_mm': e['max_mm'],
            'punkte': e['punkte'],
        }

    @staticmethod
    def symmetrisch(rest, gewicht):
        from Genesis9.netzbereiche import G9netzbereiche

        s = G9netzbereiche.spiegel()
        gespiegelt = rest[s] * np.array([-1.0, 1.0, 1.0])
        g_sp = gewicht[s]
        beide = (gewicht > 0) & (g_sp > 0)
        aus = np.where(
            beide[:, None], 0.5 * (rest + gespiegelt), np.where((g_sp > 0)[:, None], gespiegelt, rest)
        )
        return aus, np.maximum(gewicht, g_sp)

    # --------------------------------------------------------------- Textur

    def textur(self):
        from Genesis9.texturabtastung import G9texturabtastung

        wahl = self.optionen.get('textur')
        if wahl == 'aus':
            self.job.ergebnis['textur'] = {'aus': True}
            self.job.ergebnis.pop('fototextur', None)
            return
        stellung = self.job.stellung()
        if not stellung:
            raise RuntimeError('Regler fehlen — Schritte „koerper"/„gesicht" zuerst')
        self._genesis(stellung)
        abtastung = G9texturabtastung.holen()
        self.lauf.zusatz['abtastung'] = str(G9texturabtastung.pfad(abtastung.seite))
        e = self.lauf.runner('textur', von=0.05, bis=0.7)
        self.lauf.zusatz.pop('abtastung', None)
        hautton = (e.get('haut') or {}).get('hautton')
        self.job.ergebnis['textur'] = {
            'hautton': hautton,
            'deckung': e.get('deckung_je_kachel'),
            'farbangleich': e.get('farbangleich'),
            'entlichtung': e.get('entlichtung'),
            'iris': e.get('iris'),
            'wahl': wahl,
        }
        if wahl != 'mesh':
            self.job.ergebnis.pop('fototextur', None)
            return
        self.lauf.melden(0.75, 'Kacheln backen')
        fototextur = self.backen(hautton, abtastung.seite)
        # Daz-Augapfel mit der Irisfarbe des Netzes (`Meshfiguraugenbild`), neben den Kacheln.
        augen = Meshfiguraugenbild.schreiben(self.ablage.ergebnis(), (e.get('iris') or {}).get('farbe'))
        if augen:
            fototextur['augen'] = augen['datei']
            self.job.ergebnis['textur']['augenbild'] = augen
        self.job.ergebnis['fototextur'] = fototextur

    def backen(self, hautton, seite):
        from Genesis9.texturabtastung import G9texturabtastung
        from Genesis9.texturbacken import G9texturbacken

        from .meshfigurtexelpruefung import Meshfigurtexelpruefung

        with np.load(self.ablage.arbeit('meshtextur.npz')) as d:
            hd = {k: d[k] for k in d.files}
        # Helle Füllflächen, Schattenklumpen und die fleckige Kopfhaut vor dem Backen säubern.
        hd, pruefung = Meshfigurtexelpruefung(G9texturabtastung.holen(seite)).pruefen(hd)
        kacheln, _ = G9texturbacken(seite).backen(
            hd['punktfarben'],
            hd['deckung'],
            self.ablage.ergebnis(),
            praefix=self.PRAEFIX,
            hautton=hautton,
            hd=hd,
            # Ein ganz bekleideter Rumpf hat keine Netzfarbe — seine Kachel ist die getönte Daz-Haut, nicht die weiße.
            auch_ohne_deckung=True,
        )
        return {
            'kacheln': {str(k): self._name(p) for k, p in kacheln.items()},
            'seite': int(seite),
            'hautton': hautton,
            'pruefung': pruefung,
            'stand': time.strftime('%Y%m%d%H%M%S'),
        }

    @staticmethod
    def _name(pfad):
        return str(pfad).replace('\\', '/').rsplit('/', 1)[-1]
