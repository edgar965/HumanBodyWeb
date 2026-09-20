# -*- coding: utf-8 -*-
u"""Die Arme gehen nicht durch das Kleid — Dancing Queen Dress auf HumanBody UND
auf Ursula (Genesis 9), in der Haltung der Idle-Animation.

Edgar, 20.09.2026, mit dem Bild einer HumanBody-Figur im roten Kleid, der Rock
steht waagerecht ab, die hängenden Arme laufen hindurch: „Die Arme gehen ins
Kleid. verstehst du das Problem??? das kleid muss nach unten animieren!!!" —
„auch die ursula (genesis) mit diesem Kleid und dieser Idle animation
animiert falsch. Mach einen testcase auch dafür und checke ob die Arme durch
das Kleid gehen, das dürfen sie nicht!!"

WAS GEMESSEN WIRD: Im Idle hängen die Arme neben dem Körper. Der hängende Arm
wird aus der Figur selbst gebaut — Schulter = die Armpunkte am Rumpfansatz
(`segmente()['left_arm']`), Länge = der fernste Armpunkt von der Schulter —
und senkrecht nach unten gelegt. Für 20 Punkte je Arm zwischen 30 % und 90 %
der Armlänge (ohne die Fingerspitzen, siehe `BIS`) gilt: In seinem Höhenband (± 2 cm) und in seiner
Richtung von der Körperachse (± 12°) darf der Stoff nicht WEITER außen liegen
als der Arm — sonst steckt der Arm im Kleid. 2 cm Rand, damit ein Saum, der
den Arm streift, nicht zählt. Die Körperachse je Höhe ist der Schwerpunkt der
Figurpunkte ohne Arme (unter dem Schritt: die Mitte zwischen den Beinen).

WAS DER BROWSER ZEIGT, nicht was der Server liefert:
Der Stoffschwung läuft im Worker (`gemeinsam/stoffpendel.js`) - auf Ursula
seit dem 18.09., auf HumanBody seit dem 20.09.2026 (vorher warf
`G9kleidhumanbody` den Stoff weg, weil die Käfighaut Daz-Knochen nannte).
Hier läuft dieselbe Rechnung in Node auf dem Käfig der Antwort, 3 s mit der
Ruhelage als Ziel (Idle ≈ Stand), und gemessen wird das ERGEBNIS; davor die
gehäutete Antwort als Vergleichszahl. Die Käfigpunkte allein sagen, ob der
Rock absteht; die feineren Browserpunkte hängen über die Unterteilungsmatrix
daran. Gemessen am 20.09.2026, vor dem Fix: HumanBody 33 von 40 Armproben im
Kleid (42,8 cm tief), Ursula gehäutet 31 von 40.

Die Haltung der Idle-Animation ist eine Näherung (Arme senkrecht); was der
Browser wirklich zeigt, misst `scene/kleidungsprobe.js` (`__stoffschwung.probe`)
in Edgars Chrome. Ohne Körperkapseln gerechnet: ob der Rock in die Beine
fällt, sagt dieser Test nicht - nur, ob er die Arme freigibt.

Sabotage-Gegenprobe (wenn grün): `RAND` auf −1,0 → beide Fälle rot (jeder
Arm „steckt"); `haengender_arm` mit Länge 0 → beide grün ohne Probe — deshalb
verlangt jeder Fall mindestens 30 Armproben.

LongRunner: zwei Übertragungen und ein Stoffschwung in Node (rund 30–60 s).
Ohne Daz-Bibliothek oder HumanBody-Daten übersprungen.
"""
import base64
import json
import math
import unittest
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from Genesis9.garderobe import G9garderobe
from Genesis9.pfade import G9pfade
from scipy.spatial import cKDTree

from ..jsmodul import Jsmodul
from ..unit._humanbodypfad import Humanbodypfad
from ..unit._pruefablage import Pruefablage

Humanbodypfad.setzen()
Humanbodypfad.assets()

STOFFPENDEL = Jsmodul('gemeinsam', 'stoffpendel.js')

