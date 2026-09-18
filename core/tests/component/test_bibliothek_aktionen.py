# -*- coding: utf-8 -*-
"""Die drei schreibenden Bibliotheks-Aktionen antworten auf kein GET.

DER BEFUND (17.08.2026): `scan_bvh_files` war die einzige der drei ohne
Methodenschutz. Aufgefallen ist es dem Leistungstest, der sie mit einem GET
anfuhr — **35 Abfragen, 7.067 BVH-Köpfe gelesen, Datenbank geschrieben.** Ein
`<img src="/library/scan/">` auf einer fremden Seite löste damit einen vollen
Neuaufbau der Bibliothek aus.

Die `GleicherUrsprung`-Middleware fängt das nicht: Sie prüft schreibende
METHODEN, und GET gehört nicht dazu. Deshalb muss die Methode selbst stimmen.

`open_in_blender` ist der teuerste Fall der drei — ein GET darauf startet
Blender. Der Test prüft nur den Statuscode und ruft nie POST.
"""

from django.test import TestCase
from django.urls import reverse


class BibliotheksAktionenTest(TestCase):
    """GET auf eine schreibende Route ist 405, nicht 200 und nicht 302."""

    #: (Routenname, Argumente, was dahinter passiert). Über `reverse` und nicht
    #: über einen ausgeschriebenen Pfad: So bleibt der Test auch nach einer
    #: Adressänderung gültig, und der Name steht im Text — das Werkzeug
    #: `testdeckung` erkennt eine Route an ihrem Namen.
    NUR_POST = (
        ('scan_bvh', (), 'liest 7.067 Dateien und schreibt die Bibliothek'),
        ('delete_bvh', (1,), 'löscht einen Eintrag'),
        ('open_in_blender', (1,), 'startet Blender'),
    )

    def test_get_wird_abgewiesen(self):
        for name, args, wirkung in self.NUR_POST:
            with self.subTest(route=name, wirkung=wirkung):
                antwort = self.client.get(reverse(name, args=args))
                self.assertEqual(antwort.status_code, 405, wirkung)

    def test_scan_kommt_ohne_eintraege_nicht_ins_stolpern(self):
        """POST ist erlaubt und leitet auf die Liste zurück. Der Scan läuft
        gegen die echten Verzeichnisse, schreibt aber in die Test-Datenbank."""
        antwort = self.client.post(reverse('scan_bvh'))
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], '/library/')
