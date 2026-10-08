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

OHNE HAUTGEWICHTE (eine .blend ganz ohne Skelett, gemessen 09.10.2026 an „Beautiful Asian girl 5.0.blend": 15 Netze, 0 Armaturen,
Character-Creator-Namen) entscheiden Maße, Material und — wo Maße nicht trennen — der Name (`rolle_ohne_gewichte`):

    koerper        das höchste Netz (Kopf bis Fuß), bei Gleichstand das mit den meisten Punkten
    mund / auge    kleines Netz am Kopf (Unterkante ≥ 80 % der Körperhöhe) mit `teeth`/`tong` bzw. `eye` im Namen
    gesichtshaar   Wimpern und Brauen (`lash`, `brow`) am Kopf — Genesis bringt eigene, kein Stück
    haar           Alpha-Kanal im Material, Oberkante ≥ 92 % der Körperhöhe, mindestens 5 % der Körperhöhe groß
    kleid          alles andere

Alle Maße gelten für eine Figur von `REFERENZ_M`; ein Modell in anderem Maßstab (die Asian girl ist 3,26 m hoch) wird über die
Körperhöhe umgerechnet — `kategorie` arbeitet in Metern einer 1,75-m-Figur.
"""

import re
from collections import Counter

__all__ = ['Blendimportrollen']


class Blendimportrollen:
    KOERPER_MIN_M = 1.0
    AUGE_MAX_M = 0.05
    MUND = ('teeth', 'tong', 'zahn', 'zunge')
    KOPF = ('head', 'kopf')
    #: Höhe der Figur, für die alle Metermaße hier gelten (Genesis' Ruhehöhe, wie `Blendimportnachformung`).
    REFERENZ_M = 1.75
    #: Nur ohne Hautgewichte: Wimpern und Brauen; Zähne und Zunge sind höchstens so groß (Meter der Referenzfigur).
    GESICHTSHAAR = ('lash', 'wimper', 'brow', 'braue')
    MUND_MAX_M = 0.10
    #: Nur ohne Hautgewichte: Anteile der Körperhöhe. Auge, Mund, Wimper: Unterkante mindestens hier; Haar: Oberkante und Größe.
    KOPFNAH = 0.80
    HAAR_OBEN = 0.92
    HAAR_MIN = 0.05
    #: Namen, die die Höhe überstimmen oder ergänzen (`kategorie`).
    SCHUH = ('shoe', 'schuh', 'boot', 'sneaker')
    SOCKE = ('sock', 'strumpf', 'stocking')
    WAESCHE = re.compile(r'(^|[^a-z])(bra|underwear|panty|panties|briefs?)([^a-z]|$)')

    def __init__(self, inventar):
        self.netze = list((inventar or {}).get('netze') or [])
        self.ohne_armatur = list((inventar or {}).get('ohne_armatur') or [])
        self.armaturen = (inventar or {}).get('armaturen')
        #: Kein Netz trägt Hautgewichte: Datei ohne Skelett (`blendexport.Blendexport.netze` nimmt dann alle Netze).
        self.ohne_gewichte = bool(self.netze) and not any(n.get('gewichte') for n in self.netze)

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
        if netz is koerper:
            return 'koerper'
        knochen = [k.lower() for k in netz.get('gewichte') or {}]
        if not knochen:
            return self.rolle_ohne_gewichte(netz, koerper)
        if all(any(m in k for m in self.MUND) for k in knochen):
            return 'mund'
        if self.groesse(netz) < self.AUGE_MAX_M and all('eye' in k for k in knochen):
            return 'auge'
        if len(knochen) == 1 and any(k.startswith(self.KOPF) for k in knochen) and self._alpha(netz):
            return 'haar'
        return 'kleid'

    def rolle_ohne_gewichte(self, netz, koerper):
        """Rolle eines Netzes ohne Hautgewichte — nach Maßen (Anteile der Körperhöhe), Material und Namen."""
        name = str(netz['name']).lower()
        hoehe = self.hoehe(koerper)
        unten = (float(netz['min'][2]) - float(koerper['min'][2])) / hoehe
        oben = (float(netz['max'][2]) - float(koerper['min'][2])) / hoehe
        anteil = self.groesse(netz) / hoehe
        am_kopf = unten >= self.KOPFNAH
        if am_kopf and any(w in name for w in self.GESICHTSHAAR):
            return 'gesichtshaar'
        if am_kopf and anteil < self.MUND_MAX_M / self.REFERENZ_M and any(m in name for m in self.MUND):
            return 'mund'
        if am_kopf and anteil < self.AUGE_MAX_M / self.REFERENZ_M and 'eye' in name:
            return 'auge'
        if self._alpha(netz) and oben >= self.HAAR_OBEN and anteil >= self.HAAR_MIN:
            return 'haar'
        return 'kleid'

    def koerper(self):
        if not self.netze and self.ohne_armatur:
            # Gemessen 08.10.2026 an „Beautiful Asian girl 5.0.blend": 15 Netze, 0 Armaturen — die Datei ist ein Modell ohne Skelett.
            # Seit 09.10.2026 exportiert `blendexport.py` solche Netze trotzdem; diese Meldung bleibt für ein Inventar, in dem auch
            # dann nichts steht (nur Steuerformen) und für Inventare älterer Läufe.
            raise ValueError('Das Modell hat kein Skelett: %d Netze (%s%s), %s Armaturen — der Import braucht ein Modell mit Rig (Armatur und Hautgewichte, z. B. Auto-Rig Pro).'
                             % (len(self.ohne_armatur), ', '.join(self.ohne_armatur[:4]), ' …' if len(self.ohne_armatur) > 4 else '', self.armaturen if self.armaturen is not None else '0'))
        if self.ohne_gewichte:
            # Ohne Gewichte zählt keine Knochenzahl: das höchste Netz ist der Körper (Asian girl: 3,26 m gegen 1,50 m der Socken).
            hoechste = max(self.hoehe(n) for n in self.netze)
            return max((n for n in self.netze if self.hoehe(n) >= 0.9 * hoechste), key=lambda n: n['punkte'])
        hoch = [n for n in self.netze if self.hoehe(n) >= self.KOERPER_MIN_M]
        if not hoch:
            raise ValueError('Kein Körper: kein Netz an einer Armatur ist mindestens %.1f m hoch' % self.KOERPER_MIN_M)
        return max(hoch, key=lambda n: (len(n.get('gewichte') or {}), n['punkte']))

    @classmethod
    def kategorie(cls, netz, boden=0.0, skala=1.0):
        """`(ordner, Anzeigezusatz)` für `G9mbkategorien.fuer`: Höhe der Mitte über dem Boden und Ausdehnung.
        `boden` (Fußsohle des Körpers) und `skala` (Körperhöhe ÷ `REFERENZ_M`) rechnen ein Modell anderen Maßstabs um."""
        unten, oben = (float(netz['min'][2]) - boden) / skala, (float(netz['max'][2]) - boden) / skala
        name = str(netz['name']).lower()
        if any(w in name for w in cls.SCHUH) or oben < 0.25:
            return 'shoes', 'Schuhe'
        if any(w in name for w in cls.SOCKE):
            return 'accessories', 'Socken'
        if cls.WAESCHE.search(name):
            return 'underwear', 'Unterwäsche'
        if any(w in name for w in ('dress', 'kleid')) or (oben > 1.2 and unten < 0.7):
            return 'dresses', 'Kleid'
        if oben <= 1.2 and unten < 0.95:
            # Hose oder Rock; endet sie über dem Knie (~0,5 m bei 1,75 m), sind es Shorts.
            return 'pants', 'Shorts' if unten > 0.6 else 'Hose'
        return 'tops', 'Shirt'

    def zuordnen(self):
        """`[{name, datei, rolle, ordner?, art?}]` in der Reihenfolge des Inventars."""
        koerper = self.koerper()
        boden, skala = float(koerper['min'][2]), self.hoehe(koerper) / self.REFERENZ_M
        aus = []
        for netz in self.netze:
            rolle = self.rolle(netz, koerper)
            eintrag = {'name': netz['name'], 'datei': netz['datei'], 'rolle': rolle, 'punkte': netz['punkte']}
            if rolle == 'kleid':
                eintrag['ordner'], eintrag['art'] = self.kategorie(netz, boden, skala)
            aus.append(eintrag)
        # „<Figur> <Art>" ist Name UND Kennung des Stücks: zwei Stücke derselben Art (zwei Socken, BH und Slip) schrieben sich
        # sonst gegenseitig über. Dann trägt jedes den Namen seines Netzes dazu.
        gleich = Counter(e['art'] for e in aus if e['rolle'] == 'kleid')
        for e in aus:
            if e['rolle'] == 'kleid' and gleich[e['art']] > 1:
                e['art'] = '%s %s' % (e['art'], str(e['name']).strip())
        return aus
