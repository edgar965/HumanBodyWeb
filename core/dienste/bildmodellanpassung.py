# -*- coding: utf-8 -*-
"""Bildmodellanpassung — Schritte 3–7: Zielnetz, Regler, Rest, Vorschau, Speichern.

Rechnet im Arbeitsprozess mit dem Genesis-9-Paket (python14, kein Browser):

    ziel        `G9zielnetz.aus(betas, kopf)` → `ergebnis/ziel.npz`
                (Zielpunkte und Gewichte je Käfigpunkt aus `G9netzpaarung`)
    anpassung   `G9reglerableitung` (Reglersatz, Grundfigur) + `G9formanpassung`
                → `ergebnis.anpassung` (Regler, RMS je Teil, Verlauf)
    rest        `G9restmorph.ablegen` → Eigenmorph `eigen:<kennung>`,
                Regler um ihn ergänzt, RMS danach gemessen
    vorschau    `G9vorschaubild`: Icon, vorn, seite, hinten, Kopf
    speichern   `data/models/<Name>.json` (`quelle: genesis9`), wie
                „Modell speichern" der Szene (`Modelldateien`)

Alles, was die Seite zeigt, steht in `job.ergebnis` — Zahlen aus der
Messung, keine Schätzung.
"""

import logging

import numpy as np

from .bildmodellspeichern import Bildmodellspeichern
from .bildmodellumriss import Bildmodellumriss
from .bildmodellzielproportionen import Bildmodellzielproportionen

logger = logging.getLogger('core')

__all__ = ['Bildmodellanpassung']


