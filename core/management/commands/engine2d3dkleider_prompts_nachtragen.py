# -*- coding: utf-8 -*-
"""`manage.py engine2d3dkleider_prompts_nachtragen <id> <nachrichten.json>` — die Nachrichten des Nutzers den Runden eines Auftrags „2D3D Kleider"
zuordnen und in `iterationen/prompts.json` ablegen (`Engine2d3dKleiderprompts.nachtragen`).

`nachrichten.json` ist die Liste `[{zeit, text}]` (Ortszeit `YYYY-MM-DD HH:MM:SS`), z. B. aus dem Transkript der Sitzung gezogen. Jede Nachricht
kommt zu der ersten Runde, die NACH ihr begann; was nach der letzten Runde kam, steht unter `offen`. Wiederholbar.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Ordnet Nachrichten des Nutzers den Runden eines Auftrags zu (iterationen/prompts.json).'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help='Die Kennung (UUID) des Auftrags')
        parser.add_argument('nachrichten', help='JSON-Datei mit [{zeit, text}]')

    def handle(self, *args, **options):
        from core.daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        from core.dienste.engine2d3dkleiderprompts import Engine2d3dKleiderprompts
        from core.models import Engine2d3dKleiderauftrag

        job = Engine2d3dKleiderauftrag.objects.filter(id=options['job_id']).first()
        if job is None:
            raise CommandError('Kein Auftrag „2D3D Kleider" %s' % options['job_id'])
        datei = Path(options['nachrichten'])
        if not datei.is_file():
            raise CommandError('Datei fehlt: %s' % datei)
        nachrichten = json.loads(datei.read_text(encoding='utf-8'))
        runden = [e for e in (job.ergebnis or {}).get('iterationen') or [] if e.get('zeit')]
        zugeordnet, offen = Engine2d3dKleiderprompts(Engine2d3dKleiderablage(job.kennung)).nachtragen(nachrichten, runden)
        self.stdout.write('%d Nachrichten, %d Runden: %d zugeordnet, %d offen' % (len(nachrichten), len(runden), zugeordnet, offen))
