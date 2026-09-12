# -*- coding: utf-8 -*-
u"""MakeHuman-Figur fuer die Szene: Basisnetz, Garderobe, Texturen.

    GET  /api/character/mh-figur/
         {figuren: [{name, anzeige, punkte, flaechen, hoehe, teile}]}
    GET  /api/character/mh-figur/<name>/netz/
             ?teile=koerper,helfer&glaetten=0&verdeckt=tops/x,shoes/y
    POST dieselbe Adresse, JSON — zusaetzlich `makro` und `regler`
         {name, teile, glatt, verdeckt, hoehe, geformt, vertex_count,
          vertices, faces, normals}
    GET  /api/character/mh-figur/regler/
         {seiten: [{name, abschnitte: [{name, regler}]}], makro, rassen}
    GET  /api/character/mh-figur/garderobe/
         {stuecke: [{id, name, kategorie, kategoriename, vorschau}], kategorien}
    GET  /api/character/mh-figur/garderobe/<kategorie>/<stueck>/netz/
         {kennung, vertices, faces, normals, uvs, mat_color?, texture_name?}
    GET  /api/character/mh-figur/garderobe/<kategorie>/<stueck>/textur/<datei>/

Warum es diese Figur gibt und warum die Kleidung darauf exakt sitzt:
`MakeHuman/basisnetz.py`.

Die Texturen kommen aus der Bibliothek selbst und nicht aus
`garment_library/.cache` wie bei `Kleiderendpunkte.textur`: Der
Zwischenspeicher hat nicht zu jedem Stueck einen Ordner, die Bibliothek schon
— und aus ihr wird hier auch das Netz gelesen.
"""

import logging
import os

import json

from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from ..daten.netzantwort import Netzantwort
from ..daten.pfadvergleich import Pfadvergleich
from MakeHuman.basisnetz import Mhbasisnetz
from MakeHuman.formung import Mhformung
from MakeHuman.garderobe import Mhgarderobe
from MakeHuman.kleidnetz import Mhkleidnetz, MhkleidFehler
from MakeHuman.koerpernetz import Mhkoerpernetz
from MakeHuman.skelett import Mhskelett
from MakeHuman.makrowerte import Mhmakrowerte
from MakeHuman.modifikatoren import Mhmodifikatoren
from MakeHuman.reglerplan import Mhreglerplan
from MakeHuman.zielablage import Mhzielablage

logger = logging.getLogger('core')

__all__ = ['Mhfigur']


