# -*- coding: utf-8 -*-
"""Mesh3daiflaechennetzfein — das Anzeigenetz einer Testfigur auf Netzstufe 1 statt auf dem Käfig (09.11.2026).

Edgar, 09.11.2026, zur Scham von DamiraAlt in Mesh3D-AI (Frage: „Soll Mesh3D-AI die Scham in Stufe 1 zeigen statt im Käfig?“): „das ganze Anzeigenetz in Stufe 1 (groß, aber sauber)“.
Die Testseiten von Mesh3D-AI und 2d-3d-AI zeichneten den Käfig (Netzstufe 0: 27.087 Browserpunkte, 50.312 Dreiecke), die Charakter-Seite zeigt Genesis auf Stufe 1 (104.480 Punkte, 201.248
Dreiecke); das Anatomie-Stück lag dort auf der groben Lochkante (`Mesh3daimeshanatomie.anzeigenetz`, `nachgezogen(grob=True)`).

Die Kette rechnet weiter auf dem Käfig (`anzeige/netz.npz` bleibt, wie er ist: Verdeckung je Dreieck, Kostüm-Prüfung, Zeile 1). Hier entsteht beim Ausliefern die Stufe 1 daraus:
- Körper (Etikett 0, vorn, genau die Dreiecke von `netzstufe(0)`): Punkte, Gewichte, Normalen, Farbe je Punkt durch die Unterteilungsmatrix (`G9netzstufe.matrix`, Gewichte über
  `G9netzstufe._hautstufe` wie die Haut jeder Genesis-Stufe), dazu die HD-Morphe der Regler (`G9hdmorphe.beitrag`, wie `G9koerpernetz._fein`); UV der Stufe 1.
- Je Dreieck der Stufe 1 sein Käfigdreieck (`G9stufeneltern`): Material, und `eltern` im Paket — die Seiten legen damit jede Maske des Käfigs (Verdeckung unter den Stücken) auf die Kinder.
- Anatomie-Stück: auf die Lochkante der Stufe 1 gelegt (`G9stueckstarr.nachgezogen(grob=False)`, wie die Charakter-Seite), verborgen die Dreiecke des Lochs der Stufe 1
  (`G9stueckersatz.loch_fuer`). Seine Punkte im Netz findet die Rechnung über die Lage, in die der Bau sie gelegt hat (grob nachgezogen oder wie ausgeliefert, bis `GLEICH_M`); sonst
  bleibt das Stück, wo es ist, und `verborgen` folgt den Eltern (Grund im Log).
- Alles andere (Haar, Augen, Stücke) unverändert dahinter.
- `matrix` (auf Wunsch): die Unterteilungsmatrix für die Körperpunkte — `Ai2d3dzeile1` legt damit die Käfigpunkte der Zeile 1 auf die Stufe 1.

    Mesh3daiflaechennetzfein.netz(modell, daten, figur_ordner) -> dict | None     dieselben Schlüssel wie `Mesh3daiflaechennetz.laden`, dazu eltern, kaefig_dreiecke, matrix
"""

import json
import logging
import threading
import types

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Mesh3daiflaechennetzfein']


