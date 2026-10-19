# -*- coding: utf-8 -*-
"""Mesh3daiendpunkte — Seiten und Daten von „Mesh3D-AI“ (14.10.2026, Dashboard → Mesh3D-AI).

Edgar: „Mach das Menü Dashboard – Mesh3D-AI und zeige mir den Input, gewünschten Trainingsoutput und Output, mit Dummies für Ursula1.“ Danach: „wir werden mehrere Jobs außer Ursula haben …
eine Hauptansicht mit einer Tabelle wie bei /mesh-3D/, und die Unterjobs wie Ursula1 als Unterseiten“.

GET /mesh-3D-AI/                         die Liste der Jobs (Tabelle)
GET /mesh-3D-AI/<job>/                   die Jobseite (Eingabe · gewünschte Ausgabe · Ausgabe des Netzes); die Kennung ist klein geschrieben, eine andere Schreibweise leitet um
GET /api/mesh3dai/jobs/                  die Jobs (Kurzstand)
GET /api/mesh3dai/<job>/proben/          die Proben des Jobs — echt (Datensatz + Vorhersagen des jüngsten fertigen Laufs, `Mesh3daidaten`), sonst die Attrappe
GET /api/mesh3dai/<job>/eingabe/<nr>/    die Punktwolke EINER echten Probe (4.096 Punkte mit Farbe und Teil)
GET /api/mesh3dai/<job>/flaeche/<nr>/    die gehäutete Figur EINER echten Probe (Binärpaket, `Mesh3daiflaeche`) für die Ansichtsarten
GET /api/mesh3dai/<job>/apose/<nr>/      das Zwischenbild „Rig → A-Pose“ der Probe, auf der die Vorstufe lief (Binärpaket, `Mesh3daiapose`)
GET /api/mesh3dai/<job>/stand/           ECHT: fertige Proben des Datensatzes und der jüngste Trainingslauf (Platte), dazu der Abfragetakt in Minuten
GET /api/mesh3dai/<job>/animation/       die Bilder der Standardanimation
GET /api/mesh3dai/<job>/animation/flaechen/   die Flächen aller Bilder der Standardanimation (Binärpaket, ohne Haar)

Die Jobseite fragt `proben` ab; heute liefert beides die Attrappe (`Mesh3daiattrappe`), später die echte Ablage — die Seite merkt den Unterschied nur am Feld `attrappe`.
"""

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from ..dienste.mesh3daiapose import Mesh3daiapose
from ..dienste.mesh3daiattrappe import Mesh3daiattrappe
from ..dienste.mesh3daidaten import Mesh3daidaten
from ..dienste.mesh3daiflaeche import Mesh3daiflaeche
from ..dienste.mesh3daiflaechenanimation import Mesh3daiflaechenanimation
from ..dienste.mesh3daiformtraining import Mesh3daiformtraining
from ..dienste.mesh3daiformtrainingjetzt import Mesh3daiformtrainingjetzt
from ..dienste.mesh3daiformtrainingtabelle import Mesh3daiformtrainingtabelle
from ..dienste.mesh3daiformvarianten import Mesh3daiformvarianten
from ..dienste.mesh3daiformvariantentabelle import Mesh3daiformvariantentabelle
from ..dienste.mesh3daistand import Mesh3daistand
from ..dienste.mesh3daitabelle import Mesh3daitabelle
from ..dienste.mesh3daitesttabelle import Mesh3daitesttabelle
from ..dienste.mesh3daitexturwahl import Mesh3daitexturwahl

__all__ = ['Mesh3daiendpunkte']


