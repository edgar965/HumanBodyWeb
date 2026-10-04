# -*- coding: utf-8 -*-
"""Engine2d3dKleiderrang — die Rangliste hinter einer Qualitätsspalte von „2D3D Kleider" (03.10.2026).

Edgar: „die qualität soll eindeutig sein, also keine zwei Läufe mit gleicher Qualität. Beste Qualität: 1. falls eine Zahl dazwischenkommt,
ändere die Qualitäten anderer Läufe."

Eine Spalte ist eine Rangliste der bewerteten Läufe, lückenlos 1 … n. Setzt man einem Lauf den Rang k, wird er an diese Stelle der Liste
gesetzt: Wer ab dort stand, rückt um eins nach hinten; stand der Lauf vorher selbst irgendwo in der Liste, rücken die Läufe dazwischen auf.
Ein Rang hinter dem Ende der Liste (k > n + 1) wird der nächste freie (n + 1) — Lücken gibt es nicht. „Nicht bewertet" nimmt den Lauf aus
der Liste, die Läufe dahinter rücken auf.

`umordnen` rechnet nur auf einer Liste (ohne Datenbank); `setzen` liest die Spalte, ordnet um und schreibt NUR die Zeilen, deren Rang sich
ändert, und nur diese eine Spalte (`QuerySet.update`: weder `updated_at` — der `?v=` der Tabellenbilder — noch ein anderes Feld ändert sich,
und ein Lauf, der gerade seine JSON-Felder zurückschreibt, wird nicht berührt).
"""

from django.db import transaction

from ..models import Engine2d3dKleiderauftrag

__all__ = ['Engine2d3dKleiderrang']


class Engine2d3dKleiderrang:
    @staticmethod
    def umordnen(reihenfolge, lauf, rang):
        """Die neue Rangliste: `reihenfolge` = Läufe von Rang 1 an (darf `lauf` schon enthalten), `rang` = gewünschter Rang oder `None`
        (aus der Liste nehmen). Gibt eine neue Liste zurück, `reihenfolge` bleibt unverändert."""
        rest = [x for x in reihenfolge if x != lauf]
        if rang is None:
            return rest
        stelle = min(max(int(rang), 1), len(rest) + 1) - 1
        return rest[:stelle] + [lauf] + rest[stelle:]

    @classmethod
    def setzen(cls, job, spalte, rang):
        """Setzt den Rang von `job` in `spalte` und gibt die ganze Rangliste zurück: `{str(pk): rang}` für jeden bewerteten Lauf (ohne `job`
        bei `rang = None`). Bei Gleichstand in alten Daten gilt der ältere Auftrag zuerst (wie die Umrechnung in Migration 0056)."""
        with transaction.atomic():
            zeilen = list(
                Engine2d3dKleiderauftrag.objects.filter(**{spalte + '__isnull': False})
                .order_by(spalte, 'created_at', 'kennung')
                .values_list('pk', spalte)
            )
            vorher = dict(zeilen)
            neu = cls.umordnen([pk for pk, _ in zeilen], job.pk, rang)
            ergebnis = {}
            for stelle, pk in enumerate(neu, start=1):
                ergebnis[pk] = stelle
                if vorher.get(pk) != stelle:
                    Engine2d3dKleiderauftrag.objects.filter(pk=pk).update(**{spalte: stelle})
            if rang is None and job.pk in vorher:
                Engine2d3dKleiderauftrag.objects.filter(pk=job.pk).update(**{spalte: None})
        return {str(pk): stelle for pk, stelle in ergebnis.items()}
