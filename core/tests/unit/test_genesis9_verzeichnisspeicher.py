# -*- coding: utf-8 -*-
u"""Verzeichnislisten im Arbeitsspeicher und Bestandsschluessel ohne `pathlib` (`G9verzeichnisspeicher`, 10.10.2026).

Edgar: „es kann doch nicht sein, dass ein Modell mehr als 1 h braucht, sieh nach" — „arbeite mehr mit dem RAM, speichere mehr Daten in den
RAM, bevor du viel liest". Gemessen (`ProjektTemp/_wegwerf/blendimport_massstab/lesen_profil.py`): ein Neuaufbau der 672 Garderobe-Eintraege
kostete 58 s, fast alles Pfadverwaltung (`relative_to`, `sorted(Path)`, je Stueck den ganzen Herstellerordner lesen); 23 mal je Import.
Jetzt 5–9 s, und `folger` je Stueck 0,9–2,6 s statt 4,7–11,6 s. **Die Schluessel bleiben bitgleich** — sonst baute jede Ablage einmal neu.

Kunstdaten im Ordner `_wegwerf`, beide Bibliotheken per Umgebung umgelenkt. Die alte Rechnung steht als Pruefstueck (`alt`) darin:

1. `G9bestand.schluessel` = alte Rechnung — mit und ohne Aufnahme, mit Namen, die als Zeichenkette anders sortieren als `Path`
   (`A b/x` kommt nach `a/x`) und mit gemischter Gross-/Kleinschreibung.
2. `G9bestand.ueber` (Dateien UND Ordner) = alte Rechnung ueber deren Vereinigung, auch mit einer Datei, die in beiden steht.
3. `G9verzeichnisspeicher.dateien` = alle Dateien von `rglob('*')`.
4. Die Aufnahme ist ein Abbild: eine Datei, die nach dem ersten Lesen entsteht, sieht sie nicht — danach schon.
5. `gemerkt` rechnet mit Aufnahme einmal je Schluessel, ohne jedes Mal.
6. `G9dson.vergessen_eigene` behaelt die Dokumente der Daz-Bibliothek und verwirft die der eigenen und fremden.
7. `G9pfade.wurzel_von` = `relative_to` (Gross-/Kleinschreibung, die Wurzel selbst, Nachbarordner mit gleichem Anfang).

Sabotage: in `G9bestand._ordnung` die ganze Zeichenkette statt der Teile sortieren -> Fall 1 und 2 rot; in `hashen` nicht zusammenfuehren, sondern
aneinanderhaengen -> Fall 2 rot; in `gemerkt` nie merken -> Fall 5 rot; `vergessen_eigene` ohne Auswahl -> Fall 6 rot.

Nicht gelaufen (Stand 10.10.2026) — laeuft nur auf Ansage. Die Gegenprobe an echten Daten steht in
`ProjektTemp/_wegwerf/blendimport_massstab/schluessel_pruefen.py` (gelaufen: Gesamtliste, Morph-Ablage, 85 Stuecke, `wurzel_von` — alles bitgleich).
"""
import hashlib
import os
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.bestand import G9bestand
from Genesis9.dson import G9dson
from Genesis9.pfade import G9pfade
from Genesis9.verzeichnisspeicher import G9verzeichnisspeicher

WEGWERF = Path(__file__).resolve().parent / '_wegwerf'


def alt(dateien, wurzel=None):
    u"""`G9bestand.schluessel` vor dem 10.10.2026."""
    h = hashlib.sha1()
    for pfad in sorted(Path(p) for p in dateien):
        try:
            st = pfad.stat()
        except OSError:
            continue
        rel = pfad.relative_to(wurzel) if wurzel else pfad
        h.update(('%s|%d|%d\n' % (rel.as_posix(), st.st_size, int(st.st_mtime))).encode('utf-8'))
    return h.hexdigest()[:16]


def schreiben(pfad, inhalt='x'):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(inhalt, encoding='utf-8')
    return pfad


