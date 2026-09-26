# -*- coding: utf-8 -*-
"""Meshauftrag — „Modell aus Dateien", Reiter „Mesh": Fotos hinein, ein Netz (GLB/OBJ) heraus.

Edgar (26.09.2026): „brauch ich einen zweiten Tab … neuer Tab: Mesh. Im neuen Tab Mesh
möchte ich Fotos angeben können (upload files), mit batch upload … Optionen auswählen
(mach Vorschlag) und du erzeugst ein Mesh daraus (OBJ, GLB oder sowas). Das ist ein
schwieriger Task, nimm dir Zeit, ich brauche ein perfektes Ergebnis." — und: „Mache die
Auswahl Hunyuan3D und Trellis auswählbar".

WARUM EIN EIGENES MODELL: `Bildmodellauftrag` fittet eine Genesis-9-Figur (Regler, Rig,
Eigenmorph); hier entsteht ein freies Netz aus einem Bild-zu-3D-Modell (TRELLIS.2,
Hunyuan3D) mit einer Textur aus den Fotos — anderer Lauf, andere Ergebnisse.

`bilder` ist die Liste der Eingänge (`datei`, `rolle` vorne/hinten/links/rechts/gesicht/
auto/aus, Befund der Vorbereitung), `optionen` die Wahl (`Meshoptionen`), `ergebnis` die
Dateien und Zahlen (Flächen, Punkte, Dauer je Schritt, Texturdeckung je Foto).
Die Felder `progress`, `progress_detail`, `error_message`, `pid` heißen wie bei
`Bildmodellauftrag`, damit Tabelle und Beobachter gleich laufen.
"""

import uuid

from django.db import models


class Meshauftrag(models.Model):
    STATUS_CHOICES = [
        ('angelegt', 'Angelegt'),
        ('laeuft', 'Läuft'),
        ('fertig', 'Fertig'),
        ('gescheitert', 'Fehlgeschlagen'),
        ('angehalten', 'Angehalten'),
    ]
    LAEUFT = ('laeuft',)
    #: Was der Nutzer je Bild stellt — der Lauf darf es beim Speichern nicht überschreiben.
    #: `gewicht` (0..100, Vorgabe 100) und `bereich` ([x0,y0,x1,y1] normiert, Vorgabe None
    #: = ganzes Bild) seit 26.09.2026 abends: Mehrbild-Mischung (Fotogewicht, Fusion).
    NUTZERFELDER = ('rolle', 'gewicht', 'bereich')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #: Adresse der Seite (`Auftragskennung`, Datum und Uhrzeit der Anlage).
    kennung = models.CharField(max_length=19, unique=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='angelegt')
    #: Schlüssel des laufenden bzw. zuletzt erreichten Schritts (`Meshlauf.SCHRITTE`).
    schritt = models.CharField(max_length=30, blank=True)
    progress = models.IntegerField(default=0)
    progress_detail = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    optionen = models.JSONField(default=dict, blank=True)
    bilder = models.JSONField(default=list, blank=True)
    ergebnis = models.JSONField(default=dict, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '%s (Mesh, %s)' % (self.name, self.status)

    @property
    def laeuft(self):
        return self.status in self.LAEUFT

    @property
    def fertig(self):
        return self.status == 'fertig'

    def bild(self, datei):
        """Der Eintrag zu einer Eingangsdatei — oder None."""
        for eintrag in self.bilder or []:
            if eintrag.get('datei') == datei:
                return eintrag
        return None

    def bilder_sichern(self, *weitere):
        """`bilder` (und `weitere` Felder) speichern — die Rolle je Bild kommt frisch aus
        der Datenbank (der Lauf hält `bilder` minutenlang im Speicher, die Seite darf
        derweil umstellen; dieselbe Falle wie `Bildmodellauftrag.bilder_sichern`)."""
        frisch = type(self).objects.filter(pk=self.pk).values_list('bilder', flat=True).first() or []
        nach = {b.get('datei'): b for b in frisch if isinstance(b, dict)}
        for b in self.bilder or []:
            alt = nach.get(b.get('datei'))
            for feld in self.NUTZERFELDER:
                if alt and feld in alt:
                    b[feld] = alt[feld]
        self.save(update_fields=['bilder', *weitere, 'updated_at'])
