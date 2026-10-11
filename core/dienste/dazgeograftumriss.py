# -*- coding: utf-8 -*-
"""Dazgeograftumriss — das Daz-Stück hat den Umriss des Blender-Stücks, nicht den des Geografts (11.10.2026).

Edgar: „schau doch nach, wie die alte Scham mit Blender angepasst wurde … baue ein besseres cute Girl 3. Baue alle Erkenntnisse, die wir vorher hatten, in die neue Klasse hinein, sodass sie
standardmäßig bei allen Modellen angewandt wird." Gemessen an „cute girl" (`blender_absatz.py`, 11.10.2026): das Blender-Stück ist 72 × 43 mm groß, das Daz-Geograft 120 × 74 mm. Das Geograft reicht
damit in die Leistenfalten, wo das Original 10–15 mm UNTER der Haut liegt (blendimport.md Punkt 4); das Stück machte das getreu mit, sein Rand stand am Ring auf der Haut — die Absätze seitlich
(„Sprungschanze", „cm hohe Absätze"; `ProjektTemp/_wegwerf/blender_absatz.py`, Maß von `Schammessungansichten`: Absatz 2 mm hinter dem Ring p90 9,0 mm (Stufe 1) und 10,4 mm (Stufe 2) gegen 4,2 mm beim
Blender-Stück). Vermutet, nicht belegt: die Streifen ohne Textur am Rand kommen daher, dass das Geograft über das Original hinausreicht (`Dazgeograftziel.randlage`).

Die Erkenntnisse des alten Wegs (`Blendimportscham`, `blendimport.md` Punkt 4 und 8), die hier gelten:

    Umriss   das Loch ist das des Blender-Stücks (`.ersetzt.json`: Dreiecke der Haut). Seitlich begrenzt sein Schnitt die Saat auf `SAAT_BREITE_M` (26 mm) — die Leistenfalten gehören nicht dazu
    Schnitt  das Geograft wird an der Kontur des Lochs exakt geteilt (`Blendimportschamschnitt`), nicht ganz gewählt: der Rand ist die Linie, nicht die Zähne der Dreiecke
    Rand     das Randband wird weich auf die Haut gezogen (`Blendimportscham.angleichen`: 12 mm, höchstens 8 mm) — dort, wo Original und Haut weiter auseinanderliegen, bleibt es sichtbar (gemeldet)
    Naht     der Rand liegt genau auf den Ecken des Rings, Randseite, Falten (`Dazgeograft.verschweissen`, `Schamnahtrandseite`) — unverändert

HIER der erste Schritt: Umriss und Schnitt. Innen oder außen entscheidet die HAUT, nicht die Vorderansicht: der Ring des Blender-Lochs läuft von der Vorderseite (z +73 mm) um das Becken bis hinter den
Damm (z −51 mm, gemessen 11.10.2026 an „cute girl", `umriss_probe.py`), in der Vorderansicht liegen Vorder- und Rückseite übereinander — der erste Versuch mit einem Polygon in (x, y) ließ den Rand des
Geografts bis 85,5 mm neben dem Ring liegen (Bau abgebrochen). Jeder Punkt des Geografts wird auf die Haut projiziert: liegt sein Fußpunkt in einem Dreieck des Lochs, ist er innen; der Wert für den Schnitt
ist der Abstand dieses Fußpunkts zum Ring (m, innen negativ).

Der Schnitt löscht Punkte; damit die Regler des Basis-Stücks („Daz Anatomie Frau", Stufe 1) weiter über die Rohnummern der Unterteilung zugeordnet werden können (`Dazgeograftstufenzuordnung`), behält er
für jeden Punkt des Stücks die Nummer, die er VOR dem Schnitt hatte (`herkunft`; −1 für die Punkte, die der Schnitt neu auf eine Kante setzt).
"""
import numpy as np

__all__ = ['Dazgeograftumriss']


