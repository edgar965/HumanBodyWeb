# -*- coding: utf-8 -*-
"""Bildmodellauftrag — „Modell aus Bildern": Fotos hinein, Genesis-9-Figur heraus.

Edgar (18./19.09.2026): „Bei daz3d sind viele Addon-Modelle zum Verkauf …
Bist du in der Lage, diese Formen mit Hilfe der Genesis-Regler selber zu
erstellen, wenn ich dir die Bilder gebe? … Dashboard – Modell aus Dateien
… Pro Job eine Zeile … Hauptbilder und Nebenbilder getrennt anzeigen …
auf der Seite soll man die verschiedenen Optionen für einzelne Schritte
einstellen können."

WARUM EIN EIGENES MODELL: `PhotoAnalysisJob` ist EIN Foto → HumanBody-Regler,
synchron. Hier sind es viele Bilder, ein Lauf in Schritten (Zuschnitt und
Sichtung, Schätzung, Zielnetz, Anpassung, Rest, Vorschau, Speichern) mit
je eigener Wahl, ein Arbeitsprozess wie bei `BVHJob` — und das Ergebnis ist
eine Genesis-9-Reglerstellung samt Eigenmorph.

Die Felder `progress`, `progress_detail`, `error_message`, `pid` heißen
wie bei `BVHJob`/`Effektauftrag`, damit Tabelle und Beobachter passen.
`bilder` ist die Liste der Ausschnitte mit Befund (Kategorie, Gewicht,
Landmarken, Schätzung), `optionen` die Wahl je Schritt, `ergebnis` die
Zahlen der Anpassung (Regler, RMS je Teil, Restmorph, Vorschaudateien).
"""

import uuid

from django.db import models


class Bildmodellauftrag(models.Model):
    TYP_CHOICES = [
        ('genesis9', 'Genesis 9'),
    ]
    STATUS_CHOICES = [
        ('angelegt', 'Angelegt'),
        ('laeuft', 'Läuft'),
        ('fertig', 'Fertig'),
        ('gescheitert', 'Fehlgeschlagen'),
        ('angehalten', 'Angehalten'),
    ]
    LAEUFT = ('laeuft',)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #: Adresse der Seite, wie bei `BVHJob` (`Auftragskennung`).
    kennung = models.CharField(max_length=19, unique=True)
    name = models.CharField(max_length=200)
    typ = models.CharField(max_length=20, choices=TYP_CHOICES, default='genesis9')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='angelegt')
    #: Schlüssel des laufenden bzw. zuletzt erreichten Schritts.
    schritt = models.CharField(max_length=30, blank=True)
    progress = models.IntegerField(default=0)
    progress_detail = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    optionen = models.JSONField(default=dict, blank=True)
    bilder = models.JSONField(default=list, blank=True)
    ergebnis = models.JSONField(default=dict, blank=True)
    #: Name des gespeicherten Modells (`data/models/<name>.json`), wenn gesichert.
    modell = models.CharField(max_length=255, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '%s (%s, %s)' % (self.name, self.typ, self.status)

    @property
    def laeuft(self):
        return self.status in self.LAEUFT

    @property
    def fertig(self):
        return self.status == 'fertig'

    def bild(self, datei):
        """Der Eintrag zu einer Ausschnittdatei — oder None."""
        for eintrag in self.bilder:
            if eintrag.get('datei') == datei:
                return eintrag
        return None

    #: Was der Nutzer an einem Eintrag stellt (`Bildmodellbildtypen.stellen`, Spalte „Nr.") —
    #: der Arbeitsprozess darf es beim Speichern seiner Befunde nicht überschreiben.
    NUTZERFELDER = ('kategorie', 'ansicht', 'teil', 'hauptbild', 'gewicht', 'nutzung',
                    'textur_an', 'gvhmr_an', 'reihe', 'textur_reihe', 'manuell', 'freisteller')

    def bilder_sichern(self, *weitere, behalten=()):
        """`bilder` (und `weitere` Felder) speichern — die Nutzerfelder der Einträge kommen
        frisch aus der Datenbank: Ein Lauf hält `bilder` minutenlang im Speicher; was der
        Nutzer derweil auf der Seite stellt (Typ, Häkchen, Nummer), wäre beim Speichern
        des Laufs sonst weg (20.09.2026). `behalten`: Nutzerfelder, die der Aufrufer selbst
        gerade gesetzt hat — der Freisteller schreibt `freisteller` und verlor es hier sofort
        wieder (21.09.2026, Edgar: „altes Bild mit Hintergrund")."""
        frisch = type(self).objects.filter(pk=self.pk).values_list('bilder', flat=True).first() or []
        nach = {b.get('datei'): b for b in frisch if isinstance(b, dict)}
        for b in self.bilder:
            alt = nach.get(b.get('datei'))
            if not alt:
                continue
            for feld in self.NUTZERFELDER:
                if feld in behalten:
                    continue
                if feld in alt:
                    b[feld] = alt[feld]
                else:
                    b.pop(feld, None)
        self.save(update_fields=['bilder', *weitere, 'updated_at'])

    def nach_kategorie(self):
        """`{kategorie: [bilder]}` in fester Reihenfolge (`KATEGORIEN`)."""
        aus = {k: [] for k, _ in self.KATEGORIEN}
        for eintrag in self.bilder:
            aus.setdefault(eintrag.get('kategorie') or 'neben', []).append(eintrag)
        return aus

    #: Die Bereiche der Auftragsseite, in dieser Reihenfolge.
    KATEGORIEN = [
        ('koerper', 'Hauptbilder Körper'),
        ('kopf', 'Hauptbilder Kopf'),
        ('video', 'Drehvideos'),
        ('neben', 'Nebenbilder'),
        ('gruppe', 'Gruppenbilder'),
        ('leer', 'Ohne Befund'),
    ]
