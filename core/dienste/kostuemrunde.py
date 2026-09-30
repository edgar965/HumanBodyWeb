# -*- coding: utf-8 -*-
"""Kostuemrunde — eine Runde des Kostüm-Kreislaufs rechnen (bauen, rendern, benoten) und im Auftrag ablegen.

`bewerten`: die Kandidaten der Runde reihum auf mehrere dauerhaft laufende Blender-Prozesse verteilt
(`Kostuemblender`), je Kandidat die Renders in den Blickwinkeln der Vorlagen, benotet gegen die Vorlage
(`Kostuemnote`, gewichtet nach dem Gewicht der Fotos). `ablegen`: Vergleichstafel, die Renders je Blickwinkel
(`runde_NNN_ansicht_±WWW.png`, aufklappbar im Reiter) und — bei übernommenen Runden — Figur + Kostüm + Rig
(`runde_NNN_modell.glb`, `modell`) nach `iterationen/`, dazu der ganze Wertesatz (`werte`) in einen Eintrag in
`ergebnis['iterationen']` (Reiter „Iterationen" der Seite). Abgelegt werden nur Runden, die etwas zeigen — die
Ausgangslage, jede Verbesserung und jeder Vorschlag der Prüf-KI; alle Runden stehen als Zahlen in
`ergebnis['kostuem']['verlauf']`.
"""

import logging
import shutil
import time

from django.utils import timezone

from .kostuembild import Kostuembild
from .kostuemblender import Kostuemblender
from .kostuemdetail import Kostuemdetail
from .kostuemmodell import Kostuemmodell
from .kostuemmodellablage import Kostuemmodellablage
from .kostuemnote import Kostuemnote
from .kostuemtafel import Kostuemtafel

logger = logging.getLogger('core')

__all__ = ['Kostuemrunde']


