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
import unittest
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
        ziel = self.sp.pruefe(str(self.medien / 'studio_projects'
                                  / 'a.studio.json'))
        # `is_relative_to` statt `startswith`: Der Zeichenvergleich ist genau
        # der Fehler, den dieser Test verhindern soll (siehe Werkzeug
        # `pfadpraefix`) — er hat hier nichts zu suchen, auch nicht als
        # Zusicherung.
        self.assertTrue(ziel.is_relative_to(self.medien))

    def test_wurzel_selbst_wird_angenommen(self):
        """Das Verzeichnis-Listing fragt die Wurzel selbst ab — die muss durch."""
        self.assertEqual(self.sp.pruefe(str(self.medien)), self.medien)

    @unittest.skipUnless(os.name == 'nt',
                         'nur unter Windows aussagekraeftig')
    def test_gross_klein_egal_unter_windows(self):
        """A:\\Media und a:\\media sind dasselbe Verzeichnis.

        Ein String-Vergleich sieht das nicht; `normcase` schon. Auf anderen
        Systemen ist Gross-/Kleinschreibung bedeutsam, dort wird nicht geprüft."""
        # Die Bedingung steht als Dekorator: Ein `skipTest` IM Rumpf
        # sieht in der Auswertung aus wie eine bestandene Pruefung.
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

    def test_geraetename_als_dateiname_wird_abgelehnt(self):
        for roh in ('NUL', 'CON', 'COM1'):
            with self.subTest(roh=roh), self.assertRaises(PfadAbgelehnt):
                self.sp.pruefe(str(self.medien / roh))

    def test_geraetename_als_verzeichnis(self):
        """Auch MITTEN im Pfad — `…\\COM1\\datei.json` ist kein gültiges Ziel.

        Bis zum 18.08.2026 prüfte nur der letzte Pfadteil auf Gerätenamen; ein
        Gerät als Verzeichnis kam durch und scheiterte erst beim Zugriff, mit
        einem OSError statt einer klaren Ablehnung (Sparring mit Nemotron).
        """
        for roh in ('COM1', 'NUL', 'LPT1'):
            with self.subTest(roh=roh), self.assertRaises(PfadAbgelehnt):
                self.sp.pruefe(str(self.medien / roh / 'datei.json'))

    def test_datenstrom_im_namen_wird_abgelehnt(self):
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

    def test_dateiname_doppelpunkt_wird_abgelehnt(self):
        """DER FUND DER ZWEITEN SPARRING-RUNDE (13.08.2026).

        `video:1.mp4` ist unter NTFS kein Dateiname, sondern der Datenstrom
        `1.mp4` der Datei `video`. Vorher nahm `dateiname` das an. Gemessen:
        geschrieben wurde eine 0 Byte grosse Datei `video`, der Inhalt lag
        unsichtbar im Datenstrom, und der Video-Export meldete Erfolg — der
        Nutzer hätte eine leere Datei und keinen Hinweis."""
        for roh in ('video:1.mp4', 'video.mp4:versteckt', 'a:b'):
            with self.subTest(roh=roh), self.assertRaises(PfadAbgelehnt):
                SafePath.dateiname(roh, '.mp4')

    def test_vertrag_dateiname_verbietet_was_pruefe_verbietet(self):
        """Beide Methoden müssen DIESELBE Verbotsliste durchsetzen.

        Der Doppelpunkt-Fund entstand genau daraus, dass sie es nicht taten:
        `pruefe` verbot ihn, `dateiname` nicht. Ein Test je Einzelfall hätte das
        nicht gefunden — er prüft, was jemand geprüft haben WOLLTE. Dieser hier
        prüft den Vertrag der Klasse und schlägt auch dann fehl, wenn die Liste
        später um ein Zeichen wächst und nur eine der beiden Methoden es lernt."""
        for zeichen in '<>:"|?*':
            name = 'datei%sname.bvh' % zeichen
            with self.subTest(zeichen=zeichen):
                with self.assertRaises(PfadAbgelehnt):
                    SafePath.dateiname(name, '.bvh')
                with self.assertRaises(PfadAbgelehnt):
                    self.sp.pruefe(str(self.medien / name))

    def test_pfad_mit_punkt_oder_leerzeichen_am_ende(self):
        """`resolve()` behält beides, das Dateisystem schneidet es ab.

        Ohne diese Prüfung nennt die Antwort einen Pfad, den es so nie gab:
        gespeichert wird `video.mp4`, gemeldet `video.mp4.`.

        GEMESSEN (13.08.2026), weil der erste Testfall danebenlag: Ein
        Leerzeichen ganz am Ende entfernt schon das `.strip()` in `pruefe` —
        dagegen war der Wächter also längst immun. Offen waren nur der Punkt
        am Ende und Leerzeichen in einem Verzeichnisnamen mitten im Pfad."""
        for roh in (str(self.medien / 'video.mp4.'),
                    str(self.medien / 'ordner ' / 'x.json'),
                    str(self.medien / 'ordner.' / 'x.json')):
            with self.subTest(roh=roh), self.assertRaises(PfadAbgelehnt):
                self.sp.pruefe(roh)

    def test_leerzeichen_ganz_am_ende_wird_abgeschnitten_nicht_abgelehnt(self):
        """Gegenstück zum Test darüber: `.strip()` macht daraus einen gültigen
        Pfad. Das ist gewollt (Tippfehler beim Einfügen) und wird hier
        festgehalten, damit niemand es später für ein Versehen hält."""
        ziel = self.sp.pruefe(str(self.medien / 'video.mp4') + ' ')
        self.assertEqual(ziel.name, 'video.mp4')

    def test_bvh_wurzel_scheitert_verschlossen(self):
        """Zeigt die Einstellung weder auf `bvh` noch auf eine Kategorie darunter,
        muss die Wurzel VERWEIGERT werden.

        Vorher wurde nur gewarnt und `.parent` trotzdem geliefert — bei
        `…/data/animations` wäre das `…/data` gewesen, also Morphdaten, Meshes
        und Skelett zum Schreiben und Löschen freigegeben."""
        with self.settings(HUMANBODY_BVH_DIR=str(Path(settings.TOOLS_ROOT) / 'HumanBody' / 'data')):
            with self.assertRaises(PfadAbgelehnt):
                SafePath.bvh_wurzel()

    def test_bvh_wurzel_akzeptiert_beide_schreibweisen(self):
        """Sowohl `…/bvh/MocapNET` (heutige Einstellung) als auch `…/bvh`
        müssen dieselbe Wurzel ergeben."""
        erwartet = SafePath.bvh_wurzel()
        with self.settings(HUMANBODY_BVH_DIR=str(erwartet)):
            self.assertEqual(SafePath.bvh_wurzel(), erwartet)

    def test_dateiname_beginnt_nicht_mit_bindestrich(self):
        """Ein Name wie `-i.mp4` würde in einer Kommandozeile als Option gelesen.

        Der Video-Export übergibt den Pfad an ffmpeg. Heute steht das Verzeichnis
        davor und schützt; die nächste Aufrufstelle tut das vielleicht nicht."""
        for roh in ('-i.mp4', '--output.mp4', '-'):
            with self.subTest(roh=roh), self.assertRaises(PfadAbgelehnt):
                SafePath.dateiname(roh, '.mp4')
