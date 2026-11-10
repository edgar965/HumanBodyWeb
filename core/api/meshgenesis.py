# -*- coding: utf-8 -*-
"""Meshgenesisendpunkte — Seiten und Daten von „Mesh-Genesis“ (14.10.2026, Dashboard → Mesh-Genesis).

Edgar: „Mach das Menü Dashboard – Mesh3D-AI und zeige mir den Input, gewünschten Trainingsoutput und Output, mit Dummies für Ursula1.“ Danach: „wir werden mehrere Jobs außer Ursula haben …
eine Hauptansicht mit einer Tabelle wie bei /mesh-3D/, und die Unterjobs wie Ursula1 als Unterseiten“.

GET /mesh-genesis/                         die Liste der Jobs (Tabelle)
GET /mesh-genesis/<job>/                   die Jobseite (Eingabe · gewünschte Ausgabe · Ausgabe des Netzes); die Kennung ist klein geschrieben, eine andere Schreibweise leitet um
GET /api/meshgenesis/jobs/                  die Jobs (Kurzstand)
GET /api/meshgenesis/<job>/proben/          die Proben des Jobs — echt (Datensatz + Vorhersagen des jüngsten fertigen Laufs, `Meshgenesisdaten`), sonst die Attrappe
GET /api/meshgenesis/<job>/eingabe/<nr>/    die Punktwolke EINER echten Probe (4.096 Punkte mit Farbe und Teil)
GET /api/meshgenesis/<job>/eingabe/<nr>/dicht/   Tripo-Jobs: die dichte Start-Wolke (2 Mio. Punkte, Binärpaket, `Meshgenesiseingabedicht`)
GET /api/meshgenesis/<job>/flaeche/<nr>/    die gehäutete Figur EINER echten Probe (Binärpaket, `Meshgenesisflaeche`) für die Ansichtsarten
GET /api/meshgenesis/<job>/apose/<nr>/      das Zwischenbild „Rig → A-Pose“ der Probe, auf der die Vorstufe lief (Binärpaket, `Meshgenesisapose`)
GET /api/meshgenesis/<job>/stand/           ECHT: fertige Proben des Datensatzes und der jüngste Trainingslauf (Platte), dazu der Abfragetakt in Minuten
GET /api/meshgenesis/<job>/animation/       die Bilder der Standardanimation
GET /api/meshgenesis/<job>/animation/flaechen/   die Flächen aller Bilder der Standardanimation (Binärpaket, ohne Haar)

Die Jobseite fragt `proben` ab; heute liefert beides die Attrappe (`Meshgenesisattrappe`), später die echte Ablage — die Seite merkt den Unterschied nur am Feld `attrappe`.
"""

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from ..dienste.meshgenesisapose import Meshgenesisapose
from ..dienste.meshgenesisattrappe import Meshgenesisattrappe
from ..dienste.meshgenesisdaten import Meshgenesisdaten
from ..dienste.meshgenesisflaeche import Meshgenesisflaeche
from ..dienste.meshgenesisflaechenanimation import Meshgenesisflaechenanimation
from ..dienste.meshgenesisformtraining import Meshgenesisformtraining
from ..dienste.meshgenesisformtrainingjetzt import Meshgenesisformtrainingjetzt
from ..dienste.meshgenesisformtrainingtabelle import Meshgenesisformtrainingtabelle
from ..dienste.meshgenesisformvarianten import Meshgenesisformvarianten
from ..dienste.meshgenesisformvariantentabelle import Meshgenesisformvariantentabelle
from ..dienste.meshgenesisstand import Meshgenesisstand
from ..dienste.meshgenesistabelle import Meshgenesistabelle
from ..dienste.meshgenesistesttabelle import Meshgenesistesttabelle
from ..dienste.meshgenesistexturwahl import Meshgenesistexturwahl

__all__ = ['Meshgenesisendpunkte']


