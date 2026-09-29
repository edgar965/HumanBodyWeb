# -*- coding: utf-8 -*-
"""Blendermodellauftrag — Bereich „BlenderModel": Fotos hinein, ein 3D-Modell heraus.

Edgar (29.09.2026): „mach ein neues Menü Dashboard - BlenderModel, das eine Kopie der Seite,
Struktur und Jobergebnissen ist wie #meshto3d. Darin möchte ich eine neue Pipeline einbauen. Im Job
soll es eine Bildauswahl geben wie in [Mesh-Auftrag] und die 3D Modell Ausgabe wie in [Mesh-to-3D-
Auftrag] sowie alle Optionen für Jobs: neu berechnen, umbenennen usw."

WARUM EIN EIGENES MODELL: Die Kopie soll die beiden Vorlagen nicht anfassen — hier wird an einer
neuen Pipeline gebaut (`Blendermodelllauf`), und was dabei kaputtgeht, trifft weder „Mesh" noch
„Mesh to 3D". Das Modell ist die Summe der beiden:

    bilder     die Bildauswahl wie bei `Meshauftrag` (`datei`, `original`, `rolle`, `gewicht`,
               `bereich`, dazu der Befund der Vorbereitung)
    eingang    das Netz, das der Lauf aus den Fotos gebaut hat (`datei`, `original`, `bytes`) — so
               liest es die Bühne wie bei `Meshfigurauftrag`
    ergebnis   alles Gemessene je Schritt; der Schritt „netz" steht unter `ergebnis['netz']`, die
               Schritte der Figur wie bei `Meshfigurauftrag` auf der obersten Ebene (`erkennung`,
               `regler`, `rest`, `vorschau`, …), damit die Anzeige der Vorlage sie unverändert liest
    optionen   `{'netz': {…}, 'figur': {…}}` — zwei Gruppen, weil `hoehe_cm`, `gesicht` und `textur`
               in beiden Katalogen vorkommen und Verschiedenes meinen (`Blendermodelloptionen`)

Die Feldnamen für Status und Fortschritt heißen wie bei den anderen Aufträgen, damit Tabelle,
Fortschrittsbalken und Beobachter gleich laufen.
"""

import uuid

from django.db import models


class Blendermodellauftrag(models.Model):
    STATUS_CHOICES = [
        ('angelegt', 'Angelegt'),
        ('laeuft', 'Läuft'),
        ('fertig', 'Fertig'),
        ('gescheitert', 'Fehlgeschlagen'),
        ('angehalten', 'Angehalten'),
    ]
    LAEUFT = ('laeuft',)
    #: Was der Nutzer je Foto stellt — ein Lauf darf es beim Speichern nicht überschreiben.
    NUTZERFELDER = ('rolle', 'gewicht', 'bereich')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #: Adresse der Seite (`Auftragskennung`, Datum und Uhrzeit der Anlage).
    kennung = models.CharField(max_length=19, unique=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='angelegt')
    #: Schlüssel des laufenden bzw. zuletzt erreichten Schritts (`Blendermodelllauf.SCHRITTE`).
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
        return '%s (BlenderModel, %s)' % (self.name, self.status)

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
