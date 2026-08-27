# -*- coding: utf-8 -*-
"""Kleidungsbibliothek: Bestand, Vorschau, Ausgabe.

Aus core/api/kleidung.py herausgeloest (Umbau 15.08.2026). Die Datei war beim
Aufteilen von character_api.py entstanden und hatte selbst 1.081 Zeilen mit 21
Endpunkten aus vier Themen — Stoffbau, Vorlagen, Schnittmuster und Bibliothek
standen nur durch Reihenfolge getrennt beieinander.

DABEI GEFUNDEN (27.08.2026): DER KATALOG WURDE NIE MEHR AUFGEFRISCHT
====================================================================
Drei Stellen schrieben `_garment_library = None`, um den Zwischenspeicher nach
einer Aenderung zu verwerfen — nach Umbenennen/Verschieben/Kopieren/Loeschen
(`garment_manage`) und nach dem Herunterladen eines MakeHuman-Pakets
(`garment_download`, zweimal). Der Zwischenspeicher liegt aber seit dem
18.08.2026 in `dienste/kleiderbibliothek.Kleiderbibliothek`; die Modulvariable
`_garment_library` gab es hier gar nicht mehr. `global` legt sie stillschweigend
neu an, und niemand liest sie.

Die Folge war NICHT sichtbar: Kein Fehler, keine Meldung — die Kleiderliste
zeigte bis zum naechsten Serverneustart den alten Stand, mit Pfaden, die es
nach dem Umbenennen nicht mehr gab. Der Docstring von `garment_manage` sagte
die Absicht die ganze Zeit richtig an. Jetzt ruft jede dieser Stellen
`Kleiderbibliothek.neu_einlesen()`.

UMBAU 27.08.2026 (Befund `freie-funktionen`, `klassenreif` Frage 1): neun freie
Funktionen und eine Modulvariable mit `global`. Beides steht jetzt in einer
Klasse.
"""

import json
import logging
import os
import re

from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..dienste.kleiderbibliothek import Kleiderbibliothek
from ..dienste.kleiderverwaltung import Kleiderverwaltung, KleiderFehler

logger = logging.getLogger(__name__)


