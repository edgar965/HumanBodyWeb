# -*- coding: utf-8 -*-
"""Mesh3daidatenteile — die Zeilen unter dem ganzen Körper (nur Körper, Gesicht, Hände/Füße, Kleider) aus ECHTEN Daten (15.10.2026, Edgar: „fixe alles").

Bis dahin blieben diese Zeilen bei echten Daten leer. Jetzt bekommt jede Zeile dasselbe wie der ganze Körper, nur ihren Teil davon:
- **Rig:** die Knochen der Zeile (`Mesh3dairig.ZEILEN`) aus Soll und Vorhersage des Laufs, mit Kennzahlen über genau diese Knochen. Das Netz sagt die 138 Punkte des ganzen Körpers voraus; die Zeile ist ein Ausschnitt
  davon, keine eigene Vorhersage.
- **Fläche:** welche Teile der Figur die Zeile zeigt (`ETIKETTEN`: nur Körper = Haut und Anatomie, Kleider = Slip, Hose, Shirt) und wo sie ausgeschnitten wird (`ausschnitte`): das Gesicht um die Kopfmitte, Hände und
  Füße um den Mittelpunkt ihrer Knochen, gerückt auf die Plätze der Seite (`Mesh3daihaende.PLAETZE`, wie bei der Attrappe). Ein Dreieck gehört zu einem Ausschnitt, wenn sein nächster Rig-Punkt einer der
  Knochen des Ausschnitts ist und es höchstens `radius` von der Mitte liegt — das schneidet die Hand vom Oberschenkel, auf dem sie liegt (die Seite rechnet es, `Mesh3daiflaechen`).
Alle Mitten kommen aus dem SOLL; Soll und Ausgabe werden um dieselbe Strecke gerückt, ein Fehler bleibt also als Versatz zu sehen.

    Mesh3daidatenteile.beschreibungen()          -> {zeile: {titel, etiketten, punkte: [], fehler_rot_mm}}   (Antwort `teile`)
    Mesh3daidatenteile.teile(soll, ausgabe)      -> {zeile: {kennzahlen, rig, ausschnitte, eingabe}}          (je Probe)
"""

import numpy as np

from .mesh3daibild import Mesh3daibild
from .mesh3daihaende import Mesh3daihaende
from .mesh3dairig import Mesh3dairig

__all__ = ['Mesh3daidatenteile']


