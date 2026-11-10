# -*- coding: utf-8 -*-
"""Meshgenesistestfaelleendpunkte — die Testfälle der Kleider-KI für Test- und Jobseite (22.10.2026, `Meshgenesistestfaelle`).

GET /api/meshgenesis/test/<kennung>/testfaelle/<geschlecht>/   die Testfälle der Stücke dieses Tests ({"testfaelle": dict | null})
GET /api/meshgenesis/<job>/testfaelle/                         die Trainingstests des Jobs ({"testfaelle": [dict, …]}, jüngster zuerst)
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.meshgenesistestfaelle import Meshgenesistestfaelle

__all__ = ['Meshgenesistestfaelleendpunkte']


class Meshgenesistestfaelleendpunkte:
    @staticmethod
    @require_GET
    def test(request, kennung, geschlecht):
        return JsonResponse({'testfaelle': Meshgenesistestfaelle.fuer_test(kennung, geschlecht)})

    @staticmethod
    @require_GET
    def job(request, job):
        return JsonResponse({'testfaelle': Meshgenesistestfaelle.fuer_job(job)})
