# -*- coding: utf-8 -*-
"""Theatre: Eine gemerkte Animation, die es nicht mehr gibt, blockiert nicht.

BEFUND (Edgar, 15.09.2026): „Animation laden fehlgeschlagen: Retarget API
error: 404 Not Found" — ein `alert` beim Öffnen der Theatre-Seite. In den
Einstellungen stand `Results/nussie1`; der Ordner heißt seit 12.09. `A_Results`,
und der Server sucht seit 13.09. bewusst nicht in anderen Ordnern.

Zwei Stellen, beide nur als Quelltext prüfbar (beide Module importieren
`three`):

1. `fetchRetarget` gibt dem Fehler den `status` und den Klartext der Antwort
   (`BVH not found: Results/nussie1`) statt „404 Not Found".
2. `Animationslauf.laden` ruft bei 404 keinen `alert`, sondern
   `fehltMelden` — der Hinweis steht über der BVH-Bibliothek (`#anim-fehlt`)
   und verschwindet, sobald eine Animation geladen wurde.

Sabotage-Gegenprobe: in `animationslauf.js` `fehler.status === 404` durch
`false` ersetzen → Fall 2 rot.
"""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

WURZEL = Path(settings.BASE_DIR)
RETARGET = WURZEL / 'static' / 'viewer' / 'retarget_hybrid.js'
LAUF = WURZEL / 'TheatreJS' / 'src' / 'studio' / 'animationslauf.js'
BUNDLE = WURZEL / 'static' / 'theatre' / 'theatre-app.js'


class TheatreAnimationFehltTest(SimpleTestCase):
    def test_retarget_fehler_traegt_status_und_klartext(self):
        text = RETARGET.read_text(encoding='utf-8')
        self.assertIn('fehler.status = resp.status;', text)
        self.assertIn('throw await retargetFehler(resp);', text)
        # Keine HTML-Fehlerseite als Meldung.
        self.assertIn("!text.includes('<')", text)

    def test_404_ohne_alert_mit_hinweis_in_der_liste(self):
        text = LAUF.read_text(encoding='utf-8')
        fang = text.index('} catch (fehler) {')
        self.assertLess(
            text.index('fehler.status === 404', fang),
            text.index("alert('Animation laden fehlgeschlagen", fang),
        )
        self.assertIn("zeile.id = 'anim-fehlt';", text)
        self.assertIn("document.getElementById('anim-fehlt')?.remove();", text)
        # Der Hinweis nennt, was fehlt, und sagt, was zu tun ist.
        self.assertIn('gibt es nicht mehr — bitte eine andere Animation wählen', text)

    def test_bundle_ist_gebaut(self):
        """`npm run build` nach der Änderung — sonst läuft die alte Fassung."""
        self.assertIn('anim-fehlt', BUNDLE.read_text(encoding='utf-8'))