#: Der Stoffschwung in Node: Käfig, Freiheit und Kanten der Antwort aus einer
#: JSON-Datei (der Käfig hat 19k Punkte - als Argument wäre die Befehlszeile
#: zu lang, WinError 206), Ziel = Ruhelage, Ergebnis in dieselbe Datei.
SCHWUNG = """
import { readFileSync, writeFileSync } from 'node:fs';
const { Stoffpendel: S } = await import(MODUL);
const d = JSON.parse(readFileSync(%(datei)s, 'utf8'));
const ruhe = Float32Array.from(d.ruhe), frei = Float32Array.from(d.frei);
const p = S.ausKanten(ruhe, d.kanten, frei);
const ziel = Float32Array.from(ruhe);
let zurueck = 0;
for (let i = 0; i < d.bilder; i++) if (p.bild(ziel, 1 / 30).zurueckgesetzt) zurueck++;
writeFileSync(%(datei)s, JSON.stringify({ x: Array.from(p.x) }));
console.log(JSON.stringify({ zurueckgesetzt: zurueck, punkte: p.n, kanten: p.kanten.a.length,
                             biegung: p.biegung ? p.biegung.a.length : 0, anker: !!p.anker,
                             auslenkung_cm: +(p.auslenkung(ziel) * 100).toFixed(1) }));
"""


