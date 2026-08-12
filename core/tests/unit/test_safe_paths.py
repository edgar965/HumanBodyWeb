# -*- coding: utf-8 -*-
r"""Wächter für SafePath — die Pfadprüfung der Datei-Endpunkte.

WARUM DIESER TEST EXISTIERT (12.08.2026)
----------------------------------------
Vor dem Umbau nahmen drei Endpunkte jeden Pfad an. Ein POST mit
`Content-Type: text/plain` legte Verzeichnis und Datei an beliebiger Stelle an —
ausprobiert, nicht vermutet. Der vierte Endpunkt prüfte mit
`str(pfad).startswith(str(wurzel))`, was `<media>_evil\x.bvh` durchlässt, weil
"media_evil" mit "media" beginnt.

Beide Fehler sind nicht sichtbar: Der Endpunkt antwortet freundlich mit
`{"ok": true}`. Nur ein Test merkt, wenn die Prüfung wieder aufweicht — etwa weil
jemand `is_relative_to` gegen einen neuen, schnelleren Präfixvergleich tauscht.

Die Testfälle sind die Angriffsliste aus dem Review, ergänzt um die
Windows-Sonderfälle: UNC, Gerätenamen, Datenströme, Namen mit Punkt am Ende.

Aufruf:  python manage.py test core
"""
import os
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from core.safe_paths import SafePath, PfadAbgelehnt