class Verzeichnisspeicher(SimpleTestCase):

    def _wurzel(self):
        WEGWERF.mkdir(exist_ok=True)
        ordner = tempfile.TemporaryDirectory(dir=WEGWERF)
        self.addCleanup(ordner.cleanup)
        return Path(ordner.name)

    def _baum(self):
        u"""Namen, die als Zeichenkette anders sortieren als als `Path` (`A b` vor `a` — und umgekehrt), gemischte Schreibweise, Unterordner."""
        wurzel = self._wurzel()
        return wurzel, [schreiben(wurzel / n, 'x' * i) for i, n in enumerate(
            ['A b/x.txt', 'a/x.txt', 'a-b/x.txt', 'A/Y.txt', 'a/Sub/Z.dsf', 'Ünï/ü.duf', 'b.txt', 'B C/d e.txt'])]

    def test_1_schluessel_ist_bitgleich_mit_der_alten_rechnung(self):
        wurzel, dateien = self._baum()
        erwartet = alt(dateien, wurzel)
        self.assertEqual(G9bestand.schluessel(dateien, wurzel), erwartet)
        with G9verzeichnisspeicher.aufnahme():
            self.assertEqual(G9bestand.schluessel(dateien, wurzel), erwartet, 'mit Aufnahme')
        self.assertEqual(G9bestand.schluessel(dateien), alt(dateien), 'ohne Wurzel')
        self.assertEqual(G9bestand.schluessel([str(d).replace('\\', '/') for d in dateien], wurzel), erwartet, 'Schreibweise mit /')
        self.assertEqual(G9bestand.schluessel([wurzel / 'gibt-es-nicht.txt'] + dateien, wurzel), erwartet, 'fehlende Datei wird uebergangen')

    def test_2_ueber_ordner_und_dateien_ist_bitgleich_mit_der_vereinigung(self):
        wurzel, dateien = self._baum()
        einzeln = [dateien[6], dateien[1]]            # b.txt, a/x.txt (steht auch im Ordner `a`)
        ordner = [wurzel / 'a', wurzel / 'A b']
        vereinigung = list(einzeln) + [p for o in ordner for p in o.rglob('*') if p.is_file()]
        erwartet = alt(vereinigung, wurzel)
        for aufnahme in (False, True):
            if aufnahme:
                with G9verzeichnisspeicher.aufnahme():
                    schluessel, anzahl = G9bestand.ueber(einzeln, ordner, wurzel)
                    zweites, _ = G9bestand.ueber(einzeln, ordner, wurzel)
                self.assertEqual(zweites, schluessel, 'aus dem Speicher dasselbe')
            else:
                schluessel, anzahl = G9bestand.ueber(einzeln, ordner, wurzel)
            self.assertEqual(schluessel, erwartet, 'Aufnahme' if aufnahme else 'von der Platte')
            self.assertEqual(anzahl, len(vereinigung))
        self.assertEqual(G9bestand.ueber([], [], wurzel), (alt([], wurzel), 0), 'leer: gleicher Schluessel wie vorher, Anzahl 0')

    def test_3_dateien_sind_alle_dateien_von_rglob(self):
        wurzel, _dateien = self._baum()
        erwartet = {str(p) for p in wurzel.rglob('*') if p.is_file()}
        self.assertEqual(set(G9verzeichnisspeicher.dateien(wurzel)), erwartet)
        with G9verzeichnisspeicher.aufnahme():
            self.assertEqual(set(G9verzeichnisspeicher.dateien(wurzel)), erwartet)
        self.assertEqual(G9verzeichnisspeicher.dateien(wurzel / 'gibt-es-nicht'), [])

    def test_4_die_aufnahme_ist_ein_abbild(self):
        wurzel, _dateien = self._baum()
        with G9verzeichnisspeicher.aufnahme():
            vorher = {n for n, *_ in G9verzeichnisspeicher.liste(wurzel / 'a')}
            schreiben(wurzel / 'a' / 'neu.txt')
            innen = {n for n, *_ in G9verzeichnisspeicher.liste(wurzel / 'a')}
        aussen = {n for n, *_ in G9verzeichnisspeicher.liste(wurzel / 'a')}
        self.assertNotIn('neu.txt', vorher)
        self.assertEqual(innen, vorher, 'innerhalb der Aufnahme bleibt es beim Abbild')
        self.assertIn('neu.txt', aussen, 'danach liest alles wieder von der Platte')

    def test_5_gemerkt_rechnet_mit_aufnahme_einmal(self):
        aufrufe = []

        def rechnen():
            aufrufe.append(1)
            return len(aufrufe)

        with G9verzeichnisspeicher.aufnahme():
            self.assertEqual([G9verzeichnisspeicher.gemerkt(('k',), rechnen) for _ in range(3)], [1, 1, 1])
        self.assertEqual(len(aufrufe), 1)
        self.assertEqual([G9verzeichnisspeicher.gemerkt(('k',), rechnen) for _ in range(2)], [2, 3], 'ohne Aufnahme jedes Mal neu')
        with G9verzeichnisspeicher.aufnahme():
            self.assertEqual(G9verzeichnisspeicher.gemerkt(('k',), rechnen), 4, 'eine neue Aufnahme beginnt leer')

    def _bibliotheken(self):
        wurzel = self._wurzel()
        daz, eigen = wurzel / 'daz', wurzel / 'eigen'
        daz.mkdir()
        eigen.mkdir()
        for name, wert in ((G9pfade.UMGEBUNG, str(daz)), (G9pfade.UMGEBUNG_EIGENE, str(eigen))):
            patch = mock.patch.dict(os.environ, {name: wert})
            patch.start()
            self.addCleanup(patch.stop)
        return daz, eigen

    def test_6_vergessen_eigene_behaelt_nur_die_daz_dokumente(self):
        daz, eigen = self._bibliotheken()
        fremd = self._wurzel() / 'woanders.duf'
        # Die Schluessel von `G9dson._gemerkt` sind aufgeloeste Pfade (`resolve()`).
        gemerkt = {str((daz / 'data' / 'a.dsf').resolve()): 'daz', str((eigen / 'data' / 'b.dsf').resolve()): 'eigen',
                   str(fremd.resolve()): 'fremd'}
        with mock.patch.dict(G9dson._gemerkt, gemerkt, clear=True):
            G9dson.vergessen_eigene()
            self.assertEqual(list(G9dson._gemerkt.values()), ['daz'])

    def test_7_wurzel_von_wie_relative_to(self):
        daz, eigen = self._bibliotheken()
        faelle = [daz, daz / 'People' / 'x.duf', eigen, eigen / 'data', Path(str(daz).upper()) / 'X', Path(str(eigen).lower()) / 'Y',
                  Path(str(daz) + ' Kopie') / 'x', Path(str(eigen) + '2') / 'x', self._wurzel() / 'ganz-woanders']

        def erwartet(pfad):
            for wurzel in (daz, eigen):
                try:
                    Path(pfad).relative_to(wurzel)
                    return wurzel
                except ValueError:
                    continue
            return daz
        for pfad in faelle:
            self.assertEqual(G9pfade.wurzel_von(pfad), erwartet(pfad), str(pfad))
            with G9verzeichnisspeicher.aufnahme():
                self.assertEqual(G9pfade.wurzel_von(pfad), erwartet(pfad), 'mit Aufnahme: %s' % pfad)
