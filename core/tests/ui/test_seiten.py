# -*- coding: utf-8 -*-
"""UI-Tests: jede sichtbare Seite antwortet und zeigt, was sie zeigen soll.

WARUM DIESE DATEI (17.08.2026)
------------------------------
Das Werkzeug `testdeckung` hielt die URL-Tabelle gegen alle Testtexte und
meldete **28 Seiten, die in keinem einzigen Test vorkamen** — darunter die
Szene, das BVH Studio, beide Einstellungsseiten und die Webcam. Ein kaputter
Import oder ein Vorlagenfehler auf einer davon wäre erst dem Benutzer
aufgefallen.

WARUM DIE PFADE HIER AUSGESCHRIEBEN STEHEN
------------------------------------------
Eine Schleife über `get_resolver()` wäre kürzer und würde **nichts** belegen:
Sie prüft, was Django gerade registriert hat, nicht was diese Anwendung haben
SOLL. Verschwindet eine Route, verschwindet stillschweigend auch ihr Test.
Ausgeschriebene Pfade werden dagegen rot.

WARUM NICHT NUR „STATUS 200"
----------------------------
Eine Django-Seite kann mit 200 antworten und trotzdem leer sein — ein
`{% block %}`, dessen Namen die Elternvorlage nicht kennt, wird ohne Fehler
verworfen (genau das hatte am 17.08.2026 180 Vorschaubilder auf 0×0 Pixel
gesetzt). Deshalb prüft jede Zeile zusätzlich eine Zeichenkette, die nur bei
richtig gerendertem Inhalt vorkommt.
"""

from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(ALLOWED_HOSTS=['*'])
class SeitenTest(TestCase):
    """Alle Seiten ohne Parameter — Status und ein Inhaltsmerkmal."""

    #: (Pfad, Merkmal im HTML). Das Merkmal ist der Seitentitel: Er steht in
    #: der Vorlage der Seite selbst, nicht im gemeinsamen Rahmen — ein leerer
    #: Inhaltsblock fällt damit auf.
    #:
    #: Die Titel tragen seit dem 24.08.2026 die Form `HumanBody · <Seite>`;
    #: vorher hing an ihnen „— MocapNET", der Name des Projekts von früher.
    #: Das Trennzeichen gehört zum Merkmal: „Szene" allein steht auch im
    #: Seitenmenü und würde eine leere Seite durchgehen lassen.
    SEITEN = (
        ('/humanbody/config/', 'HumanBody · Konfiguration'),
        ('/humanbody/scene/', 'HumanBody · Szene'),
        ('/humanbody/scene-model/', 'HumanBody Szene - Modell'),
        ('/humanbody/animations/', 'HumanBody · Animationen'),
        ('/humanbody/theatre-studio/', 'Theatre Studio'),
        ('/humanbody/theatre/help/', 'Theatre Help'),
        ('/humanbody/rigging/help/', 'Rigging'),
        ('/humanbody/test-animation/', 'Test Animation'),
        ('/humanbody/test-character/', 'Test Charakter'),
        ('/humanbody/test-smpl/', 'SMPL Test'),
        ('/humanbody/photo-to-3d/', 'Foto To 3D'),
        ('/humanbody/photo-to-3d/jobs/', 'Photo-to-3D Jobs'),
        ('/settings/bvh-studio/', 'BVH Studio'),
        ('/settings/smpl/', 'SMPL Body'),
        ('/settings/video-to-bvh-2d/', 'Video to BVH: 2D'),
        ('/settings/video-to-bvh-3d/', 'Video to BVH: 3D'),
        ('/test/mocapnet/', 'MocapNET'),
        ('/webcam/', 'Live Webcam'),
        ('/process/VideoToBVH/', 'Video To BVH'),
        ('/process/result/', 'Result'),
        ('/process/list/', 'Verarbeitet'),
        ('/library/', 'BVH'),
    )

    #: Seiten, die absichtlich weiterleiten — mit ihrem Ziel. Ein `assertEqual`
    #: auf 200 hätte sie zu Unrecht rot gemacht, ein `assertLess(400)` hätte
    #: eine falsche Weiterleitung durchgelassen. Der Routenname steht dabei,
    #: weil ein einzelner Schrägstrich als Suchmarke zu kurz ist.
    WEITERLEITUNGEN = (
        ('dashboard', '/process/result/'),
        ('settings_videobvh', '/settings/video-to-bvh-2d/'),
    )

    def test_seiten_antworten_mit_inhalt(self):
        for pfad, merkmal in self.SEITEN:
            with self.subTest(pfad=pfad):
                antwort = self.client.get(pfad)
                self.assertEqual(antwort.status_code, 200)
                self.assertContains(antwort, merkmal)

    def test_weiterleitungen_gehen_ans_richtige_ziel(self):
        for route, ziel in self.WEITERLEITUNGEN:
            with self.subTest(route=route):
                antwort = self.client.get(reverse(route))
                self.assertEqual(antwort.status_code, 302)
                self.assertEqual(antwort['Location'], ziel)

    def test_theatre_und_bvh_studio(self):
        """Die zwei Hauptseiten des Studios — eigener Test, weil hier nicht der
        Titel das Merkmal ist, sondern das Einstiegsskript. Ohne das lädt die
        Seite mit 200 und bleibt eine leere Bühne."""
        for pfad, merkmal in (
                ('/humanbody/theatre/', 'theatre/theatre-app.js'),
                ('/humanbody/bvh-studio/', 'viewer/bvh_studio/index.js')):
            with self.subTest(pfad=pfad):
                self.assertContains(self.client.get(pfad), merkmal)

    def test_foto_seite_darf_im_eigenen_rahmen_laufen(self):
        """`photo_to_3d_page` trägt `xframe_options_sameorigin`. Ging der
        Dekorator beim Umbau auf `TemplateView` verloren, wäre die Seite im
        eigenen iframe leer geblieben (17.08.2026)."""
        antwort = self.client.get('/humanbody/photo-to-3d/')
        self.assertEqual(antwort['X-Frame-Options'], 'SAMEORIGIN')
