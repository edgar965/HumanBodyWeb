# -*- coding: utf-8 -*-
"""Mesh3daitestfaelleendpunkte — die Testfälle der Kleider-KI für Test- und Jobseite (22.10.2026, `Mesh3daitestfaelle`).

GET /api/mesh3dai/test/<kennung>/testfaelle/<geschlecht>/   die Testfälle der Stücke dieses Tests ({"testfaelle": dict | null})
GET /api/mesh3dai/<job>/testfaelle/                         die Trainingstests des Jobs ({"testfaelle": [dict, …]}, jüngster zuerst)
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.mesh3daitestfaelle import Mesh3daitestfaelle

__all__ = ['Mesh3daitestfaelleendpunkte']


class Mesh3daitestfaelleendpunkte:
    @staticmethod
    @require_GET
    def test(request, kennung, geschlecht):
        return JsonResponse({'testfaelle': Mesh3daitestfaelle.fuer_test(kennung, geschlecht)})

    @staticmethod
    @require_GET
    def job(request, job):
        return JsonResponse({'testfaelle': Mesh3daitestfaelle.fuer_job(job)})
