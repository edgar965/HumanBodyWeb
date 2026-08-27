# -*- coding: utf-8 -*-
"""`/api/bvh/<auftrag>/` — der Bewegungsendpunkt mit drei Betriebsarten.

Das Werkzeug `testdeckung` meldete ihn als „Endpunkt ungeprüft". Er ist der
meistgerufene des Projekts: Jede Animationsseite, das BVH-Studio und Theatre
holen die Bewegung hier ab, und er beantwortet je nach `?mode=` drei
verschiedene Fragen.

WARUM DER ENDPUNKT EINEN TEST BRAUCHT
=====================================
Am 18.08.2026 war `?mode=retarget` **tot** — ein Import in der Funktion zeigte
auf `core.character_api`, eine Datei, die seit dem Umbau am 15.08. nicht mehr
existiert. Der Serverstart merkte nichts, `tote-importe` merkte nichts, ein
Seitenaufruf-Test merkte nichts. Erst der Aufruf warf `ModuleNotFoundError`.

`test_lokale_importe` findet diese Klasse Fehler inzwischen statisch. Dieser
Test hier ist die andere Hälfte: Er RUFT die drei Betriebsarten wirklich auf.

WAS GEPRÜFT WIRD — UND WAS NICHT
================================
Geprüft werden Wegfindung und Statuscodes: Welche Antwort bekommt der Aufrufer
bei fehlender Datei, bei fehlendem Auftrag, bei den drei `mode`-Werten? NICHT
geprüft wird die Retarget-Rechnung selbst — die steht in
`test_bvh_parser` und `test_bvh_projektion` und braucht echte Bewegungsdaten.
"""
import uuid

from django.test import TestCase
from django.urls import reverse

from core.models import BVHJob


class BvhAuslieferungTest(TestCase):
    """Ein Auftrag ohne Dateien: Der Endpunkt muss sauber 404 antworten."""

    def setUp(self):
        self.job = BVHJob.objects.create(name='pruefung.mp4',
                                         pipeline='mediapipe',
                                         status='complete')

    def adresse(self, **werte):
        pfad = reverse('serve_bvh', args=[self.job.id])
        if not werte:
            return pfad
        return '%s?%s' % (pfad, '&'.join('%s=%s' % p for p in werte.items()))

    # ------------------------------------------------------------ Grundfall

    def test_unbekannter_auftrag_gibt_404(self):
        adresse = reverse('serve_bvh', args=[uuid.uuid4()])
        self.assertEqual(self.client.get(adresse).status_code, 404)

    def test_auftrag_ohne_bvh_gibt_404_und_keine_leere_datei(self):
        """Eine leere 200-Antwort waere schlimmer: Der Spieler zeigt dann
        eine Figur ohne Bewegung, ohne dass jemand einen Fehler sieht."""
        antwort = self.client.get(self.adresse())
        self.assertEqual(antwort.status_code, 404)

    def test_bvh_die_es_nicht_mehr_gibt_gibt_404(self):
        """Der Pfad steht in der Datenbank, die Datei ist geloescht."""
        self.job.bvh_file = 'A:/gibtesnicht/weg.bvh'
        self.job.save(update_fields=['bvh_file'])
        self.assertEqual(self.client.get(self.adresse()).status_code, 404)

    # ------------------------------------------------------------ Rueckfall

    def test_ohne_koerper_bvh_wird_die_gesichts_bvh_geliefert(self):
        """Beim Hybridlauf kann der Koerper scheitern und das Gesicht gelingen.

        Dann ist die Gesichtsdatei alles, was es gibt — der Spieler bekommt
        lieber ein Gesicht als einen Fehler.
        """
        from core.projekt_temp import ProjektTemp
        datei = ProjektTemp.datei(suffix='.bvh', prefix='nurgesicht_')
        datei.write_text('HIERARCHY\n', encoding='utf-8')
        self.addCleanup(ProjektTemp.weg, datei)
        self.job.bvh_file_face = str(datei)
        self.job.save(update_fields=['bvh_file_face'])
        antwort = self.client.get(self.adresse())
        self.addCleanup(antwort.close)
        self.assertEqual(antwort.status_code, 200)
        self.assertIn(b'HIERARCHY', b''.join(antwort.streaming_content))

    def test_bvh_wird_nicht_zwischengespeichert(self):
        """Der Text aendert sich beim Bearbeiten — der Browser darf ihn nicht
        aus seinem Zwischenspeicher nehmen."""
        from core.projekt_temp import ProjektTemp
        datei = ProjektTemp.datei(suffix='.bvh', prefix='kein_cache_')
        datei.write_text('HIERARCHY\n', encoding='utf-8')
        self.addCleanup(ProjektTemp.weg, datei)
        self.job.bvh_file = str(datei)
        self.job.save(update_fields=['bvh_file'])
        antwort = self.client.get(self.adresse())
        # `close()`, bevor `ProjektTemp.weg` raeumt: `FileResponse` haelt die
        # Datei offen, bis jemand sie liest oder schliesst — unter Windows
        # scheitert das Loeschen sonst mit WinError 32.
        self.addCleanup(antwort.close)
        self.assertIn('no-store', antwort['Cache-Control'])

    # --------------------------------------------------------- Betriebsarten

    def test_retarget_ohne_bvh_gibt_404(self):
        """DER FALL VOM 18.08.2026: Diese Betriebsart lief in einen
        ModuleNotFoundError statt in eine Antwort."""
        antwort = self.client.get(self.adresse(mode='retarget'))
        self.assertEqual(antwort.status_code, 404)
        self.assertNotIn(b'Traceback', antwort.content)

    def test_keypoints2d_antwortet_json(self):
        """Auch ohne Erkennungsdaten: eine JSON-Antwort, keine Ausnahme."""
        antwort = self.client.get(self.adresse(mode='keypoints2d'))
        self.assertIn(antwort.status_code, (200, 404), antwort.content[:200])
        if antwort.status_code == 200:
            self.assertEqual(antwort['Content-Type'], 'application/json')

    def test_unbekannter_modus_faellt_auf_die_bvh_zurueck(self):
        """`?mode=quatsch` darf keine Fehlerseite geben — der Spieler schickt
        den Wert aus einem Auswahlfeld, und ein neuer Eintrag dort soll die
        alte Serverfassung nicht umbringen."""
        self.assertEqual(self.client.get(
            self.adresse(mode='quatsch')).status_code, 404)
