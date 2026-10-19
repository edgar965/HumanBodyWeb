# -*- coding: utf-8 -*-
"""Meshfigurgriff — die Finger der Figur schließen sich um das, was die Hand im Netz hält (14.10.2026, Edgar: „die Hand muss um den Zauberstab sein").

Anlass: Am Zauberer liegt die Hand der Figur in der Haltung des Netzes auf dem Stab (Handmitte 42 mm von der Achse, gemessen `hand_stab_netz.py`), aber offen und neben ihm — „Mesh to 3D" stellt keine Finger
(Gewicht 0,0, `Meshfigurabstand.GEWICHT`), die Figur hat immer Genesis' gestreckte Ruhehand. Beim Blender-Import löst das der Schritt „finger" (`Blendimportfinger`: 21 Fingerwinkel je Hand, an die Originalhand gepasst); für den Weg
„netz" gab es nichts — dort ist das Original ein verschmolzenes Netz, und die Hand steht nirgends als eigenes Teil. Hier dieselbe Suche (`Blendimportfingermodell`, `Blendimportfingersuche`, ein Maß: Abstand zur FLÄCHE der Figurhand,
nicht zu den Käfigpunkten), mit drei Unterschieden:

* **Ziel der Suche** sind die Netzpunkte, die Sapiens als Hand sieht (`Meshfigurhalter.HAND_KLASSEN`, mindestens `MIN_STIMMEN` Pixel) UND höchstens `RADIUS_M` von der FAUST DES NETZES liegen (`bewegung.haelt.zentrum`, die Mitte der Handflächen, die den
  Bestandteil berühren) — nicht von der Hand der Figur: die steht in der Anpassung von Lauf zu Lauf bis zu 8 cm anders (zwei Läufe am Zauberer, Käfig sonst auf 2,1 mm gleich) und am Zauberer 25 cm neben der Netzhand. Sapiens' Handfläche reicht beim
  Zauberer bis 60 cm weit (das Etikett fließt über Stab und Robe), darum die Reichweite.
* **Hände, die etwas halten:** ein Bestandteil (`Meshfigurteile`), dessen Berührung mit Handflächen des Netzes `Meshfigurhalter` gefunden hat (`bewegung.haelt`), nennt die Seite. Eine leere Hand blieb bis 14.10.2026 mittags, wie sie war — die Probe der Blender-Importe
  (`Blendimportfinger._probe`) zeigte, dass die Suche eine offene, entspannte Hand zur Faust krümmt (die Originalfinger sind kürzer als die der Genesis-Hand). Seither bekommt auch sie die Suche (`LEERE_HAENDE`, Edgar: „Finger-Pose“), mit der Hand der Figur als Mitte des Ziels
  und derselben Annahme wie beim Griff; seit dem Handmaß (`Meshfigurhandmass`) hat die Figurhand die Länge der Netzhand, das Argument der kürzeren Finger gilt dort nicht mehr.
* **Armwinkel mit im Modell** (`Meshfigurgriffmodell`): Oberarm, Unterarm und Handgelenk der Seite dürfen mitwandern, damit die Hand auf der Faust des Netzes liegt; die Hand wandert höchstens `MAX_WEG_M`.

Die Winkel gelten für die Figur in der HALTUNG des Netzes (`ergebnis.haltung.drehung`, `Meshfighaltung`): `anwenden` addiert sie dort hinein (Finger starten bei 0, Arm bei den Winkeln der Anpassung), der Browser backt die Figur damit (`G9figur.formung`). In der Ruhe und in der Animation
sind die Finger die der Bewegung (die Tanz-BVH treibt Finger) — dort schließt sich die Faust nicht. Ablage: `arbeit/griff.json` (Stempel aus Figur, Regler, Seiten und Ziel — gleicher Stempel, keine neue Suche), `ergebnis.griff`.
"""

import hashlib
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurgriff']


