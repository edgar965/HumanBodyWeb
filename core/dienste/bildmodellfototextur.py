# -*- coding: utf-8 -*-
"""Bildmodellfototextur — Textur Stufe 2: Fotofarbe je Texel, über das Modell selbst, als UDIM gebacken.

Edgar (19.09.2026): „warum ist das Modell noch mit dieser miserablen Textur? …
mach ca. 10 Nahaufnahmen von Ursula mit HD" — und am 20.09.: „ich verstehe
nicht diese Bilder, mach klare Bilder was in das Bein, Nagel hineinkommt.
das ist doch reinstes Chaos!" Stufe 1 tönt die Daz-Haut (`Bildmodelltextur`,
Hautton). Stufe 2 nimmt die Farbe der Fotos selbst:

  1. `G9texturmodell`: das ANGEPASSTE MODELL (Käfig der Reglerstellung, Füße
     auf 0) mit Dreiecken, Körperteil je Punkt und Landmarken (COCO, Füße,
     Hände aus dem Skelett, 68 Gesichtspunkte aus `G9gesichtslandmarken`) —
     die Textur liegt auf diesem Netz, also projiziert es auch. Bis zum 19.09.
     lief die Projektion über das SMPL-X-Netz des Schätzers: jedes Bild lag
     anders daneben, Brauen doppelt, Streifen auf den Beinen.
  2. `_run_fotofarben.py` (python10): je Bild mit Häkchen „Textur" das Modell
     ins Bild projizieren — Kamera bekannt (gerenderte Testfallbilder,
     `kamera_bekannt` → `G9bildkamera`) oder aus dem Rig gegen die Landmarken
     (`Nahaufnahme`, PnP). Tiefentest, Personenmaske, Sichtwinkel, Haut → je
     TEXEL der fünf Kacheln (`Fototextur`, Abtastung `G9texturabtastung`,
     2048²) die Proben aller Bilder; `Texturmischung` gleicht die Helligkeit
     auf der Überlappung an und blendet mehrbandig. Ein Nebenbild mit
     Körperteil färbt nur dieses Teil (`teile`). Dazu je Bild und Kachel ein
     Beitragsbild (welche Pixel des Fotos in die Kachel gehen).
  3. `G9texturbacken`: Albedo der Grundhaut (auf den Stufe-1-Ton getönt),
     darüber die Punktfarben (Gouraud, aus den Texeln zurückgerechnet) als
     Füllung, darüber die Texelfarben; je Kachel die Herkunftskarte, und
     `G9kachelkarte` beschriftet die Inseln mit ihrem Körperteil.

Ergebnis `ergebnis.fototextur = {kacheln: {1001: 'fototextur_1001.jpg', …},
herkunft, karten, bilder, je_bild (mit beitraege), texel, deckung, hautton,
seite, stand}`; die Seite legt die Kacheln als `map` auf das Modell
(`texturauflage.js`) und zeigt sie unten im Bereich „Textur"
(`texturansicht.js`, `texturkachel.js`). Eigener Schritt `textur` im Lauf.
"""

import json
import logging
import os
import subprocess
import time

import numpy as np
from django.conf import settings

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellbildtypen import Bildmodellbildtypen
from .bildmodellmehrbild import Bildmodellmehrbild
from .bildmodelltextur import Bildmodelltextur

logger = logging.getLogger('core')

__all__ = ['Bildmodellfototextur']


