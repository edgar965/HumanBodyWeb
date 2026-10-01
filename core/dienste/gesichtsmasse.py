# -*- coding: utf-8 -*-
"""Gesichtsmasse — die Maße des Gesichts auf dem Vorderfoto gegen dieselben Maße auf dem Kopf-Render des Modells
(01.10.2026; der Ersatz für KeenTools FaceBuilder, Konzept 3.4: keine Pins, sondern die 478 FaceLandmarker-Punkte auf
BEIDEN Bildern — derselbe Detektor, seine Eigenheiten kürzen sich).

Je Maß eine Strecke zwischen Landmarken (MediaPipe-Nummern), normiert auf die Gesichtshöhe Stirn (10) – Kinn (152);
das Verhältnis Foto ÷ Render sagt, ob das Modell dort zu schmal oder zu breit ist. `IterationGesicht` macht daraus
Kopfregler-Schritte. Der Kopf-Render kommt aus `Genesishaarrender.bild_kopf` (Kamera auf den Kopf, 1024 × 1024 — auf
dem Figurrender wäre das Gesicht 30 Pixel groß), seit 01.10.2026 je Kopfstand einmal über vier Saaten
(`Gesichtsvorrat`, `SAATEN`). Ohne Vorderfoto (|Winkel| > 30°) oder ohne erkanntes Gesicht kein
Befund (None), ohne Abbruch der Runde.
"""

import logging
import math

from .fotolandmarken import Fotolandmarken

logger = logging.getLogger('core')

__all__ = ['Gesichtsmasse']


