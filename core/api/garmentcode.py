# -*- coding: utf-8 -*-
"""GarmentCode: Zustand, Koerpermasse, Schnitt erzeugen, Vorschau ausliefern.

Kleidung wird hier KONSTRUIERT, nicht angepasst — der Gegenentwurf zur
Garderobe in `api/kleidung.py`. Warum das der Weg ist, steht in
`dienste/garmentcode.py`.
"""

import json
import logging
import os

from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from GarmentCode.dienst import GarmentcodeDienst

logger = logging.getLogger(__name__)


class Garmentcode:
    """Die Endpunkte des GarmentCode-Reiters.

    ALLE Endpunkte sind `@staticmethod`, nie `@classmethod`. Der Grund ist
    `require_POST`/`require_GET`: Sie lesen `args[0].method`, und unter einem
    `@classmethod` ist `args[0]` die KLASSE — der Aufruf endet in
    `AttributeError: type object 'Garmentcode' has no attribute 'method'`
    (06.09.2026 an drei Endpunkten gleichzeitig gemessen). Klassenbezuege
    stehen deshalb ausgeschrieben.
    """

    #: Nur diese Dateien darf die Vorschau ausliefern — der Ordnername kommt
    #: aus dem Browser, also wird der Pfad nie aus der Anfrage zusammengebaut,
    #: sondern gegen den Ausgabeordner geprueft.
    ERLAUBTE_ENDUNGEN = ('.png', '.svg', '.pdf', '.json', '.yaml')

    @staticmethod
    @require_GET
    def zustand(request):
        """Ist GarmentCode da, und welche Vorlagen bringt es mit?"""
        zustand = GarmentcodeDienst.zustand()
        # Die Simulation haengt an einer eigenen Python-Umgebung und dem
        # selbst gebauten Warp — sie kann fehlen, waehrend Schnittmuster
        # laengst gehen. Die Seite soll das unterscheiden koennen.
        try:
            zustand['drapierbereit'] = GarmentcodeDienst.drapierbereit()
        except Exception:
            logger.exception('GarmentCode: Drapier-Pruefung gescheitert')
            zustand['drapierbereit'] = False
        return JsonResponse(zustand)

    @staticmethod
    @require_POST
    def drapieren(request):
        """Aus einem erzeugten Schnittmuster ein 3D-Netz rechnen."""
        from GarmentCode.baufeineinstellung import Baufeineinstellung
        from GarmentCode.drapierung import DrapierFehler
        spez = request.POST.get('spezifikation') or ''
        if not spez:
            return JsonResponse({'fehler': 'Kein Schnittmuster angegeben'},
                                status=400)
        # Die beiden Regler unter „Bauen" (Edgar, 09.09.2026). Sie gehoeren
        # nur hierher, nicht in `aus_anfrage` — das Erzeugen eines Schnitts
        # kennt weder Haut noch Simulation.
        fein = Baufeineinstellung.aus_anfrage(request.POST)
        # Die Simulationsregler aus dem aufklappbaren Bereich darunter. Sie
        # kommen mit der Vorsilbe `sim_` und nur, soweit sie abweichen.
        from GarmentCode.simulationsregler import Simulationsregler
        sim = Simulationsregler.aus_anfrage(request.POST)
        try:
            anfrage = Garmentcode.aus_anfrage(request)
            ergebnis = GarmentcodeDienst.drapieren(
                spez, koerper=anfrage['koerper'],
                geschlecht=anfrage['geschlecht'], morphs=anfrage['morphs'],
                bauart=anfrage['bauart'], smpl=anfrage['smpl'],
                meta=anfrage['meta'], fein=fein, sim=sim)
        except DrapierFehler as fehler:
            logger.warning('Drapierung gescheitert: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except Exception as fehler:
            logger.exception('Drapierung: unerwarteter Fehler')
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
        # Die Adresse, unter der der Browser die Rig-Datei holen kann. Ohne
        # sie bleibt das drapierte Netz auf der Platte liegen (Edgar,
        # 06.09.2026: „nach dem Bauen sollte die Kleidung am ausgewaehlten
        # HumanBody liegen").
        # Die Korrektur-Bilanz ist ein dict und gehoert nicht als Ganzes in
        # die Antwort — die eine Zahl, die zaehlt, schon.
        korrektur = ergebnis.pop('korrektur', None) or {}
        ergebnis['aus_der_haut'] = korrektur.get('eingesunken', 0)
        # Womit gebaut wurde, gehoert in die Antwort: Sonst laesst sich ein
        # Ergebnis spaeter nicht mehr einer Reglerstellung zuordnen.
        ergebnis['feineinstellung'] = fein.als_dict()
        ergebnis['simulationswerte'] = sim.als_dict()
        ordner = os.path.basename(ergebnis.get('ordner') or '')
        datei = ergebnis.get('rig_datei')
        if ordner and datei:
            ergebnis['rig_url'] = '/api/garmentcode/datei/%s/%s/' % (ordner, datei)
        return JsonResponse(ergebnis)

    @staticmethod
    @require_GET
    def regler(request):
        """Die Feineinstellungen eines Kleidungsstuecks.

        Welche Regler gelten, haengt am Stueck: eine Hose hat keinen Kragen.
        Deshalb GET mit `vorlage`, nicht eine feste Liste.
        """
        vorlage = request.GET.get('vorlage', '')
        return JsonResponse({
            'vorlage': vorlage,
            'gruppen': GarmentcodeDienst.regler(vorlage),
            # Fertige Kombinationen zum Anhaken (08.09.2026). Sie kommen
            # MIT den Gruppen, nicht ueber einen zweiten Aufruf: Ein Preset
            # gehoert zu genau diesen Reglern, und ein getrennter Abruf
            # koennte auf ein anderes Stueck treffen.
            'presets': GarmentcodeDienst.presets(vorlage),
            # Und die Voreinstellungen fuer das ganze Stueck, die oben im
            # Reiter stehen (Edgar, 08.09.2026: „oben im Tab, nach dem
            # Farben bereich"). Sie haengen zusaetzlich an den
            # meta-Feldern, weil die Rumpfweite nur beim ungefitteten
            # `Shirt` existiert.
            'passform': GarmentcodeDienst.passform(vorlage)})

    @staticmethod
    @require_POST
    def masse(request):
        """Die Masse der gewaehlten Figur — mit ihren Reglerwerten."""
        anfrage = Garmentcode.aus_anfrage(request)
        werte, herkunft = GarmentcodeDienst.masse(
            anfrage['geschlecht'], morphs=anfrage['morphs'],
            bauart=anfrage['bauart'], koerper=anfrage['koerper'],
            meta=anfrage['meta'])
        return JsonResponse({
            'masse': {name: round(float(wert), 2)
                      for name, wert in sorted(werte.items())
                      if not name.startswith('_')},
            'herkunft': herkunft,
            'morphs': len(anfrage['morphs'] or {}),
        })

    @staticmethod
    def aus_anfrage(request):
        """Geschlecht, Bauart und Morphs aus dem Rumpf der Anfrage.

        Die Morphs kommen als JSON, weil es Dutzende sind und sie sonst
        einzeln im Formular staenden.
        """
        try:
            morphs = json.loads(request.POST.get('morphs') or '{}')
        except ValueError:
            logger.warning('GarmentCode: Morphs unlesbar, nehme Grundkoerper')
            morphs = {}
        try:
            regler = json.loads(request.POST.get('regler') or '{}')
        except ValueError:
            logger.warning('GarmentCode: Reglerwerte unlesbar, nehme Vorgabe')
            regler = {}
        try:
            meta = json.loads(request.POST.get('meta') or '{}')
        except ValueError:
            logger.warning('GarmentCode: Metaregler unlesbar, nehme keine')
            meta = {}
        # `koerper`: ein Referenzkoerper von GarmentCode statt der Figur —
        # Masse aus dessen YAML, Drapierung auf ihm (06.09.2026). Ob er die
        # SMPL-Segmentierung braucht, weiss der Server selbst; der Browser
        # muss es nicht mitschicken.
        from ..dienste.smplfigur import Smplfiguren
        koerper = request.POST.get('koerper') or None
        return {
            'vorlage': request.POST.get('vorlage', 't-shirt'),
            'geschlecht': request.POST.get('geschlecht', 'female'),
            'bauart': request.POST.get('bauart') or None,
            'morphs': morphs if isinstance(morphs, dict) else {},
            'regler': regler if isinstance(regler, dict) else {},
            'meta': meta if isinstance(meta, dict) else {},
            'koerper': koerper,
            'smpl': bool(koerper) and Smplfiguren.ist_smpl(koerper),
        }

    @staticmethod
    @require_POST
    def erzeugen(request):
        """Einen Schnitt bauen. Antwort nennt Ordner und Vorschaubild."""
        from GarmentCode.entwurf import EntwurfFehler
        anfrage = Garmentcode.aus_anfrage(request)
        try:
            ergebnis = GarmentcodeDienst.erzeugen(
                anfrage['vorlage'], geschlecht=anfrage['geschlecht'],
                morphs=anfrage['morphs'], bauart=anfrage['bauart'],
                regler=anfrage['regler'], koerper=anfrage['koerper'],
                meta=anfrage['meta'])
        except EntwurfFehler as fehler:
            logger.warning('GarmentCode gescheitert: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except Exception as fehler:
            logger.exception('GarmentCode: unerwarteter Fehler')
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)

        ordner = ergebnis.get('ordner', '')
        bild = GarmentcodeDienst.vorschaubild(ordner)
        ergebnis['spezifikation'] = GarmentcodeDienst.spezifikation(ergebnis) or ''
        ergebnis['vorschau'] = (
            '/api/garmentcode/datei/%s/%s/' % (os.path.basename(ordner), bild)
            if bild else '')
        return JsonResponse(ergebnis)

    @staticmethod
    @require_GET
    def datei(request, ordner, name):
        """Eine Datei aus einem Ergebnisordner ausliefern."""
        from GarmentCode.entwurf import Entwurf
        if not name.lower().endswith(Garmentcode.ERLAUBTE_ENDUNGEN):
            return JsonResponse({'fehler': 'Dateityp nicht erlaubt'}, status=400)
        wurzel = os.path.abspath(Entwurf.AUSGABE)
        pfad = os.path.abspath(os.path.join(wurzel, ordner, name))
        # Der Ordnername kommt aus dem Browser: nur unterhalb der Wurzel.
        if not pfad.startswith(wurzel + os.sep) or not os.path.isfile(pfad):
            return JsonResponse({'fehler': 'Nicht gefunden'}, status=404)
        return FileResponse(open(pfad, 'rb'))
