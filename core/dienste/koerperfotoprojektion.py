# -*- coding: utf-8 -*-
"""Koerperfotoprojektion — die Haut des Körpers aus den FOTOS, nicht aus dem TRELLIS-Netz (02.10.2026, nachts).

Befund Edgar: „die Textur der Beine von hinten ist auch sehr schlecht … Die ganzen iterativen Anpassungen sollen sich an
den Fotos als Vorlage richten, NICHT mehr an dem Trellis Modell." Bis dahin backte der Schritt „Körper" die
Hautkacheln aus den Farbproben des Netzes (`Meshfigurende.backen`) — dessen Textur ist TRELLIS' eigene Malerei, an den
Beinen hinten verwaschen und fleckig; die Runden übernahmen sie unverändert (`Koerpertextur`).

Hier holt der Körper seine Farbe in der Runde aus den Fotos — mit derselben Abbildung wie die Note und die
Fotoprojektion der Stücke (`Fotoprojektion`, Kennfarbenrender in der Haltung der Fotos, Teilmaske des Körpers: was ein
Kleid im Modell verdeckt, nimmt keine Farbe):

1. je Kachel die Texel des Körpers rastern (`G9uvraster`, `RASTER` px; die Kacheln selbst haben 2048 px)
2. Farbe aus den Fotos (Gewicht Normale · Blick⁴), Deckung = bester Blick (Normale · Blick) × im Foto auf der Figur
3. nur Hautfarbe übernehmen: ist die Fotofarbe nicht warm (Shirt, Shorts, Socke unter einem kürzeren Modellstück),
   bleibt die gebackene — außer dort, wo auch die gebackene nicht warm ist (Haar auf der Kopfhaut)
4. weicher Übergang: Deckung geglättet (`WEICH`), Lücken der Fotofarbe aufgefüllt, auf Kachelgröße gezogen und über die
   gebackene Kachel gelegt

Einmal je Körper (`ergebnis.fototextur.stand`) und Fassung: Die neuen Kacheln stehen in `fototextur.kacheln` — Runde,
Bühne (`Engine2d3dKleiderstandmodell`) und Export lesen sie dort —, die gebackenen bleiben als `fototextur.kacheln_netz`.
Rechnet „Körper" neu, ersetzt er `fototextur` ganz, und die nächste Runde projiziert wieder.

Fassung 2 (05.10.2026, Edgar: „Fotohaut nur auf Wunsch ist schlecht, da in den folgenden Iterationen die Fotohaut dann doch verschlechtert wird … untersuche richtig und fixe"). Gemessen an Sapiens 2
(`ProjektTemp/_wegwerf/edgar/kopf_probe.py`, Kopfbilder und Kacheln vorher/nachher):

* Die KOPFKACHEL (1001) bleibt die gebackene. Die Projektion kennt keine Kamera der Fotos, sie richtet nur an Höhe und Schwerpunkt der Figur aus; am Kopf (4 cm breite Augen, 6 cm Mund) liegen
  Augen, Brauen und Mund dadurch einige Millimeter daneben. Das Ergebnis: dunkle Schmieren in den Augenhöhlen, ein grauer Balken über der Oberlippe, Foto-Haar auf Schläfen und Nacken gemalt — das Gesicht
  mit der gebackenen Kachel sah im Kopfbild deutlich natürlicher aus. Das Haar übernimmt die Haarkappe (`Haarumbau`), die Schläfen- und Nackenbemalung ist nicht mehr nötig.
* Um Kleider herum nimmt die Haut keine Fotofarbe (`RAND_KLEID`, Pixel der Projektionsfläche): Am Saum der Hose standen schwarze Streifen und neben der Socke ein heller Block auf der Beinkachel — Foto-Pixel der
  Kleidung, die der um `Fotoprojektion.TOLERANZ` erweiterten Körpermaske zufielen.
* Die Haltung muss die der Fotos sein (Startrezept, `Standvorabkleider.haltungszeilen`): Mit gespreizten Armen vor Fotos mit hängenden Armen deckte die Fotohaut 0,4 % der Armkachel und 0,5 % des Rumpfs.
"""

import logging
import time

import numpy as np
from PIL import Image

from .fotoabgleich import Fotoabgleich
from .hautmischung import Hautmischung
from .hautproben import Hautproben
from .hautprobenmehrpose import Hautprobenmehrpose

logger = logging.getLogger('core')

__all__ = ['Koerperfotoprojektion']