class Meshgenesisendpunkte:
    @staticmethod
    @require_GET
    def liste(request):
        # Das Band „Attrappe“ nur, solange ein Job noch keinen fertigen Lauf hat (seit 15.10.2026 zeigt ein Job mit Lauf echte Daten).
        attrappe = any(Meshgenesisdaten.lauf(j['ordner']) is None for j in Meshgenesisattrappe.stammdaten())
        # Zweiter Reiter „Test“ (16.10.2026): Netze ohne Trainingsdaten (`Meshgenesistesttabelle`); dritter „Formtraining“ (18.10.2026): Läufe der gemeinsamen Netze und Formvarianten.
        laeufe = Meshgenesisformtraining.laeufe()
        varianten = Meshgenesisformvarianten.alle()
        return render(request, 'meshgenesis_liste.html', {'tabelle': Meshgenesistabelle().tabelle(), 'testtabelle': Meshgenesistesttabelle().tabelle(),
                                                       'formtraining': Meshgenesisformtrainingtabelle().tabelle(laeufe),
                                                       'formvarianten': Meshgenesisformvariantentabelle().tabelle(varianten),
                                                       'jetzt': Meshgenesisformtrainingjetzt.zeilen(laeufe, Meshgenesisformvarianten.summe(varianten), Meshgenesisformtraining.gpu()),
                                                       'hinweis': Meshgenesisattrappe.HINWEIS if attrappe else ''})

    @staticmethod
    @require_GET
    def seite(request, job):
        gefunden = Meshgenesisattrappe.job(job)
        if gefunden is None:
            raise Http404('Kein Job %s' % job)
        if job != gefunden['id']:
            return redirect(Meshgenesistabelle.adresse(gefunden))
        lauf = Meshgenesisdaten.lauf(gefunden['ordner'])
        hinweis = Meshgenesisdaten.hinweis(lauf, modell=gefunden.get('modell')) if lauf else Meshgenesisattrappe.HINWEIS
        if lauf is None and gefunden.get('paar'):
            # Trainingspaar ohne Ergebnis: Start und Ziel sind echt — kein Band „Attrappe“ (Edgar sah es am 18.10.2026 auf dem neuen Job Matt1).
            hinweis = Meshgenesisdaten.HINWEIS_PAAR % {'ergebnis': Meshgenesisdaten.OHNE_ERGEBNIS_PAAR}
        # Zeile oben: wann gerechnet, wie lange (22.10.2026, `Meshgenesislaufzeile`).
        from ..dienste.meshgenesislaufzeile import Meshgenesislaufzeile
        return render(request, 'meshgenesis.html', {'hinweis': hinweis, 'echt': lauf is not None or bool(gefunden.get('paar')), 'job': gefunden,
                                                 'texturweg': Meshgenesistexturwahl.gewaehlt(), 'texturkante': Meshgenesistexturwahl.KANTE,
                                                 'laufzeile': Meshgenesislaufzeile.teile(gefunden)})

    @staticmethod
    @require_GET
    def jobs(request):
        return JsonResponse({'jobs': Meshgenesisdaten.jobs()})

    @staticmethod
    @require_GET
    def proben(request, job):
        """Echt, wenn ein fertiger Trainingslauf liegt (`Meshgenesisdaten`), sonst die Attrappe — die Seite unterscheidet am Feld `attrappe`."""
        gefunden = Meshgenesisattrappe.job(job)
        if gefunden is None:
            raise Http404('Kein Job %s' % job)
        daten = Meshgenesisdaten.proben(gefunden) or Meshgenesisattrappe.proben(gefunden['id'])
        if daten is None:
            # Die Attrappe gibt es nur für Ursula1; ein anderer Job zeigt erst nach seinem ersten fertigen Lauf etwas.
            if gefunden.get('paar'):
                return JsonResponse({'error': '%s ist ein Trainingspaar: Start (Tripo-Netz) und Ziel (Genesis-Export) liegen bereit. %s' % (gefunden['name'], Meshgenesisdaten.OHNE_ERGEBNIS_PAAR)},
                                    status=404)
            return JsonResponse({'error': 'Für %s gibt es noch keinen fertigen Trainingslauf.' % gefunden['name']}, status=404)
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def eingabe(request, job, nr):
        """Die Punktwolke der Außenfläche EINER echten Probe (4.096 Punkte mit Farbe) — die Seite holt sie erst, wenn die Probe gewählt wird."""
        gefunden = Meshgenesisattrappe.job(job)
        daten = Meshgenesisdaten.eingabe(gefunden, nr) if gefunden else None
        if daten is None:
            raise Http404('Keine Probe %s in %s' % (nr, job))
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def eingabe_dicht(request, job, nr):
        """Die dichte Start-Wolke eines Tripo-Jobs (2 Mio. Punkte, Binärpaket `Meshgenesiseingabedicht`, rund 20 MB); 404, solange `eingabe_dicht.npz` fehlt."""
        from ..dienste.meshgenesiseingabedicht import Meshgenesiseingabedicht

        gefunden = Meshgenesisattrappe.job(job)
        paket = Meshgenesiseingabedicht.paket(gefunden, nr) if gefunden else None
        if paket is None:
            raise Http404('Keine dichte Wolke für Probe %s in %s' % (nr, job))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def flaeche(request, job, nr):
        """Die gehäutete Figur EINER echten Probe als Binärpaket (`Meshgenesisflaeche`, rund 2 MB) — für die Ansichtsarten (Oberfläche, Drahtnetz, Textur …); 404, solange `flaeche.npz` fehlt."""
        gefunden = Meshgenesisattrappe.job(job)
        paket = Meshgenesisflaeche.paket(gefunden['ordner'], nr) if gefunden else None
        if paket is None:
            raise Http404('Keine Fläche für Probe %s in %s' % (nr, job))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def apose(request, job, nr):
        """Das Zwischenbild „Rig → A-Pose" EINER Probe als Binärpaket (`Meshgenesisapose`, 17.10.2026): die Fläche in der Ruhelage der Rig-Figur, ihr Rig und was das Netz der Vorstufe dort abstimmt."""
        from ..dienste.meshgenesisrig import Meshgenesisrig

        gefunden = Meshgenesisattrappe.job(job)
        lauf = Meshgenesisdaten.lauf(gefunden['ordner']) if gefunden else None
        paket = Meshgenesisapose.paket(lauf, [k['name'] for k in Meshgenesisrig.beschreibung()['knochen']]) if lauf and int(nr) == Meshgenesisapose.PROBE else None
        if paket is None:
            raise Http404('Kein Zwischenbild „Rig → A-Pose“ für Probe %s in %s' % (nr, job))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def animationsflaechen(request, job):
        """Die Flächen aller Bilder der Standardanimation in EINEM Binärpaket (`Meshgenesisflaechenanimation`, rund 40 MB, ohne Haar) — erst geholt, wenn Play die Bewegung lädt."""
        gefunden = Meshgenesisattrappe.job(job)
        daten = Meshgenesisdaten.animation(gefunden) if gefunden else None
        paket = Meshgenesisflaechenanimation.paket(gefunden['ordner'], [b['id'] for b in daten['bilder']]) if daten else None
        if paket is None:
            raise Http404('Keine Flächen der Animation für %s' % job)
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def stand(request, job):
        """Datensatz und jüngster Trainingslauf von der Platte — ECHT, nicht Attrappe; die Jobseite fragt im Takt der Einstellung (Einstellungen → Mesh-Genesis)."""
        gefunden = Meshgenesisattrappe.job(job)
        if gefunden is None:
            raise Http404('Kein Job %s' % job)
        return JsonResponse(Meshgenesisstand.lesen(gefunden))

    @staticmethod
    @require_GET
    def animation(request, job):
        """Die Bilder der Standardanimation — erst auf den ersten Klick auf Play geholt (rund 1 MB). Echt, wenn ein Lauf alle Bilder der Bewegung vorhergesagt hat, sonst die Attrappe."""
        gefunden = Meshgenesisattrappe.job(job)
        daten = (Meshgenesisdaten.animation(gefunden) or Meshgenesisattrappe.animation(gefunden['id'])) if gefunden else None
        if daten is None:
            raise Http404('Kein Job %s' % job)
        return JsonResponse(daten)