class Mhfigur:
    u"""Lesende Endpunkte auf das MakeHuman-Basisnetz und seine Kleidung."""

    #: Was ohne `teile=` gezeigt wird — dasselbe wie MakeHuman selbst zeigt.
    VORGABETEILE = ('koerper',)
    #: Bildendungen, die als Textur ausgeliefert werden.
    BILDARTEN = {'.png': 'image/png', '.jpg': 'image/jpeg',
                 '.jpeg': 'image/jpeg'}

    # --------------------------------------------------------------- Figuren

    @staticmethod
    @require_GET
    def liste(request):
        if not Mhbasisnetz.vorhanden():
            return JsonResponse({'figuren': [], 'fehler':
                                 u'MakeHuman/base.obj fehlt'})
        return JsonResponse({'figuren': [Mhbasisnetz.holen().steckbrief()]})

    @staticmethod
    @csrf_exempt
    @require_http_methods(['GET', 'POST'])
    def netz(request, name):
        u"""Das Netz — mit GET in der Vorgabeform, mit POST samt Reglern.

        ZWEI VERFAHREN, WEIL DIE STELLUNG NICHT IN EINE ADRESSE PASST: 269
        Regler als Abfrageteil waeren mehrere Kilobyte, und Browser wie
        Server kuerzen so etwas irgendwann stillschweigend. GET bleibt fuer
        den einfachen Fall (und fuer die Tests), POST traegt `makro` und
        `regler` im Rumpf.
        """
        if name != 'basis':
            return JsonResponse({'fehler': u'Unbekanntes MakeHuman-Modell'},
                                status=404)
        if not Mhbasisnetz.vorhanden():
            return JsonResponse({'fehler': u'MakeHuman/base.obj fehlt'},
                                status=404)
        rumpf = Mhfigur._rumpf(request)
        teile = Mhfigur._teile(request, rumpf)
        glatt = Mhfigur._ja(request, rumpf, 'glaetten')
        getragen = Mhfigur._getragen(request, rumpf)
        formung = Mhformung.aus_abfrage(rumpf.get('makro'), rumpf.get('regler'))
        try:
            netz = Mhkoerpernetz(teile, glatt, getragen, formung).bauen()
        except (OSError, ValueError) as fehler:
            logger.warning('MakeHuman-Basisnetz nicht lesbar: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        antwort = Netzantwort.aus(netz['punkte'], faces=netz['dreiecke'],
                                  normals=netz['normalen'])
        antwort.update({
            'name': name, 'teile': list(teile), 'glatt': glatt,
            'verdeckt': list(getragen), 'hoehe': netz['hoehe'],
            'geformt': Mhzielablage.bereit() and Mhmodifikatoren.vorhanden(),
            # Das Skelett kommt MIT dem Netz: Seine Gelenke sind Mittelwerte
            # von Punkten DIESER Reglerstellung. Ein zweiter Endpunkt muesste
            # die 269 Regler noch einmal uebertragen und koennte dabei
            # danebenliegen.
            'skelett': Mhfigur._skelett(formung),
            # Ohne Hautgewichte bleibt die Figur beim Abspielen starr:
            # Das Skelett bewegt sich, das Netz nicht (07.09.2026).
            'hautgewichte': Mhfigur._hautgewichte(netz.get('haut')),
        })
        return JsonResponse(antwort)

    @staticmethod
    def _hautgewichte(haut):
        u"""Die Gewichte base64, mit den Breiten aus `Netzantwort.TYPEN`.

        Als JSON-Liste waeren es beim geglaetteten Netz 53.514 x 8 Zahlen.
        Die Knochen stehen als NAMEN da: Ihre Nummer im `THREE.Skeleton`
        entscheidet erst der Bauplan.
        """
        if not haut:
            return None
        return {
            'knochen': haut['knochen'],
            'skin_indices': Netzantwort.feld(haut['index'], 'skin_indices'),
            'skin_weights': Netzantwort.feld(haut['gewicht'], 'skin_weights'),
        }

    @staticmethod
    def _skelett(formung):
        u"""`default.mhskel`, gerechnet auf dieser Reglerstellung — oder `None`.

        Fehlt der Upstream-Klon, ist das kein Fehler des Netzes: Die Figur
        erscheint dann ohne Knochen, statt dass der ganze Aufruf scheitert.
        """
        if not Mhskelett.vorhanden():
            return None
        try:
            return Mhskelett(formung).bauen()
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('MakeHuman-Skelett nicht baubar: %s', fehler)
            return None

    @staticmethod
    def _rumpf(request):
        u"""Der JSON-Rumpf eines POST — bei GET ein leeres Woerterbuch."""
        if request.method != 'POST':
            return {}
        try:
            daten = json.loads(request.body.decode('utf-8') or '{}')
        # stumm gewollt: kaputtes JSON aus dem Browser heisst 'keine Angaben'
        except (ValueError, UnicodeDecodeError):
            return {}
        return daten if isinstance(daten, dict) else {}

    @classmethod
    def _teile(cls, request, rumpf):
        u"""`teile=koerper,helfer` — Unbekanntes faellt weg, Leeres gilt nicht."""
        aus_rumpf = rumpf.get('teile')
        gewuenscht = (aus_rumpf if isinstance(aus_rumpf, list)
                      else [t.strip()
                            for t in request.GET.get('teile', '').split(',')])
        gewaehlt = tuple(t for t in Mhbasisnetz.TEILE if t in gewuenscht)
        return gewaehlt or cls.VORGABETEILE

    @staticmethod
    def _ja(request, rumpf, name):
        if name in rumpf:
            return bool(rumpf[name])
        return request.GET.get(name, '0') == '1'

    @staticmethod
    def _getragen(request, rumpf):
        u"""Die Stuecke, deren Haut ausgeblendet wird.

        Nur Kennungen, die es wirklich gibt: `Mhloeschmaske` sucht sonst
        Verzeichnisse, die ein Fremder in die Abfrage geschrieben hat.
        """
        aus_rumpf = rumpf.get('verdeckt')
        roh = (aus_rumpf if isinstance(aus_rumpf, list)
               else [k.strip()
                     for k in request.GET.get('verdeckt', '').split(',')])
        bekannt = {stueck['id'] for stueck in Mhgarderobe.liste()}
        return tuple(k for k in roh if k in bekannt)

    # ----------------------------------------------------------- Modellieren

    @staticmethod
    @require_GET
    def regler(request):
        u"""MakeHumans Modellierregler: Seiten, Abschnitte, Grenzen, Vorgaben."""
        if not Mhmodifikatoren.vorhanden():
            return JsonResponse({
                'seiten': [], 'makro': dict(Mhmakrowerte.VORGABEN),
                'rassen': list(Mhmakrowerte.RASSEN), 'ziele_bereit': False,
                'fehler': u'MakeHuman-Upstream fehlt — siehe MakeHuman/HERKUNFT.md',
            })
        return JsonResponse({
            'seiten': Mhreglerplan.holen(),
            'makro': dict(Mhmakrowerte.VORGABEN),
            'rassen': list(Mhmakrowerte.RASSEN),
            'ziele_bereit': Mhzielablage.bereit(),
        })

    # -------------------------------------------------------------- Garderobe

    @staticmethod
    @require_GET
    def garderobe(request):
        stuecke = Mhgarderobe.liste()
        kategorien = []
        for stueck in stuecke:
            eintrag = {'schluessel': stueck['kategorie'],
                       'name': stueck['kategoriename']}
            if eintrag not in kategorien:
                kategorien.append(eintrag)
        return JsonResponse({'stuecke': stuecke, 'kategorien': kategorien,
                             'anzahl': len(stuecke)})

    @staticmethod
    @csrf_exempt
    @require_http_methods(['GET', 'POST'])
    def kleidnetz(request, kategorie, stueck):
        u"""Ein Kleidungsstueck — mit POST auf dem GEFORMTEN Traeger.

        Die `.mhclo` haengt jeden Stoffpunkt an drei Koerperpunkte. Wandern
        die (Alter, Gewicht, Muskeln …), wandert der Stoff mit; deshalb muss
        hier dieselbe Reglerstellung ankommen wie beim Koerper.
        """
        kennung = '%s/%s' % (kategorie, stueck)
        rumpf = Mhfigur._rumpf(request)
        formung = Mhformung.aus_abfrage(rumpf.get('makro'), rumpf.get('regler'))
        try:
            daten = Mhkleidnetz(kennung, formung).netz()
        except MhkleidFehler as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=fehler.status)
        except (OSError, ValueError) as fehler:
            logger.warning('MakeHuman-Kleid %s nicht ladbar: %s', kennung,
                           fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        haut = daten.pop('haut', None)
        antwort = Netzantwort.aus(daten.pop('punkte'),
                                  faces=daten.pop('dreiecke'),
                                  normals=daten.pop('normalen'),
                                  uvs=daten.pop('uvs'))
        antwort.update(daten)
        antwort['hautgewichte'] = Mhfigur._hautgewichte(haut)
        return JsonResponse(antwort)

    @staticmethod
    @require_GET
    def textur(request, kategorie, stueck, datei):
        u"""Eine Texturdatei aus dem Ordner des Kleidungsstuecks."""
        ordner = Mhgarderobe.verzeichnis('%s/%s' % (kategorie, stueck))
        if not ordner:
            return HttpResponseNotFound('Garment not found')
        name = os.path.basename(datei)
        pfad = os.path.join(ordner, name)
        if not Pfadvergleich.liegt_unter(pfad, Mhgarderobe.wurzel()):
            return HttpResponseNotFound('Invalid path')
        art = Mhfigur.BILDARTEN.get(os.path.splitext(name)[1].lower())
        if not art or not os.path.isfile(pfad):
            return HttpResponseNotFound('Texture not found')
        return FileResponse(open(pfad, 'rb'), content_type=art)
