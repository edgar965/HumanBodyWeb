# Handgeschrieben am 2026-10-03: die Handwertung „Qualität" wird ein Rang statt einer Note.
#
# Edgar: „die qualität soll eindeutig sein, also keine zwei Läufe mit gleicher Qualität. Beste Qualität: 1."
# Bis 0055 stand in `qualitaet_mesh` / `qualitaet_3d` eine Note 1–5 (5 = sehr gut, Gleichstände erlaubt). Jetzt steht dort der RANG:
# 1 = der beste Lauf, jede Zahl höchstens einmal je Spalte (`Engine2d3dKleiderrang`). Einmalige Umrechnung der vorhandenen Noten:
# die höhere Note zuerst, bei Gleichstand der ältere Auftrag zuerst (nach `created_at`, dann `kennung`) — die Reihenfolge innerhalb einer
# Note ist damit festgelegt, nicht gemessen. Nicht umkehrbar: aus Rängen lassen sich die alten Noten nicht zurückholen.

from django.db import migrations

SPALTEN = ('qualitaet_mesh', 'qualitaet_3d')


def noten_zu_raengen(apps, schema_editor):
    Auftrag = apps.get_model('core', 'Engine2d3dKleiderauftrag')
    for spalte in SPALTEN:
        zeilen = list(Auftrag.objects.filter(**{spalte + '__isnull': False}).values_list('pk', spalte, 'created_at', 'kennung'))
        zeilen.sort(key=lambda z: (-z[1], z[2], z[3]))
        for rang, (pk, _note, _erstellt, _kennung) in enumerate(zeilen, start=1):
            Auftrag.objects.filter(pk=pk).update(**{spalte: rang})


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_engine2d3dkleiderauftrag_qualitaetsspalten'),
    ]

    operations = [
        migrations.RunPython(noten_zu_raengen, migrations.RunPython.noop),
    ]
