# -*- coding: utf-8 -*-
"""Blendimportrollen — welches Netz einer .blend Körper, Auge, Mund, Haar oder Kleidungsstück ist.

Aus dem Inventar von `blendexport.py` (Maße, Hautgewichte je Knochen, Bilder je Kanal), ohne Namensliste der Netze:

    koerper   das Netz mit den meisten benutzten Knochen (Haut über Rumpf, Arme, Beine, Gesicht), mind. 40 % der Figurhöhe
              (Rainys Körper reicht nur von der Hüfte zum Scheitel: 47 %)
    auge      kleiner als 12 cm (beide Augen in EINEM Netz) und nur an Knochen mit „eye" im Namen
    mund      nur an Zahn- oder Zungenknochen (`teeth`, `tong`) — fällt weg, Genesis bringt eigene
    haar      ein Alpha-Kanal im Material, mindestens 80 % der Gewichte auf Kopf- und Halsknochen, Oberkante ab 92 % der Körperhöhe
    augenzubehoer  kleines Netz am Kopf mit „eye"/„tear" im Knochennamen, aber nicht nur Augenknochen (CC: EyeOcclusion, TearLine) — fällt
              weg, Genesis bringt Tränenfilm und Feuchte selbst
    kleid     alles andere; Kategorie aus Höhe und Name (`kategorie`)

Gemessen an „cute girl" (08.10.2026): Körper 133 Knochen, Shirt 24, Jeans 9, Haar 1 (`head.x`, Alpha), Augen je 1
(`c_eye.l`/`.r`), Zähne/Zunge je 3. Der Dialog zeigt die Rollen; geraten wird nichts, was nicht in diesen Zahlen steht.

Gemessen an `Asian_Girl.blend` (Character Creator MIT Rig, 09.10.2026, `ProjektTemp/_wegwerf/asian/`): Die alte Regel („EIN Kopfknochen, Name
beginnt mit `head`") ließ alle fünf Frisurnetze (`CC_Base_Head`, dazu `NeckTwist`, `Spine02`, Schlüsselbeine: Anteil auf Kopf und Hals 0,94–1,0) als „Shirt"
in der Garderobe, ebenso beide Augen in einem Netz (8,4 cm breit) sowie EyeOcclusion und TearLine. Mehrere Frisurnetze tragen darum je ihren Netznamen
im Stücknamen (`zuordnen`) — sonst überschrieben sie sich (Name = Kennung).

OHNE HAUTGEWICHTE (eine .blend ganz ohne Skelett, gemessen 09.10.2026 an „Beautiful Asian girl 5.0.blend": 15 Netze, 0 Armaturen,
Character-Creator-Namen) entscheiden Maße, Material und — wo Maße nicht trennen — der Name (`rolle_ohne_gewichte`):

    koerper        das höchste Netz (Kopf bis Fuß), bei Gleichstand das mit den meisten Punkten
    mund / auge    kleines Netz am Kopf (Unterkante ≥ 80 % der Körperhöhe) mit `teeth`/`tong` bzw. `eye` im Namen
    gesichtshaar   Wimpern und Brauen (`lash`, `brow`) am Kopf — Genesis bringt eigene, kein Stück
    haar           Alpha-Kanal im Material, Oberkante ≥ 92 % der Körperhöhe, mindestens 5 % der Körperhöhe groß
    kleid          alles andere

Alle Maße gelten für eine Figur von `REFERENZ_M`; ein Modell in anderem Maßstab (die Asian girl ist 3,26 m hoch) wird über die
Höhe der GANZEN Figur umgerechnet (`figur`: tiefster bis höchster Punkt aller Netze, nicht das Körper-Netz — Rainys Körper hat keine
Beine, seoris keinen Kopf) — `kategorie` arbeitet in Metern einer 1,75-m-Figur. Der Export bringt Figuren, die höher als 2,5 m sind,
ohnehin schon auf 1,75 m (`Blendexport.faktor_fuer`); hier gilt dasselbe Verhältnis für alles, was ungerechnet ankommt.
"""

import re
from collections import Counter

__all__ = ['Blendimportrollen']