class Mesh3daidatenteile:
    TITEL = {'koerper_nackt': 'Nur Körper', 'gesicht': 'Gesicht', 'haende': 'Hände/Füße', 'kleider': 'Kleider'}
    #: Teile der Figur je Zeile (Etiketten aus `flaeche.npz`); `None` = alle.
    ETIKETTEN = {'koerper_nackt': ('koerper', 'anatomie'), 'gesicht': None, 'haende': None, 'kleider': ('slip', 'hose', 'hemd')}
    #: Mitte des Kopfes über dem Kopfknochen, entlang Hals → Kopf (m). Gemessen an der A-Pose: Kopfknochen y 1,518, Gesichtsknochen y 1,479–1,590, Scheitel mit Haar 1,699 —
    #: 0,06 legt die Mitte auf y 1,578 (mit 0,09 wie `Mesh3dairig.KOPFMITTE_M` der Attrappe lag sie bei 1,608, über den Augen; der Kopf hing im Feld nach unten).
    KOPFMITTE_M = 0.06
    #: Größter Abstand eines Dreiecks von der Mitte seines Ausschnitts (m). Setzung nach Augenmaß: Kopf mit Haar 0,16, Hand 0,13 (Handgelenk bis Fingerspitze rund 0,19), Fuß 0,16.
    RADIUS_M = {'gesicht': 0.16, 'hand': 0.13, 'fuss': 0.16}
    SCHWELLE_MM = 10.0
    #: Die vier Ausschnitte von „Hände und Füße": Platz auf der Seite, Seite des Körpers, Gruppen der Knochen.
    HAENDE = (('Hand L', 'l_', ('hand', 'finger'), 'hand'), ('Hand R', 'r_', ('hand', 'finger'), 'hand'),
              ('Fuß L', 'l_', ('fuss', 'zehen'), 'fuss'), ('Fuß R', 'r_', ('fuss', 'zehen'), 'fuss'))

    #: Die Eingabe zeigt dieselben Teile wie Soll und Ausgabe — außer bei „Nur Körper“: dort ist die Eingabe die Außenfläche MIT Kleidern (gerade die soll das Netz durchschauen).
    EINGABE_ALLE = ('koerper_nackt',)

    @classmethod
    def beschreibungen(cls):
        return {s: {'titel': t, 'etiketten': list(cls.ETIKETTEN[s] or ()), 'eingabe_etiketten': [] if s in cls.EINGABE_ALLE else list(cls.ETIKETTEN[s] or ()),
                    'punkte': [], 'fehler_rot_mm': Mesh3dairig.FEHLER_ROT_MM} for s, t in cls.TITEL.items()}

    @classmethod
    def _ausschnitte(cls, schluessel, soll, indizes, knochen):
        """`[(mitte, ziel, radius, Knochen des Ausschnitts als globale Indizes)]`."""
        namen = [k['name'] for k in knochen]
        if schluessel == 'gesicht':
            kopf, hals = soll[namen.index('head')], soll[namen.index('neck2')]
            achse = (kopf - hals) / max(float(np.linalg.norm(kopf - hals)), 1e-9)
            return [(kopf + cls.KOPFMITTE_M * achse, np.zeros(3), cls.RADIUS_M['gesicht'], list(indizes))]
        if schluessel == 'haende':
            aus = []
            for name, seite, gruppen, art in cls.HAENDE:
                eigene = [i for i in indizes if namen[i].startswith(seite) and knochen[i]['gruppe'] in gruppen]
                platz = Mesh3daihaende.PLAETZE[name]
                aus.append((soll[eigene].mean(axis=0), np.array([platz[0], platz[1], 0.0]), cls.RADIUS_M[art], eigene))
            return aus
        return []

    @classmethod
    def teile(cls, soll, ausgabe, vergleich=None, nr=None):
        """`vergleich` (`Mesh3daivergleich`, 16.10.2026): mittlere und nächste Trainingspose über die Knochen der Zeile, für die Tabelle unter dem Ergebnis."""
        beschr = Mesh3dairig.beschreibung()
        knochen = beschr['knochen']
        aus = {}
        for schluessel in cls.TITEL:
            indizes = beschr['zeilen'][schluessel]
            ausschnitte = cls._ausschnitte(schluessel, soll, indizes, knochen)
            verschub = np.zeros((len(knochen), 3))
            for mitte, ziel, _r, eigene in ausschnitte:
                verschub[eigene] = ziel - mitte
            s, a = soll[indizes] + verschub[indizes], ausgabe[indizes] + verschub[indizes]
            namen = [knochen[i]['name'] for i in indizes]
            k = Mesh3daibild._kennzahlen(s, a, namen, [knochen[i]['gruppe'] for i in indizes], cls.SCHWELLE_MM)
            # Die Punkte selbst schickt der Server NICHT noch einmal (sie stehen in `probe.rig`; mit ihnen wuchs die Antwort von 1,7 auf 5,1 MB, gemessen): die Seite nimmt die Knochen der Zeile
            # (`rig.zeilen`) aus dem Rig der Probe und rückt sie um `ziel − mitte` ihres Ausschnitts (`Mesh3daiechtteile`). Hier stehen nur die Kennzahlen und die Ausschnitte.
            k.pop('je_gelenk_mm')
            if vergleich is not None:
                k.update(vergleich.werte(nr, soll, indizes))
            aus[schluessel] = {
                'kennzahlen': k, 'eingabe': {'echt': True},
                'rig': {'kennzahlen': {'mittel_mm': k['mittel_mm'], 'groesster_mm': k['groesster_mm'], 'groesster_knochen': k['groesster_gelenk'], 'knochen': len(indizes)}},
                'ausschnitte': [{'mitte': np.round(m, 4).tolist(), 'ziel': np.round(z, 4).tolist(), 'radius': r, 'knochen': e} for m, z, r, e in ausschnitte],
            }
        return aus
