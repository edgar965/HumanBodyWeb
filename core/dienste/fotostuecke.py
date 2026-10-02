# -*- coding: utf-8 -*-
"""Fotostuecke — die Kleidung aus dem Netz der Fotos als EIGENE Genesis-9-Stücke (Oberteil, Hose, Socken) — Form UND
Textur aus den Fotos (01.10.2026).

Edgar (01.10.2026): „Erzeuge für alle Objekte aus den Bildern eigene Assets wie Haare, Kleider, Uhr usw." Bis dahin zog
die Runde ein Bibliotheksstück an (`g9_base_shirt`) und verformte es mit Zonen-Morphen und Hülle Richtung Netz — Runde
15 des Testauftrags 2026.10.01.12.38.09: Schultern und Ärmel aufgerissen, Socken zwischen den Füßen. Das Netz der Fotos
HAT das Shirt schon, in Form und Farbe: Schritt „kleidung" teilt es (`arbeit/kleidung_maske.npz`, `stueck` je Fläche:
`STUECKE`), `Kleidungsentposen` rechnet es in die Ruhelage der Figur zurück (wie `Meshfigurkleidung.objekt`).

Je Stück: Flächen des Stücks → Ruhelage der Figur → OBJ mit Textur → `G9eigenstueck.schreiben` (Gewichte der 3
nächsten Hautpunkte) → Ruhelage auf der GRUNDFIGUR zurückrechnen (`G9gcfigurbau.ruhelage`, wie die GarmentCode-Stücke
auf der Figur des Reiters) → neu schreiben. Kennung in der Garderobe: `eigen_foto_<kürzel>_<name>`.

Gemerkt in `job.ergebnis['fotostuecke']` mit dem Stand von Netz, Maske und Figur — ein zweiter Aufruf baut nur neu, wenn
sich davon etwas geändert hat (`artefakte-benennen`).
"""

import json
import logging

import numpy as np

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage

logger = logging.getLogger('core')

__all__ = ['Fotostuecke']


