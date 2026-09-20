# -*- coding: utf-8 -*-
"""`Figurwahlzeile`: das Markup einer Listenzeile des Figurwahl-Dialogs.

WARUM (11.09.2026): Die Zeile wurde aus `figurwahldialog.js` herausgelöst, als
der Dialog eine zweite Aufgabe bekam (Modell austauschen, `lage: false`,
eigene `kennung`). Geprüft wird, was beim Herauslösen verloren gehen kann:
Anzeige und Unterzeile werden maskiert, Pflege-Knöpfe kommen nur mit
`pflege`, ohne Unterzeile gibt es kein leeres `preset-sub`.

Dazu (20.09.2026, Edgar: „mach ein Kontextmenü, mit dem ich das Modell
löschen kann"): Das Rechtsklickmenü einer Zeile trägt Umbenennen und Löschen
und ruft dieselbe `pflegen(was)` wie die Knöpfe. Sabotage-Gegenprobe: in
`menue` `pflegen('loeschen')` durch `pflegen('umbenennen')` ersetzen → rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'figurwahlzeile.js')

SKRIPT = """
const { Figurwahlzeile } = await import(MODUL);
const pruefe = (was, ist) => { if (!ist) throw new Error(was); };
const M = Figurwahlzeile.markup;

const mit = M({ name: 'Elf.glb', anzeige: 'Elf <b>', unterzeile: 'weiblich · 2.5 MB' }, true);
pruefe('Anzeige maskiert', mit.includes('Elf &lt;b&gt;') && !mit.includes('Elf <b>'));
pruefe('Unterzeile', mit.includes('class="preset-sub">weiblich · 2.5 MB<'));
pruefe('Umbenennen-Knopf', mit.includes('data-tun="umbenennen"'));
pruefe('Löschen-Knopf', mit.includes('data-tun="loeschen"'));

const ohne = M({ name: 'Female1', anzeige: 'Female1', unterzeile: '' }, false);
pruefe('keine Unterzeile', !ohne.includes('preset-sub'));
pruefe('keine Werkzeuge', !ohne.includes('data-tun') && !ohne.includes('eintragswerkzeuge'));
pruefe('Name steht drin', ohne.includes('>Female1<'));

// --- Rechtsklickmenü: zwei Einträge, jeder ruft `pflegen` mit seinem Werkzeug ---
const gerufen = [];
const menue = Figurwahlzeile.menue((was) => gerufen.push(was));
pruefe('zwei Einträge', menue.length === 2);
pruefe('Texte', menue.map(e => e.text).join(',') === 'Umbenennen,Löschen');
pruefe('Symbole', menue.map(e => e.symbol).join(',') === 'fa-pen,fa-trash');
menue[1].tun(); menue[0].tun();
pruefe('Löschen ruft pflegen(loeschen), Umbenennen pflegen(umbenennen)',
       gerufen.join(',') === 'loeschen,umbenennen');
console.log(JSON.stringify({ok: true}));
"""


class FigurwahlzeileTest(SimpleTestCase):
    databases = set()

    def test_zeile_maskiert_den_namen_und_zeigt_werkzeuge_nur_mit_unterzeile(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