class Meshfigurgriff:
    DATEI = 'griff.json'
    #: Hochzählen, wenn sich das Verfahren ändert: ein Stempel mit anderer Fassung gilt nicht. 2 (14.10.2026): auch leere Hände (`leere`).
    FASSUNG = 2
    #: Auch Hände ohne Gegenstand bekommen Finger, die zur Hand des Netzes passen (Edgar, 14.10.2026: „Finger-Pose“ — die Figurhand ist immer Genesis' gestreckte Ruhehand, die Hand des Netzes ist entspannt gebeugt). Gleiche Annahme wie beim Griff
    #: (Median UND p90 um ein Fünftel besser als die gestreckte Hand an bester Stelle); False: nur Hände mit Gegenstand, wie bis 14.10.2026 mittags.
    LEERE_HAENDE = True
    #: Netzpunkte als Ziel: höchstens so weit von der Faust des Netzes (Hand ~19 cm lang).
    RADIUS_M = 0.14
    #: Weniger Punkte hat eine gesehene Hand nie (Zauberer rechts 4.265, links 2.412 binnen 14 cm): dann gibt es nichts zu messen.
    MINDEST_PUNKTE = 500
    #: Die Winkel gelten nur, wenn Median UND p90 des Abstands Netz-Hand → Figurhand unter diesem Anteil der gestreckten Hand liegen (wie `Blendimportfinger.RUHE_VORTEIL`, eine Setzung).
    VORTEIL = 0.8
    #: So weit (m) darf die Handmitte der Figur durch die Armwinkel des Griffs wandern (Zauberer: die Hand der Anpassung liegt 25 cm neben der Netzhand, im Probelauf wanderte sie 5–6 cm).
    MAX_WEG_M = 0.30

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    @classmethod
    def sicher(cls, lauf):
        """Rechnen (oder die gleiche Rechnung von vorhin übernehmen) und in die Haltung legen; wirft nie — ein Zusatz."""
        try:
            return cls(lauf).rechnen()
        except Exception as fehler:  # noqa: BLE001 — die Figur bleibt mit offener Hand, der Grund steht im Ergebnis und im Log
            logger.exception('Mesh to 3D %s: Griff gescheitert', lauf.job.kennung)
            lauf.job.ergebnis['griff'] = {'fassung': cls.FASSUNG, 'fehler': str(fehler)[:300]}
            return lauf.job.ergebnis['griff']

    # ------------------------------------------------------------------ Welche Hand

    def halter(self):
        """`{seite: {name, zentrum}}` — die Hände, die laut `ergebnis.teile` etwas halten: das Netz hat Handflächen am Bestandteil gefunden (`bewegung.haelt`, `Meshfigurhalter`; `zentrum` = wo die echte Faust liegt). Ob der Gegenstand lang und dünn ist,
        spielt für die Finger keine Rolle (auch ein Schildgriff wird gefasst)."""
        aus = {}
        for t in self.job.ergebnis.get('teile') or []:
            haelt = (t.get('objekt') or {}).get('haelt') or {}
            if haelt.get('seite') in ('r', 'l'):
                aus.setdefault(haelt['seite'], {'name': t.get('name'), 'zentrum': haelt.get('zentrum')})
        return aus

    def leere(self, halter):
        """`{seite: {name, zentrum: None, leer: True}}` — die Hände ohne Gegenstand (`LEERE_HAENDE`): ihr Ziel liegt um die Hand der Figur (`ziel`), denn es gibt keine Faust des Netzes, die ihre Lage nennt."""
        if not self.LEERE_HAENDE:
            return {}
        return {s: {'name': 'leere Hand', 'zentrum': None, 'leer': True} for s in ('r', 'l') if s not in halter}

    def ziel(self, scan, klassen, mitte, seite=None):
        """Die Netzpunkte (Lage des Netzes) dieser Hand: Flächen, die Sapiens als Hand sieht (eine der beiden Handklassen: am Zauberer trugen 2.005 Flächen der rechten Hand das Etikett `Left_Hand`), binnen `RADIUS_M` von `mitte` (die Faust des Netzes,
        sonst die Hand der Figur). `seite` nur für den Bericht."""
        from .meshfigurhalter import Meshfigurhalter

        flaechen = np.asarray(scan.flaechen)
        punkte = np.asarray(scan.punkte)
        gesehen = (klassen.max(axis=1) >= Meshfigurhalter.MIN_STIMMEN) & np.isin(klassen.argmax(axis=1), Meshfigurhalter.HAND_KLASSEN)
        nah = gesehen & (np.linalg.norm(punkte[flaechen].mean(axis=1) - mitte, axis=1) < self.RADIUS_M)
        return punkte[np.unique(flaechen[nah].reshape(-1))]

    # ------------------------------------------------------------------ Rechnen

    def rechnen(self):
        from .meshfigurkleidung import Meshfigurkleidung

        halter = self.halter()
        halter = {**self.leere(halter), **halter}
        if not halter:
            self.job.ergebnis['griff'] = {'fassung': self.FASSUNG, 'hinweis': 'In keiner Hand ein Gegenstand'}
            return self.job.ergebnis['griff']
        arbeit = self.ablage.arbeit
        sapiens, posiert, ende = arbeit('sapiens_flaechen.npz'), arbeit('posiert.npy'), arbeit('genesis_ende.npz')
        if not (sapiens.is_file() and posiert.is_file() and ende.is_file()):
            self.job.ergebnis['griff'] = {'fassung': self.FASSUNG, 'hinweis': 'Etiketten, Käfig oder Figur fehlen'}
            return self.job.ergebnis['griff']
        scan, _ = Meshfigurkleidung(self.lauf).koerpernetz()
        with np.load(sapiens) as d:
            klassen = np.asarray(d['klassen'])
        if len(klassen) != len(scan.flaechen):
            self.job.ergebnis['griff'] = {'fassung': self.FASSUNG, 'hinweis': 'Die Etiketten gehören zu einem anderen Netz'}
            return self.job.ergebnis['griff']
        kaefig = np.load(posiert).astype(np.float64)
        with np.load(ende) as d:
            teil = np.asarray(d['teil'])
        from Genesis9.koerperteile import G9koerperteile

        mitten = {s: kaefig[teil == G9koerperteile.NUMMER[s + '_hand']].mean(axis=0) for s in halter}
        # Das Ziel liegt um die Faust des NETZES (`zentrum`), nicht um die Hand der Figur — die steht von Lauf zu Lauf bis zu 8 cm anders und am Zauberer 25 cm neben der Netzhand.
        ziele = {s: self.ziel(scan, klassen, np.asarray(halter[s].get('zentrum') or mitten[s], dtype=np.float64), s) for s in halter}
        stempel = self._stempel(kaefig, halter, ziele)
        gemerkt = self._gemerkt(stempel)
        if gemerkt is not None:
            bericht = {**gemerkt, 'uebernommen_aus_ablage': True}
        else:
            bericht = {'fassung': self.FASSUNG, 'seiten': self._suchen(halter, ziele, kaefig)}
            self._ablegen(stempel, bericht)
        self.job.ergebnis['griff'] = bericht
        bericht['drehung_knochen'] = self.anwenden(bericht)
        return bericht

    def _suchen(self, halter, ziele, kaefig):
        from .blendimporthaltung import Blendimporthaltung

        lage = SimpleNamespace(ablage=self.ablage, stellung=self.job.stellung, finger_drehung={}, kaefig_posiert=kaefig)
        halt = Blendimporthaltung(lage)
        if halt.vorbereiten() is None:
            return {s: {'uebernommen': False, 'grund': 'Der Auftrag führt keine Haltung'} for s in halter}
        # Die Hände hängen nicht voneinander ab: nebeneinander (19.10.2026; je Hand rechnen die Starts schon in Fäden, `Blendimportfingersuche`). Ergebnis je Seite wie vorher, sortiert.
        with ThreadPoolExecutor(max(1, len(halter))) as pool:
            fertig = dict(pool.map(lambda s: (s, self._eine_seite(s, halter[s], ziele[s], halt)), sorted(halter)))
        return {s: fertig[s] for s in sorted(halter)}

    def _eine_seite(self, seite, eintrag_halter, ziel, halt):
        """Eine Hand: Suche der Finger (und Armwinkel) und die Annahme — der Eintrag von `seiten[seite]`."""
        from .blendimportfingersuche import Blendimportfingersuche
        from .meshfigurgriffmodell import Meshfigurgriffmodell

        eintrag = {'haelt': eintrag_halter['name'], 'netzpunkte': int(len(ziel)), 'uebernommen': False, 'griff': {}}
        if eintrag_halter.get('leer'):
            eintrag['leer'] = True
        if len(ziel) < self.MINDEST_PUNKTE:
            eintrag['grund'] = 'nur %d Netzpunkte, die Sapiens als Hand sieht, in Handreichweite' % len(ziel)
            return eintrag
        modell = Meshfigurgriffmodell(halt, seite, ziel)
        ohne = modell.ohne_finger()                                        # die beste Lage der GESTRECKTEN Hand: das müssen die Finger schlagen
        erg = Blendimportfingersuche(modell, lambda text: logger.info('Mesh to 3D %s: Griff %s', self.job.kennung, text)).suchen()
        v, n = ohne['kennzahlen'], erg['nachher']
        eintrag.update(ohne_finger=v, nachher=n, start=erg['start'], sekunden=erg['sekunden'], phi=[round(float(x), 2) for x in erg['phi']])
        # Wie weit wandert die Hand der Figur (Mitte der Handpunkte) durch Armwinkel und Finger? Mehr als `MAX_WEG_M` ist keine Korrektur mehr, sondern eine andere Pose.
        weg = float(np.linalg.norm(modell.posiert(erg['phi']).mean(axis=0) - modell.posiert(np.zeros(modell.anzahl)).mean(axis=0)))
        eintrag['weg_mm'] = round(weg * 1000.0, 1)
        gilt = (bool(erg['uebernommen']) and n['original_median_mm'] < self.VORTEIL * v['original_median_mm'] and n['original_p90_mm'] < self.VORTEIL * v['original_p90_mm'] and weg <= self.MAX_WEG_M)
        if gilt:
            eintrag.update(uebernommen=True, griff=modell.als_griff(erg['phi']))
        else:
            eintrag['grund'] = ('Hand wanderte %.0f cm (mehr als %.0f cm)' % (100 * weg, 100 * self.MAX_WEG_M) if weg > self.MAX_WEG_M else
                                'Median und p90 des Abstands Netz-Hand → Figurhand werden durch die Finger nicht um %.0f %% besser als bei gestreckter Hand an bester Stelle' % (100.0 * (1.0 - self.VORTEIL)))
        logger.info('Mesh to 3D %s: Griff %s — %s', self.job.kennung, seite, {k: v for k, v in eintrag.items() if k != 'griff'})
        return eintrag

    # ------------------------------------------------------------------ Haltung

    def anwenden(self, bericht):
        """Die Winkel des Griffs (Finger, dazu der Zuwachs an Oberarm, Unterarm und Handgelenk der haltenden Seite) zu `ergebnis.haltung.drehung` addieren (die Bühne backt die Figur damit); `ergebnis.haltung` wird bei jedem Lauf
        der Vorschau neu geschrieben, darum gilt das auch für einen übernommenen Griff. Gibt die Zahl der Knochen mit Winkel zurück (0 ohne gültige Haltung)."""
        haltung = self.job.ergebnis.get('haltung') or {}
        if not (haltung.get('gueltig') and isinstance(haltung.get('drehung'), dict)):
            return 0
        n = 0
        for eintrag in (bericht.get('seiten') or {}).values():
            if not (isinstance(eintrag, dict) and eintrag.get('uebernommen')):
                continue
            for knochen, kanaele in (eintrag.get('griff') or {}).items():
                ziel = haltung['drehung'].setdefault(knochen, {})
                for kanal, zuwachs in kanaele.items():
                    ziel[kanal] = round(float(ziel.get(kanal, 0.0)) + float(zuwachs), 3)          # Zuwachs: Finger starten bei 0, Arm und Handgelenk bei den Winkeln der Anpassung
                n += 1
        return n

    # ------------------------------------------------------------------ Ablage

    def _stempel(self, kaefig, halter, ziele):
        """Gleiche Figur, gleiche Regler, gleiche Seiten, gleiches Ziel → dieselbe Suche."""
        h = hashlib.sha1()
        h.update(np.ascontiguousarray(kaefig.astype(np.float32)).tobytes())
        h.update(json.dumps([self.FASSUNG, sorted(halter), self.job.stellung(), [len(ziele[s]) for s in sorted(ziele)], [round(float(ziele[s].sum()), 4) for s in sorted(ziele)]],
                            sort_keys=True, default=str).encode('utf-8'))
        return h.hexdigest()[:16]

    def _gemerkt(self, stempel):
        pfad = self.ablage.arbeit(self.DATEI)
        if not pfad.is_file():
            return None
        try:
            daten = json.loads(pfad.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        return daten.get('bericht') if daten.get('stempel') == stempel else None

    def _ablegen(self, stempel, bericht):
        from ..atomic_write import AtomarSchreiber

        AtomarSchreiber.json_schreiben(self.ablage.arbeit(self.DATEI), {'stempel': stempel, 'bericht': bericht, 'geschrieben': time.strftime('%Y-%m-%d %H:%M:%S')})
