# -*- coding: utf-8 -*-
"""Haarumbau — die Frisur der Garderobe wird zum Haar der Vorlage: geschnitten an der Haarlinie, geklemmt an die Hülle, getragen auf einer Haarkappe in der Haarfarbe (05.10.2026).

Edgar (nach Runde 1 von Sapiens 2): „Das Haar in der Vorlage soll perfekt auf ein Haar aus Genesis umgebaut werden, inkl. Textur, Form, Farbe." Gemessen am Kopfbild und am Haarabgleich der Runde
(`ProjektTemp/_wegwerf/edgar/kopf_probe.py`): Das Mavick-Haar saß vorn auf der Stirn (IoU des Haars in der Vorderansicht 0,19; die Haarlinie des Fotos liegt höher), seitlich zu weit vorn und im Nacken zu
tief, und wo seine Karten Lücken ließen, schien die Kopfhaut durch — dunkel, weil die Fotohaut dort Haar auf die Kopfkachel gemalt hatte. Die Haarkappe des Standmodells (`Haarkappe`) trifft die Form besser
(IoU hinten 0,94 statt 0,83, Seite 0,63 statt 0,54), sieht aber wie ein Helm aus.

Beides zusammen: Die Frisur bleibt das, was die Garderobe und das Rezept wählen (Karten, Strähnen, Textur, Regler), wird aber

1. an der Haarlinie der Haarkappe abgeschnitten — Stirn, Schläfe, Ohren und Hals bleiben frei (Dreiecke, deren Schwerpunkt unter der Linie liegt, fallen weg; Gruppen und Texturen behalten ihre Reihenfolge),
2. wie bisher an die Hülle des Fotohaars geklemmt (`Haarklemme`, im Aufruf davor) und
3. auf die Haarkappe gesetzt, die in der angezeigten Haarfarbe (`haar_farbe` × 2 × Grau, wie `Farbangleich.start_grau` sie umkehrt) alles unter und zwischen den Karten füllt.

Nur für KURZES Haar (`Haarkappe.kurzhaarig`) und nur für Kartenhaar; Stranghaar (`kurven`) bleibt, wie es ist. Ohne Hülle des Fotohaars (`haar_huelle.npz`/`haar.glb`) bleibt alles unverändert. Abschaltbar:
Option `iterationen.haarumbau` = aus.
"""

import logging

import numpy as np

from .haarkappe import Haarkappe

logger = logging.getLogger('core')

__all__ = ['Haarumbau']