class Kleiderendpunkte:
    """Die HTTP-Schale um `Kleiderbibliothek` und `Kleiderverwaltung`."""

    #: Endungen einer Vorschau, in dieser Reihenfolge gesucht.
    VORSCHAU_ENDUNGEN = ('.thumb', '_diffuse.png')

    # ------------------------------------------------------------- Bestand

    @staticmethod
    @require_GET
    def bestand(request):
        """Alle Kleidungsstuecke, nach Kategorie gruppiert."""
        katalog = Kleiderbibliothek.holen().catalog
        kategorie = request.GET.get('category', '')
        if kategorie:
            katalog = [g for g in katalog if g['category'] == kategorie]
        nach_kategorie = {}
        for stueck in katalog:
            nach_kategorie.setdefault(stueck['category'], []).append(stueck)
        return JsonResponse({
            'categories': sorted(nach_kategorie.keys()),
            'garments': nach_kategorie,
            'total': len(katalog),
        })

    @staticmethod
    @require_GET
    def neu_einlesen(request):
        """Das Kleiderverzeichnis erneut durchsuchen."""
        katalog = Kleiderbibliothek.neu_einlesen()
        return JsonResponse({'ok': True, 'count': len(katalog.catalog)})

    @staticmethod
    @csrf_exempt
    @require_POST
    def verwalten(request):
        """Kleider umbenennen, verschieben, kopieren, in den Papierkorb legen.

        POST /api/character/garment/manage/ mit JSON-Feld `action`:
        rename, move, copy, delete

        Die Arbeit macht `Kleiderverwaltung`; hier steht nur die HTTP-Schale —
        wie bei `bvh_manage`. Der Endpunkt FEHLTE bis zum 17.08.2026, obwohl
        die Kontextmenues der Kleider- und der MakeHuman-Liste ihn von acht
        Stellen aus aufriefen: vier tote Aktionen in zwei Listen, ohne Hinweis
        fuer den Benutzer.

        Nach jeder Aenderung ist der Bibliotheks-Zwischenspeicher hinfaellig —
        die Kennung eines Kleides ist sein Pfad, und der hat sich gerade
        geaendert.
        """
        try:
            daten = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        try:
            antwort = Kleiderverwaltung.ausfuehren(daten)
        except KleiderFehler as fehler:
            return JsonResponse({'error': fehler.text}, status=fehler.kennzahl)
        Kleiderbibliothek.neu_einlesen()
        return JsonResponse(antwort)

    # ------------------------------------------------------ MakeHuman holen

    @staticmethod
    def _herunterlader():
        from GarmentFitter import MakeHumanDownloader
        return MakeHumanDownloader(
            str(settings.HUMANBODY_GARMENT_LIBRARY_DIR))

    @staticmethod
    @require_GET
    def angebot(request):
        """Welche MakeHuman-Pakete stehen zum Herunterladen bereit?"""
        lader = Kleiderendpunkte._herunterlader()
        pakete = lader.list_available_packs()
        mitgeliefert = []
        try:
            mitgeliefert = lader.list_builtin_assets()
        except Exception:
            logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)
        return JsonResponse({'packs': pakete, 'builtin_assets': mitgeliefert})

    @staticmethod
    @csrf_exempt
    @require_POST
    def herunterladen(request):
        """MakeHuman-Bestand holen — ein Paket oder ein einzelnes Stueck.

        JSON-Rumpf: `pack_name` (ZIP-Paket, z. B. 'shirts01') ODER
        `asset_name` (ein mitgeliefertes Stueck).
        """
        try:
            rumpf = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        lader = Kleiderendpunkte._herunterlader()
        paket = rumpf.get('pack_name', '')
        stueck = rumpf.get('asset_name', '')
        if paket:
            eingerichtet = lader.download_pack(paket)
            Kleiderbibliothek.neu_einlesen()
            return JsonResponse({'ok': True, 'installed': eingerichtet,
                                 'count': len(eingerichtet)})
        if stueck:
            kennung = lader.download_builtin_asset(stueck)
            Kleiderbibliothek.neu_einlesen()
            return JsonResponse({'ok': kennung is not None,
                                 'garment_id': kennung})
        return JsonResponse({'error': 'pack_name or asset_name required'},
                            status=400)

    # -------------------------------------------------------------- Ausgabe

    @staticmethod
    @csrf_exempt
    @require_POST
    def ausgabeordner(request):
        """Den Ordner fuer OBJ + Gewichte eines Kleides vorbereiten."""
        try:
            rumpf = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        kennung = rumpf.get('garment_id', '')
        name = rumpf.get('name', 'garment').strip()
        if not kennung or not name:
            return JsonResponse({'error': 'garment_id and name required'},
                                status=400)
        sauber = re.sub(r'[^\w\s\-]', '', name).strip()
        if not sauber:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        wurzel = str(settings.HUMANBODY_GARMENT_EXPORT_DIR)
        os.makedirs(wurzel, exist_ok=True)
        ziel = os.path.normpath(os.path.join(wurzel, sauber))
        if not ziel.startswith(os.path.normpath(wurzel)):
            return JsonResponse({'error': 'Invalid path'}, status=400)
        return JsonResponse({
            'ok': True, 'export_dir': ziel,
            'message': 'Export directory prepared: %s' % sauber,
        })

    # ------------------------------------------------------------- Vorschau

    @staticmethod
    @require_GET
    def vorschaubild(request, garment_path):
        """Das Vorschaubild eines Kleides (`.thumb` oder `_diffuse.png`)."""
        wurzel = str(settings.HUMANBODY_GARMENT_LIBRARY_DIR)
        sauber = os.path.normpath(garment_path).replace('\\', '/')
        if '..' in sauber:
            return HttpResponseNotFound('Invalid path')
        ordner = os.path.join(wurzel, sauber)
        if not os.path.normpath(ordner).startswith(os.path.normpath(wurzel)):
            return HttpResponseNotFound('Invalid path')
        if not os.path.isdir(ordner):
            return HttpResponseNotFound('Garment not found')
        # `.thumb` hat Vorrang; erst wenn es keines gibt, die Diffuse-Textur.
        for endung in Kleiderendpunkte.VORSCHAU_ENDUNGEN:
            for name in sorted(os.listdir(ordner)):
                if name.endswith(endung):
                    return FileResponse(open(os.path.join(ordner, name), 'rb'),
                                        content_type='image/png')
        return HttpResponseNotFound('No thumbnail')

    @staticmethod
    @require_GET
    def textur(request, garment_id, filename):
        """Eine Texturdatei aus dem Zwischenspeicher der Kleiderbibliothek."""
        speicher = os.path.join(str(settings.HUMANBODY_DATA_DIR), '..',
                                'garment_library', '.cache')
        kleid = garment_id.split('/')[-1] if '/' in garment_id else garment_id
        name = os.path.basename(filename)
        if '..' in name or '..' in kleid:
            return HttpResponseNotFound('Invalid path')
        pfad = os.path.join(speicher, kleid, name)
        if not os.path.isfile(pfad):
            return HttpResponseNotFound('Texture not found')
        art = 'image/png' if name.endswith('.png') else 'image/jpeg'
        return FileResponse(open(pfad, 'rb'), content_type=art)