class SafePathTest(TestCase):
    """Prüft Annahme und Ablehnung — beides, denn ein Wächter, der alles
    ablehnt, wäre genauso kaputt wie einer, der alles durchlässt.

    `TestCase`, nicht `SimpleTestCase`: Die Wurzeln enthalten die vom Nutzer
    eingestellten Verzeichnisse, und die stehen in `AppSettings` — also in der
    Datenbank. Mit `SimpleTestCase` schlug dieser Zugriff fehl, wurde in
    `_prefs_wurzeln` protokolliert und verschluckt, und die Tests prüften
    unbemerkt eine kürzere Wurzelliste als im Betrieb gilt."""

    def setUp(self):
        self.bvh_wurzel = SafePath.bvh_wurzel()
        self.medien = Path(settings.MEDIA_ROOT).resolve()
        # Eine Wurzel ohne Nutzer-Einstellungen: so sind die Fälle unabhängig
        # davon, was in AppSettings steht.
        self.sp = SafePath([self.medien])

    # ------------------------------------------------------------- Muss erlaubt

    def test_pfad_in_der_wurzel_wird_angenommen(self):
        ziel = self.sp.pruefe(str(self.medien / 'studio_projects' / 'a.studio.json'))
        self.assertTrue(str(ziel).startswith(str(self.medien)))

    def test_wurzel_selbst_wird_angenommen(self):
        """Das Verzeichnis-Listing fragt die Wurzel selbst ab — die muss durch."""
        self.assertEqual(self.sp.pruefe(str(self.medien)), self.medien)

    def test_gross_klein_egal_unter_windows(self):
        """A:\\Media und a:\\media sind dasselbe Verzeichnis.

        Ein String-Vergleich sieht das nicht; `normcase` schon. Auf anderen
        Systemen ist Gross-/Kleinschreibung bedeutsam, dort wird nicht geprüft."""
        if os.name != 'nt':
            self.skipTest('nur unter Windows aussagekräftig')
        gemischt = str(self.medien).upper() + os.sep + 'x.json'
        self.assertIsNotNone(self.sp.pruefe(gemischt))

    def test_bvh_kategorien_erlaubt(self):
        """Die Kategorie-Ordner (Aist, Bandai, Mixamo …) müssen beschreibbar bleiben."""
        ziel = SafePath([self.bvh_wurzel]).pruefe(str(self.bvh_wurzel / 'Aist' / 'x.bvh'))
        self.assertTrue(ziel.is_relative_to(self.bvh_wurzel))

    # ----------------------------------------------------------- Muss abgelehnt

    def test_praefix_falle(self):
        """DER FEHLER DER ALTEN PRÜFUNG: Nachbarverzeichnis mit gleichem Anfang."""
        with self.assertRaises(PfadAbgelehnt):
            self.sp.pruefe(str(self.medien) + '_evil' + os.sep + 'x.json')

    def test_aufwaerts_aus_der_wurzel(self):
        with self.assertRaises(PfadAbgelehnt):
            self.sp.pruefe(str(self.medien / '..' / '..' / 'evil.json'))

    def test_fremder_absoluter_pfad(self):
        with self.assertRaises(PfadAbgelehnt):
            self.sp.pruefe(r'C:\Windows\System32\evil.json')

    def test_unc_pfad(self):
        """UNC vor jedem Dateisystemzugriff ablehnen — sonst baut Windows SMB auf."""
        for roh in (r'\\attacker\share\evil.json', '//attacker/share/evil.json',
                    r'\\?\C:\Windows\evil.json'):
            with self.subTest(roh=roh), self.assertRaises(PfadAbgelehnt):
                self.sp.pruefe(roh)

    def test_geraetename(self):
        for roh in ('NUL', 'CON', 'COM1'):
            with self.subTest(roh=roh), self.assertRaises(PfadAbgelehnt):
                self.sp.pruefe(str(self.medien / roh))

    def test_datenstrom(self):
        """NTFS-Datenstrom: die Datei landet nicht als Datei."""
        with self.assertRaises(PfadAbgelehnt):
            self.sp.pruefe(str(self.medien / 'x.json') + ':versteckt')

    def test_leerer_pfad(self):
        for roh in ('', '   ', None):
            with self.subTest(roh=roh), self.assertRaises(PfadAbgelehnt):
                self.sp.pruefe(roh)

    def test_fehlermeldung_nennt_den_pfad_nicht(self):
        """Die Absage darf nicht verraten, was auf der Platte liegt.

        Vorher stand der volle Pfad in der Antwort (`File not found: {fp}`) —
        das ist eine Auskunft über fremde Verzeichnisse. Er gehört ins Protokoll."""
        try:
            self.sp.pruefe(r'C:\Windows\System32\config\SAM')
            self.fail('haette abgelehnt werden muessen')
        except PfadAbgelehnt as e:
            self.assertNotIn('System32', str(e))
            self.assertNotIn('SAM', str(e))

    # --------------------------------------------------------------- Dateinamen

    # ------------------------------------------------- Zuschnitt der Wurzeln

    def test_projektwurzel_gibt_nicht_das_ganze_arbeitsverzeichnis_frei(self):
        """TOOLS_ROOT darf keine Wurzel sein.

        Der erste Entwurf hatte sie drin; die Live-Prüfung schrieb daraufhin
        anstandslos nach `A:\\3DTools\\evil.json`. Damit wären auch
        `ui/settings.py`, `.git/` und die `.npy`-Morphdaten beschreibbar
        gewesen (12.08.2026)."""
        sp = SafePath.fuer_studio_projekte()
        tools = Path(settings.TOOLS_ROOT).resolve()
        self.assertNotIn(tools, sp.wurzeln,
                         'TOOLS_ROOT ist als Wurzel eingetragen — das hebt den Schutz auf')
        for roh in (str(tools / 'evil.studio.json'),
                    str(tools / 'HumanBodyWeb' / 'ui' / 'settings.py'),
                    str(tools / 'HumanBodyWeb' / 'media_evil' / 'x.studio.json')):
            with self.subTest(roh=roh), self.assertRaises(PfadAbgelehnt):
                sp.pruefe(roh)

    def test_studio_standardverzeichnis_ist_erlaubt(self):
        """Das Vorgabe-Verzeichnis der Projekte muss beschreibbar bleiben."""
        sp = SafePath.fuer_studio_projekte()
        ziel = sp.pruefe(str(SafePath.projekt_standard() / 'a.studio.json'))
        self.assertTrue(ziel.is_relative_to(SafePath.projekt_standard().resolve()))

    # --------------------------------------------------------------- Dateinamen

    def test_dateiname_ohne_pfadanteil_wird_angenommen(self):
        self.assertEqual(SafePath.dateiname('szene.mp4'), 'szene.mp4')

    def test_dateiname_endung_wird_ergaenzt(self):
        self.assertEqual(SafePath.dateiname('szene', '.mp4'), 'szene.mp4')
        self.assertEqual(SafePath.dateiname('szene.MP4', '.mp4'), 'szene.MP4')

    def test_dateiname_mit_pfadanteil_wird_abgelehnt(self):
        """Nicht zurechtschneiden, sondern ablehnen — sonst liegt die Datei
        woanders als der angezeigte Name vermuten lässt."""
        for roh in (r'..\..\evil.mp4', 'unter/evil.mp4', r'C:\evil.mp4', '..', '.'):
            with self.subTest(roh=roh), self.assertRaises(PfadAbgelehnt):
                SafePath.dateiname(roh, '.mp4')

    def test_dateiname_mit_punkt_am_ende(self):
        """Windows schneidet den Punkt ab — Anzeige und Platte gehen auseinander."""
        with self.assertRaises(PfadAbgelehnt):
            SafePath.dateiname('szene.mp4.')

    def test_dateiname_geraet(self):
        with self.assertRaises(PfadAbgelehnt):
            SafePath.dateiname('NUL.mp4')
