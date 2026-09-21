# -*- coding: utf-8 -*-
u"""Die Daz-Garderobe im Browser hat Edgars Kategorien (20.09.2026), am Quelltext.

`Genesis9garderobe.fuellen` gruppiert nicht mehr nach den drei Arten, sondern
nach `Genesis9garderobekategorien.gruppen` (Stand vom Server), jede Zeile
bekommt das Kontextmenü (`menue`), und die Adresse im Browser ist dieselbe,
die Django unter `g9_figur_garderobe_kategorien` führt. Ohne den letzten
Abgleich liefe ein umbenannter Endpunkt in eine 404, die `Serverabruf` nur
in die Konsole schriebe (siehe `Kleiderverwaltung`, 17.08.2026).

Warum Quelltext statt Node: `genesis9garderobe.js` hängt über `Genesis9lauf`
an `state.js` → `three/addons`, das löst der Node-Harness nicht auf.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer').joinpath(*teile).read_text(encoding='utf-8')


class GarderobeKategorienJsTest(SimpleTestCase):
    databases = set()

    def test_1_liste_gruppiert_nach_kategorien_mit_menue(self):
        text = quelltext('scene', 'genesis9', 'genesis9garderobe.js')
        self.assertNotIn('static ARTEN', text, 'die festen drei Arten sind durch Kategorien ersetzt')
        self.assertIn('Genesis9garderobekategorien.gruppen(stuecke, stand)', text)
        # 21.09.2026: alle zu, offen nur die Kategorie des in der Szene gewählten Stücks
        # (seine Zeile markiert), Kopf in der Schrift von „Farbe / Material".
        self.assertIn("Genesis9garderobekategorien.offen(titel, eigene.some(s => s.id === gewaehlt))", text)
        self.assertIn("if (stueck.id === gewaehlt) zeile.classList.add('selected')", text)
        self.assertIn('<summary class="aufklappkopf">', text)
        kategorien = quelltext('scene', 'genesis9', 'genesis9garderobekategorien.js')
        self.assertIn('static offen(name, enthaeltGewaehltes = false)', kategorien)
        self.assertNotIn('static ZU', kategorien, 'keine Ausnahme mehr — die Vorgabe ist zu')
        self.assertIn('Genesis9garderobekategorien.menue(zeile, stueck, neuzeichnen)', text)
        self.assertIn('escapeHtml(titel)', text, 'Kategorienamen kommen von Edgar — als Text')

    def test_2_adresse_stimmt_mit_django_ueberein(self):
        text = quelltext('scene', 'genesis9', 'genesis9garderobekategorien.js')
        adresse = reverse('g9_figur_garderobe_kategorien')
        self.assertIn(f"static ADRESSE = '{adresse}';", text)
        self.assertIn("Kontextmenue.binden(zeile", text)
        self.assertIn("'Neue Kategorie …'", text)