class Mesh3daiendpunkte:
    @staticmethod
    @require_GET
    def liste(request):
        # Das Band „Attrappe“ nur, solange ein Job noch keinen fertigen Lauf hat (seit 15.10.2026 zeigt ein Job mit Lauf echte Daten).
        attrappe = any(Mesh3daidaten.lauf(j['ordner']) is None for j in Mesh3daiattrappe.stammdaten())
        # Zweiter Reiter „Test“ (16.10.2026): Netze ohne Trainingsdaten (`Mesh3daitesttabelle`); dritter „Formtraining“ (18.10.2026): Läufe der gemeinsamen Netze und Formvarianten.
        laeufe = Mesh3daiformtraining.laeufe()
        varianten = Mesh3daiformvarianten.alle()
        return render(request, 'mesh3dai_liste.html', {'tabelle': Mesh3daitabelle().tabelle(), 'testtabelle': Mesh3daitesttabelle().tabelle(),
                                                       'formtraining': Mesh3daiformtrainingtabelle().tabelle(laeufe),
                                                       'formvarianten': Mesh3daiformvariantentabelle().tabelle(varianten),
                                                       'jetzt': Mesh3daiformtrainingjetzt.zeilen(laeufe, Mesh3daiformvarianten.summe(varianten), Mesh3daiformtraining.gpu()),
                                                       'hinweis': Mesh3daiattrappe.HINWEIS if attrappe else ''})

    @staticmethod
    @require_GET
    def seite(request, job):
        gefunden = Mesh3daiattrappe.job(job)
        if gefunden is None:
            raise Http404('Kein Job %s' % job)
        if job != gefunden['id']:
            return redirect(Mesh3daitabelle.adresse(gefunden))
        lauf = Mesh3daidaten.lauf(gefunden['ordner'])
        hinweis = Mesh3daidaten.hinweis(lauf, modell=gefunden.get('modell')) if lauf else Mesh3daiattrappe.HINWEIS
        if lauf is None and gefunden.get('paar'):
            # Trainingspaar ohne Ergebnis: Start und Ziel sind echt — kein Band „Attrappe“ (Edgar sah es am 18.10.2026 auf dem neuen Job Matt1).
            hinweis = Mesh3daidaten.HINWEIS_PAAR % {'ergebnis': Mesh3daidaten.OHNE_ERGEBNIS_PAAR}
        return render(request, 'mesh3dai.html', {'hinweis': hinweis, 'echt': lauf is not None or bool(gefunden.get('paar')), 'job': gefunden,
                                                 'texturweg': Mesh3daitexturwahl.gewaehlt(), 'texturkante': Mesh3daitexturwahl.KANTE})

    @staticmethod
    @require_GET
    def jobs(request):
        return JsonResponse({'jobs': Mesh3daidaten.jobs()})

    @staticmethod
    @require_GET
    def proben(request, job):
        """Echt, wenn ein fertiger Trainingslauf liegt (`Mesh3daidaten`), sonst die Attrappe — die Seite unterscheidet am Feld `attrappe`."""
        gefunden = Mesh3daiattrappe.job(job)
        if gefunden is None:
            raise Http404('Kein Job %s' % job)
        daten = Mesh3daidaten.proben(gefunden) or Mesh3daiattrappe.proben(gefunden['id'])
        if daten is None:
            # Die Attrappe gibt es nur für Ursula1; ein anderer Job zeigt erst nach seinem ersten fertigen Lauf etwas.
            if gefunden.get('paar'):
                return JsonResponse({'error': '%s ist ein Trainingspaar: Start (Tripo-Netz) und Ziel (Genesis-Export) liegen bereit. %s' % (gefunden['name'], Mesh3daidaten.OHNE_ERGEBNIS_PAAR)},
                                    status=404)
            return JsonResponse({'error': 'Für %s gibt es noch keinen fertigen Trainingslauf.' % gefunden['name']}, status=404)
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def eingabe(request, job, nr):
        """Die Punktwolke der Außenfläche EINER echten Probe (4.096 Punkte mit Farbe) — die Seite holt sie erst, wenn die Probe gewählt wird."""
        gefunden = Mesh3daiattrappe.job(job)
        daten = Mesh3daidaten.eingabe(gefunden, nr) if gefunden else None
        if daten is None:
            raise Http404('Keine Probe %s in %s' % (nr, job))
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def flaeche(request, job, nr):
        """Die gehäutete Figur EINER echten Probe als Binärpaket (`Mesh3daiflaeche`, rund 2 MB) — für die Ansichtsarten (Oberfläche, Drahtnetz, Textur …); 404, solange `flaeche.npz` fehlt."""
        gefunden = Mesh3daiattrappe.job(job)
        paket = Mesh3daiflaeche.paket(gefunden['ordner'], nr) if gefunden else None
        if paket is None:
            raise Http404('Keine Fläche für Probe %s in %s' % (nr, job))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def apose(request, job, nr):
        """Das Zwischenbild „Rig → A-Pose" EINER Probe als Binärpaket (`Mesh3daiapose`, 17.10.2026): die Fläche in der Ruhelage der Rig-Figur, ihr Rig und was das Netz der Vorstufe dort abstimmt."""
        from ..dienste.mesh3dairig import Mesh3dairig

        gefunden = Mesh3daiattrappe.job(job)
        lauf = Mesh3daidaten.lauf(gefunden['ordner']) if gefunden else None
        paket = Mesh3daiapose.paket(lauf, [k['name'] for k in Mesh3dairig.beschreibung()['knochen']]) if lauf and int(nr) == Mesh3daiapose.PROBE else None
        if paket is None:
            raise Http404('Kein Zwischenbild „Rig → A-Pose“ für Probe %s in %s' % (nr, job))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def animationsflaechen(request, job):
        """Die Flächen aller Bilder der Standardanimation in EINEM Binärpaket (`Mesh3daiflaechenanimation`, rund 40 MB, ohne Haar) — erst geholt, wenn Play die Bewegung lädt."""
        gefunden = Mesh3daiattrappe.job(job)
        daten = Mesh3daidaten.animation(gefunden) if gefunden else None
        paket = Mesh3daiflaechenanimation.paket(gefunden['ordner'], [b['id'] for b in daten['bilder']]) if daten else None
        if paket is None:
            raise Http404('Keine Flächen der Animation für %s' % job)
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def stand(request, job):
        """Datensatz und jüngster Trainingslauf von der Platte — ECHT, nicht Attrappe; die Jobseite fragt im Takt der Einstellung (Einstellungen → Mesh3D-AI)."""
        gefunden = Mesh3daiattrappe.job(job)
        if gefunden is None:
            raise Http404('Kein Job %s' % job)
        return JsonResponse(Mesh3daistand.lesen(gefunden))

    @staticmethod
    @require_GET
    def animation(request, job):
        """Die Bilder der Standardanimation — erst auf den ersten Klick auf Play geholt (rund 1 MB). Echt, wenn ein Lauf alle Bilder der Bewegung vorhergesagt hat, sonst die Attrappe."""
        gefunden = Mesh3daiattrappe.job(job)
        daten = (Mesh3daidaten.animation(gefunden) or Mesh3daiattrappe.animation(gefunden['id'])) if gefunden else None
        if daten is None:
            raise Http404('Kein Job %s' % job)
        return JsonResponse(daten)