class Mesh3daiflaechennetzfein:
    #: Etiketten im Anzeigenetz (`Ursula.TEILE`): 0 Körper, 1 Anatomie
    KOERPER, ANATOMIE = 0, 1
    #: Punkte des Stücks im Netz und die Lage, in die der Bau sie legte, gelten bis hier als derselbe Punkt (Meter; das Netz speichert float32)
    GLEICH_M = 1e-5
    #: so viele fertige Netze im Speicher (je Figur rund 15 MB)
    BEHALTEN = 6
    _ablage = {}
    _schloss = threading.Lock()

    @classmethod
    def netz(cls, modell, daten, figur_ordner=None, stand=None):
        """Die Stufe 1 zu `daten` (`Mesh3daiflaechennetz.laden(modell)`) oder None, wenn der Körper nicht der Genesis-Käfig ist. `figur_ordner`: Ordner mit `modell.json` (für Regler und
        Anatomie-Stück); ohne bleibt das Stück, wo es ist. `stand`: Stand der Dateien des Netzes (`Mesh3daiflaechennetz._stand`), Schlüssel der Ablage mit dem von `modell.json`."""
        try:
            modell_stand = (figur_ordner / 'modell.json').stat().st_mtime_ns if figur_ordner is not None else None
        except OSError:
            modell_stand = None
        schluessel = (str(modell), stand if stand is not None else id(daten), modell_stand)
        with cls._schloss:
            if schluessel in cls._ablage:
                return cls._ablage[schluessel]
        try:
            aus = cls._rechnen(daten, figur_ordner)
        except Exception as fehler:  # noqa: BLE001 — die Seite zeigt dann den Käfig wie bisher; nie die Antwort verlieren
            logger.warning('Mesh3daiflaechennetzfein: %s nicht auf Stufe 1 (%s: %s)', modell, type(fehler).__name__, fehler, exc_info=True)
            aus = None
        with cls._schloss:
            while len(cls._ablage) >= cls.BEHALTEN:
                cls._ablage.pop(next(iter(cls._ablage)))
            cls._ablage[schluessel] = aus
        return aus

    @classmethod
    def _rechnen(cls, d, figur_ordner):
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.stufeneltern import G9stufeneltern
        s0, s1 = G9basisnetz.netzstufe(0), G9basisnetz.netzstufe(1)
        n_roh = len(G9basisnetz.holen().punkte)
        ursprung = np.asarray(s0.ursprung, dtype=np.int64)
        n0, t0 = len(ursprung), len(s0.dreiecke)
        f, et = d['dreiecke'].astype(np.int64), d['etikett']
        if 'ruhe' not in d or len(f) < t0 or not (et[:t0] == cls.KOERPER).all() or (et[t0:] == cls.KOERPER).any() \
                or not np.array_equal(f[:t0], np.asarray(s0.dreiecke, dtype=np.int64)) or (f[t0:] < n0).any():
            logger.info('Mesh3daiflaechennetzfein: Körper ist nicht der Genesis-Käfig vorn (oder keine Ruhelage) — Stufe 0 bleibt')
            return None
        eltern = G9stufeneltern.fuer(1)
        w = s1.matrix(n_roh).tocsr()
        n1 = s1.punktzahl
        erst = np.full(n_roh, -1, dtype=np.int64)
        erst[ursprung[::-1]] = np.arange(n0 - 1, -1, -1)                       # je Daz-Punkt der erste Browserpunkt
        if (erst < 0).any():
            raise ValueError('%d Käfigpunkte ohne Browserpunkt' % int((erst < 0).sum()))
        ruhe0 = d['ruhe'].astype(np.float64)
        ruhe_roh = ruhe0[erst]
        formung = cls._formung(figur_ordner)
        ruhe1 = np.asarray(w @ ruhe_roh, dtype=np.float64)
        hd = None
        if formung is not None:
            from Genesis9.hdmorphe import G9hdmorphe
            hd = G9hdmorphe.beitrag(formung.formeln, s1, s1, ruhe_roh)
            if hd is not None:
                ruhe1 = ruhe1 + hd
        haut = types.SimpleNamespace(index=d['knochen'][erst].astype(np.int64), gewicht=d['gewicht'][erst].astype(np.float64) / 255.0,
                                     knochen=[str(k) for k in range(int(d['knochen'].max()) + 1)])
        fein_haut = s1._hautstufe(s1._cc, haut)
        rest = slice(n0, None)
        aus = {'fassung': d['fassung'], 'materialien': d['materialien'], 'teilfarben': d['teilfarben'], 'anatomie_fertig': d.get('anatomie_fertig', False)}
        versatz = n1 - n0
        aus['dreiecke'] = np.vstack([np.asarray(s1.dreiecke, dtype=np.int64), f[t0:] + versatz]).astype(np.uint32)
        aus['etikett'] = np.concatenate([np.full(len(s1.dreiecke), cls.KOERPER, dtype=np.uint8), et[t0:]])
        aus['material'] = np.concatenate([d['material'][:t0][eltern['kaefig']], d['material'][t0:]]).astype(np.int16)
        aus['eltern'] = np.concatenate([eltern['kaefig'], np.arange(t0, len(f))]).astype(np.uint32)
        aus['kaefig_dreiecke'] = int(len(f))
        aus['knochen'] = np.vstack([fein_haut['index'].astype(np.uint8), d['knochen'][rest]])
        aus['gewicht'] = np.vstack([np.clip(np.round(fein_haut['gewicht'] * 255), 0, 255).astype(np.uint8), d['gewicht'][rest]])
        aus['uv'] = np.vstack([np.asarray(s1.uv, dtype=np.float32).reshape(-1, 2), d['uv'][rest]]).astype(np.float32)
        aus['ruhe'] = np.vstack([ruhe1, ruhe0[rest]]).astype(np.float32)
        if 'normalen' in d:
            n = np.asarray(w @ (d['normalen'][erst].astype(np.float64) / 127.0))
            n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
            aus['normalen'] = np.vstack([np.clip(np.round(n * 127), -127, 127).astype(np.int8), d['normalen'][rest]])
        if 'punktfarbe' in d:
            c = np.asarray(w @ d['punktfarbe'][erst].astype(np.float64))
            aus['punktfarbe'] = np.vstack([np.clip(np.round(c), 0, 255).astype(np.uint8), d['punktfarbe'][rest]])
        aus['matrix'] = w
        bericht = cls._anatomie(aus, d, figur_ordner, formung, ruhe1, n0, versatz)
        if 'verborgen' not in aus and len(d.get('verborgen', ())):
            maske = np.zeros(len(f), dtype=bool)
            maske[d['verborgen'].astype(np.int64)] = True
            aus['verborgen'] = np.nonzero(maske[aus['eltern']])[0].astype(np.uint32)
        logger.info('Mesh3daiflaechennetzfein: Stufe 1 %d Punkte, %d Dreiecke (Käfig %d/%d), HD %s, Anatomie: %s', len(aus['uv']), len(aus['dreiecke']), len(d['uv']), len(f),
                    'ja' if hd is not None else 'nein', bericht)
        return aus

    @staticmethod
    def _formung(figur_ordner):
        """`G9formung` der Regler aus `modell.json` der Figur, oder None."""
        if figur_ordner is None or not (figur_ordner / 'modell.json').is_file():
            return None
        from Genesis9.formung import G9formung
        figur = json.loads((figur_ordner / 'modell.json').read_text(encoding='utf-8')).get('figur') or {}
        return G9formung(figur.get('regler') or {})

    @classmethod
    def _anatomie(cls, aus, d, figur_ordner, formung, haut1, n0, versatz):
        """Das starre Stück der Figur auf die Lochkante der Stufe 1 (`aus['ruhe']`, `aus['verborgen']` gesetzt) → Text für das Log."""
        from Genesis9.garderobe import G9garderobe
        from Genesis9.stueckersatz import G9stueckersatz
        from Genesis9.stueckstarr import G9stueckstarr
        from scipy.spatial import cKDTree
        f, et = d['dreiecke'].astype(np.int64), d['etikett']
        an = np.unique(f[et == cls.ANATOMIE].reshape(-1))
        if formung is None or not len(an):
            return 'kein Stück oder keine modell.json'
        figur = json.loads((figur_ordner / 'modell.json').read_text(encoding='utf-8')).get('figur') or {}
        kennung = next((k for k in (figur.get('kleidung') or {}) if G9garderobe.eintrag(k) and G9stueckstarr.ist(G9garderobe.eintrag(k))), None)
        if kennung is None:
            return 'kein starres Stück in der Kleidung'
        eintrag, teile = G9garderobe.eintrag(kennung), G9garderobe.teile(kennung)
        loch = G9stueckersatz.loch_fuer(eintrag)
        lage = d['ruhe'][an].astype(np.float64)
        kaefig = formung.punkte() - np.array([0.0, float(formung.boden()), 0.0])
        # wo der Bau das Stück hinlegte: grob nachgezogen (`Mesh3daimeshanatomie.anzeigenetz`) oder wie ausgeliefert (`G9stueckstarr.gezeigt`, Bau vor dem 08.11.2026)
        for name, rechnung in (('grob', lambda: G9stueckstarr.nachgezogen(eintrag, teile, kaefig, formung, grob=True)), ('gezeigt', lambda: G9stueckstarr.gezeigt(teile, formung))):
            quelle = np.vstack(rechnung())
            abstand, j = cKDTree(quelle).query(lage)
            if float(abstand.max()) <= cls.GLEICH_M:
                break
        else:
            return 'Punkte des Stücks nicht wiedergefunden (%.3f mm) — Stück bleibt auf dem Käfig' % (1000 * float(abstand.max()))
        if not loch or int(loch.get('von', 0)) != int(np.count_nonzero(aus['etikett'] == cls.KOERPER)):
            return 'kein Loch der Stufe 1 für %s' % kennung
        fein = np.vstack(G9stueckstarr.nachgezogen(eintrag, teile, haut1, formung, grob=False))
        neu = fein[j]
        ziel = an + np.where(an >= n0, versatz, 0)
        aus['ruhe'][ziel] = neu.astype(np.float32)
        aus['verborgen'] = np.asarray(loch['dreiecke'], dtype=np.uint32)
        # Die Ringpunkte der Haut rücken um ihre Verschiebung (`loch.verschiebung`, der Haut gefolgt wie die Ringecken: `G9stueckfolge.loch`) — wie `Stueckloch.verschieben` in der
        # Charakter-Seite (Einzug vor der Häutung); der Rand des Stücks liegt genau dort (Ringecke = Hautpunkt + d). Ohne das standen an n3 links und rechts Spalten bis ~6 mm
        # (im Chrome gesehen 09.11.2026, grau gerendert). Die Nahtkopien dieser Punkte rücken mit.
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.stueckfolge import G9stueckfolge
        v = (G9stueckfolge(haut1, False).loch(loch) or {}).get('verschiebung') or {}
        geruckt = 0
        if v.get('punkte'):
            cc = G9basisnetz.netzstufe(1)._cc
            urbild = np.concatenate([np.arange(int(cc.geo_vertex_count), dtype=np.int64), np.asarray(cc.kopien_eltern, dtype=np.int64)])
            d_je = np.zeros((len(urbild), 3))
            nr = np.asarray(v['punkte'], dtype=np.int64)
            d_je[nr] = np.asarray(v['d'], dtype=np.float64)
            schub = d_je[urbild]                                 # Kopien wie ihr Original
            schub[nr] = d_je[nr]
            beruehrt = np.linalg.norm(schub, axis=1) > 0
            aus['ruhe'][:len(urbild)][beruehrt] += schub[beruehrt].astype(np.float32)
            geruckt = int(beruehrt.sum())
        weg = np.linalg.norm(neu - lage, axis=1)
        return '%s auf der Lochkante der Stufe 1 (vorher %s), verschoben Median %.2f mm, max %.2f mm, %d Dreiecke verborgen, %d Hautpunkte der Lochkante gerückt' % (
            kennung, name, 1000 * float(np.median(weg)), 1000 * float(weg.max()), len(aus['verborgen']), geruckt)
