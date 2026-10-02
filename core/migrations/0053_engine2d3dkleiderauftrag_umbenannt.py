# -*- coding: utf-8 -*-
"""Haar Engine -> Engine2d3dKleider (02.10.2026): Modell und Tabelle umbenennen, gespeicherte Pfade nachziehen.

Die Ordner `3DObjects/haarengineauftraege` und `output/Export/HaarEngine` heißen jetzt `3DObjects/engine2d3dkleiderauftraege` und
`output/Export/Engine2d3dKleider`; `eingang` und `ergebnis` der Aufträge nennen sie als absolute Pfade.
"""
from django.db import migrations

TAUSCH = (('haarengineauftraege', 'engine2d3dkleiderauftraege'), ('HaarEngine', 'Engine2d3dKleider'))


def _tauschen(wert, richtung):
    if isinstance(wert, str):
        for alt, neu in TAUSCH:
            wert = wert.replace(*((alt, neu) if richtung > 0 else (neu, alt)))
        return wert
    if isinstance(wert, list):
        return [_tauschen(e, richtung) for e in wert]
    if isinstance(wert, dict):
        return {k: _tauschen(v, richtung) for k, v in wert.items()}
    return wert


def _umstellen(richtung):
    def lauf(apps, schema_editor):
        modell = apps.get_model('core', 'Engine2d3dKleiderauftrag')
        for eintrag in modell.objects.all():
            geaendert = []
            for feld in ('eingang', 'ergebnis'):
                alt = getattr(eintrag, feld)
                neu = _tauschen(alt, richtung)
                if neu != alt:
                    setattr(eintrag, feld, neu)
                    geaendert.append(feld)
            if geaendert:
                modell.objects.filter(pk=eintrag.pk).update(**{f: getattr(eintrag, f) for f in geaendert})
    return lauf


class Migration(migrations.Migration):
    dependencies = [('core', '0052_haarengine_status_wartet')]

    operations = [
        migrations.RenameModel('Haarengineauftrag', 'Engine2d3dKleiderauftrag'),
        migrations.RunPython(_umstellen(1), _umstellen(-1)),
    ]