class Haarumbau:
    #: Weiter als so viele Meter vom Kopfmittelpunkt gilt ein Haarpunkt als außerhalb des Haarbereichs (`Haarkappe.REICHWEITE` gilt für die Haut, nicht für das Haar mit Volumen).
    REICHWEITE = 0.30
    OHNE = ('_beard',)
    #: Wie hell die Karten einer getönten Frisur im Mitsuba-Render erscheinen, gemessen an der berechneten Farbe (Tönung × 2 × Grau-Mittel): Die Karten beschatten sich selbst und lassen Lücken.
    #: Gemessen 05.10.2026 an Mavick Hair Style, Kopfbild (`ProjektTemp/_wegwerf/edgar/haar_farbe_messen.py`): Tönung 0,216 → Karten 0,205 bei berechnet 0,324 (0,63); Tönung 0,353 → Karten 0,337
    #: bei berechnet 0,53 (0,64); die Kappe daneben traf ihre berechnete Farbe (0,314 und 0,496). An anderen Frisuren nicht gemessen.
    KARTEN_HELL = 0.64

    @classmethod
    def anzeigefarbe(cls, hexfarbe):
        """Die Farbe der Haarkappe: so hell, wie die Karten der getönten Frisur im Render erscheinen (Tönung × 2 × Grau-Mittel des Grunds, `Farbangleich.GRAU_MITTEL`, × `KARTEN_HELL`) — Kappe und Karten
        sehen gleich hell aus, auch dort, wo die Karten Lücken lassen."""
        from iterationen2d3d.farbangleich import Farbangleich
        rgb = Farbangleich.rgb_aus(hexfarbe)
        return [min(1.0, max(0.0, c * 2.0 * Farbangleich.GRAU_MITTEL * cls.KARTEN_HELL)) for c in rgb]

    @classmethod
    def herrenhaar(cls, koerper, ablage, haarfarbe):
        """Statt der Frisur der Garderobe ein eigenes Kurzhaar (`Herrenhaar`, Option `iterationen.haarumbau` = herren): Strähnen aus den Wurzeln auf der Kopfhaut in der Haarfarbe, Umriss und Haarlinie aus dem Fotohaar → die Teile
        (Kappe, Strähnengruppen) — oder None, wo es nicht gilt (keine Hülle des Fotohaars, kein kurzes Haar, Fehler): dann baut der Aufrufer die Frisur und `anwenden` sie um. `haarfarbe`: `modell.farben['haar']` (#rrggbb),
        die Tönung der Frisur — sie wird wie bei der Kappe in die angezeigte Farbe umgerechnet (`anzeigefarbe`)."""
        if ablage is None or not haarfarbe:
            return None
        from .herrenhaar import Herrenhaar
        netz = {'punkte': koerper['punkte'], 'dreiecke': koerper['dreiecke'], 'haut': koerper['haut']}
        try:
            haar = Herrenhaar(ablage, netz)
            if not haar.kappe.kurzhaarig():
                logger.info('Herrenhaar: kein kurzes Haar (Radius des Netzhaars im Nacken %s) oder keine Hülle des Fotohaars — die Frisur bleibt', haar.kappe.radius_nacken())
                return None
            return haar.teile(cls.anzeigefarbe(haarfarbe))
        except Exception:  # noqa: BLE001 — ohne das eigene Haar bleibt die Frisur wie gewählt (Warnung im Log)
            logger.exception('Herrenhaar: nicht gebaut')
            return None

    @classmethod
    def haarteile(cls, bau, modell):
        """Das Haar eines `Kleidermodellbau` (`bau`) für `modell`: bei `haarumbau == 'herren'` das eigene Kurzhaar (`herrenhaar` — die Frisur der Garderobe wird dann gar nicht gebaut), sonst die Frisur, an die Hülle
        des Fotohaars geklemmt (`Haarklemme`) und, bei `haarumbau`, an der Haarlinie geschnitten und auf die Haarkappe gesetzt (`anwenden`). `[]` bei `ohne_haar`."""
        if bau.ohne_haar:
            return []
        farbe = (modell.farben or {}).get('haar')
        herren = cls.herrenhaar(bau.koerper(), bau.ablage, farbe) if bau.haarumbau == 'herren' else None
        if herren:
            return herren
        haar = bau._haar(modell)                                                         # noqa: SLF001 — der Bau gehört zusammen
        klemme = bau._haarklemme() if haar else None                                     # noqa: SLF001
        haar = klemme.anwenden(haar) if klemme else haar
        return cls.anwenden(haar, bau.koerper(), bau.ablage, farbe) if bau.haarumbau and haar else haar

    @classmethod
    def anwenden(cls, haar, koerper, ablage, haarfarbe):
        """`haar`: die Haarteile (`art == 'haar'`) nach der Haarklemme; `koerper`: das Körperteil (Punkte, Dreiecke, Haut) in der A-Pose; `haarfarbe`: `modell.farben['haar']` (#rrggbb).
        → die Teile mit abgeschnittener Frisur und der Haarkappe dazu — oder `haar` selbst, wo der Umbau nicht gilt (siehe oben)."""
        if not haar or ablage is None:
            return haar
        netz = {'punkte': koerper['punkte'], 'dreiecke': koerper['dreiecke'], 'haut': koerper['haut']}
        kappe = Haarkappe(ablage, netz)
        try:
            if not kappe.kurzhaarig():
                radius = kappe.radius_nacken()
                logger.info('Haarumbau: kein kurzes Haar (Radius des Netzhaars im Nacken %s, Grenze 0,17 m) oder keine Hülle des Fotohaars — die Frisur bleibt, wie sie ist', '%.3f m' % radius if radius is not None else 'unbekannt')
                return haar
            teil = kappe.teil(cls.anzeigefarbe(haarfarbe))
            if teil is None:
                return haar
            teil['dreiecke'] = np.asarray(teil['dreiecke'], dtype=np.int64).reshape(-1, 3)
            geschnitten = [cls._schneiden(t, kappe) for t in haar]
        except Exception:  # noqa: BLE001 — ohne Umbau bleibt die Frisur wie gewählt (Warnung im Log)
            logger.exception('Haarumbau: nicht gebaut')
            return haar
        return geschnitten + [teil]

    @classmethod
    def _schneiden(cls, teil, kappe):
        """Die Dreiecke der Frisur unter der Haarlinie weglassen. Reihenfolge, Punkte, UV und Normalen bleiben; Gruppen (`index_ab`/`index_anzahl`, Indizes) und Texturen (`ab`/`anzahl`, Dreiecke)
        zählen die behaltenen Dreiecke neu."""
        if teil.get('art') != 'haar' or any(o in str(teil.get('sorte')) for o in cls.OHNE) or teil.get('kurven') is not None:
            return teil
        d = np.asarray(teil['dreiecke'], dtype=np.int64).reshape(-1, 3)
        grad = kappe.grad_je_punkt(teil['punkte'], cls.REICHWEITE)
        behalten = grad[d].mean(axis=1) > 0.0
        if behalten.all():
            return teil
        davor = np.concatenate([[0], np.cumsum(behalten)])          # behaltene Dreiecke vor Dreieck i

        def bereich(ab, anzahl):
            return int(davor[ab]), int(davor[ab + anzahl] - davor[ab])

        gruppen = []
        for g in teil.get('gruppen') or []:
            ab, anzahl = bereich(int(g['index_ab']) // 3, int(g['index_anzahl']) // 3)
            gruppen.append(dict(g, index_ab=3 * ab, index_anzahl=3 * anzahl))
        textur = []
        for x in teil.get('textur') or []:
            ab, anzahl = bereich(int(x['ab']), int(x['anzahl']))
            textur.append(dict(x, ab=ab, anzahl=anzahl))
        logger.info('Haarumbau %s: %d von %d Dreiecken unter der Haarlinie weggelassen', teil.get('sorte'), int((~behalten).sum()), len(behalten))
        return dict(teil, dreiecke=d[behalten], gruppen=gruppen, textur=textur)
