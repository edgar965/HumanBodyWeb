# -*- coding: utf-8 -*-
"""Liste der Foto-Analyse-Auftraege.

Aus ``core/api/seiten.py`` herausgeloest (Umbau 17.08.2026). Die Seite ist
keine reine Vorlage: Textur- und Silhouettenpfad stehen nicht als Spalte am
Auftrag, sondern in dessen ``result_json`` — die Liste muss sie also erst
herausholen.

Die zwei Pfade werden dem Auftragsobjekt angehaengt, statt ein zweites
Wörterbuch je Zeile aufzubauen: Die Vorlage liest sie als ``job.texture_path``
neben den echten Modellfeldern, ohne zweiten Namen fuer dieselbe Zeile.
"""

import json
import logging

from django.views.generic import TemplateView

logger = logging.getLogger('core')


class FotoauftraegeSeite(TemplateView):
    """Alle Auftraege mit ihren Ergebnispfaden."""

    template_name = 'photo_analysis_jobs.html'

    #: Schluessel in ``result_json`` -> Feldname fuer die Vorlage.
    ERGEBNISPFADE = (('texture_path', 'texture_path'),
                     ('silhouette_path', 'silhouette_path'))

    def get_context_data(self, **kwargs):
        from ..models import PhotoAnalysisJob
        auftraege = list(PhotoAnalysisJob.objects.all())
        for auftrag in auftraege:
            ergebnis = self._ergebnis(auftrag)
            for schluessel, feld in self.ERGEBNISPFADE:
                setattr(auftrag, feld, ergebnis.get(schluessel, ''))
        return dict(super().get_context_data(**kwargs), jobs=auftraege)

    @staticmethod
    def _ergebnis(auftrag):
        """``result_json`` als Wörterbuch — kaputtes JSON ergibt eine leere
        Zeile, nicht eine leere Seite."""
        if not auftrag.result_json:
            return {}
        try:
            daten = json.loads(auftrag.result_json)
        except (json.JSONDecodeError, TypeError):
            logger.warning('[fotoauftraege] result_json unlesbar: Auftrag %s',
                           auftrag.pk)
            return {}
        return daten if isinstance(daten, dict) else {}


#: Name gesetzt, siehe ``core/api/seiten.py``.
photo_analysis_jobs_page = FotoauftraegeSeite.as_view()
photo_analysis_jobs_page.__name__ = 'photo_analysis_jobs_page'
