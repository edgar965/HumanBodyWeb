# -*- coding: utf-8 -*-
"""Blendimportrollen — welches Netz einer .blend Körper, Auge, Mund, Haar oder Kleidungsstück ist.

Aus dem Inventar von `blendexport.py` (Maße, Hautgewichte je Knochen, Bilder je Kanal), ohne Namensliste der Netze:

    koerper   das Netz mit den meisten benutzten Knochen (Haut über Rumpf, Arme, Beine, Gesicht), mind. 1 m hoch
    auge      kleiner als 5 cm und nur an Knochen mit „eye" im Namen
    mund      nur an Zahn- oder Zungenknochen (`teeth`, `tong`) — fällt weg, Genesis bringt eigene
    haar      alle Gewichte auf EINEM Kopfknochen und ein Alpha-Kanal im Material (Haarkarten)
    kleid     alles andere; Kategorie aus Höhe und Name (`kategorie`)

Gemessen an „cute girl" (08.10.2026): Körper 133 Knochen, Shirt 24, Jeans 9, Haar 1 (`head.x`, Alpha), Augen je 1
(`c_eye.l`/`.r`), Zähne/Zunge je 3. Der Dialog zeigt die Rollen; geraten wird nichts, was nicht in diesen Zahlen steht.
"""

__all__ = ['Blendimportrollen']


class Blendimportrollen:
    KOERPER_MIN_M = 1.0
    AUGE_MAX_M = 0.05
    MUND = ('teeth', 'tong', 'zahn', 'zunge')
    KOPF = ('head', 'kopf')

    def __init__(self, inventar):
        self.netze = list((inventar or {}).get('netze') or [])

    @staticmethod
    def hoehe(netz):
        return float(netz['max'][2] - netz['min'][2])

    @staticmethod
    def groesse(netz):
        return max(float(b - a) for a, b in zip(netz['min'], netz['max'], strict=True))

    @staticmethod
    def _alpha(netz):
        return any(m.get('alpha') for m in netz.get('materialien') or [])

    def rolle(self, netz, koerper):
        knochen = [k.lower() for k in netz.get('gewichte') or {}]
        if netz is koerper:
            return 'koerper'
        if knochen and all(any(m in k for m in self.MUND) for k in knochen):
            return 'mund'
        if self.groesse(netz) < self.AUGE_MAX_M and knochen and all('eye' in k for k in knochen):
            return 'auge'
        if len(knochen) == 1 and any(k.startswith(self.KOPF) for k in knochen) and self._alpha(netz):
            return 'haar'
        return 'kleid'

    def koerper(self):
        hoch = [n for n in self.netze if self.hoehe(n) >= self.KOERPER_MIN_M]
        if not hoch:
            raise ValueError('Kein Körper: kein Netz an einer Armatur ist mindestens %.1f m hoch' % self.KOERPER_MIN_M)
        return max(hoch, key=lambda n: (len(n.get('gewichte') or {}), n['punkte']))

    @staticmethod
    def kategorie(netz):
        """`(ordner, Anzeigezusatz)` für `G9mbkategorien.fuer`: Höhe der Mitte über dem Boden und Ausdehnung."""
        unten, oben = float(netz['min'][2]), float(netz['max'][2])
        name = str(netz['name']).lower()
        if any(w in name for w in ('shoe', 'schuh', 'boot', 'sneaker')) or oben < 0.25:
            return 'shoes', 'Schuhe'
        if any(w in name for w in ('dress', 'kleid')) or (oben > 1.2 and unten < 0.7):
            return 'dresses', 'Kleid'
        if oben <= 1.2 and unten < 0.95:
            # Hose oder Rock; endet sie über dem Knie (~0,5 m bei 1,75 m), sind es Shorts.
            return 'pants', 'Shorts' if unten > 0.6 else 'Hose'
        return 'tops', 'Shirt'

    def zuordnen(self):
        """`[{name, datei, rolle, ordner?, art?}]` in der Reihenfolge des Inventars."""
        koerper = self.koerper()
        aus = []
        for netz in self.netze:
            rolle = self.rolle(netz, koerper)
            eintrag = {'name': netz['name'], 'datei': netz['datei'], 'rolle': rolle, 'punkte': netz['punkte']}
            if rolle == 'kleid':
                eintrag['ordner'], eintrag['art'] = self.kategorie(netz)
            aus.append(eintrag)
        return aus