class Koerperfotoprojektion:
    #: 3 (05.10.2026, Edgar: „das Licht aus der Vorlage herausrechnen", „die Beine und Arme haben Nähte", „Texturprobleme auch bei der Hand"): Licht je Ansicht heraus (`Fotolicht`, Option `iterationen.licht`), Ton
    #: der Fotohaut und der gebackenen Kachel angeglichen statt überblendet, keine Fotofarbe an der Hand (`Hautmischung`, `Hautproben`).
    #: 4 (06.10.2026, Edgar: „Kopfform, Augenbrauen, Haar ist auf dem Modell ganz anders als im Mesh", Haut dunkelbraun gegen helles Mesh): die Kopfkachel bekommt Fotohaut aus dem Vorderfoto, ausgerichtet über die Landmarken
    #: (`Kopfregistrierung`); ein Auftrag mit Fassung 3 rechnet beim nächsten Lauf neu.
    #: 5 (08.10.2026, Edgar: „Beine: nur 7 % Fotohaut. Eine Haltung passt nicht auf zwei verschiedene Aufnahmen"): jedes Foto projiziert in SEINER Haltung (`Haltungsansichten`, Option `iterationen.haltung_je_foto`, `Hautprobenmehrpose`);
    #: ein Auftrag mit Fassung 4 rechnet beim nächsten Lauf neu, ebenso beim Wechsel der Option.
    FASSUNG = 5
    GROESSE = (1024, 1536)
    RASTER = 1024
    #: Die Kopfkachel: Foto nur über die Kopfregistrierung (Kreuzprüfung unter `Kopfregistrierung.FEHLER_MAX_MM`) — sonst bleibt die gebackene Haut (Fassung 2: Foto ohne Registrierung verschob Augen und Mund).
    AUSGENOMMEN = (1001,)
    #: Texel der Kopfkachel sind etwa so viel kleiner als die der Körperkacheln (Gesicht 14 cm in ~460 Texeln gegen 1,1 mm je Texel am Körper): die Längen der Hautmischung wachsen mit.
    KOPF_MASSSTAB = 3.5
    #: Abstand zur Kleidung (Pixel der Projektionsfläche, 1 Pixel ≈ 1,1 mm), in dem die Haut keine Fotofarbe nimmt. Gemessen (Sapiens 2, `kopf_probe.py`): bei 4 sind die schwarzen Streifen am Saum und
    #: der helle Block über der Socke weg; bei 12 war die dünne dunkle Linie unter dem Saum nicht besser (sie liegt schon in der gebackenen Kachel), die Deckung aber kleiner (0,362 statt 0,374).
    #: Fassung 3: 16 statt 4 — der Schatten unter dem Saum der Hose und des Ärmels ist noch Kleidung (Edgar: die dunkle Linie am Oberschenkel); gemessen an hautfoto_1003.jpg: bei 8 stand die Linie noch.
    RAND_KLEID = 16
    #: Abstand zum Rand einer UV-Insel (Texel des Rasters), über den die Fotofarbe auf null ausblendet.
    RAND_INSEL = 6
    #: So viele Pixel der Fotofigur am Rand zählen für die Haut nicht (Hintergrundanteil der Randpixel). Fassung 3: 5 statt 3 — an den Armen stand ein dunkler Rand um jeden Fleck aus Fotohaut (Kante gegen die helle Wand).
    RAND_FOTO = 5
    #: Warm = Haut: R > G > B mit R − B über dieser Schwelle (0…1); wie `Fotostuecke.HAUT_ABSTAND` sinngemäß.
    WARM = 0.04

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage
        #: Berichte des `Fotoabgleich` je Ansicht (`hautfoto.abgleich`).
        self._abgleiche = []

    def noetig(self):
        from .iterationsoptionenfoto import Iterationsoptionenfoto as O
        f = (self.job.ergebnis or {}).get('fototextur') or {}
        hautfoto = f.get('hautfoto') or {}
        return bool(f.get('kacheln')) and (hautfoto.get('fassung') != self.FASSUNG or hautfoto.get('haltung_je_foto') != O.haltung_je_foto(self.job)
                                           or hautfoto.get('foto_abgleich') != O.foto_abgleich(self.job))

    @classmethod
    def warm(cls, rgb):
        rgb = np.asarray(rgb, dtype=np.float64)
        return (rgb[..., 0] > rgb[..., 1]) & (rgb[..., 1] > rgb[..., 2]) & (rgb[..., 0] - rgb[..., 2] > cls.WARM)

    # ------------------------------------------------------------ Rechnung

    def _projektion(self, teile, referenzen, render, aus, index, licht=0.0):
        """`licht`: Stärke, mit der das Licht der Fotos herausgerechnet wird (`Fotolicht`; 0 = aus — `Begutachtungswerkzeug._haarzonen` misst Verhältnisse am Haar und nimmt die Farbe, wie sie ist)."""
        from iterationen2d3d.fotoprojektion import Fotoprojektion

        from .kleidfotoprojektion import Kleidfotoprojektion
        kfp = Kleidfotoprojektion(self.ablage, render, aus)
        kfp.GROESSE = self.GROESSE
        alle = np.vstack([np.asarray(t['punkte']) for t in teile])
        kamera = Fotoprojektion.aus_render(alle, render.RAND, self.GROESSE)
        projektion = Fotoprojektion(kamera.mitte, kamera.halb, self.GROESSE, licht=licht)
        koerper = teile[index].get('art') == 'koerper'
        from .iterationsoptionenfoto import Iterationsoptionenfoto
        abgleich = koerper and Iterationsoptionenfoto.foto_abgleich(self.job)
        for r, abbildung, foto, masken in kfp._ansichten(teile, referenzen):
            ausschluss, foto_maske, foto_farbe = None, foto.maske, foto.farbe
            if abgleich:        # das Foto in den Rahmen der Modellsilhouette ziehen (08.10.2026, `Fotoabgleich`)
                foto_farbe, foto_maske, bericht = Fotoabgleich.abgleichen(foto.farbe, foto.maske, np.any(masken, axis=0))
                self._abgleiche.append(dict(bericht, winkel=r.winkel))
            if koerper:         # Kleidung, Zubehör: ihr Rand nimmt der Haut die Fotofarbe (`RAND_KLEID`); Augen, Mund und Brauen gehören zum Körper
                andere = [m for i, m in enumerate(masken) if teile[i].get('art') != 'koerper']
                if andere:
                    ausschluss = Fotoprojektion.erweitern(np.any(andere, axis=0), self.RAND_KLEID)
                # Die Randpixel der Fotofigur tragen Hintergrund: sie ergaben helle Linien an den Seiten der Beine (Rand der Fotofläche in der Kachel).
                foto_maske = ~Fotoprojektion.erweitern(~np.asarray(foto_maske, dtype=bool), self.RAND_FOTO)
            projektion.ansicht(r.winkel, abbildung, foto_farbe, foto_maske, masken[index], ausschluss)
        return projektion

    def _kopf(self, teile, referenzen, render, aus):
        """Kopfkachel aus dem Vorderfoto (`Kopfregistrierung`) → `(Hautproben des Kopfes, Bericht)` oder None (dann bleibt die gebackene; der Grund steht im Log und im Steckbrief)."""
        from .kopfregistrierung import Kopfregistrierung
        try:
            kopf, bericht = Kopfregistrierung(self.ablage, render).projektion(teile, referenzen, aus)
        except (OSError, ValueError, RuntimeError, KeyError) as fehler:
            kopf, bericht = None, 'Fehler: %s' % fehler
        if kopf is None:
            logger.warning('2D3D Kleider %s: Kopfkachel bleibt gebacken (%s)', self.job.kennung, bericht)
            self._kopf_grund = bericht
            return None
        self._kopf_grund = None
        return kopf, bericht

    @staticmethod
    def _licht_uebertragen(projektion, kopf):
        """Das Licht der Fotos, über die Körperkacheln geschätzt, gilt auch für den Kopf (es hängt an Lage und Normale, nicht an der Kachel); die Gesichtsfarbe selbst taugt dafür nicht — sie ist erst durch den Warp richtig."""
        kopf.licht = projektion.licht
        kopf._licht_fertig = True  # noqa: SLF001
        for a in kopf.ansichten:
            gleich = next((b for b in projektion.ansichten if abs(b['winkel'] - a['winkel']) < 1e-6 and b.get('licht') is not None), None)
            if gleich is not None:
                a['licht'] = gleich['licht']

    def _kachel(self, proben, p, grund_pfad, ziel, kopf=False):
        """Eine Kachel: Fotofarbe (vom Licht befreit, ohne Hand) und Deckung im Raster, mit dem Ton der gebackenen Kachel angeglichen und nahtlos eingearbeitet (`Hautmischung`) → Anteil gedeckter Texel.
        `kopf`: die Kopfkachel — kein Hautton-Test (das Gesichtsoval der Foto-Maske sagt, was Haut ist; der graue Bart ist keine „warme" Farbe) und die Längen der Mischung im Maßstab des Kopfes (`KOPF_MASSSTAB`)."""
        from Genesis9.kleidfototextur import G9kleidfototextur
        from scipy.ndimage import distance_transform_edt
        s = self.RASTER
        with Image.open(grund_pfad) as bild:
            grund = np.asarray(bild.convert('RGB'), dtype=np.float32) / 255.0
        klein = np.asarray(Image.fromarray((grund * 255).astype(np.uint8)).resize((s, s), Image.BILINEAR), dtype=np.float32) / 255.0
        f, d, _getroffen = proben.farbe(p)
        zeile, spalte = p['index'][:, 0], p['index'][:, 1]
        if not kopf:
            d = d * (self.warm(f) | ~self.warm(klein[zeile, spalte]))    # Fotofarbe ohne Hautton nur, wo auch die Haut keinen hat
        farbe = np.zeros((s, s, 3), np.float32)
        deckung = np.zeros((s, s), np.float32)
        farbe[zeile, spalte], deckung[zeile, spalte] = f, d
        maske = p['maske']
        if not (deckung > 0).any():
            return 0.0
        voll = G9kleidfototextur._fuellen(farbe, deckung > 0, maske)
        # Zum Rand der UV-Inseln hin blendet die Fotofarbe aus: An den Nähten (Vorder- und Rückseite der Beine) sah die Projektion nur streifende Blickwinkel und legte helle Linien entlang der Beine.
        deckung = deckung * np.clip(distance_transform_edt(maske) / self.RAND_INSEL, 0.0, 1.0)
        neu, bericht = Hautmischung.mischen(klein, maske, voll, deckung, massstab=self.KOPF_MASSSTAB if kopf else 1.0)
        gross = grund.shape[1], grund.shape[0]
        unterschied = np.stack([np.asarray(Image.fromarray((neu - klein)[..., c].astype(np.float32)).resize(gross, Image.BILINEAR)) for c in range(3)], axis=-1)
        Image.fromarray(np.clip((grund + unterschied) * 255 + 0.5, 0, 255).astype(np.uint8)).save(ziel, quality=92)
        logger.info('2D3D Kleider %s: Hautmischung %s', self.job.kennung, bericht)
        return float((deckung[maske] > 0.5).mean())

    def _proben_je_ansicht(self, ansichten, referenzen, render, aus, licht):
        """Je Foto eine Projektion mit dieser einen Ansicht, gebaut mit den Teilen in DER Haltung des Fotos (`Haltungsansichten`) → `(Hautprobenmehrpose, [Körperteil in der Haltung je Foto])`.
        Hat ein Foto keine Silhouette (`Kleidfotoprojektion._ansichten`), trägt seine Projektion keine Ansicht und zählt nicht."""
        proben, koerper_je = [], []
        for r in referenzen:
            ohne = [t for t in ansichten.von(r) if t.get('art') != 'haar']
            koerper = next(t for t in ohne if t.get('art') == 'koerper')
            projektion = self._projektion(ohne, [r], render, aus, ohne.index(koerper), licht=licht)
            proben.append(Hautproben(projektion, koerper.get('haut'), koerper['dreiecke']))
            koerper_je.append(koerper)
        return Hautprobenmehrpose(proben), koerper_je

    def bauen(self, teile, referenzen, render, aus, ansichten=None):
        """Fotohaut je Kachel, Textur der Körperteile umgehängt → Steckbrief (oder None, wenn nichts zu tun war). `ansichten`: `Haltungsansichten` — haben Fotos eine eigene Haltung (08.10.2026), projiziert jedes in SEINER
        (`Hautprobenmehrpose`: Lage und Normale der Texel, Kennfarben und Licht je Foto), sonst alle in der Haltung des Modells wie bisher."""
        from Genesis9.uvraster import G9uvraster
        if not self.noetig() or not referenzen:
            return None
        t0 = time.perf_counter()
        index = next((i for i, t in enumerate(teile) if t.get('art') == 'koerper'), None)
        if index is None:
            return None
        koerper, ruhe = teile[index], teile[index].get('ruhe', teile[index])
        if ruhe.get('uv') is None or not ruhe.get('textur'):
            return None
        f = dict(self.job.ergebnis['fototextur'])
        netz = dict(f.get('kacheln_netz') or f['kacheln'])
        # Die Teile tragen die Kachel, die `Koerpertextur` ihnen gab — nach einer früheren Fotohaut die `hautfoto_<k>.jpg`, nicht die gebackene. Beide Namen gehören zur Kachel; sonst fiele ein NEUES Rechnen (Fassung, Option) bis auf
        # die Kachel 1005 aus (gemessen 08.10.2026, N1-Kopie: Deckung nur {1005: 0.0}).
        pfade = {str(self.ablage.ergebnis(n)): int(k) for namen in (f['kacheln'], netz) for k, n in namen.items()}
        ohne_haar = [t for t in teile if t.get('art') != 'haar']
        from .iterationsoptionen import Iterationsoptionen
        from .iterationsoptionenfoto import Iterationsoptionenfoto as O
        mehr = ansichten is not None and ansichten.verschieden
        licht = Iterationsoptionen.licht(self.job)
        if mehr:
            proben, koerper_je = self._proben_je_ansicht(ansichten, referenzen, render, aus, licht)
        else:
            projektion = self._projektion(ohne_haar, referenzen, render, aus, next(i for i, t in enumerate(ohne_haar) if t is koerper), licht=licht)
            proben = Hautproben(projektion, koerper.get('haut'), koerper['dreiecke'])
        gruppen = {}
        for i, eintrag in enumerate(ruhe['textur']):
            k = pfade.get(str(eintrag.get('albedo')))
            if k is not None:
                gruppen.setdefault(k, []).append({'name': 'k%d_%d' % (k, i), 'index_ab': 3 * int(eintrag['ab']),
                                                  'index_anzahl': 3 * int(eintrag['anzahl'])})
        neu, deckung = {}, {}
        unbekannt = sorted({str(e.get('albedo')) for e in ruhe['textur'] if pfade.get(str(e.get('albedo'))) is None and e.get('albedo')})
        if unbekannt or len(gruppen) < len(netz):
            logger.warning('2D3D Kleider %s: Fotohaut — Kacheln mit Gruppen %s von %s; Bilder ohne Kachel: %s', self.job.kennung, sorted(gruppen), sorted(netz), unbekannt)
        kopf = self._kopf(teile, referenzen, render, aus) if any(k in self.AUSGENOMMEN for k in gruppen) else None
        proben_kopf = Hautproben(kopf[0], koerper.get('haut'), koerper['dreiecke']) if kopf else None
        samml, samml_kopf = {}, {}
        for k, liste in sorted(gruppen.items()):
            if k in self.AUSGENOMMEN and kopf is None:
                continue
            raster = G9uvraster(koerper['punkte'], koerper['dreiecke'], ruhe['uv'], liste, groesse=self.RASTER)
            karten = [x for x in raster.alle().values() if x['maske'].any()]
            if not karten:
                continue
            if k in self.AUSGENOMMEN:
                samml_kopf[k] = proben_kopf.sammeln(karten)
            elif mehr:          # je Foto das Raster auf dem Körper in der Haltung dieses Fotos (dieselben Texel, andere Lage und Normale)
                samml[k] = proben.sammeln([[x for x in raster.umgelegt(kv['punkte']).alle().values() if x['maske'].any()] for kv in koerper_je])
            else:
                samml[k] = proben.sammeln(karten)
        if samml:
            proben.licht_schaetzen(list(samml.values()))           # das Licht je Ansicht über ALLE Kacheln zusammen (`Fotolicht`)
        if kopf:
            self._licht_uebertragen(proben.projektion, proben_kopf.projektion)
        for k, p in {**samml, **samml_kopf}.items():
            name = 'hautfoto_%d.jpg' % k
            deckung[k] = round(self._kachel(proben_kopf if k in samml_kopf else proben, p, self.ablage.ergebnis(netz[str(k)]), self.ablage.ergebnis(name), kopf=k in samml_kopf), 3)
            if deckung[k] > 0:
                neu[str(k)] = name
        kacheln = dict(netz, **neu)
        f.update(kacheln=kacheln, kacheln_netz=netz, hautfoto={
            'fassung': self.FASSUNG, 'deckung': deckung, 'sekunden': round(time.perf_counter() - t0, 1),
            'haltung_je_foto': O.haltung_je_foto(self.job), 'haltungen': sorted(r.datei for r in referenzen) if mehr else [],
            'foto_abgleich': O.foto_abgleich(self.job), 'abgleich': self._abgleiche,
            'kopf': kopf[1] if kopf else {'aus': getattr(self, '_kopf_grund', None) or 'nicht gerechnet'}})
        self.job.ergebnis = dict(self.job.ergebnis, fototextur=f)
        self.job.save(update_fields=['ergebnis', 'updated_at'])
        umbenannt = {str(self.ablage.ergebnis(netz[k])): str(self.ablage.ergebnis(n)) for k, n in neu.items()}
        for t in {id(koerper): koerper, id(ruhe): ruhe}.values():
            for eintrag in t.get('textur') or []:
                eintrag['albedo'] = umbenannt.get(str(eintrag.get('albedo')), eintrag.get('albedo'))
        logger.info('2D3D Kleider %s: Haut aus den Fotos — Deckung je Kachel %s, %.1f s', self.job.kennung, deckung,
                    time.perf_counter() - t0)
        return f['hautfoto']
