# -*- coding: utf-8 -*-
"""`manage.py dazgeograft_einbauen [--geschlecht mann|frau]` — das Daz-Geograft „Anatomical Elements" als eigenes Stück der Garderobe (10.10.2026).

Wandelt `data/Daz 3D/Genesis 9/Anatomical Elements Male|Female` (Genesis 9 Starter Essentials Expansion; die Bibliothek wird nur gelesen) in ein Stück
„Daz Anatomie Mann|Frau" in der eigenen Bibliothek (`Dazgeograft`). Lässt sich beliebig oft wiederholen: das Stück wird neu geschrieben, seine Regler beim
nächsten Aufruf neu gebaut.
"""

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Baut das Daz-Geograft (Anatomical Elements) als Stück der eigenen Garderobe.'

    def add_arguments(self, parser):
        parser.add_argument('--geschlecht', default='mann', choices=['mann', 'frau'])
        parser.add_argument('--realism', type=float, default=1.0, help='Wert des Morphs „Realism HD" (Vorgabe des Produkts: 1)')
        parser.add_argument('--nur-varianten', action='store_true', help='Nur die Charakter-Varianten neu schreiben (das Stück bleibt, Sekunden statt Minuten)')
        parser.add_argument('--nur-gewichte', action='store_true',
                            help='Nur die Hautbindung des vorhandenen Stücks durch Dazs eigene ersetzen (`Dazgeograft.gewichte`), alles andere bleibt; die alte .dsf kommt nach ProjektTemp/sicherungen/')

    def handle(self, *args, **options):
        from core.dienste.dazgeograft import Dazgeograft

        if options['nur_varianten']:
            self._varianten(options['geschlecht'], Dazgeograft)
            return
        if options['nur_gewichte']:
            self._gewichte(options['geschlecht'], options['realism'], Dazgeograft)
            return
        try:
            bilanz = Dazgeograft(options['geschlecht']).bauen(options['realism'])
        except ValueError as fehler:
            raise CommandError(str(fehler)) from fehler
        self.stdout.write('Stück %s: %d Punkte, %d Flächen — %s' % (bilanz['stueck'], bilanz['punkte'], bilanz['flaechen'], bilanz['duf']))
        self.stdout.write('Bericht: %s' % bilanz['bericht'])

    def _varianten(self, geschlecht, dazgeograft):
        """Die Varianten des vorhandenen Stücks neu schreiben (`Dazgeograftvarianten.schreiben`)."""
        from core.dienste.dazgeograftvarianten import Dazgeograftvarianten
        from Genesis9.pfade import G9pfade

        stueck = G9pfade.eigene() / 'People' / 'Genesis 9' / 'Clothing' / 'EIGEN' / ('%s.duf' % dazgeograft.NAMEN[geschlecht][0])
        if not stueck.is_file():
            raise CommandError('Das Stück %s fehlt — erst ohne --nur-varianten bauen' % stueck.name)
        namen = Dazgeograftvarianten.schreiben(stueck, geschlecht, dazgeograft.GRUPPEN[geschlecht])
        self.stdout.write('Varianten (%d): %s' % (len(namen), ', '.join(namen)))

    def _gewichte(self, geschlecht, realism, dazgeograft):
        """Nur die `SkinBinding` der vorhandenen Stück-.dsf neu (28.10.2026): ein ganzer Neubau liefe mit dem Code nach dem Bau (11.10.2026 08:37) und änderte mehr als die
        Gewichte. Punkte der Datei in cm, um den Boden der Grundfigur gehoben (`G9stueckstarr`); Ring aus der `.ersetzt.json`. Die alte Datei bleibt als Sicherung."""
        import gzip
        import json
        import shutil
        import time

        import numpy as np
        from django.conf import settings

        from core.atomic_write import AtomarSchreiber
        from core.dienste.dazgeograftquelle import Dazgeograftquelle
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.pfade import G9pfade

        anzeige = dazgeograft.NAMEN[geschlecht][0]
        dsf = G9pfade.eigene() / 'data' / 'EIGEN' / anzeige / ('EIGEN_%s.dsf' % anzeige.replace(' ', '_'))
        ersetzt = G9pfade.eigene() / 'People' / 'Genesis 9' / 'Clothing' / 'EIGEN' / ('%s.ersetzt.json' % anzeige)
        if not dsf.is_file() or not ersetzt.is_file():
            raise CommandError('Das Stück %s fehlt (%s) — erst ohne --nur-gewichte bauen' % (anzeige, dsf))
        roh = dsf.read_bytes()
        gepackt = roh[:2] == b'\x1f\x8b'
        doc = json.loads(gzip.decompress(roh) if gepackt else roh)
        geo = doc['geometry_library'][0]
        punkte = np.asarray(geo['vertices']['values'], dtype=np.float64) * 0.01 - np.array([0.0, G9eigenstueck.koerper()[4], 0.0])
        flaechen = np.asarray([f[2:] for f in geo['polylist']['values']], dtype=object)
        dreiecke = np.asarray([[f[0], f[i], f[i + 1]] for f in flaechen for i in range(1, len(f) - 1)], dtype=np.int64)
        ring = json.loads(ersetzt.read_text(encoding='utf-8'))['loch']['ring']
        g = dazgeograft(geschlecht)
        quelle = Dazgeograftquelle(geschlecht)
        kaefig = quelle.punkte + float(realism) * quelle.morph(g.REALISM)
        gewichte = g.gewichte(g.figur(), punkte, dreiecke, np.asarray(ring['lage'], dtype=np.float64), np.asarray(ring['punkte'], dtype=np.int64), quelle, kaefig)
        haut = next(m for m in doc['modifier_library'] if m.get('id') == 'SkinBinding')['skin']
        alt = {j['id']: round(sum(w for _i, w in j['node_weights']['values']), 1) for j in haut['joints']}
        haut['joints'] = [{'id': name, 'node': '#%s' % name, 'node_weights': {'count': len(werte), 'values': werte}} for name, werte in gewichte.items()]
        neu = {name: round(sum(w for _i, w in werte), 1) for name, werte in gewichte.items()}
        sicherung = settings.TOOLS_ROOT / 'ProjektTemp' / 'sicherungen' / 'dazgeograft'
        sicherung.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dsf, sicherung / ('%s_%s.dsf' % (dsf.stem, time.strftime('%Y%m%d_%H%M%S'))))
        text = json.dumps(doc, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        AtomarSchreiber.bytes_schreiben(dsf, gzip.compress(text) if gepackt else text)
        self.stdout.write('%s: Gewichtssummen je Knochen vorher %s, nachher %s' % (anzeige, alt, neu))
        self.stdout.write('Bericht: %s — Sicherung in %s' % (g.gewichte_bericht, sicherung))