class Bildmodellanpassung:
    ZIEL = 'ziel.npz'
    GRUND = {
        'feminine': {'BaseFeminine_figure_ctrl_Character': 1.0},
        'masculine': {'BaseMasculine_figure_ctrl_Character': 1.0},
        'keine': {},
    }

    def __init__(self, job, ablage, optionen):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen
        self.job.ergebnis = dict(self.job.ergebnis or {})

    def _sichern(self, *felder):
        self.job.save(update_fields=list(felder) + ['updated_at'])

    # ---------------------------------------------------------------- Ziel

    def grund(self):
        wahl = self.optionen.get('basis', 'auto')
        if wahl == 'auto':
            wahl = (self.job.ergebnis.get('schaetzung') or {}).get('geschlecht') or 'feminine'
        return dict(self.GRUND.get(wahl, self.GRUND['feminine'])), wahl

    def ziel(self, melder=None):
        from Genesis9.netzpaarung import G9netzpaarung
        from Genesis9.zielnetz import G9zielnetz

        s = self.job.ergebnis.get('schaetzung') or {}
        betas = s.get('betas')
        kopf = None
        if s.get('kopf'):
            pfad = self.ablage.schaetzung() / s['kopf']
            if pfad.is_file():
                kopf = np.load(pfad)
        if melder:
            melder(0.2, 'SMPL-X-Zielnetz')
        zielnetz = G9zielnetz.aus(betas, kopf, symmetrisch=self.optionen.get('symmetrie', 'an') == 'an')
        paarung = G9netzpaarung.holen()
        person = self.optionen.get('person') if isinstance(self.optionen.get('person'), dict) else {}
        hoehe = None
        if person.get('groesse_cm'):
            hoehe = float(person['groesse_cm'])
        elif self.optionen.get('groesse') == 'cm' and self.optionen.get('groesse_cm'):
            hoehe = float(self.optionen['groesse_cm'])
        elif self.optionen.get('groesse') == 'basis':
            hoehe = paarung.hoehe_basis * 100.0
        # Gewicht: Beta 1 des Zielnetzes, bis Volumen × Dichte stimmt (`G9koerpergewicht`).
        gewicht_beleg = None
        if person.get('gewicht_kg'):
            from Genesis9.koerpergewicht import G9koerpergewicht

            ziel_hoehe = hoehe or zielnetz.hoehe() * 100.0
            betas, gewicht_beleg = G9koerpergewicht.betas_fuer_gewicht(
                betas, ziel_hoehe, float(person['gewicht_kg'])
            )
            zielnetz = G9zielnetz.aus(betas, kopf, symmetrisch=self.optionen.get('symmetrie', 'an') == 'an')
        punkte, gewicht = paarung.zielpunkte(zielnetz, hoehe)
        gelenke = paarung.zielgelenke(zielnetz, hoehe)
        self.ablage.ergebnis().mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            self.ablage.ergebnis() / self.ZIEL,
            punkte=punkte.astype(np.float32),
            gewicht=gewicht.astype(np.float32),
            gelenknamen=np.array(list(gelenke)),
            gelenke=np.array([gelenke[k] for k in gelenke], dtype=np.float32),
        )
        g = gewicht > 0
        self.job.ergebnis['ziel'] = {
            **zielnetz.steckbrief(),
            'paarung': paarung.steckbrief(),
            'hoehe_ziel_cm': round(float(punkte[g, 1].max() - punkte[g, 1].min()) * 100, 1)
            if g.any()
            else None,
            'ohne_betas': betas is None,
            'gewicht': gewicht_beleg,
            'person': person,
        }
        self._sichern('ergebnis')

    def _ziel_laden(self, roh=False):
        """Das geformte Ziel (`ziel_prop.npz`, Proportionen-Eingaben), sonst das rohe."""
        pfad = self.ablage.ergebnis() / self.ZIEL
        geformt = self.ablage.ergebnis() / Bildmodellzielproportionen.DATEI
        if not roh and geformt.is_file():
            pfad = geformt
        if not pfad.is_file():
            raise RuntimeError('Zielnetz fehlt — Schritt „ziel" zuerst')
        with np.load(pfad) as d:
            gelenke = {str(n): d['gelenke'][i] for i, n in enumerate(d['gelenknamen'])}
            return d['punkte'].astype(float), d['gewicht'].astype(float), gelenke

    # ----------------------------------------------------------- Anpassen

    def anpassen(self, melder=None):
        from Genesis9.formanpassung import G9formanpassung
        from Genesis9.reglerableitung import G9reglerableitung

        from .bildmodellhaende import Bildmodellhaende
        from .bildmodelloptionen import Bildmodelloptionen

        punkte, gewicht, gelenke = self._ziel_laden(roh=True)
        if melder:
            melder(0.01, 'Umriss der Fotos aufs Zielnetz')
        punkte, gelenke, umriss = Bildmodellumriss(self.job, self.optionen).formen(punkte, gelenke)
        if melder:
            melder(0.02, 'Proportionen aufs Zielnetz')
        punkte, gelenke, proportionen = Bildmodellzielproportionen(
            self.job, self.ablage, self.optionen
        ).formen(punkte, gewicht, gelenke, vorgeformt=umriss is not None)
        grund, wahl = self.grund()
        satz = self.optionen.get('reglersatz', 'charaktere')
        if melder:
            melder(0.05, 'Reglerableitung %s' % satz)
        ableitung = G9reglerableitung.holen(satz, grund)
        if melder:
            melder(0.3, 'Ausgleichung (%d Regler)' % len(ableitung.namen))
        fest = self._festgehalten(ableitung)
        haende = {'haende': 0}
        if self.optionen.get('nebenbilder', 'aus') == 'haende':
            werte, haende = Bildmodellhaende(self.job, grund).regler()
            # Festgehalten nur, was der Satz kennt — und was der Nutzer
            # nicht selbst gestellt hat.
            for k, v in werte.items():
                if k in ableitung.namen and k not in fest:
                    fest[k] = v
        anpassung = G9formanpassung(
            ableitung,
            punkte,
            gewicht,
            gelenke if self.optionen.get('gelenke', 'an') == 'an' else None,
            daempfung=Bildmodelloptionen.DAEMPFUNG.get(self.optionen.get('daempfung'), 0.02),
            fest=fest,
        )
        e = anpassung.anpassen(
            lambda d, n, z: (
                melder and melder(0.3 + 0.6 * d / n, 'Durchgang %d/%d: %.2f mm' % (d, n, z['rms_mm']))
            )
        )
        np.save(self.ablage.ergebnis() / 'rest.npy', e['rest'].astype(np.float32))
        self.job.ergebnis['anpassung'] = {
            'regler': e['regler'],
            'verlauf': e['verlauf'],
            'teile': e['teile'],
            'punkte_rms_mm': e['punkte_rms_mm'],
            'gelenke_mm': e['gelenke_mm'],
            'reglersatz': satz,
            'grund': grund,
            'basis': wahl,
            'variablen': len(ableitung.namen),
            'festgehalten': fest,
            'haende': haende,
            'proportionen': proportionen,
            'umriss': umriss,
        }
        self.job.ergebnis.pop('rest', None)
        self._sichern('ergebnis')

    def _festgehalten(self, ableitung):
        """Regler, die der Nutzer auf der Seite festgehalten hat
        (`optionen.fest`: {variable: wert}) — nur bekannte Variablen."""
        roh = self.optionen.get('fest') if isinstance(self.optionen.get('fest'), dict) else {}
        roh = roh or (self.job.optionen or {}).get('fest') or {}
        aus = {}
        for k, v in (roh or {}).items():
            if k in ableitung.namen:
                try:
                    aus[k] = float(v)
                except TypeError, ValueError:
                    continue
        return aus

    # ---------------------------------------------------------------- Rest

    def rest(self, melder=None):
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung
        from Genesis9.restmorph import G9restmorph

        from .bildmodelloptionen import Bildmodelloptionen

        a = self.job.ergebnis.get('anpassung')
        if not a:
            raise RuntimeError('Anpassung fehlt — Schritt „anpassung" zuerst')
        if self.optionen.get('restmorph', 'an') != 'an':
            self.job.ergebnis['rest'] = {'aus': True}
            self._sichern('ergebnis')
            return
        punkte, gewicht, _ = self._ziel_laden()
        rest = np.load(self.ablage.ergebnis() / 'rest.npy').astype(float)
        if melder:
            melder(0.3, 'Restmorph glätten')
        name = '%s %s' % (self.job.name, self.job.kennung[-8:].replace('.', ''))
        regler, zahlen = G9restmorph.ablegen(
            name,
            rest,
            gewicht,
            {'quelle': 'modell aus bildern', 'auftrag': self.job.kennung},
            schritte=Bildmodelloptionen.GLAETTUNG.get(self.optionen.get('glaettung'), 6),
        )
        stellung = dict(a['regler'])
        stellung[regler] = 1.0
        p, _, _ = G9reglerableitung.lage(G9formung(stellung))
        r = punkte - p
        g = gewicht > 0
        zahlen['rms_mit_morph_mm'] = round(float(np.sqrt((r[g] ** 2).sum(1).mean())) * 1000, 2)
        self.job.ergebnis['rest'] = {'regler': regler, **zahlen}
        self._sichern('ergebnis')

    # ------------------------------------------------------------ Vorschau

    def stellung(self):
        """Die Regler des Ergebnisses samt Restmorph."""
        a = self.job.ergebnis.get('anpassung') or {}
        stellung = dict(a.get('regler') or {})
        r = self.job.ergebnis.get('rest') or {}
        if r.get('regler'):
            stellung[r['regler']] = 1.0
        return stellung

    def vorschau(self, melder=None):
        """Bilder, Maße, Proportionen, Fototextur, Testfall — `Bildmodellvorschau`."""
        from .bildmodellvorschau import Bildmodellvorschau

        vorschau = Bildmodellvorschau(self.job, self.ablage, self.optionen, self.stellung(), self._ziel_laden)
        vorschau.ausfuehren(melder)
        self._sichern('ergebnis')

    # ----------------------------------------------------------- Speichern

    def modelldaten(self):
        return Bildmodellspeichern(self.job, self.optionen, self.stellung()).modelldaten()

    def speichern(self, melder=None):
        return Bildmodellspeichern(self.job, self.optionen, self.stellung()).speichern(melder)
