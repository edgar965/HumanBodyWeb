# -*- coding: utf-8 -*-
"""Haarengineauftrag — Bereich „Haar Engine": Vorlagenfotos hinein, eine Figur mit Haar heraus.

Kopie des Bereichs „BlenderModel" (`Blendermodellauftrag`) für die Genesis Haar Engine
(`Genesishaarengine`): Auftrag, Iterationen und Seiten sind gleich gebaut, die Blender-Aufrufe sind durch
die Engine ersetzt. Eigenes Modell, eigene Tabelle, eigene Ordner — was hier geändert wird, trifft
BlenderModel nicht.

    bilder     die Bildauswahl (die Vorlagen) wie bei `Meshauftrag`: `datei`, `original`, `rolle`, `gewicht`, `bereich`
    eingang    bleibt leer — es gibt kein Netz aus Fotos; das Feld heißt weiter so, weil die Anzeige der Figur
               (`static/viewer/meshfigur/`) es liest
    ergebnis   alles Gemessene je Schritt: `regler` und `grundfigur` (Schritt „grundfigur"), `kreislauf` (Stand der Iterationen),
               `iterationen` (die Runden), `export`, `film`, `gespeichert`, dazu `vorlage_foto` (das kleine Bild der Tabelle)
    optionen   `{'figur': {…}, 'iterationen': {…}, 'film': {…}}` (`Haarengineoptionen`)

Die Feldnamen für Status und Fortschritt heißen wie bei den anderen Aufträgen, damit Tabelle,
Fortschrittsbalken und Beobachter gleich laufen.
"""

import uuid

from django.db import models


class Haarengineauftrag(models.Model):
    STATUS_CHOICES = [
        ('angelegt', 'Angelegt'),
        ('laeuft', 'Läuft'),
        ('fertig', 'Fertig'),
        ('gescheitert', 'Fehlgeschlagen'),
        ('angehalten', 'Angehalten'),
        # Begutachtung (30.09.2026): die Runde ist gerechnet, der Auftrag wartet auf das nächste Rezept.
        ('wartet', 'Wartet auf Begutachtung'),
    ]
    LAEUFT = ('laeuft',)
    #: Was der Nutzer je Foto stellt — ein Lauf darf es beim Speichern nicht überschreiben.
    NUTZERFELDER = ('rolle', 'gewicht', 'bereich')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #: Adresse der Seite (`Auftragskennung`, Datum und Uhrzeit der Anlage).
    kennung = models.CharField(max_length=19, unique=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='angelegt')
    #: Schlüssel des laufenden bzw. zuletzt erreichten Schritts (`Haarenginelauf.SCHRITTE`).
    schritt = models.CharField(max_length=30, blank=True)
    progress = models.IntegerField(default=0)
    progress_detail = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    optionen = models.JSONField(default=dict, blank=True)
    bilder = models.JSONField(default=list, blank=True)
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
        return '%s (Haar Engine, %s)' % (self.name, self.status)

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
        """`bilder` (und `weitere` Felder) speichern — Rolle, Gewicht, Bereich und die REIHENFOLGE
        kommen frisch aus der Datenbank: Der Lauf hält `bilder` minutenlang im Speicher, die Seite
        darf derweil umstellen (dieselbe Falle wie `Meshauftrag.bilder_sichern`)."""
        frisch = [
            b
            for b in (type(self).objects.filter(pk=self.pk).values_list('bilder', flat=True).first() or [])
            if isinstance(b, dict)
        ]
        nach = {b.get('datei'): b for b in frisch}
        for b in self.bilder or []:
            alt = nach.get(b.get('datei'))
            for feld in self.NUTZERFELDER:
                if alt and feld in alt:
                    b[feld] = alt[feld]
        rang = {b.get('datei'): i for i, b in enumerate(frisch)}
        self.bilder = sorted(self.bilder or [], key=lambda b: rang.get(b.get('datei'), len(rang) + 1))
        self.save(update_fields=['bilder', *weitere, 'updated_at'])

    def stellung(self):
        """Die Regler des Ergebnisses samt Eigenmorph und „Kopf-Eigen" — `{regler: wert}` (leer vor
        der Anpassung). Wie `Meshfigurauftrag.stellung`: Die Ketten lesen `ergebnis.regler`, sie sehen
        beide Morphe nicht."""
        e = self.ergebnis or {}
        stellung = dict((e.get('regler') or {}).get('stellung') or {})
        rest = e.get('rest') or {}
        if rest.get('regler'):
            stellung[rest['regler']] = 1.0
        kopf = e.get('kopfeigen') or {}
        if stellung and kopf.get('regler'):
            stellung[kopf['regler']] = float(kopf.get('wert', 1.0))
        return stellung
