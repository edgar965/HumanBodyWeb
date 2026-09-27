# -*- coding: utf-8 -*-
"""Meshfigurauftrag — Reiter „Mesh to 3D": ein Menschen-Netz hinein, eine Genesis-9-Figur heraus.

Edgar (26./27.09.2026): „mache einen neuen Tab Mesh to 3D. Darin soll, ein wenig ähnlich wie im
Tab 3D, ein Genesis-3D-Objekt erzeugt werden, aber nicht aus einem Bild, sondern aus einem Mesh.
Mesh soll per Upload hochgeladen werden können." — und: „du kannst doch für alle Regler, die
Genesis hat, so lange regeln, bis ein Genesis so passt, dass der Abstand zwischen dem Genesis-
Modell und dem Mesh am kleinsten ist".

WARUM EIN EIGENES MODELL: `Bildmodellauftrag` schätzt aus Fotos (Sichtung, Schätzer, Kopf,
Umriss), `Meshauftrag` erzeugt ein freies Netz. Hier ist das Netz die Eingabe, die Figur das
Ergebnis — anderer Lauf (`Meshfigurlauf`), andere Ergebnisse. Die Feldnamen für Status und
Fortschritt heißen wie dort, damit Tabelle und Beobachter gleich laufen.

`eingang` ist die hochgeladene Datei (`datei`, `original`, `bytes`), `optionen` die Wahl
(`Meshfiguroptionen`), `ergebnis` alles Gemessene je Schritt (Erkennung, Körper- und
Gesichtskette mit Verlauf, Regler, Rest, Textur, Vorschau, Testfall, Ablage).
"""

import uuid

from django.db import models


class Meshfigurauftrag(models.Model):
    STATUS_CHOICES = [
        ('angelegt', 'Angelegt'),
        ('laeuft', 'Läuft'),
        ('fertig', 'Fertig'),
        ('gescheitert', 'Fehlgeschlagen'),
        ('angehalten', 'Angehalten'),
    ]
    LAEUFT = ('laeuft',)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #: Adresse der Seite (`Auftragskennung`, Datum und Uhrzeit der Anlage).
    kennung = models.CharField(max_length=19, unique=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='angelegt')
    #: Schlüssel des laufenden bzw. zuletzt erreichten Schritts (`Meshfigurlauf.SCHRITTE`).
    schritt = models.CharField(max_length=30, blank=True)
    progress = models.IntegerField(default=0)
    progress_detail = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    optionen = models.JSONField(default=dict, blank=True)
    eingang = models.JSONField(default=dict, blank=True)
    ergebnis = models.JSONField(default=dict, blank=True)
    #: Name des gespeicherten Modells (`data/models/<modell>.json`), leer bis „speichern".
    modell = models.CharField(max_length=200, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '%s (Mesh to 3D, %s)' % (self.name, self.status)

    @property
    def laeuft(self):
        return self.status in self.LAEUFT

    @property
    def fertig(self):
        return self.status == 'fertig'

    def stellung(self):
        """Die Regler des Ergebnisses samt Eigenmorph — `{regler: wert}` (leer vor der Anpassung)."""
        e = self.ergebnis or {}
        stellung = dict((e.get('regler') or {}).get('stellung') or {})
        rest = e.get('rest') or {}
        if rest.get('regler'):
            stellung[rest['regler']] = 1.0
        return stellung