class Gesichtsmasse:
    #: Maß → Landmarkenpaar (MediaPipe FaceMesh, 478 mit Iris).
    MASSE = {
        'breite': (234, 454),        # Wangenknochen links / rechts
        'augen': (468, 473),         # Pupillen
        'nase': (129, 358),          # Nasenflügel
        'nase_laenge': (168, 4),     # Nasenwurzel – Nasenspitze
        'mund': (61, 291),           # Mundwinkel
        'kinn': (17, 152),           # Unterlippe – Kinn
    }
    HOEHE = (10, 152)
    VORN_BIS = 30.0
    RENDER = 'gesicht_render.png'
    #: Kopf-Render für die Landmarken: bei 512 px ist ein Bildpunkt 1–2,5 % eines Maßes (Nase 40 px breit) — 1024 px
    #: halbiert das Rauschen (01.10.2026).
    RENDER_GROESSE = (1024, 1024)
    #: Suchworte der Kopfregler, die `IterationGesicht` stellt — nur die gehen in den Befund. Die Namen sind die von
    #: Genesis 9 (Reglerplan „kopf", 386 Regler; „Face Width", „Nose Width", „Mouth Width" gibt es dort nicht), die
    #: Wirkung ist gemessen (`ProjektTemp/_wegwerf/kleider2d3d/gesichtsregler_probe.py`, `IterationGesicht.REGLER`).
    SUCHWORTE = ('Face Upper Width', 'Eyes Distance', 'Eyes Height A', 'Nose Width Lower', 'Lips Width',
                 'Chin Length')

    def __init__(self, ablage, render):
        self.ablage = ablage
        self.render = render

    @classmethod
    def masse(cls, punkte, breite=1.0, hoehe=1.0):
        """`punkte`: 478 × (x, y) in Bildanteilen, `breite`/`hoehe` das Bild in Pixeln — die Anteile kommen erst
        in Pixel: auf einem Foto 2123 × 4041 wäre sonst jede Breite um 1,9 gegen die Höhe gestaucht, der
        Kopf-Render (512 × 512) nicht (01.10.2026, Edgars Vorderfoto: Gesichtsbreite 1,78 statt 0,94)
        → `{mass: Länge / Gesichtshöhe}` oder None."""
        if not punkte or len(punkte) < 474:
            return None
        breite, hoehe_px = float(breite or 1.0), float(hoehe or 1.0)

        def strecke(a, b):
            return math.hypot((punkte[a][0] - punkte[b][0]) * breite, (punkte[a][1] - punkte[b][1]) * hoehe_px)

        gesicht = strecke(*cls.HOEHE)
        if gesicht < 1e-6:
            return None
        aus = {name: round(strecke(a, b) / gesicht, 4) for name, (a, b) in cls.MASSE.items()
               if max(a, b) < len(punkte)}
        # Augenhöhe: Abstand Stirn → Augenmitte relativ zur Gesichtshöhe (höher liegende Augen = kleinerer Wert).
        if len(punkte) > 473:
            augen_y = 0.5 * (punkte[468][1] + punkte[473][1])
            aus['augen_hoehe'] = round((augen_y - punkte[10][1]) * hoehe_px / gesicht, 4)
        return aus

    @classmethod
    def kopfregler(cls):
        """`[{name, anzeige}]` der Kopfregler zu den Suchworten — aus dem Reglerplan, einmal je Prozess."""
        if getattr(cls, '_kopfregler', None) is None:
            from Genesis9.reglerplan import G9reglerplan
            aus = []
            for bereich in G9reglerplan.bereiche():
                if bereich.get('schluessel') != 'kopf':
                    continue
                for r in bereich.get('regler') or []:
                    anzeige = str(r.get('anzeige') or '')
                    if any(anzeige.strip().endswith(w) for w in cls.SUCHWORTE):
                        aus.append({'name': r['name'], 'anzeige': anzeige})
            cls._kopfregler = aus
        return cls._kopfregler

    #: Saaten des Kopf-Renders, über die neu gemessen wird (Median je Maß; je Render ~0,45 s bei 1024²). Unter zwei
    #: Renders mit Gesicht kein Befund — ein einzelner Wurf ist genau das Rauschen, das hier wegsoll.
    SAATEN = (0, 1, 2, 3)
    #: Fassung der Messart im Schlüssel des Vorrats — wer ändert, WAS gerendert oder wie gemittelt wird, zählt hoch
    #: (01.10.2026: ein Eintrag aus dem verworfenen Render nur mit dem Körper kam sonst wieder heraus).
    FASSUNG = 3

    @staticmethod
    def median(masse):
        """Je Maß der Median über die Renders mit Gesicht → dict oder None (weniger als zwei mit Gesicht)."""
        import statistics
        masse = [m for m in masse if m]
        if len(masse) < 2:
            return None
        return {k: round(float(statistics.median(m[k] for m in masse)), 4) for k in masse[0] if all(k in m for m in masse)}

    def eintragen(self, befund, teile, referenzen, aus):
        """`befund['gesicht']` setzen, wenn es zu messen ist — ein Fehler hält die Runde nicht auf."""
        try:
            gesicht = self.befund(teile, referenzen, aus)
        except (OSError, ValueError, RuntimeError, KeyError) as fehler:
            logger.warning('Gesichtsmaße nicht gemessen (%s)', fehler)
            return
        if gesicht:
            befund['gesicht'] = gesicht

    def befund(self, teile, referenzen, aus):
        """→ `{'foto', 'render', 'verhaeltnis', 'ansicht', 'kopfregler'}` oder None."""
        vorn = [r for r in referenzen if abs(float(r.winkel)) <= self.VORN_BIS]
        if not vorn:
            return None
        r = min(vorn, key=lambda x: abs(float(x.winkel)))
        # Gemessen wird je KOPFSTAND einmal (`Gesichtsvorrat`, Schlüssel nur aus dem Körper): Haar und Kragen stehen im
        # Render wie im Foto, eine Haar-Operation misst aber nicht neu — sie stellt keinen Kopfregler, und jeder neue
        # Render rauschte (ein unsichtbarer Clump hob die Note um 0,013). Neu gemessen wird über `SAATEN` Renders, je
        # Maß der Median (Detektor ±1 % je Maß, auch bei 512 Abtastungen; `ProjektTemp/_wegwerf/ortsmorph/kopfrauschen.py`).
        from .gesichtsvorrat import Gesichtsvorrat
        kopf = [t for t in teile if t.get('art') == 'koerper'] or list(teile)
        vorrat = Gesichtsvorrat(self.ablage)
        schluessel = Gesichtsvorrat.schluessel(kopf, r.winkel, self.RENDER_GROESSE,
                                               (Fotolandmarken.FASSUNG, self.FASSUNG, len(self.SAATEN)))
        m_render = vorrat.holen(schluessel)
        pfade = [] if m_render is not None else [aus / self.RENDER.replace('.png', '_s%d.png' % s) for s in self.SAATEN]
        try:
            for saat, pfad in zip(self.SAATEN, pfade, strict=False):
                self.render.bild_kopf([(t['punkte'], t['dreiecke'], t['farbe']) for t in teile], r.winkel, pfad,
                                      groesse=self.RENDER_GROESSE, saat=saat)
        except (ValueError, OSError, RuntimeError) as fehler:
            logger.warning('Gesichtsmaße: Kopf-Render fehlgeschlagen (%s)', fehler)
            return None
        from ..daten.haarengineablage import Haarengineablage
        foto = self.ablage.unter(Haarengineablage.EINGANG) / r.datei
        befunde = Fotolandmarken(self.ablage).holen([foto] + pfade)
        bf = befunde.get(r.datei) or {}
        m_foto = self.masse(bf.get('gesicht'), bf.get('breite'), bf.get('hoehe'))
        if m_render is None:
            m_render = self.median([self.masse(b.get('gesicht'), b.get('breite'), b.get('hoehe'))
                                    for b in (befunde.get(p.name) or {} for p in pfade)])
            vorrat.ablegen(schluessel, m_render)
        if not m_foto or not m_render:
            logger.info('Gesichtsmaße: kein Gesicht auf %s', 'Foto' if not m_foto else 'Render')
            return None
        verhaeltnis = {k: round(m_foto[k] / m_render[k], 4) for k in m_foto if k in m_render and m_render[k] > 1e-6}
        return {'foto': m_foto, 'render': m_render, 'verhaeltnis': verhaeltnis, 'ansicht': r.original,
                'winkel': r.winkel, 'kopfregler': self.kopfregler(), 'fassung': self.FASSUNG}