class Fotostuecke:
    #: `stueck`-Nummer der Kleidungsmaske → Name; „Zubehör" (4) bleibt draußen (Fäden, Kleinkram).
    STUECKE = {1: 'oberteil', 2: 'hose', 3: 'socken'}
    #: Garderobenordner je Stück (`G9mbkategorien.fuer`) — das Haar ist ein Zubehör, kein Bibliothekshaar.
    ORDNER = {'socken': 'accessories', 'hose': 'pants', 'haar': 'accessories'}
    #: Weniger Flächen ist kein Stück (Fehlklassifikation).
    FLAECHEN_MIN = 500
    FASSUNG = 20                # 20: Stoff liegt auf den Schultern auf (`Fotohuelle._aufliegen`, 02.10.2026)
    #: 'huelle': Form aus der angepassten Figur (`Fotohuelle`, seit Fassung 13 — keine Risse unter den Ärmeln);
    #: 'netz': die Flächen des Netzes selbst, in die Ruhelage zurückgerechnet (bis Fassung 12).
    FORM = 'huelle'

    def __init__(self, job, ablage=None):
        self.job = job
        self.ablage = ablage or Engine2d3dKleiderablage(job.kennung)

    def _stand(self):
        dateien = [self.ablage.arbeit(n) for n in ('kleidung_maske.npz', 'genesis_ende.npz', 'posiert.npy')]
        dateien.append(self.ablage.netzdatei())
        return [self.FASSUNG] + [[str(p), p.stat().st_mtime_ns] if p and p.is_file() else None for p in dateien]

    def holen(self):
        """`{name: garderobenkennung}` — gebaut, wenn nötig; leer ohne Kleidung oder Figur."""
        alt = (self.job.ergebnis or {}).get('fotostuecke') or {}
        stand = json.loads(json.dumps(self._stand()))
        if alt.get('stand') == stand and alt.get('stuecke'):
            return dict(alt['stuecke'])
        try:
            stuecke, bericht = self.bauen()
        except Exception as fehler:  # noqa: BLE001 — ohne Fotostücke bleiben die Bibliotheksstücke
            logger.exception('2D3D Kleider %s: Fotostücke nicht gebaut', self.job.kennung)
            stuecke, bericht = {}, {'fehler': str(fehler)[:300]}
        self.job.ergebnis = dict(self.job.ergebnis or {}, fotostuecke={'stand': stand, 'stuecke': stuecke,
                                                                        'bericht': bericht})
        self.job.save(update_fields=['ergebnis', 'updated_at'])
        return stuecke

    def bauen(self):
        from Kleidung.kleidungsentposen import Kleidungsentposen

        from .meshfigurkleidung import Meshfigurkleidung
        maske = self.ablage.arbeit('kleidung_maske.npz')
        ruhe, posiert = self.ablage.arbeit('genesis_ende.npz'), self.ablage.arbeit('posiert.npy')
        if not (maske.is_file() and ruhe.is_file() and posiert.is_file()):
            return {}, {'fehler': 'Maske oder Figur fehlen'}
        scan, _ = Meshfigurkleidung(type('Lauf', (), {'job': self.job, 'ablage': self.ablage})()).koerpernetz()
        if scan.uv_ecken is None or scan.textur is None:
            return {}, {'fehler': 'Netz ohne Textur'}
        with np.load(maske) as d:
            stueck = np.asarray(d['stueck'])
            haut = np.asarray(d['haut'], dtype=bool) if 'haut' in d.files else np.zeros(len(stueck), dtype=bool)
        with np.load(ruhe) as d:
            koerper = (np.asarray(d['punkte'], dtype=np.float64), np.asarray(d['dreiecke'], dtype=np.int64))
            entposen = Kleidungsentposen(koerper[0], np.load(posiert).astype(np.float64))
            from .huellenschnitt import Huellenschnitt
            hals = Huellenschnitt.halsgewichte(d)
        alle = np.arange(len(scan.flaechen))
        hoehe = scan.punkte[scan.flaechen].mean(axis=1)[:, 1]
        rgb = scan.farben(alle, np.full((len(alle), 3), 1.0 / 3.0)).astype(np.float64) / 255.0
        warm = (rgb[:, 0] > rgb[:, 1]) & (rgb[:, 1] > rgb[:, 2]) & (rgb[:, 0] - rgb[:, 2] > self.HAUT_ABSTAND)
        if self.FORM == 'huelle':                     # Form aus der Figur, Farbe aus dem Netz (`Fotohuelle`)
            from .fotohuelle import Fotohuelle
            huelle = Fotohuelle(scan, stueck, haut, koerper[0], entposen.posiert, koerper[1], farbsperre=warm,
                                halsgewicht=hals)
            aus, bericht = {}, {}
            for nummer, name in self.STUECKE.items():
                kern = self._kern(self._zusammen(scan.flaechen, (stueck == nummer) & ~haut & ~warm), hoehe, name)
                teil = huelle.bauen(nummer, (hoehe[kern].min(), hoehe[kern].max()) if kern.any() else None)
                if teil is not None and len(teil[1]) >= self.FLAECHEN_MIN:
                    aus[name], bericht[name] = self._schreiben(name, *teil)
            return aus, bericht
        masken = {}
        for nummer, name in self.STUECKE.items():
            wahl = self._kern(self._zusammen(scan.flaechen, (stueck == nummer) & ~haut & ~warm), hoehe, name)
            glatt = self._glaetten(scan.flaechen, wahl, self.GLAETTEN_JE.get(name))
            masken[name] = self._zusammen(scan.flaechen, glatt)
        haarmaske = self.ablage.arbeit('haar_maske.npz')
        if haarmaske.is_file():                 # das Haar des Netzes (Schritt „haar") — ohne Hautton- und Höhenfilter
            with np.load(haarmaske) as d:
                if len(d['haar']) == len(scan.flaechen):
                    masken['haar'] = self._zusammen(scan.flaechen, np.asarray(d['haar'], dtype=bool))
        aus, bericht = {}, {}
        for name, wahl in masken.items():
            if int(wahl.sum()) < self.FLAECHEN_MIN:
                continue
            genutzt, neu = np.unique(scan.flaechen[wahl].reshape(-1), return_inverse=True)
            punkte = entposen.ruhelage(scan.punkte[genutzt])
            flaechen = neu.reshape(-1, 3)
            heil = self._ungedehnt(scan.punkte[genutzt], punkte, flaechen) & self._ungeklappt(
                scan.punkte[genutzt], punkte, flaechen, entposen.posiert, *koerper)
            if not heil.all():                   # gezerrte und umgeklappte Flächen (Achsel) heraus, neu nummerieren
                index = np.flatnonzero(wahl)
                wahl = np.zeros_like(wahl)
                wahl[index[heil]] = True
                wahl = self._zusammen(scan.flaechen, wahl)
                genutzt, neu = np.unique(scan.flaechen[wahl].reshape(-1), return_inverse=True)
                punkte = entposen.ruhelage(scan.punkte[genutzt])
                flaechen = neu.reshape(-1, 3)
            kennung, b = self._schreiben(name, punkte, flaechen, scan.uv_ecken[wahl], scan.textur)
            b['geklappt'] = int((~heil).sum())
            aus[name], bericht[name] = kennung, b
        return aus, bericht

    #: Eine Fläche, deren längste Kante beim Zurückrechnen in die Ruhelage um mehr als diesen Faktor wächst, ist gezerrt
    #: (Stoff zwischen hängendem Arm und Rumpf, in der A-Pose zur Haut über der Achsel gezogen — Risse unter Ärmeln).
    DEHNUNG_MAX = 1.8

    @classmethod
    def _ungedehnt(cls, vorher, nachher, flaechen):
        """(F,) bool — Flächen, deren längste Kante höchstens um `DEHNUNG_MAX` gewachsen ist."""
        def laenge(p):
            e = p[flaechen]
            return np.max(np.stack([np.linalg.norm(e[:, i] - e[:, (i + 1) % 3], axis=1) for i in range(3)]), axis=0)
        return laenge(np.asarray(nachher)) <= cls.DEHNUNG_MAX * np.maximum(laenge(np.asarray(vorher)), 1e-6)

    #: Eine Fläche ist umgeklappt, wenn ihre Normale gegenüber der Hautnormale am nächsten Figurpunkt vor dem
    #: Zurückrechnen deutlich auf der einen, danach deutlich auf der anderen Seite steht (Kosinus über ±`KLAPP`) —
    #: Ärmelstoff zwischen Arm und Rumpf faltet sich über sich selbst (Fassung 10: Ärmel und Saum voller sichtbarer
    #: Rückseiten). Absolut geht es nicht: die Flächen des TRELLIS-Netzes sind nicht einheitlich orientiert.
    KLAPP = 0.2

    @classmethod
    def _ungeklappt(cls, vorher, nachher, flaechen, koerper_posiert, koerper, dreiecke):
        """(F,) bool — Flächen, die beim Zurückrechnen nicht die Seite gewechselt haben."""
        a = cls._kosinus(vorher, flaechen, koerper_posiert, dreiecke)
        b = cls._kosinus(nachher, flaechen, koerper, dreiecke)
        return ~(((a > cls.KLAPP) & (b < -cls.KLAPP)) | ((a < -cls.KLAPP) & (b > cls.KLAPP)))

    @staticmethod
    def _kosinus(punkte, flaechen, koerper, dreiecke):
        """(F,) — Kosinus zwischen Flächennormale und Hautnormale am nächsten Figurpunkt."""
        from scipy.spatial import cKDTree
        e = np.asarray(punkte)[flaechen]
        n = np.cross(e[:, 1] - e[:, 0], e[:, 2] - e[:, 0])
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        k = koerper[dreiecke]
        kn = np.zeros_like(koerper)
        for i in range(3):                                         # Punktnormalen der Figur (flächengewichtet)
            np.add.at(kn, dreiecke[:, i], np.cross(k[:, 1] - k[:, 0], k[:, 2] - k[:, 0]))
        kn /= np.maximum(np.linalg.norm(kn, axis=1, keepdims=True), 1e-12)
        _, index = cKDTree(koerper).query(e.mean(axis=1), workers=-1)
        return np.einsum('ij,ij->i', n, kn[index])

    #: Zusammenhangsteile unter diesem Anteil der Flächen des Stücks fallen weg (Hautflecken, Fäden, Inseln).
    TEIL_MIN = 0.03
    #: Hautton je Fläche (r > g > b, r − b über diesem Abstand, 0…1) gehört nicht zum Stück — die Kleidungsteilung
    #: nahm fleckige Haut der Beine in Hose und Socken (Testauftrag: Oberschenkelband, Knöchel). Wie `Kleiderwahl.haut`.
    #: Grenze: warmfarbene Kleidung (rot, orange, beige) fiele hier mit heraus — dann gilt der Schalter der Fotoprüfung.
    HAUT_ABSTAND = 0.10

    #: Höhenkern eines Stücks (`_kern`): Bänder von `KERN_BAND` m, zusammenhängend um das dichteste, solange ein Band
    #: mindestens `KERN_ANTEIL` von dessen Flächen hat. Gemessen am Testauftrag (Flächen je 2 cm): Hose dicht
    #: 0,64–0,84 m, dazu ein Klumpen bei 0,22 m und ein Faden (~11 je Band); Socken von 12.114 am Boden stetig
    #: dünner bis 0,22 m (die Schienbeine, deren Netztextur grau ist — nach Farbe nicht von der Socke zu trennen). Ein
    #: Farbtonfilter riss Löcher ins Shirt und ließ die Reste stehen.
    KERN_BAND = 0.02
    KERN_ANTEIL = 0.15
    #: Je Stück strenger: die Hose hat unter dem Saum einen dichten Hautstreifen (0,64–0,68 m, Netztextur grau).
    KERN_ANTEIL_JE = {'hose': 0.35}

    @classmethod
    def _kern(cls, wahl, hoehe, name=None):
        """`wahl` auf den zusammenhängenden Höhenkern um das dichteste Band beschränkt."""
        if not wahl.any():
            return wahl
        band = np.floor((hoehe - hoehe[wahl].min()) / cls.KERN_BAND).astype(int)
        zahl = np.bincount(band[wahl])
        dicht = int(np.argmax(zahl))
        genug = zahl >= cls.KERN_ANTEIL_JE.get(name, cls.KERN_ANTEIL) * zahl[dicht]
        von = dicht
        while von > 0 and genug[von - 1]:
            von -= 1
        bis = dicht
        while bis + 1 < len(zahl) and genug[bis + 1]:
            bis += 1
        return wahl & (band >= von) & (band <= bis)

    #: Ränder glätten (`_glaetten`): so viele Flächenringe ab- und wieder anfügen (Öffnen) — dünne Lappen und Fransen an
    #: Ausschnitt, Saum und Achsel fallen weg, die Form bleibt (Runde 23: Shirtränder ausgefranst).
    GLAETTEN_RINGE = 3
    #: Hose und Socken nur ein Ring: drei rissen den Hosenbund auf (Haut zwischen Shirt und Hose, Fassung 8).
    GLAETTEN_JE = {'hose': 1, 'socken': 1}

    @classmethod
    def _glaetten(cls, flaechen, wahl, ringe=None):
        """Morphologisches Öffnen auf dem Netz: `ringe` Mal die Randflächen weg (Flächen mit einem Punkt außerhalb),
        dann ebenso oft innerhalb der alten Wahl wieder dazu."""
        from scipy.sparse import coo_matrix
        f = np.asarray(flaechen, dtype=np.int64)
        n_punkte = int(f.max()) + 1
        zeilen = np.repeat(np.arange(len(f)), 3)
        inzidenz = coo_matrix((np.ones(len(zeilen)), (zeilen, f.reshape(-1))), shape=(len(f), n_punkte)).tocsr()
        alt, jetzt = wahl.copy(), wahl.copy()
        for _ in range(cls.GLAETTEN_RINGE if ringe is None else ringe):    # abtragen
            draussen = np.zeros(n_punkte, dtype=bool)                      # Punkte an einer nicht gewählten Fläche
            draussen[np.unique(f[~jetzt])] = True
            jetzt = jetzt & ~(inzidenz @ draussen.astype(np.float64) > 0)
        for _ in range(cls.GLAETTEN_RINGE if ringe is None else ringe):    # wieder anfügen, nur in der alten Wahl
            punkte = np.zeros(n_punkte, dtype=np.float64)
            punkte[np.unique(f[jetzt])] = 1.0
            jetzt = alt & ((inzidenz @ punkte) > 0)
        return jetzt

    @classmethod
    def _zusammen(cls, flaechen, wahl):
        """`wahl` ohne Hautflächen (`haut` der Maske — dunkle Flecken an den Beinen galten als „Hose", Testauftrag
        2026.10.01.12.38.09: 0,23–0,84 m) und ohne kleine Zusammenhangsteile (`TEIL_MIN`)."""
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import connected_components
        index = np.flatnonzero(wahl)
        if not len(index):
            return wahl
        f = np.asarray(flaechen)[index]
        zeilen = np.repeat(np.arange(len(index)), 3)
        punkt = coo_matrix((np.ones(len(zeilen)), (zeilen, f.reshape(-1))), shape=(len(index), int(f.max()) + 1))
        nachbarn = (punkt @ punkt.T).tocoo()                       # Flächen mit gemeinsamem Punkt
        n, teil = connected_components(nachbarn, directed=False)
        groesse = np.bincount(teil, minlength=n)
        aus = np.zeros_like(wahl)
        aus[index[groesse[teil] >= cls.TEIL_MIN * len(index)]] = True
        return aus

    def _schreiben(self, name, punkte, flaechen, uv_ecken, textur):
        """Ein Stück: OBJ + Textur, schreiben, Ruhelage auf der Grundfigur, neu schreiben → (Kennung, Bericht)."""
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.gcfigurbau import G9gcfigurbau
        from Genesis9.mbkategorien import G9mbkategorien
        from Genesis9.objleser import G9objleser
        from PIL import Image
        kuerzel = self.job.kennung.replace('.', '')[-8:]
        # Die Fassung steht in der Kennung: ein neu gebautes Stück ist ein anderes Stück — sonst wechselte die Form unter
        # derselben Kennung, die Runde sah keinen Umbau und lastete die Notenänderung einem Farbschritt an (Testauftrag,
        # Runde 40, `~/.claude/rules/artefakte-benennen.md`).
        kennung, anzeige = G9eigenstueck.kennung_und_name('Eigen Foto %s %s f%d' % (kuerzel, name, self.FASSUNG))
        ordner = G9eigenstueck.arbeitsordner(kennung)
        ordner.mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.asarray(textur, dtype=np.uint8)).save(ordner / 'textur.png')
        (ordner / 'stueck.mtl').write_text('newmtl Stoff\nKd 1 1 1\nmap_Kd textur.png\n', encoding='utf-8')
        uv = np.asarray(uv_ecken, dtype=np.float64).reshape(-1, 2)
        zeilen = ['mtllib stueck.mtl', 'usemtl Stoff'] + ['v %.6f %.6f %.6f' % tuple(p) for p in punkte]
        zeilen += ['vt %.6f %.6f' % tuple(t) for t in uv]
        zeilen += ['f %d/%d %d/%d %d/%d' % (a + 1, 3 * i + 1, b + 1, 3 * i + 2, c + 1, 3 * i + 3)
                   for i, (a, b, c) in enumerate(np.asarray(flaechen, dtype=np.int64))]
        obj = ordner / 'stueck.obj'
        obj.write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
        netz = G9objleser.lesen(str(obj))
        roh = np.asarray(netz['punkte'], dtype=np.float64)
        kategorie = G9mbkategorien.fuer(self.ORDNER.get(name, 'tops'), anzeige)
        material = {'name': kennung + '_Mat', 'farbe': (1.0, 1.0, 1.0), 'bild': str(ordner / 'textur.png'),
                    'shininess': None, 'opacity': None}
        bilanz = G9eigenstueck.schreiben(roh, netz, kennung, anzeige, kategorie, material, heben=False)
        figur = dict(self.job.stellung() or {})
        ruhe, bericht = G9gcfigurbau.ruhelage(bilanz['stueck'], figur, roh, roh)
        bilanz = G9eigenstueck.schreiben(ruhe, netz, kennung, anzeige, kategorie, material, heben=False)
        bericht.update(stueck=bilanz['stueck'], flaechen=bilanz['flaechen'], angezogen=G9gcfigurbau.pruefen(
            bilanz['stueck'], figur, roh))
        return bilanz['stueck'], bericht
