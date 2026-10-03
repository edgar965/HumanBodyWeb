# -*- coding: utf-8 -*-
"""Iterationsrunde — eine Runde der Iterationen rechnen (bauen, rendern, benoten) und im Auftrag ablegen
(30.09.2026).

`bewerten`: die Kandidaten der Runde gehen an die Genesis-Engine (`Genesisengine2d3dkleider.rendern`),
je Kandidat kommen die Renders in den Blickwinkeln der Vorlagen zurück und werden gegen die Vorlage benotet
(`Iterationsnote`, gewichtet nach dem Gewicht der Fotos). `ablegen`: Vergleichstafel, die Renders je
Blickwinkel (`runde_NNN_ansicht_±WWW.png`, aufklappbar im Reiter) und — bei übernommenen Runden — Figur +
Haar + Rig (`runde_NNN_modell.glb`) nach `iterationen/`, dazu der ganze Wertesatz (`werte`) in einen
Eintrag in `ergebnis['iterationen']` (Reiter „Iterationen" der Seite). Abgelegt werden nur Runden, die etwas
zeigen — die Ausgangslage, jede Verbesserung und jeder Vorschlag der Prüf-KI; alle Runden stehen als Zahlen
in `ergebnis['kreislauf']['verlauf']`.

Gegenüber `Kostuemrunde` in BlenderModel fehlt, was zum Bau in Blender gehörte: Fototextur, Umriss-Hülle,
Sichtmodell und das Detailbild für die Prüf-KI.
"""

import logging
import shutil
import time

from django.utils import timezone

from .genesisengine2d3dkleider import Genesisengine2d3dkleider
from .iterationsbild import Iterationsbild
from .iterationsnote import Iterationsnote
from .iterationstafel import Iterationstafel

logger = logging.getLogger('core')

__all__ = ['Iterationsrunde']