class Bildmodellfototextur:
    """Modell hinlegen, Runner rufen, backen — Schritt „textur"."""

    RUNNER = '_run_fotofarben.py'
    AUFTRAG = 'fotofarben_auftrag.json'
    MODELL = 'fototextur_modell.npz'
    TEXEL = 'fototextur.npz'
    WARTEZEIT = 1800

    def __init__(self, job, ablage, optionen):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen

    # -------------------------------------------------------------- Bilder

    @staticmethod
    def projizierbar(b):
        """Kamera bekannt, oder ein Rig, Gesichtspunkte oder Hände zum Registrieren."""
        return bool(b.get('kamera_bekannt') or (b.get('rigs') or {}) or b.get('gesicht68')
                    or b.get('haende_punkte'))

    def bilder(self):
        """Alle gewählten Bilder, die projizierbar sind."""
        aus = []
        # Option `textur_nebenbilder = aus`: nur Hauptbilder, die auch die Form geben (Edgar, 20.09.2026:
        # „die Option, die Nebenbilder einzubinden oder nicht, damit ich sehen kann, ob das was bringt").
        nur_haupt = (self.optionen or {}).get('textur_nebenbilder', 'an') == 'aus'
        for b in self.job.bilder:
            if b.get('video') or not Bildmodelltextur.gewaehlt(b):
                continue
            if nur_haupt and not Bildmodellbildtypen.fuer_form(b):
                continue
            if self.projizierbar(b):
                aus.append(b)
        return aus

    def stellung(self):
        """Die Regler des Ergebnisses samt Restmorph (wie `Bildmodellanpassung.stellung`)."""
        a = self.job.ergebnis.get('anpassung') or {}
        stellung = dict(a.get('regler') or {})
        r = self.job.ergebnis.get('rest') or {}
        if r.get('regler'):
            stellung[r['regler']] = 1.0
        return stellung

    # ------------------------------------------------------------- Runner

    @staticmethod
    def teile_nummern(b):
        from Genesis9.koerperteile import G9koerperteile

        teile = Bildmodellbildtypen.textur_teile(b)
        return [G9koerperteile.NUMMER[t] for t in teile if t in G9koerperteile.NUMMER] if teile else None

    def _eintrag(self, b, posierung=None):
        from Genesis9.bildkamera import G9bildkamera

        e = {
            'datei': str(self.ablage.zuschnitt() / b['datei']),
            'gewicht': float(b.get('gewicht') or 1.0) or 1.0,
            'rigs': {k: v for k, v in (b.get('rigs') or {}).items() if v},
            'gesicht68': b.get('gesicht68'),
            'haende': [{k: h.get(k) for k in ('seite', 'guete', 'bild')}
                       for h in (b.get('haende_punkte') or [])],
            'breite': int(b.get('breite') or 0),
            'hoehe': int(b.get('hoehe') or 0),
            # Kopfbild → das Gesicht kommt nur von ihm (21.09.2026, Edgar: „Das soll nur von dem
            # Gesicht kommen"); Maske aus dem Freisteller (rembg, weich) statt YOLO-Seg im Runner.
            'kategorie': b.get('kategorie'),
            'maske': self._maske(b['datei']),
        }
        kamera = G9bildkamera.aus_browser(b.get('kamera_bekannt'), b.get('kasten'))
        if kamera:
            e['kamera'] = kamera
        elif posierung is not None:
            # T1 (Konzept 20.09., nachts): der Käfig in der Pose und Kamera des Fotos aus GVHMR —
            # statt Käfig in Ruhehaltung + starrer Rig-Registrierung (Damira: 15,8–46,1 px daneben).
            try:
                pose = posierung.fuer_bild(b)
            except Exception as fehler:  # noqa: BLE001 — dann wie bisher über das Rig
                logger.warning('Bildmodell %s: Posierung von %s fehlgeschlagen: %s',
                               self.job.kennung, b.get('datei'), fehler)
                pose = None
            if pose:
                e.update(pose)
        teile = self.teile_nummern(b)
        if teile:
            e['teile'] = teile
        return e

    def _maske(self, datei):
        """Pfad der weichen Personenmaske (rembg, `Bildmodellfreisteller`, einmal je Bild ~4 s) —
        None, wenn sie nicht zu rechnen ist: dann nimmt der Runner die YOLO-Maske wie vor dem
        21.09.2026 (grobe Kante, graue Ränder in der Textur)."""
        from .bildmodellfreisteller import Bildmodellfreisteller

        freisteller = Bildmodellfreisteller(self.job, self.ablage)
        try:
            freisteller.maske(datei)
            return str(freisteller.maskenpfad(datei))
        except Exception as fehler:  # noqa: BLE001
            logger.warning('Bildmodell %s: keine Maske für %s — Textur mit YOLO-Maske: %s',
                           self.job.kennung, datei, fehler)
            return None

    def _gesichtstabelle(self, bilder):
        """Fehlt die Tabelle der 68 Gesichtspunkte: aus einem Testfallbild mit bekannter Kamera
        und Gesichtsbefund gegen die Referenzfigur bauen (einmal je Rechner)."""
        from Genesis9.bildkamera import G9bildkamera
        from Genesis9.gesichtslandmarken import G9gesichtslandmarken
        from Genesis9.texturmodell import G9texturmodell

        from .bildmodelltestfall import Bildmodelltestfall

        if G9gesichtslandmarken.holen() is not None:
            return
        eintrag = Bildmodelltestfall(self.job, self.optionen).eintrag()
        if eintrag is None:
            return
        kandidaten = [b for b in bilder if b.get('kamera_bekannt') and len(b.get('gesicht68') or []) >= 68]
        kandidaten.sort(key=lambda b: -float(((b.get('gesicht') or {}).get('hoehe')) or 0))
        if not kandidaten:
            return
        b = kandidaten[0]
        referenz = G9texturmodell(eintrag['regler'])
        kamera = G9bildkamera.aus_browser(b['kamera_bekannt'], b.get('kasten'))
        tabelle = G9gesichtslandmarken.bauen(referenz.punkte, referenz.flaechen, kamera, b['gesicht68'],
                                             quelle=b['datei'])
        if tabelle is not None:
            tabelle.speichern()

    def _auftrag(self, bilder, modell, abtastung):
        ordner = self.ablage.ergebnis()
        modell.speichern(ordner / self.MODELL)
        for alt in ordner.glob('beitrag_*.jpg'):     # Beitragsbilder des letzten Laufs
            alt.unlink()
        from .bildmodellposierung import Bildmodellposierung

        posierung = Bildmodellposierung(self.job, self.ablage, modell)
        auftrag = {
            'modell': str(ordner / self.MODELL),
            'bilder': [self._eintrag(b, posierung) for b in bilder],
            'abtastung': str(abtastung.pfad(abtastung.seite)),
            'ausgabe_textur': str(ordner / self.TEXEL),
            'beitraege': str(ordner),
        }
        pfad = ordner / self.AUFTRAG
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(auftrag, f)
        return pfad

    def fotofarben(self, bilder, modell, abtastung):
        """`(hd {farbe_k, gewicht_k, herkunft_k, punktfarbe, punktgewicht}, antwort)` aus python10."""
        pfad = self._auftrag(bilder, modell, abtastung)
        prozess = subprocess.Popen(
            [settings.PIPELINE_PYTHON, os.path.join(Wrapperpfad.pfad(), self.RUNNER), str(pfad)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
            errors='replace', cwd=Wrapperpfad.pfad(),
        )
        try:
            aus, fehler = prozess.communicate(timeout=self.WARTEZEIT)
        except subprocess.TimeoutExpired:
            prozess.kill()
            raise RuntimeError('Fotofarben: keine Antwort nach %d s' % self.WARTEZEIT) from None
        antwort = Bildmodellmehrbild.antwort(aus)
        if not antwort or 'error' in antwort:
            raise RuntimeError('Fotofarben: %s' % ((antwort or {}).get('error') or (fehler or '')[-400:]))
        with np.load(self.ablage.ergebnis() / self.TEXEL) as d:
            return {k: d[k] for k in d.files}, antwort

    # ------------------------------------------------------------- Backen

    def _kacheln(self, hd, abtastung, melder=None):
        """`(kacheln, herkunft, hautton)` — Lücken füllen, Kacheln backen (python14, Sekunden)."""
        from Genesis9.restmorph import G9restmorph
        from Genesis9.texturbacken import G9texturbacken

        gedeckt = np.asarray(hd['punktgewicht'], dtype=float) > 0
        if melder:
            melder(0.6, 'Lücken füllen (%d von %d Punkten gedeckt)' % (int(gedeckt.sum()), len(gedeckt)))
        # Lücken: ungedeckte Punkte nehmen den Mittelwert ihrer Nachbarn (Kanten des Käfigs);
        # die Deckung läuft über dieselben Kanten aus (weicher Rand statt harter Kante).
        gewicht_feld = gedeckt.astype(float)
        gefuellt = G9restmorph.glaetten(np.asarray(hd['punktfarbe'], dtype=float), gewicht_feld, schritte=0)
        feder = G9restmorph.glaetten(np.repeat(gewicht_feld[:, None], 3, axis=1), gewicht_feld,
                                     schritte=0)[:, 0]
        alpha = np.clip((feder - 0.2) / 0.8, 0.0, 1.0)
        hautton = Bildmodelltextur.hautton(self.job.bilder).get('hautton')
        if melder:
            melder(0.7, 'Kacheln backen (%d²)' % abtastung.seite)
        kacheln, herkunft = G9texturbacken(abtastung.seite).backen(
            gefuellt, alpha, self.ablage.ergebnis(), 'fototextur', hautton, hd)
        return kacheln, herkunft, hautton

    def nachbacken(self, melder=None):
        """Nur die Kacheln neu, aus `fototextur.npz` (kein python10, Sekunden) — nach einer
        Änderung am Backen (weißer Hintergrund, 20.09.2026). None ohne Texel oder Ergebnis."""
        from Genesis9.texturabtastung import G9texturabtastung

        pfad = self.ablage.ergebnis() / self.TEXEL
        alt = self.job.ergebnis.get('fototextur')
        if not pfad.is_file() or not alt:
            return None
        with np.load(pfad) as d:
            hd = {k: d[k] for k in d.files}
        kacheln, herkunft, hautton = self._kacheln(hd, G9texturabtastung.holen(), melder)
        return self._verschiebung(dict(
            alt, kacheln={str(k): os.path.basename(v) for k, v in kacheln.items()},
            herkunft={str(k): os.path.basename(v) for k, v in herkunft.items()},
            hautton=hautton, stand=int(time.time())), melder)

    def _posen(self, bilder, melder=None):
        """T1: Pose und Kamera je Körperbild aus GVHMR nachholen (`Bildmodellposierung.nachholen`)."""
        from .bildmodellposierung import Bildmodellposierung

        Bildmodellposierung.nachholen(self.job, self.ablage, bilder, melder)

    def backen(self, melder=None):
        """Alles in einem: Modell, Runner, Kacheln, Karten. None ohne taugliche Bilder."""
        from Genesis9.kachelkarte import G9kachelkarte
        from Genesis9.texturabtastung import G9texturabtastung
        from Genesis9.texturmodell import G9texturmodell

        bilder = self.bilder()
        if not bilder:
            return None
        if melder:
            melder(0.02, 'Texturabtastung (%d²) und Modell' % G9texturabtastung.SEITE)
        abtastung = G9texturabtastung.holen()
        self._gesichtstabelle(bilder)
        self._posen(bilder, melder)
        modell = G9texturmodell(self.stellung())
        if melder:
            melder(0.05, 'Fototextur aus %d Bildern (python10)' % len(bilder))
        hd, antwort = self.fotofarben(bilder, modell, abtastung)
        gedeckt = np.asarray(hd['punktgewicht'], dtype=float) > 0
        kacheln, herkunft, hautton = self._kacheln(hd, abtastung, melder)
        ordner = self.ablage.ergebnis()
        karten = G9kachelkarte(abtastung, modell.teil).schreiben(ordner)
        texel = antwort.get('texel') or {}
        aus = {
            'kacheln': {str(k): os.path.basename(v) for k, v in kacheln.items()},
            'herkunft': {str(k): os.path.basename(v) for k, v in herkunft.items()},
            'karten': {str(k): os.path.basename(v) for k, v in karten.items()},
            'bilder': len(bilder),
            'je_bild': antwort.get('je_bild'),
            'deckung': round(float(gedeckt.mean()), 3),
            'deckung_hd': round(float(texel.get('gedeckt', 0)) / max(1, int(texel.get('gesamt', 0) or 1)), 3),
            'seite': abtastung.seite,
            'hautton': hautton,
            'stand': int(time.time()),
        }
        logger.info('Bildmodell %s: Fototextur %s', self.job.kennung,
                    {k: v for k, v in aus.items() if k != 'je_bild'})
        return self._verschiebung(aus, melder)

    def _verschiebung(self, aus, melder=None):
        """Alter/Tonus/Masse als Verschiebungskacheln dazu (`Bildmodellhautverschiebung`, 21.09.2026)."""
        from .bildmodellhautverschiebung import Bildmodellhautverschiebung

        return Bildmodellhautverschiebung.anfuegen(aus, self.optionen.get('person'),
                                                   self.ablage.ergebnis(), melder)
