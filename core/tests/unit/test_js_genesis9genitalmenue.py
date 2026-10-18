# -*- coding: utf-8 -*-
u"""Das Kontextmenü der Kästen im Bereich „Genitalien" (18.10.2026), am Quelltext.

Edgar mit Bild des Kastens „Daz · weiblich — Daz Anatomie Frau": „mach mir bei den Einträgen im Tab ein Kontextmenü mit dem ich die
Assets löschen, verschieben und umbenennen kann". Die Kästen sind Stücke der Garderobe; das Menü nimmt deren Einträge
(`Genesis9garderobekategorien.verschiebenEintrag`, `Genesis9garderobepflege`), und Kasten und Garderobenzeile ziehen gegenseitig mit.

Warum Quelltext statt Node: `genesis9genitalien.js` hängt über `Genesis9garderobe` an `state.js` → `three/addons`, das löst der
Node-Harness nicht auf (wie `test_js_genesis9garderobe.py`).
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer').joinpath(*teile).read_text(encoding='utf-8')


class GenitalmenueJsTest(SimpleTestCase):
    databases = set()

    def test_1_kasten_und_zeile_tragen_das_menue(self):
        text = quelltext('charakter', 'genesis9', 'genesis9genitalien.js')
        self.assertIn("import { Genesis9genitalmenue } from './genesis9genitalmenue.js';", text)
        self.assertIn('Genesis9genitalmenue.binden(kasten, zeile, inst, stueck, Genesis9genitalien.titel);', text)
        # Das Menü braucht den Stand der Kategorien, auch wenn die Garderobe nie gebaut wurde.
        self.assertIn('Genesis9garderobekategorien.stand()', text)
        menue = quelltext('charakter', 'genesis9', 'genesis9genitalmenue.js')
        self.assertIn("kasten.querySelector(':scope > summary')", menue, 'der Kopf, nicht der ganze Kasten (darin liegen die Regler)')
        self.assertIn('Kontextmenue.binden(ziel, eintraege)', menue)

    def test_2_drei_eintraege_wie_in_der_garderobe(self):
        menue = quelltext('charakter', 'genesis9', 'genesis9genitalmenue.js')
        self.assertIn('Genesis9garderobekategorien.verschiebenEintrag(', menue)
        self.assertIn("'In der Garderobe verschieben nach'", menue)
        self.assertIn("text: 'Umbenennen …'", menue)
        self.assertIn("text: 'Löschen'", menue)
        kategorien = quelltext('charakter', 'genesis9', 'genesis9garderobekategorien.js')
        self.assertIn('static verschiebenEintrag(stueck, neuzeichnen, zeile, text = \'Verschieben nach\')', kategorien)
        # Das Menü der Garderobe selbst nimmt denselben Eintrag — es gibt keine zweite Fassung der Combo-Box.
        self.assertIn('Genesis9garderobekategorien.verschiebenEintrag(stueck, neuzeichnen, zeile)', kategorien)

    def test_3_loeschen_nimmt_die_garderobenzeile_mit_und_baut_nichts_neu(self):
        menue = quelltext('charakter', 'genesis9', 'genesis9genitalmenue.js')
        self.assertIn('Genesis9garderobepflege.loeschen(stueck, null, kasten)', menue)
        self.assertNotIn('Genesis9garderobe.aktualisieren', menue, 'kein Neuaufbau der Garderobe (Edgar, 18.10.2026)')
        pflege = quelltext('charakter', 'genesis9', 'genesis9garderobepflege.js')
        # Die Pflege nimmt auf dem Erfolgsweg mit, was vom Stück noch steht — ob die Zeile oder der Kasten angeklickt wurde.
        self.assertIn('Genesis9garderobepflege._mitnehmen(stueck);', pflege)
        self.assertIn('Genesis9garderobezeile.entfernen(zeile)', pflege)
        self.assertIn('Genesis9genitalkasten.entfernen(stueck.id)', pflege)
        zeile = quelltext('charakter', 'genesis9', 'genesis9garderobezeile.js')
        self.assertIn('static zeileVon(kennung)', zeile)
        self.assertIn('g9-kleid-${kennung}', zeile, 'dieselbe Kennung wie das Häkchen in `Genesis9garderobe._zeile`')

    def test_4_umbenennen_setzt_kopf_und_garderobenname_neu(self):
        pflege = quelltext('charakter', 'genesis9', 'genesis9garderobepflege.js')
        self.assertIn('Genesis9kleidung.stuecke()', pflege, 'der Name kommt aus dem frischen Katalog (leer = Name der Bibliothek)')
        self.assertIn('Genesis9garderobezeile.benennen(', pflege)
        self.assertIn('Genesis9genitalkasten.benennen(stueck.id, neu.name)', pflege)
        kasten = quelltext('charakter', 'genesis9', 'genesis9genitalkasten.js')
        self.assertIn('text.textContent = `${kasten._titel(kasten._stueck)} `;', kasten)
        genitalien = quelltext('charakter', 'genesis9', 'genesis9genitalien.js')
        self.assertIn('static titel(stueck)', genitalien)
        self.assertIn('Genesis9genitalien.titel(stueck)', genitalien, 'der Kopf wird über `titel` gebaut — sonst weicht er nach dem Umbenennen ab')

    def test_5_auch_von_der_garderobe_aus_zieht_der_kasten_mit(self):
        """Edgar, 18.10.2026: „es sollen doch ALLE Assets umbenannt und gelöscht werden können?" — in beide Richtungen, ohne Neuladen."""
        pflege = quelltext('charakter', 'genesis9', 'genesis9garderobepflege.js')
        self.assertIn("import { Genesis9genitalkasten } from './genesis9genitalkasten.js';", pflege)
        # Umbenennen: nur nach Annahme durch den Server nachziehen (`_senden` meldet es).
        self.assertIn("if (await Genesis9garderobepflege._senden(stueck, 'umbenennen'", pflege)
        self.assertIn('await Genesis9garderobepflege._nachziehen(stueck);', pflege)
        # Löschen ohne bekannte Zeile (Weg ohne Sofort-Ausblenden) nimmt den Kasten genauso mit.
        self.assertIn("if (await Genesis9garderobepflege._senden(stueck, 'loeschen'", pflege)
        kasten = quelltext('charakter', 'genesis9', 'genesis9genitalkasten.js')
        self.assertNotIn('\nimport ', kasten, 'ohne Importe: die Pflege nimmt den Kasten, der Bereich hängt über das Menü an der Pflege (kein Ring)')
        self.assertIn("kasten.dataset.stueck === kennung", kasten)
        menue = quelltext('charakter', 'genesis9', 'genesis9genitalmenue.js')
        self.assertIn('Genesis9genitalkasten.merken(kasten, stueck, titel);', menue, 'der Kasten kennt sein Stück und seinen Kopftext')