class Iterationsrunde:
    #: So selten wird ein Modell-GLB geschrieben (Sekunden zwischen zwei); dazwischen zeigt die Bühne das jüngste.
    MODELL_ABSTAND_S = 45.0
    #: Rand um die Figur beim Zuschneiden eines Renders, als Anteil ihrer Höhe.
    RAND = 0.04
    #: Größe eines Felds der Vergleichstafel für die Prüf-KI (Bildpunkte, Breite × Höhe).
    KRITIK_GROESSE = (256, 384)

    def __init__(self, lauf, koerper, referenzen, parallel=1):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.koerper = koerper
        self.referenzen = referenzen
        self._letztes_modell = None
        # Die Engine (`parallel` Prozesse); `schliessen` am Ende des Laufs.
        self.engine = Genesisengine2d3dkleider(lauf, parallel=parallel)

    def schliessen(self):
        self.engine.schliessen()

    def winkel(self):
        return sorted({float(r.winkel) for r in self.referenzen})

    def ordner(self, runde):
        return self.ablage.arbeit('runden') / ('runde_%04d' % runde)

    def bewerten(self, runde, kandidaten, melden=None):
        """`kandidaten`: [(name, werte)] → [{name, werte, note, je_ansicht, renders, teile, vorn_grad,
        sekunden}] in derselben Folge."""
        aus = self.ordner(runde)
        bericht = self.engine.rendern(self.koerper, aus, kandidaten, self.winkel(), fortschritt=melden)
        ergebnisse = []
        for name, werte in kandidaten:
            eintrag = bericht['kandidaten'][name]
            je_ansicht, renders, paare = [], {}, []
            for r in self.referenzen:
                datei = eintrag['bilder'][str(int(round(r.winkel)))]
                render = Iterationsbild.aus_render(aus / name / datei)
                note = Iterationsnote.vergleichen(r.bild, render)
                renders[r.datei] = render
                je_ansicht.append(
                    {
                        'datei': r.datei,
                        'original': r.original,
                        'winkel': r.winkel,
                        'bild': aus / name / datei,
                        **note,
                    }
                )
                paare.append((r.gewicht, note))
            ergebnisse.append(
                {
                    'name': name,
                    'werte': werte,
                    'note': Iterationsnote.gesamt(paare),
                    'je_ansicht': je_ansicht,
                    'renders': renders,
                    'teile': eintrag.get('teile') or {},
                    'vorn_grad': bericht.get('vorn_grad'),
                    'sekunden': bericht.get('sekunden'),
                }
            )
        return ergebnisse

    def modell(self, runde, werte):
        """Figur + Haar + Rig einer übernommenen Runde als GLB, in der gestellten Haltung → Pfad oder
        None (nicht gebaut oder gescheitert — Fehler im Log, die Runde bleibt gültig). Eigener Aufruf der
        Engine NUR für diesen Wertesatz: Ein Modell für alle Kandidaten jeder Runde wäre ein Mehrfaches des
        Renderns."""
        aus = self.ordner(runde) / 'modell'
        try:
            bericht = self.engine.rendern(self.koerper, aus, [('modell', werte)], [], glb=True)
        except RuntimeError as fehler:
            logger.warning('2D3D Kleider %s: Modell der Runde %d: %s', self.job.kennung, runde, fehler)
            return None
        eintrag = bericht['kandidaten']['modell']
        datei = aus / 'modell' / (eintrag.get('glb') or 'haar.glb')
        return datei if datei.is_file() else None

    def modell_faellig(self):
        """Ein Modell-GLB je `MODELL_ABSTAND_S` Sekunden genügt — die Bühne zeigt ohnehin das jüngste."""
        jetzt = time.perf_counter()
        if self._letztes_modell is None or jetzt - self._letztes_modell >= self.MODELL_ABSTAND_S:
            self._letztes_modell = jetzt
            return True
        return False

    @classmethod
    def zuschneiden(cls, quelle, ziel):
        """Render auf die Figur zuschneiden (Alpha > 0, dazu `RAND` der Höhe): Die Kamera fasst mehr als die
        Figur, im Bild wäre sie neben dem Foto der Vorlage zu klein zum Vergleichen."""
        from PIL import Image

        with Image.open(quelle) as bild:
            rahmen = bild.getchannel('A').getbbox() if 'A' in bild.getbands() else None
            if rahmen is None:
                bild.save(ziel)
                return
            r = int(round((rahmen[3] - rahmen[1]) * cls.RAND))
            links, oben = max(0, rahmen[0] - r), max(0, rahmen[1] - r)
            rechts, unten = min(bild.width, rahmen[2] + r), min(bild.height, rahmen[3] + r)
            bild.crop((links, oben, rechts, unten)).save(ziel)

    def kritiktafel(self, runde):
        """Die Vergleichstafel für die Prüf-KI in doppelter Auflösung (256 × 384 je Feld gegen 128 × 192 der
        Anzeige), gebaut aus den abgelegten Renders der Runde. → Pfad oder None."""
        eintrag = next(
            (e for e in self.job.ergebnis.get('iterationen') or [] if e.get('runde') == runde), None
        )
        if eintrag is None:
            return None
        renders = {a['original']: a for a in eintrag.get('je_ansicht') or [] if a.get('render')}
        paare = []
        for r in self.referenzen:
            a = renders.get(r.original)
            pfad = self.ablage.iterationen(a['render']) if a else None
            if pfad is None or not pfad.is_file():
                continue
            vorlage = Iterationsbild.aus_vorlage(self.ablage.unter('eingang') / r.datei, self.KRITIK_GROESSE)
            render = Iterationsbild.aus_render(pfad, self.KRITIK_GROESSE)
            paare.append((r.winkel, vorlage, render, {'iou': a['iou']}))
        if not paare:
            return None
        ziel = self.ablage.arbeit('runden') / 'kritik.png'
        ziel.parent.mkdir(parents=True, exist_ok=True)
        return Iterationstafel.bauen(paare, ziel)

    def aufraeumen(self, runde):
        """Die Zwischendateien der Runde (Renders, GLBs der Kandidaten) — abgelegt ist, was bleiben soll."""
        shutil.rmtree(self.ordner(runde), ignore_errors=True)

    def ablegen(
        self,
        runde,
        art,
        erg,
        notiz,
        aenderungen=None,
        kritik=None,
        uebernommen=True,
        start=None,
        mit_modell=True,
    ):
        """Tafel (+ GLB, wenn übernommen und `mit_modell`) nach `iterationen/`, Eintrag in
        `ergebnis['iterationen']`. → Pfad der Tafel. `start`: `time.perf_counter()` zu Beginn der Runde —
        daraus die Dauer der Iteration (`sekunden`, samt Prüf-KI und Modell-GLB), die die Tabelle neben der
        Uhrzeit zeigt. `mit_modell`: das Modell nur, wenn `modell_faellig` — nicht in jeder Runde."""
        ziel = self.ablage.iterationen()
        ziel.mkdir(parents=True, exist_ok=True)
        tafel = 'runde_%03d_vergleich.png' % runde
        Iterationstafel.bauen(
            [
                (r.winkel, r.bild, erg['renders'][r.datei], n)
                for r, n in zip(self.referenzen, erg['je_ansicht'], strict=True)
            ],
            ziel / tafel,
        )
        dateien = {'vergleich': tafel}
        je_ansicht = []
        for a in erg['je_ansicht']:
            bild = 'runde_%03d_%s' % (runde, a['bild'].name)
            if a['bild'].is_file():
                self.zuschneiden(a['bild'], ziel / bild)
            je_ansicht.append({k: a[k] for k in ('original', 'winkel', 'iou', 'farbe')} | {'render': bild})
        if uebernommen and mit_modell:
            glb = self.modell(runde, erg['werte'])
            if glb is not None:
                dateien['modell'] = 'runde_%03d_modell.glb' % runde
                shutil.copyfile(glb, ziel / dateien['modell'])
        eintrag = {
            'runde': runde,
            'zeit': timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'),
            'sekunden': round(time.perf_counter() - start, 1) if start is not None else None,
            'art': art,
            'uebernommen': uebernommen,
            'notiz': notiz,
            'note': erg['note'],
            'je_ansicht': je_ansicht,
            'werte': erg['werte'],
            'aenderungen': aenderungen or {},
            'teile': erg['teile'],
            'dateien': dateien,
        }
        if kritik:
            eintrag['kritik'] = kritik
        self.job.ergebnis.setdefault('iterationen', []).append(eintrag)
        return ziel / tafel