def bibliothek_da():
    try:
        return G9pfade.vorhanden() and bool(G9pfade.people_fremd())
    except Exception:  # noqa: BLE001 — ohne Bibliothek: kein Test
        return False


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek mit Genesis 9 fehlt')
class KleidArmeFrei(SimpleTestCase):
    databases = set()
    KLEID = 'dancing_queen_dress'
    BAUART = 'Female_Caucasian'
    URSULA = 'p3d_ursula'
    #: Höhenband um einen Armpunkt, Meter.
    BAND = 0.02
    #: Richtungssektor um den Armpunkt, Grad.
    SEKTOR = 12.0
    #: So weit muss der Stoff AUSSERHALB des Arms liegen, damit der Arm „im Kleid" steckt.
    RAND = 0.02
    #: Armproben je Arm, zwischen `AB` und `BIS` der Armlänge (Schulter -> Fingerspitze).
    #: Die letzten 10 % sind die Fingerspitzen: Sie hängen auf Höhe des Saums und
    #: streifen ihn bei einem Glockenrock immer - gemessen auf HumanBody nach dem
    #: Fix 2-4 cm an drei Proben auf 0,68 m. Das ist Berührung, nicht „der Arm
    #: geht durch das Kleid" (vorher: 43 cm auf Hüfthöhe).
    PROBEN = 20
    AB = 0.3
    BIS = 0.9
    #: Stoffschwung bis zur Ruhe (Genesis), Sekunden.
    SEKUNDEN = 3.0
    #: So viele Stoffpunkte braucht ein Sektor, damit dort überhaupt Stoff ist.
    MINDESTENS = 5

    # ------------------------------------------------------------ Helfer

    @staticmethod
    def feld(text, typ):
        return np.frombuffer(base64.b64decode(text), dtype=typ)

    @classmethod
    def punkte(cls, teil):
        return cls.feld(teil['vertices'], np.float32).reshape(-1, 3).astype(np.float64)

    @staticmethod
    def haengender_arm(figur, arm, rumpf):
        u"""(Schulter, Länge) aus den Armpunkten der Figur in Ruhe.

        Die Schulter ist der Ansatz des Arms am Rumpf: die 5 % Armpunkte, die
        dem Rumpf am nächsten liegen — gilt für A- wie T-Pose (die „obersten"
        Armpunkte lägen in der T-Pose über die ganze Armlänge verteilt).
        Die Länge ist der fernste Armpunkt von dort, die Fingerspitze.
        """
        p = np.asarray(figur)[np.asarray(arm, dtype=np.int64)]
        abstand, _ = cKDTree(rumpf).query(p, workers=-1)
        ansatz = p[abstand <= np.percentile(abstand, 5)]
        schulter = ansatz.mean(axis=0)
        laenge = float(np.linalg.norm(p - schulter, axis=1).max())
        return schulter, laenge

    @classmethod
    def armproben(cls, figur, segmente, rumpf):
        u"""Je Arm `PROBEN` Punkte des senkrecht hängenden Arms."""
        proben = []
        for seite in ('left_arm', 'right_arm'):
            arm = segmente.get(seite) or []
            if len(arm) < 50:
                continue
            schulter, laenge = cls.haengender_arm(figur, arm, rumpf)
            for s in np.linspace(cls.AB * laenge, cls.BIS * laenge, cls.PROBEN):
                proben.append((seite, schulter - np.array([0.0, s, 0.0])))
        return proben

    @classmethod
    def im_stoff(cls, punkt, achse, stoff):
        u"""Wie tief `punkt` im Stoff steckt (m) — oder None, wenn außen oder kein Stoff."""
        band = stoff[np.abs(stoff[:, 1] - punkt[1]) < cls.BAND]
        if len(band) < cls.MINDESTENS:
            return None
        dx, dz = punkt[0] - achse[0], punkt[2] - achse[2]
        r_arm = math.hypot(dx, dz)
        winkel = math.atan2(dz, dx)
        w = np.arctan2(band[:, 2] - achse[2], band[:, 0] - achse[0])
        diff = np.abs((w - winkel + math.pi) % (2 * math.pi) - math.pi)
        sektor = band[diff < math.radians(cls.SEKTOR)]
        if len(sektor) < cls.MINDESTENS:
            return None
        r_stoff = float(np.hypot(sektor[:, 0] - achse[0], sektor[:, 2] - achse[2]).max())
        tiefe = r_stoff - r_arm
        return tiefe if tiefe > cls.RAND else None

    @classmethod
    def steckende(cls, stoff, figur, segmente):
        u"""[(Seite, Höhe, Tiefe)] — jede Armprobe, die im Stoff steckt."""
        figur = np.asarray(figur)
        arme = set()
        for seite in ('left_arm', 'right_arm'):
            arme.update(int(i) for i in (segmente.get(seite) or []))
        ohne_arme = np.ones(len(figur), dtype=bool)
        ohne_arme[sorted(arme)] = False
        rumpf = figur[ohne_arme]
        aus, proben = [], cls.armproben(figur, segmente, rumpf)
        for seite, p in proben:
            koerper = rumpf[np.abs(rumpf[:, 1] - p[1]) < cls.BAND]
            if len(koerper) < 20:
                continue
            achse = koerper.mean(axis=0)
            tiefe = cls.im_stoff(p, achse, stoff)
            if tiefe is not None:
                aus.append((seite, float(p[1]), tiefe))
        return aus, len(proben)

    def bezug_pruefen(self, stoff, figur, name):
        u"""Kleid und Figur müssen im selben Bezug liegen — sonst misst der Test Unsinn."""
        figur = np.asarray(figur)
        hoehe = float(figur[:, 1].max() - figur[:, 1].min())
        oben = float(np.percentile(stoff[:, 1], 99))
        self.assertTrue(figur[:, 1].min() + 0.4 * hoehe < oben < figur[:, 1].min() + 0.95 * hoehe,
                        '%s: Kleidoberkante %.2f m, Figur %.2f … %.2f m — nicht derselbe Bezug'
                        % (name, oben, figur[:, 1].min(), figur[:, 1].max()))

    def meldung(self, name, steckende, proben, zusatz=''):
        tiefste = max(steckende, key=lambda e: e[2]) if steckende else None
        if not tiefste:
            return '%s: 0 von %d Armproben im Kleid%s.' % (name, proben, zusatz)
        return ('%s: %d von %d Armproben stecken im Kleid%s — tiefste %.1f cm (%s, Höhe %.2f m). '
                'Die Arme gehen durch das Kleid; der Rock hängt nicht nach unten.'
                % (name, len(steckende), proben, zusatz, tiefste[2] * 100, tiefste[0], tiefste[1]))

    # ------------------------------------------------ was der Browser zeigt

    def im_browser(self, antwort, name):
        u"""Die Stoffpunkte, wie der Browser sie zeigt: dForce-Teile nach `SEKUNDEN`
        Stoffschwung in Node (Ziel = Ruhelage), die anderen gehäutet.
        Gibt (Punkte, Hinweise)."""
        from Genesis9.stoff import G9stoff
        teile = [(f, lage) for f, lage in G9garderobe.teile(self.KLEID)
                 if getattr(f, 'ART', None) != 'strang']
        self.assertEqual(len(teile), len(antwort['teile']),
                         '%s: Teile der Antwort ≠ Teile des Stücks' % name)
        geschwungen, hinweise = [], []
        for (folger, _lage), teil in zip(teile, antwort['teile'], strict=True):
            if not teil.get('stoff'):
                geschwungen.append(self.punkte(teil))
                hinweise.append('%s ohne Stoffschwung' % teil['name'])
                continue
            ruhe = self.feld(teil['stoff']['kaefig'], np.float32).reshape(-1, 3)
            frei = self.feld(teil['stoff']['frei'], np.float32)
            kanten = np.asarray(G9stoff.kanten(folger.polys), dtype=np.int64).ravel()
            daten = json.dumps({'ruhe': [round(float(v), 5) for v in ruhe.ravel()],
                                'frei': [round(float(v), 4) for v in frei],
                                'kanten': [int(v) for v in kanten],
                                'bilder': int(self.SEKUNDEN * 30)})
            with Pruefablage.datei(daten, endung='.json', vorsatz='stoff_') as pfad:
                ausgabe = STOFFPENDEL.laufen(SCHWUNG % {'datei': json.dumps(pfad)})
                x = json.loads(Path(pfad).read_text(encoding='utf-8'))['x']
            if ausgabe['zurueckgesetzt']:
                hinweise.append('%s: %d Bilder zurückgesetzt' % (teil['name'], ausgabe['zurueckgesetzt']))
            geschwungen.append(np.asarray(x, dtype=np.float64).reshape(-1, 3))
            hinweise.append('%s: %d Käfigpunkte, %d Kanten, %d Biegungen, Anker %s, '
                            'Auslenkung nach %.0f s %.1f cm'
                            % (teil['name'], ausgabe['punkte'], ausgabe['kanten'], ausgabe['biegung'],
                               'ja' if ausgabe['anker'] else 'NEIN', self.SEKUNDEN, ausgabe['auslenkung_cm']))
        return np.vstack(geschwungen), hinweise

    def pruefen(self, antwort, figur, segmente, name):
        u"""Gehäutet messen (das erste Bild), dann wie der Browser zeigt - und melden."""
        gehaeutet = np.vstack([self.punkte(teil) for teil in antwort['teile']])
        self.bezug_pruefen(gehaeutet, figur, name)
        vorher, _ = self.steckende(gehaeutet, figur, segmente)
        stoff, hinweise = self.im_browser(antwort, name)
        steckende, proben = self.steckende(stoff, figur, segmente)
        self.assertGreaterEqual(proben, 30, 'zu wenige Armproben')
        zusatz = '; gehäutet, vor dem Schwung: %d; %s' % (len(vorher), ', '.join(hinweise))
        titel = '%s (nach %.0f s Stoffschwung)' % (name, self.SEKUNDEN)
        meldung = self.meldung(titel, steckende, proben, zusatz)
        print(' ' + meldung)
        self.assertEqual(steckende, [], meldung)

    # ------------------------------------------------------------ 1. HumanBody

    def test_1_humanbody_die_arme_gehen_nicht_durch_das_kleid(self):
        from GarmentCode.koerperdienst import Garmentkoerper

        from core.api.g9kleidhumanbody import G9kleidhumanbody
        from core.dienste.g9aufhumanbody import G9aufhumanbody
        traeger = G9aufhumanbody('female', self.BAUART, {}, {})
        figur = traeger.figur()['punkte']
        segmente = Garmentkoerper.segmente('female')
        self.assertTrue(segmente.get('left_arm'), 'HumanBody ohne Armsegment')
        rumpf = {'figurart': 'humanbody', 'geschlecht': 'female', 'bauart': self.BAUART,
                 'morphs': {}, 'meta': {}}
        antwort = G9kleidhumanbody.antwort(self.KLEID, G9garderobe.eintrag(self.KLEID) or {}, rumpf)
        self.assertIsInstance(antwort, dict, getattr(antwort, 'content', antwort))
        # Die Käfighaut muss Rigify-Knochen nennen - sonst startet der Worker im Browser nie.
        im_skelett = {k['name'] for k in json.loads(
            (Path(settings.HUMANBODY_DATA_DIR) / 'def_skeleton.json').read_text(encoding='utf-8'))['bones']}
        for teil in antwort['teile']:
            if teil.get('stoff'):
                knochen = set(teil['stoff'].get('hautgewichte', {}).get('knochen') or [])
                self.assertTrue(knochen, '%s: Käfig ohne Haut' % teil['name'])
                self.assertTrue(knochen <= im_skelett,
                                '%s: %s' % (teil['name'], sorted(knochen - im_skelett)[:5]))
        self.pruefen(antwort, figur, segmente, 'HumanBody')

    # --------------------------------------------------------------- 2. Ursula

    def test_2_ursula_die_arme_gehen_nicht_durch_das_kleid(self):
        from core.api.g9garderobe import G9garderobeapi
        from core.dienste.g9garmentfigur import G9garmentfigur
        rumpf = {'figur': self.URSULA, 'regler': {}, 'variante': '', 'stil': [], 'regler_stueck': {},
                 'pose': '', 'ausdruck': '', 'griffe': {}, 'getragen': [], 'rang': 0}
        antwort = G9garderobeapi._kleid(self.KLEID, G9garderobe.eintrag(self.KLEID) or {}, rumpf)
        self.assertIsInstance(antwort, dict, getattr(antwort, 'content', antwort))
        g9 = G9garmentfigur({})
        figur, segmente = g9.punkte(), g9.segmente()
        self.assertTrue(segmente.get('left_arm'), 'Genesis ohne Armsegment')
        self.pruefen(antwort, figur, segmente, 'Ursula')