class Kostuemrunde:
    #: So selten wird ein Modell-GLB geschrieben (Sekunden zwischen zwei); dazwischen zeigt die Bühne das jüngste.
    MODELL_ABSTAND_S = 45.0

    #: So selten entsteht das Sichtmodell (Sekunden zwischen zwei) — es kostet mehr als das Modell aus Teilen.
    SICHT_ABSTAND_S = 300.0

    def __init__(self, lauf, koerper, referenzen, parallel=1, textur=True, huelle=True, sicht=True):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.koerper = koerper
        self.referenzen = referenzen
        self.textur = textur
        self.huelle = huelle
        self.sicht = sicht
        self._letzte_sicht = None
        self._texturen = None
        self._masken = None
        self._basis = None
        self._letztes_modell = None
        # Dauerhafte Blender-Arbeiter (`parallel` Prozesse, die Figur einmal je Lauf geladen); `schliessen` am
        # Ende.
        self.blender = Kostuemblender(lauf, parallel=parallel, dauerhaft=True)

    def schliessen(self):
        self.blender.schliessen()

    def winkel(self):
        return sorted({float(r.winkel) for r in self.referenzen})

    def ordner(self, runde):
        return self.ablage.arbeit('kostuem') / ('runde_%04d' % runde)

    def bewerten(self, runde, kandidaten, melden=None, basis=None):
        """`kandidaten`: [(name, werte)] → [{name, werte, note, je_ansicht, renders, glb}] in derselben Folge.
        `basis`: das Ausgangsmodell (Wertesatz) der Runde — an ihm hängt die Normierung der Umriss-Hülle."""
        aus = self.ordner(runde)
        self._basis = (
            basis  # das Modell der Runde (`modell`) wird mit derselben Normierung gebaut wie die Kandidaten
        )
        bericht = self.blender.rendern(
            self.koerper, aus, kandidaten, self.winkel(), fortschritt=melden, **self.huellenwahl(basis)
        )
        ergebnisse = []
        for name, werte in kandidaten:
            eintrag = bericht['kandidaten'][name]
            je_ansicht, renders, paare = [], {}, []
            for r in self.referenzen:
                datei = eintrag['bilder'][str(int(round(r.winkel)))]
                render = Kostuembild.aus_render(aus / name / datei)
                note = Kostuemnote.vergleichen(r.bild, render)
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
                    'note': Kostuemnote.gesamt(paare),
                    'je_ansicht': je_ansicht,
                    'renders': renders,
                    'teile': eintrag.get('teile') or {},
                    'vorn_grad': bericht.get('vorn_grad'),
                    'sekunden': bericht.get('sekunden'),
                }
            )
        return ergebnisse

    TEXTUR_GROESSE = (384, 576)
    TEXTUR_WINKEL = (0, 90, 180, -90)

    #: Ab diesem Anteil der Höhe (von oben) und heller als dieser Mittelwert (0…1) gilt ein Bildpunkt der Vorlage als
    #: Bodenschatten, nicht als Figur.
    SCHATTEN_AB = 0.93
    SCHATTEN_HELL = 0.70

    def texturen(self):
        """{winkel: Pfad} der normierten, nach außen verlängerten Vorlagenflächen für die Fototextur — je Lauf
        einmal gebaut (`Kostuembild.aufgefuellt`, dieselbe Fläche wie die Note, nur größer)."""
        if self._texturen is None:
            import numpy as np
            from PIL import Image

            ordner = self.ablage.arbeit('kostuem_texturen')
            ordner.mkdir(parents=True, exist_ok=True)
            aus = {}
            for r in self.referenzen:
                pfad = ordner / ('tex_%+04d.png' % round(r.winkel))
                flaeche = Kostuembild.aus_vorlage(self.ablage.unter('eingang') / r.datei, self.TEXTUR_GROESSE)
                farbe = (np.clip(flaeche.aufgefuellt(), 0, 1) * 255).astype(np.uint8)
                # Alpha = die Figur: Die Fototextur (`Fototextur`) nimmt außerhalb keine Farbe aus dem verlängerten Rand.
                # Ganz unten zählt der helle Bodenschatten der Vorlage nicht zur Figur (er färbte den Saum grau-weiß).
                figur = flaeche.maske.copy()
                unten = int(self.SCHATTEN_AB * figur.shape[0])
                figur[unten:] &= flaeche.farbe[unten:].mean(axis=2) < self.SCHATTEN_HELL
                form = (figur * 255).astype(np.uint8)
                Image.fromarray(np.dstack([farbe, form]), 'RGBA').save(pfad)
                aus[r.winkel] = pfad
            self._texturen = aus
        return self._texturen

    #: Kantenlänge (Bildpunkte) der Öffnung der Vorlagen-Silhouette: was dünner ist (Stab, Haarsträhne), fällt weg.
    MASKEN_OEFFNUNG = 7

    def masken(self):
        """{winkel: Pfad} der Silhouetten der Vorlage für die Umriss-Hülle (`Kostuemhuelle`): dieselbe
        normierte Fläche wie die Fototextur, weiß = Figur, GEÖFFNET — sonst zöge der Stab den Mantel bis zur
        Hand hinaus."""
        if self._masken is None:
            import numpy as np
            from PIL import Image, ImageFilter

            ordner = self.ablage.arbeit('kostuem_texturen')
            ordner.mkdir(parents=True, exist_ok=True)
            aus = {}
            for r in self.referenzen:
                pfad = ordner / ('maske_%+04d.png' % round(r.winkel))
                flaeche = Kostuembild.aus_vorlage(self.ablage.unter('eingang') / r.datei, self.TEXTUR_GROESSE)
                bild = Image.fromarray((flaeche.maske * 255).astype(np.uint8))
                bild = bild.filter(ImageFilter.MinFilter(self.MASKEN_OEFFNUNG)).filter(
                    ImageFilter.MaxFilter(self.MASKEN_OEFFNUNG)
                )
                bild.save(pfad)
                aus[r.winkel] = pfad
            self._masken = aus
        return self._masken

    def huellenwahl(self, basis):
        """Die Angaben für `Kostuemblender.rendern`, wenn der Mantel dem Umriss folgen soll (sonst leer)."""
        return {'masken': self.masken(), 'basis': basis} if self.huelle else {}

    def modell(self, runde, werte, sicht=False):
        """Figur + Kostüm + Rig einer übernommenen Runde als GLB, in der gestellten Haltung (Edgar,
        29.09.2026: „bitte auch Modell in den Runden"). Eigener Blender-Aufruf NUR für diesen Wertesatz: je
        Kandidat gemessen ~1,3 s mehr (Bindung + Export, 7,2 MB) — für alle Kandidaten jeder Runde wäre das
        ein Mehrfaches des Rendern. Mit `textur` bekommt das Modell die Farben der Vorlage (Fototextur,
        Vertexfarben; GLB ~16 MB, gemessen ~12 s im Arbeiter unter Last) und vier Ansichten damit.
        → `Kostuemmodell` (leere Felder: nicht gebaut oder gescheitert — Fehler im Log, die Runde bleibt gültig).
        `sicht`: dazu das Sichtmodell (Umriss der Fotos mit Fototextur), der Bau kostet ~10 s mehr."""
        aus = self.ordner(runde) / 'modell'
        befehl = {'glb': True, **self.huellenwahl(self._basis or werte)}
        winkel = []
        if self.textur:
            texturen = self.texturen()
            winkel = sorted(texturen)
            befehl.update(texturen=texturen, textur_winkel=self.TEXTUR_WINKEL)
            befehl['sicht'] = sicht and self.huelle
        try:
            bericht = self.blender.rendern(self.koerper, aus, [('modell', werte)], winkel, **befehl)
        except RuntimeError as fehler:
            logger.warning('BlenderModel %s: Modell der Runde %d: %s', self.job.kennung, runde, fehler)
            return Kostuemmodell()
        eintrag = bericht['kandidaten']['modell']
        ordner = aus / 'modell'
        datei = ordner / (eintrag.get('glb') or 'kostuem.glb')
        sicht_datei = ordner / eintrag['sicht_glb'] if eintrag.get('sicht_glb') else None
        return Kostuemmodell(
            datei if datei.is_file() else None,
            {w: ordner / name for w, name in (eintrag.get('textur_bilder') or {}).items()},
            sicht_datei if sicht_datei is not None and sicht_datei.is_file() else None,
            {w: ordner / name for w, name in (eintrag.get('sicht_bilder') or {}).items()},
        )

    def modell_faellig(self):
        """Ein Modell-GLB je `MODELL_ABSTAND_S` Sekunden genügt — die Bühne zeigt ohnehin das jüngste, und ein
        GLB mit Fototextur kostet mehr als eine ganze Runde."""
        jetzt = time.perf_counter()
        if self._letztes_modell is None or jetzt - self._letztes_modell >= self.MODELL_ABSTAND_S:
            self._letztes_modell = jetzt
            return True
        return False

    def sicht_faellig(self):
        """Das Sichtmodell kostet mehr als das Modell aus Teilen (Schichten, Bindung von ~140.000 Punkten: gemessen ~10 s
        mehr): alle `SICHT_ABSTAND_S` Sekunden, wenn ein Modell fällig ist."""
        jetzt = time.perf_counter()
        if (
            self.sicht
            and self.huelle
            and (self._letzte_sicht is None or jetzt - self._letzte_sicht >= self.SICHT_ABSTAND_S)
        ):
            self._letzte_sicht = jetzt
            return True
        return False

    RAND = 0.04

    @classmethod
    def zuschneiden(cls, quelle, ziel):
        """Render auf die Figur zuschneiden (Alpha > 0, dazu `RAND` der Höhe): Die Kamera fasst 1,5
        Figurhöhen, die Figur füllte im Bild nur zwei Drittel — neben dem Foto der Vorlage zu klein zum
        Vergleichen."""
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

    KRITIK_GROESSE = (256, 384)

    def kritiktafel(self, runde):
        """Die Vergleichstafel für die Prüf-KI in doppelter Auflösung (256 × 384 je Feld gegen 128 × 192 der
        Anzeige): Die Vorlagenbilder sind 262 × 497 Bildpunkte, die Anzeige-Tafel schrumpfte sie auf 192
        Zeilen — Stabkopf, Schuhe und Gesicht waren dort nur wenige Bildpunkte groß. Gebaut aus den abgelegten
        Renders der Runde. → Pfad oder None."""
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
            vorlage = Kostuembild.aus_vorlage(self.ablage.unter('eingang') / r.datei, self.KRITIK_GROESSE)
            render = Kostuembild.aus_render(pfad, self.KRITIK_GROESSE)
            paare.append((r.winkel, vorlage, render, {'iou': a['iou']}))
        if not paare:
            return None
        ziel = self.ablage.arbeit('kostuem') / 'kritik.png'
        ziel.parent.mkdir(parents=True, exist_ok=True)
        return Kostuemtafel.bauen(paare, ziel)

    DETAIL_GROESSE = (512, 768)

    def detailtafel(self, runde):
        """Ausschnitte der Vorderansicht (Kopf und Hut, Stabspitze, Gürtel) für die Prüf-KI, Vorlage oben und Render
        darunter (`Kostuemdetail`) — sie soll auf die Stellen achten, die auf der Tafel nur wenige Bildpunkte groß sind.
        → Pfad oder None (Runde nicht abgelegt oder ohne Render der Vorderansicht)."""
        eintrag = next(
            (e for e in self.job.ergebnis.get('iterationen') or [] if e.get('runde') == runde), None
        )
        if eintrag is None or not self.referenzen:
            return None
        vorn = min(self.referenzen, key=lambda r: abs(r.winkel))
        a = next(
            (
                a
                for a in eintrag.get('je_ansicht') or []
                if a.get('original') == vorn.original and a.get('render')
            ),
            None,
        )
        # Mit Fototextur, wenn die Runde ein Modell bekam: Die Prüf-KI soll das beurteilen, was am Ende auf der Bühne
        # steht (Gesicht, Bart, Gürtel mit Farbe und Stoff), nicht die flachen Suchfarben.
        pfad = None
        for name in (a or {}).get('textur'), (a or {}).get('render'):
            if name and self.ablage.iterationen(name).is_file():
                pfad = self.ablage.iterationen(name)
                break
        if pfad is None:
            return None
        vorlage = Kostuembild.aus_vorlage(self.ablage.unter('eingang') / vorn.datei, self.DETAIL_GROESSE)
        render = Kostuembild.aus_render(pfad, self.DETAIL_GROESSE)
        ziel = self.ablage.arbeit('kostuem') / 'kritik_detail.png'
        ziel.parent.mkdir(parents=True, exist_ok=True)
        return Kostuemdetail.bauen(vorlage, render, ziel)

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
        Uhrzeit zeigt. `mit_modell`: das Modell (GLB, Fototextur) nur, wenn `modell_faellig` — nicht in jeder
        Runde."""
        ziel = self.ablage.iterationen()
        ziel.mkdir(parents=True, exist_ok=True)
        tafel = 'runde_%03d_vergleich.png' % runde
        Kostuemtafel.bauen(
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
            sicht = self.sicht_faellig()
            Kostuemmodellablage.ablegen(self, runde, erg['werte'], dateien, je_ansicht, sicht=sicht)
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