class Dazgeograftumriss:
    #: Der Schnitt liegt so weit (m) hinter dem Rand des Lochs: das Stück deckt das Loch ganz, die Naht holt den Rand dann auf den Ring. Eine Setzung — kleiner als ein Dreieck der Stufe 2.
    UEBERSTAND_M = 0.0015
    #: Weniger Dreiecke bleiben nicht: das Geograft liegt nicht über dem Loch.
    MINDEST_DREIECKE = 200
    #: Nur Hautdreiecke, deren Mitte so nah (m) am Kasten des Geografts liegt, zählen für die Projektion (Schnelligkeit: 201.248 Dreiecke der Haut gegen einige Tausend).
    KASTEN_RAND_M = 0.04
    #: Abstand (m) der Proben entlang des Rings, an denen der Abstand zum Ring gemessen wird (Fehler höchstens die Hälfte).
    RING_PROBE_M = 0.0003
    #: Endung der Datei neben der `.duf`, die die Herkunft der Punkte hält (`herkunft_ablegen`).
    HERKUNFT_ENDUNG = '.herkunft.json'

    # ------------------------------------------------------------ Loch des Blender-Stücks

    @staticmethod
    def loch(kennung, anzahl_dreiecke=None):
        """`bool` je Dreieck der Haut (Stufe 1): unter dem Stück `kennung` (z. B. `cute_girl_scham`) — das Loch aus seiner `.ersetzt.json`. `ValueError`, wenn das Stück kein Loch nennt oder die Haut eine
        andere Zahl Dreiecke hat (anderes Netz; ohne `anzahl_dreiecke` gilt die des Lochs)."""
        from Genesis9.garderobe import G9garderobe
        from Genesis9.stueckersatz import G9stueckersatz

        eintrag = G9garderobe.eintrag(kennung)
        if not eintrag:
            raise ValueError('das Stück %s gibt es in der Garderobe nicht' % kennung)
        angabe = G9stueckersatz.loch_fuer(eintrag)
        if not angabe or not angabe.get('dreiecke'):
            raise ValueError('das Stück %s hat kein Loch (gebaut ohne Naht?): sein Umriss ist unbekannt' % kennung)
        von = int(angabe['von'])
        if anzahl_dreiecke is not None and von != int(anzahl_dreiecke):
            raise ValueError('das Loch von %s gilt für %d Dreiecke der Haut, die Figur hat %d' % (kennung, von, int(anzahl_dreiecke)))
        maske = np.zeros(von, dtype=bool)
        maske[np.asarray(angabe['dreiecke'], dtype=np.int64)] = True
        return maske

    # ------------------------------------------------------------ Herkunft der Punkte (für die Regler des Basis-Stücks)

    @classmethod
    def herkunft_ablegen(cls, duf, stufe, nahtfrei, herkunft):
        """Neben die `.duf` des Stücks: Stufe des Geografts, Zahl seiner Punkte nach dem Verschweißen der UV-Nähte (`Dazgeograft.nahtfrei`) und `herkunft` (Nummer vor dem Schnitt je Punkt des Stücks, −1 = neu)."""
        import json
        from pathlib import Path

        pfad = Path(duf)
        ziel = pfad.with_name(pfad.stem + cls.HERKUNFT_ENDUNG)
        # ohne Zuschnitt `herkunft: null` — eine Datei aus einem früheren Bau unter demselben Namen darf nicht weitergelten
        liste = None if herkunft is None else [int(x) for x in herkunft]
        ziel.write_text(json.dumps({'stufe': int(stufe), 'nahtfrei': None if nahtfrei is None else int(nahtfrei), 'herkunft': liste}), encoding='utf-8')
        return ziel

    @classmethod
    def herkunft_lesen(cls, eintrag):
        """`{stufe, nahtfrei, herkunft}` des Garderobeneintrags oder `None` (Stück ohne Zuschnitt: die Punkte tragen ihre Nummern aus dem Geograft)."""
        import json
        from pathlib import Path

        from Genesis9.garderobe import G9garderobe

        pfad = Path(G9garderobe.datei(eintrag))
        datei = pfad.with_name(pfad.stem + cls.HERKUNFT_ENDUNG)
        if not datei.is_file():
            return None
        daten = json.loads(datei.read_text(encoding='utf-8'))
        if daten.get('herkunft') is None:
            return None
        daten['herkunft'] = np.asarray(daten['herkunft'], dtype=np.int64)
        return daten

    # ------------------------------------------------------------ Abstand zum Ring (auf der Haut)

    @classmethod
    def abstand(cls, haut, maske, ring, punkte):
        """Abstand (m) der `punkte` zum Rand des Lochs, gemessen von ihrem Fußpunkt auf der Haut: negativ, wenn der Fußpunkt in einem Dreieck des Lochs liegt. `haut`: die Figur als `trimesh.Trimesh`
        (Stufe 1, alle Dreiecke), `maske`: bool je Dreieck der Haut, `ring`: `(k, 3)` Ecken des Rings (geschlossen)."""
        import trimesh
        from scipy.spatial import cKDTree

        punkte = np.asarray(punkte, dtype=np.float64)
        zentren = np.asarray(haut.triangles_center)
        nah = np.all((zentren > punkte.min(axis=0) - cls.KASTEN_RAND_M) & (zentren < punkte.max(axis=0) + cls.KASTEN_RAND_M), axis=1)
        teil = trimesh.Trimesh(np.asarray(haut.vertices), np.asarray(haut.faces)[nah], process=False)
        fuss, _abstand, dreieck = trimesh.proximity.closest_point(teil, punkte)
        innen = np.asarray(maske)[np.flatnonzero(nah)[dreieck]]
        ring = np.asarray(ring, dtype=np.float64)
        naechste = np.roll(ring, -1, axis=0)
        teile = np.maximum(1, np.ceil(np.linalg.norm(naechste - ring, axis=1) / cls.RING_PROBE_M).astype(np.int64))
        t = np.concatenate([np.arange(n) / n for n in teile])
        von = np.repeat(np.arange(len(ring)), teile)
        proben = ring[von] + t[:, None] * (naechste[von] - ring[von])
        weg = cKDTree(proben).query(fuss)[0]
        return np.where(innen, -weg, weg)

    # ------------------------------------------------------------ Schnitt

    @classmethod
    def zuschneiden(cls, punkte, dreiecke, uv_ecken, haut, maske, ring):
        """`(punkte, dreiecke, uv_ecken, herkunft, bericht)`: nur der Teil des Netzes über dem Loch (`maske` der Haut `haut`, Rand `ring`; plus `UEBERSTAND_M`), an der Kontur exakt geteilt, das größte
        zusammenhängende Stück, die Punkte neu gezählt. `herkunft[i]` = Nummer des Punkts `i` im Netz VOR dem Schnitt, −1 für die neuen Schnittpunkte. `ValueError`, wenn zu wenig übrig bleibt."""
        from scipy import sparse
        from scipy.sparse import csgraph

        from .blendimportschamschnitt import Blendimportschamschnitt

        punkte = np.asarray(punkte, dtype=np.float64)
        dreiecke = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        werte = cls.abstand(haut, maske, ring, punkte) - cls.UEBERSTAND_M
        alle, d, uv = Blendimportschamschnitt.schneiden(punkte, dreiecke, uv_ecken, werte)
        if len(d) < cls.MINDEST_DREIECKE:
            raise ValueError('nach dem Schnitt am Umriss bleiben nur %d Dreiecke: das Geograft liegt nicht über dem Loch' % len(d))
        n = len(alle)
        a = np.concatenate([d[:, 0], d[:, 1]])
        b = np.concatenate([d[:, 1], d[:, 2]])
        _, marke = csgraph.connected_components(sparse.coo_matrix((np.ones(len(a)), (a, b)), shape=(n, n)), directed=False)
        je_dreieck = marke[d[:, 0]]
        gross = int(np.bincount(je_dreieck).argmax())
        behalten = je_dreieck == gross
        benutzt, neu = np.unique(d[behalten], return_inverse=True)
        herkunft = np.where(benutzt < len(punkte), benutzt, -1).astype(np.int64)
        bericht = {'dreiecke_vorher': int(len(dreiecke)), 'dreiecke': int(behalten.sum()), 'punkte_vorher': int(len(punkte)), 'punkte': int(len(benutzt)),
                   'schnittpunkte': int((herkunft < 0).sum()), 'inseln_weg': int((~behalten).sum()), 'ueberstand_mm': cls.UEBERSTAND_M * 1000.0}
        return alle[benutzt], neu.reshape(-1, 3), uv[behalten], herkunft, bericht
