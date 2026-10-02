# -*- coding: utf-8 -*-
"""Begutachtungswerkzeug — was eine Begutachtungsrunde um den Bau herum braucht: Sichtkörper der Fotos, Stofflöser,
Fotoprojektion und die gebackene Haut des Körpers (aus `Begutachtungsrunde` herausgelöst, 01.10.2026 — die Datei stand
bei 299 Zeilen).

Eine Instanz je Lauf: Sichtkörper und Körperpunkte werden zwischengespeichert (je Modellhöhe auf den cm).
"""

import numpy as np

__all__ = ['Begutachtungswerkzeug']


class Begutachtungswerkzeug:
    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage
        self._koerper_punkte = None
        self._sicht = None

    def takt(self, text):
        """Abschnitt `text` beginnt: die Dauer des vorigen ins Log (Frage Edgar 02.10.2026 „warum dauert eine Runde so
        lange?" — gemessen waren nur 43–44 s je Runde im Block, nicht wofür)."""
        import logging
        import time
        jetzt = time.perf_counter()
        vorher = getattr(self, '_takt', None)
        if vorher:
            logging.getLogger('core').info('2D3D Kleider %s: %.1f s %s', self.job.kennung, jetzt - vorher[0], vorher[1])
        self._takt = (jetzt, text)

    def zubehoer(self, referenzen):
        """`{'uhr': ['l'|'r', …]}` — was die Fotos an Zubehör zeigen (`Uhrerkennung`), einmal je Lauf; fehlt das Stück
        dazu in der Garderobe, wird es gebaut (`G9uhrstueck`, ~1 s). Fehler: leer, mit Log — Zubehör ist Beiwerk."""
        if getattr(self, '_zubehoer', None) is None:
            import logging
            try:
                from Genesis9.garderobe import G9garderobe
                from Genesis9.uhrstueck import G9uhrstueck

                from .uhrerkennung import Uhrerkennung
                uhr = [s for s, e in Uhrerkennung(self.ablage).erkennen(referenzen).items() if e['gefunden']]
                for seite in uhr:
                    if not G9garderobe.eintrag('eigen_uhr_%s' % seite):
                        G9uhrstueck.bauen(seite)
                self._zubehoer = {'uhr': uhr, 'bart': self._bart()}
            except Exception:  # noqa: BLE001 — Beiwerk: die Runde läuft ohne weiter
                logging.getLogger('core').exception('2D3D Kleider %s: Zubehör nicht erkannt', self.job.kennung)
                self._zubehoer = {}
        return self._zubehoer

    #: So viele Netzflächen in der Bartzone der Haarmaske (`Haarmaske._bart`: Haar im unteren Gesicht bei kurzem
    #: Kopfhaar) sind ein Bart. Testauftrag 2026.10.01.12.38.09 (Schnurrbart + Stoppeln): 2.064.
    BART_MIN = 300

    def _bart(self):
        """True, wenn das Netz der Fotos einen Bart zeigt (Schritt „haar", `arbeit/haar_maske.npz`) — nur auf der
        männlichen Grundfigur: der Kinnbeweis der Haarmaske (`Haarmaske.KINN_ANTEIL`) hat keine Gegenprobe ohne Bart."""
        pfad = self.ablage.arbeit('haar_maske.npz')
        if ((self.job.optionen or {}).get('figur') or {}).get('basis') != 'masculine' or not pfad.is_file():
            return False
        with np.load(pfad) as d:
            return 'bart' in d.files and int(np.asarray(d['bart'], dtype=bool).sum()) >= self.BART_MIN

    def haarfarbe(self):
        """Mittlere Farbe (sRGB 0…1) der Haarflächen des Netzes (`haar_maske.haar` × Netztextur) — der Startwert der
        Haarfarbe für Runde 1, bevor ein Render sie misst; None ohne Maske oder Textur."""
        if getattr(self, '_haarfarbe', False) is False:
            self._haarfarbe = None
            pfad = self.ablage.arbeit('haar_maske.npz')
            if pfad.is_file():
                from .meshfigurkleidung import Meshfigurkleidung
                scan, _ = Meshfigurkleidung(type('Lauf', (), {'job': self.job, 'ablage': self.ablage})()).koerpernetz()
                with np.load(pfad) as d:
                    haar = np.asarray(d['haar'], dtype=bool)
                if scan.textur is not None and len(haar) == len(scan.flaechen) and haar.any():
                    index = np.flatnonzero(haar)
                    rgb = scan.farben(index, np.full((len(index), 3), 1.0 / 3.0)).astype(np.float64) / 255.0
                    self._haarfarbe = [round(float(c), 4) for c in np.median(rgb, axis=0)]
        return self._haarfarbe

    def fotostuecke(self):
        """`{oberteil|hose|socken: Garderobenkennung}` — die Kleider aus dem Netz der Fotos (`Fotostuecke`, beim ersten
        Mal ~150 s, danach aus dem Auftrag); leer, wenn es keine gibt."""
        if getattr(self, '_fotostuecke', None) is None:
            from .fotostuecke import Fotostuecke
            self._fotostuecke = Fotostuecke(self.job, self.ablage).holen()
        return self._fotostuecke

    def kacheln(self):
        """`{kachel: Pfad}` der gebackenen Haut — der Körper der Runde trägt sie (`Koerpertextur`)."""
        from .koerpertextur import Koerpertextur
        return Koerpertextur.kacheln(self.job, self.ablage)

    def drapierer(self):
        """Die Stofflöser für `kleid_drapieren` — Newton (Vorgabe), Blender und der Stoffsolver (Blenders Cloth auf der GPU), alle im
        Arbeitsordner des Auftrags."""
        from .engine2d3dkleiderblender import Engine2d3dKleiderblender
        from .kleiddrapierung import Kleiddrapierung
        from .stoffsolverdrapierung import Stoffsolverdrapierung
        return {'newton': Kleiddrapierung(self.ablage.arbeit('stoff')),
                'blender': Engine2d3dKleiderblender(self.ablage.arbeit('blender')),
                'stoffsolver': Stoffsolverdrapierung(self.ablage.arbeit('stoffsolver'))}

    def haardynamik(self):
        """Der Arbeiter für `haar_dynamik` (Blenders Haar-Dynamik als Stoffsolver auf der GPU), im Arbeitsordner des Auftrags —
        nur per Rezeptzeile von Hand; die Automatik und die Prüf-KI wählen sie nie (`Begutachtungskritik.VERBOTEN`)."""
        from .haardynamik import Haardynamik
        return Haardynamik(self.ablage.arbeit('haardynamik'))

    def fototextur(self, modell, teile, referenzen, render, bau, aus):
        """Die Haut aus den Fotos (`Koerperfotoprojektion`, einmal je Körper), dann die Fotoprojektion der gewünschten
        Stücke (`Kleidfotoprojektion`) und die Texturen der Teile danach neu."""
        import logging

        from .kleidfotoprojektion import Kleidfotoprojektion
        from .koerperfotoprojektion import Koerperfotoprojektion
        farbig = [r for r in referenzen if r.farbe]          # Fotos mit anderer Kleidung zählen nur für die Form
        try:
            Koerperfotoprojektion(self.job, self.ablage).bauen(teile, farbig, render, aus)
            self._haarzonen(teile, farbig, render, aus)
        except Exception:  # noqa: BLE001 — ohne Fotohaut rechnet die Runde mit der gebackenen weiter
            logging.getLogger('core').exception('2D3D Kleider %s: Haut/Haarzonen aus den Fotos nicht gebaut',
                                                self.job.kennung)
        if not getattr(modell, 'fotowuensche', None):
            return {}
        bericht = Kleidfotoprojektion(self.ablage, render, aus).bauen(modell, teile, farbig)
        gebaut = [k for k, b in bericht.items() if not b.get('fehler')]
        if gebaut:
            bau.textur_auffrischen([t.get('ruhe', t) for t in teile], modell, set(gebaut))
            for t in teile:                     # die gehäuteten Kopien tragen dieselben Bilder wie ihre Ruhelage
                t['textur'] = t.get('ruhe', t)['textur']
        return bericht

    def _haarzonen(self, teile, referenzen, render, aus):
        """Fotofarbe je Kopfzone relativ zum ganzen Haar (`Haarzonen.messen`), einmal je Frisur → `ergebnis.haarzonen`
        (`IterationHaare.zonen` macht daraus `m.haar_zonenfarbe`)."""
        from .haarzonen import Haarzonen
        from .koerperfotoprojektion import Koerperfotoprojektion
        alt = dict((self.job.ergebnis or {}).get('haarzonen') or {})
        gemessen = dict(alt)
        for i, t in enumerate(teile):
            sorte = str(t.get('sorte'))
            if (t.get('art') != 'haar' or not t.get('textur') or sorte in gemessen
                    or any(o in sorte for o in Haarzonen.OHNE)):
                continue
            projektion = Koerperfotoprojektion(self.job, self.ablage)._projektion(teile, referenzen, render, aus, i)
            gemessen[sorte] = Haarzonen.messen([t], projektion).get(sorte) or {}
        if gemessen != alt:
            self.job.ergebnis = dict(self.job.ergebnis or {}, haarzonen=gemessen)
            self.job.save(update_fields=['ergebnis', 'updated_at'])

    def bestes_glb(self, z, name):
        """Die GLB der besten Runde (A-Pose mit Rig) — einmal am Ende eines Laufs statt in jeder Runde (Edgar
        02.10.2026: „ich brauche kein GLB je Runde"); Export, Film und Animationsexport lesen sie
        (`iterationen/runde_NNN_modell.glb`, Kopie `ergebnis/<name>`)."""
        import shutil

        from Genesis9.modellmitkleidern import ModellMitKleidern

        from .haarzonen import Haarzonen
        from .kleidermodellbau import Kleidermodellbau
        beste = int(z.get('runde_bester') or 0)
        if not beste or not z.get('modell'):
            return None
        pfad = self.ablage.iterationen('runde_%03d_modell.glb' % beste)
        if not pfad.is_file():
            modell = ModellMitKleidern.aus(z['modell'])
            bau = Kleidermodellbau(self.job.stellung(), None, koerper=modell.koerper, kacheln=self.kacheln())
            bau.glb(Haarzonen.anwenden(bau.teile(modell), modell.farben), pfad)
        shutil.copyfile(pfad, self.ablage.ergebnis(name))
        return pfad

    def sichtkoerper(self, referenzen, z):
        """`Sichtkoerper` aus den Silhouetten der Vorlagen — je Lauf einmal je Modellhöhe (auf den cm); None ohne
        Fotos."""
        from iterationen2d3d.sichtkoerper import Sichtkoerper

        from .kleidermodellbau import Kleidermodellbau
        if not referenzen:
            return None
        if self._koerper_punkte is None:
            self._koerper_punkte = np.asarray(Kleidermodellbau(self.job.stellung()).koerper()['punkte'])
        hoehe = round(float(z.get('modell_hoehe') or self._koerper_punkte[:, 1].max()), 2)
        if self._sicht is not None and self._sicht[0] == hoehe:
            return self._sicht[1]
        sicht = Sichtkoerper([(r.winkel, r.bild.maske) for r in referenzen], hoehe, self._koerper_punkte)
        self._sicht = (hoehe, sicht)
        return sicht