class Blendimportrollen:
    #: Der Körper ist mindestens so hoch wie dieser Anteil der Figur (alle Netze zusammen); früher fest 1,0 m, bei 1,75 m ≈ 0,57.
    KOERPER_MIN_ANTEIL = 0.4
    #: Beide Augen in EINEM Netz sind 8,4 cm breit (Asian_Girl, gemessen); je Auge ein Netz bleibt darunter (cute girl: < 5 cm).
    AUGE_MAX_M = 0.12
    MUND = ('teeth', 'tong', 'zahn', 'zunge')
    #: Mit Gewichten: Knochen, deren Anteil das Haar am Kopf festhält (Frisuren hängen an `head`, lange auch an `NeckTwist`, Schlüsselbein).
    #: `spine.006` ist der Kopf eines Rigify-Skeletts (DEF-Skelett, CLAUDE.md): an ihm hängt das Haar von „hinako" zu 96 %.
    KOPFKNOCHEN = ('head', 'kopf', 'neck', 'hals', 'spine.006')
    HAAR_KOPFANTEIL = 0.8
    #: Hilfsknochen der Augen (Lidschatten, Tränenlinie) — Netze daran, die nicht das Auge selbst sind, ersetzt Genesis.
    AUGENNAH = ('eye', 'tear')
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

    def figur(self, koerper):
        """`(boden, hoehe)` der GANZEN Figur: tiefster und höchster Punkt aller Netze (und des Körpers), nicht nur des Körper-Netzes.
        Rainy: der Körper reicht von der Hüfte (1,73 m) bis zum Scheitel (3,28 m), die Beine stecken in Hose und Stiefel — mit der
        Höhe des Körper-Netzes (1,55 m) und seiner Unterkante als „Boden" wurde die Jacke zur Hose und die Wimpern zum Shirt. Seori:
        der Körper (`head.002`) hat keinen Kopf, der steckt in einem eigenen Netz. Ein vollständiger Körper ändert nichts."""
        unten = min([float(koerper['min'][2])] + [float(n['min'][2]) for n in self.netze])
        oben = max([float(koerper['max'][2])] + [float(n['max'][2]) for n in self.netze])
        return unten, oben - unten

    @staticmethod
    def groesse(netz):
        return max(float(b - a) for a, b in zip(netz['min'], netz['max'], strict=True))

    @staticmethod
    def _alpha(netz):
        return any(m.get('alpha') for m in netz.get('materialien') or [])

    #: Ein Material heißt `body`, `skin` oder `haut` — als eigenes Wort (`Std_Skin_Body`, `body`), nicht in `bodysuit`.
    HAUT_MATERIAL = re.compile(r'(^|[^a-z])(body|skin|haut)([^a-z]|$)')

    @classmethod
    def _hautnetz(cls, netz):
        return any(cls.HAUT_MATERIAL.search(str(m.get('name') or '').lower()) for m in netz.get('materialien') or [])

    #: Überblendungen, bei denen die Deckkraft zählt — auch ohne Bild (Konstante am Principled-Alpha).
    DURCHSICHTIG = ('HASHED', 'BLEND', 'CLIP')

    @classmethod
    def _haarmaterial(cls, netz, anteil_hoehe):
        """Haar trägt eine Deckkraft: ein Alpha-Bild ODER — wenn es mindestens `HAAR_MIN` der Körperhöhe lang ist — eine durchsichtige
        Überblendung. Gemessen 10.10.2026 an „hinako": das Haar (60 cm hoch) hat KEIN Alpha-Bild, nur `HASHED` — `_alpha` allein sah es
        als Kleidungsstück („Shirt hair"). Die Höhe hält die kleinen durchsichtigen Netze (Augen, Wimpern) draußen."""
        if any(w in str(netz['name']).lower() for w in cls.GESICHTSHAAR):
            return False  # Wimpern (Alpha-Bild, am Kopf) sind keine Frisur — sonst fielen sie mit dem Spitzen-Anteil am Kopf ins Haar.
        if cls._alpha(netz):
            return True
        return anteil_hoehe >= cls.HAAR_MIN and any(m.get('ueberblendung') in cls.DURCHSICHTIG for m in netz.get('materialien') or [])

    def rolle(self, netz, koerper):
        if netz is koerper:
            return 'koerper'
        gewichte = {k.lower(): float(w) for k, w in (netz.get('gewichte') or {}).items()}
        if not gewichte:
            return self.rolle_ohne_gewichte(netz, koerper)
        knochen = list(gewichte)
        if all(any(m in k for m in self.MUND) for k in knochen):
            return 'mund'
        boden, hoehe = self.figur(koerper)
        klein = self.groesse(netz) / (hoehe / self.REFERENZ_M) < self.AUGE_MAX_M
        if klein and all('eye' in k for k in knochen):
            return 'auge'
        unten = (float(netz['min'][2]) - boden) / hoehe
        oben = (float(netz['max'][2]) - boden) / hoehe
        if self._haarmaterial(netz, self.hoehe(netz) / hoehe) and oben >= self.HAAR_OBEN and self.kopfanteil(gewichte) >= self.HAAR_KOPFANTEIL:
            return 'haar'
        if klein and unten >= self.KOPFNAH and any(w in k for k in knochen for w in self.AUGENNAH):
            return 'augenzubehoer'
        return 'kleid'

    @classmethod
    def kopfanteil(cls, gewichte):
        """Anteil der Gewichtssumme auf Kopf- und Halsknochen (`KOPFKNOCHEN`); `gewichte` {knochen klein: Summe}."""
        gesamt = sum(gewichte.values())
        if gesamt <= 0:
            return 0.0
        return sum(w for k, w in gewichte.items() if any(m in k for m in cls.KOPFKNOCHEN)) / gesamt

    def rolle_ohne_gewichte(self, netz, koerper):
        """Rolle eines Netzes ohne Hautgewichte — nach Maßen (Anteile der Körperhöhe), Material und Namen."""
        name = str(netz['name']).lower()
        boden, hoehe = self.figur(koerper)
        unten = (float(netz['min'][2]) - boden) / hoehe
        oben = (float(netz['max'][2]) - boden) / hoehe
        anteil = self.groesse(netz) / hoehe
        am_kopf = unten >= self.KOPFNAH
        if am_kopf and any(w in name for w in self.GESICHTSHAAR):
            return 'gesichtshaar'
        if am_kopf and anteil < self.MUND_MAX_M / self.REFERENZ_M and any(m in name for m in self.MUND):
            return 'mund'
        if am_kopf and anteil < self.AUGE_MAX_M / self.REFERENZ_M and 'eye' in name:
            return 'auge'
        # Ohne Gewichte nur das Alpha-Bild: eine durchsichtige Überblendung allein trägt auch Helme, Hüte und Mäntel (gemessen 10.10.2026).
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
            # Es sei denn, ein Netz trägt das HAUTMATERIAL und ist ein großer Teil der Figur: seori hat den Körper in zwei Netzen — `head` (Material
            # „body": Kopf, Schultern, Arme; 0,92 m der 1,74 m) und `head.002` (Material „sock": die Beine, 1,28 m). „Das höchste" nahm die Beine
            # ohne Kopf, die Erkennung fand keine Person („index 11 is out of bounds … size 0", 10.10.2026). Die Beine kommen dann über die
            # Körperergänzung unter der Kante (`Blendimportkoerperergaenzung`).
            figur = max(float(n['max'][2]) for n in self.netze) - min(float(n['min'][2]) for n in self.netze)
            haut = [n for n in self.netze if self._hautnetz(n) and self.hoehe(n) >= self.KOERPER_MIN_ANTEIL * figur]
            if haut:
                return max(haut, key=lambda n: (self.hoehe(n), n['punkte']))
            return max((n for n in self.netze if self.hoehe(n) >= 0.9 * hoechste), key=lambda n: n['punkte'])
        # Mindesthöhe als Anteil der Figur, nicht in Metern: Rainys Körper reicht nur von der Hüfte zum Scheitel (47 % der Figur) — auf
        # 1,75 m umgerechnet 0,82 m, unter den 1,0 m von früher; dann wurde die Hose (1,04 m) zum Körper (gemessen 10.10.2026).
        # Eine ganze 1,75-m-Figur braucht damit 0,70 m statt 1,0 m; gewählt wird weiter nach den meisten Knochen.
        mindest = self.KOERPER_MIN_ANTEIL * (max(float(n['max'][2]) for n in self.netze) - min(float(n['min'][2]) for n in self.netze))
        hoch = [n for n in self.netze if self.hoehe(n) >= mindest]
        if not hoch:
            raise ValueError('Kein Körper: kein Netz an einer Armatur ist mindestens %.1f m hoch' % mindest)
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
        boden, hoehe = self.figur(koerper)
        skala = hoehe / self.REFERENZ_M
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
        # Mehrere Frisurnetze (CC: Bang, Bun, Hair_Base, Real_Hair, Female_Angled): „<Figur> Haar" gäbe allen denselben Namen. EIN Netz bleibt „Haar".
        if sum(e['rolle'] == 'haar' for e in aus) > 1:
            for e in aus:
                if e['rolle'] == 'haar':
                    e['art'] = 'Haar %s' % str(e['name']).strip()
        return aus
