# -*- coding: utf-8 -*-
"""`Anatomiekarten`: was zu den gerechneten Karten des Anatomie-Stücks gehört — Schlüssel, Ablage, Zurücknehmen (11./12.10.2026), geprüft in Node.

Edgar (Bild, „cute girl DAZ" auf dunkler Haut): „Skin änderung funktioniert nicht bei der Scham, die neue skin Textur erscheint da nicht, nur die farbe." Die Karten selbst rechnet
`Anatomiebacken` (Texel für Texel, siehe `test_js_anatomiezuordnung.py`); diese Klasse hält, was dazu gehört. Körper, Stück und Karten sind Attrappen mit den Feldern, die der Code
liest; echte Texturen tragen `isTexture`.

1. `schluessel` hängt an der Form des Stücks und an den Karten der Haut-Gruppen: gleiche Karten → gleicher Schlüssel, eine andere Farbkarte (andere Haut) → anderer; ohne Farbkarte
   (kein `isTexture`) oder ohne Haut-Gruppe → `null` (dann bleibt `Anatomiehaut` bei der einfachen Farbe).
2. `gebacken` liefert die Karten nur zum passenden Schlüssel; ein Fehlschlag (`{leer: true}`) ist ein Ergebnis, kein „noch nicht gerechnet".
3. `setzen` legt die gerechneten Karten auf das Material (dieselben Objekte, Farbe kopiert) und merkt die eigenen; `traegtHaut` ist dann wahr — das schaltet an der Naht die
   Angleichung aus (`Hautloch.randAbgleichen`: Relief der Haut, flache Hautfarbe am Rand des Stücks, beides machte den Übergang verschwommen, Edgar 12.10.2026).
4. `zuruecknehmen` bringt Normalen und Rauheit zurück, danach `traegtHaut` falsch; ein zweites `setzen` überschreibt die gemerkten eigenen Karten nicht.
5. Kam nach dem Umstellen die EIGENE Karte wieder an das Material (`m.map` ≠ `hautKarte`), trägt das Stück keine Haut mehr — die Angleichung muss dann wieder gelten.
6. `original` nennt die eigenen Karten auch, solange gerechnete auf dem Material liegen.

Sabotage-Gegenprobe: in `schluessel` die Karten-uuids streichen → Fall 1 rot; in `traegtHaut` den Vergleich `m.map ===` weglassen → Fall 5 rot; `delete ablage.hautKarte` in
`zuruecknehmen` streichen → Fall 4 rot. Nicht gelaufen (12.10.2026) — läuft nur auf Ansage.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

KARTEN = Jsmodul('gemeinsam', 'anatomiekarten.js')

ATTRAPPEN = """
const farbe = (r, g, b) => ({ r, g, b, copy(o) { this.r = o.r; this.g = o.g; this.b = o.b; return this; } });
let zaehler = 0;
const textur = (name) => ({ isTexture: true, name, uuid: 'tex-' + name + '-' + (++zaehler) });
const hautmaterial = (map) => ({ userData: { gruppe: 'Body' }, map, normalMap: textur('n'), roughnessMap: textur('r'), color: farbe(1, 1, 1) });
const koerper = (...materialien) => ({ bodyMesh: { material: materialien } });
const stueck = () => ({ geometry: { uuid: 'geo-1' }, material: { map: textur('atlas'), normalMap: textur('stueck-n'), roughnessMap: textur('stueck-r'),
                                                                   color: farbe(0.8, 0.7, 0.6), userData: {}, needsUpdate: false } });
const gebacken = () => ({ map: textur('neu'), normalMap: textur('neu-n'), roughnessMap: textur('neu-r'), farbe: farbe(0.5, 0.5, 0.5), schluessel: 'x' });
"""


class AnatomiekartenTest(SimpleTestCase):
    databases = set()

    def test_schluessel_und_gebacken(self):
        skript = ATTRAPPEN + """
const { Anatomiekarten: K } = await import(MODUL);
const a = textur('farbe'), n = stueck();
const inst = koerper(hautmaterial(a));

// 1. Schlüssel
const s1 = K.schluessel(inst, n, ['Body']);
pruefe('Schlüssel vorhanden', typeof s1, 'string');
pruefe('derselbe Zustand, derselbe Schlüssel', K.schluessel(inst, n, ['Body']), s1);
pruefe('andere Haut (andere Farbkarte), anderer Schlüssel', K.schluessel(koerper(hautmaterial(textur('farbe2'))), n, ['Body']) !== s1, true);
pruefe('andere Form des Stücks', K.schluessel(inst, { geometry: { uuid: 'geo-2' } }, ['Body']) !== s1, true);
pruefe('Karte ohne isTexture', K.schluessel(koerper(hautmaterial({ name: 'ohne' })), n, ['Body']), null);
pruefe('Gruppe zählt nicht als Haut', K.schluessel(inst, n, ['Legs']), null);

// 2. gebacken
n.userData = { anatomieGebacken: { map: 1, schluessel: s1 } };
pruefe('passender Schlüssel', K.gebacken(n, s1).map, 1);
pruefe('anderer Schlüssel', K.gebacken(n, 'anders'), null);
n.userData = { anatomieGebacken: { leer: true, schluessel: s1 } };
pruefe('Fehlschlag ist ein Ergebnis', K.gebacken(n, s1).leer, true);
pruefe('noch nichts gerechnet', K.gebacken({ userData: {} }, s1), null);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = KARTEN.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_setzen_traegt_haut_und_zuruecknehmen(self):
        skript = ATTRAPPEN + """
const { Anatomiekarten: K } = await import(MODUL);
const netz = stueck(), m = netz.material, g = gebacken();
const eigeneKarte = m.map, eigeneN = m.normalMap, eigeneR = m.roughnessMap;
const ablage = { karte: m.map, farbe: m.color };
m.userData.anatomieHaut = ablage;

// 6. original vor dem Setzen: die Karten des Materials
pruefe('original: Karte', K.original(m).karte === eigeneKarte, true);
pruefe('trägt keine Haut', K.traegtHaut(netz), false);

// 3. setzen
K.setzen(m, g, ablage);
pruefe('Farbkarte', m.map === g.map, true);
pruefe('Normalen', m.normalMap === g.normalMap, true);
pruefe('Rauheit', m.roughnessMap === g.roughnessMap, true);
pruefe('Farbe kopiert', [m.color.r, m.color.g, m.color.b], [0.5, 0.5, 0.5]);
pruefe('trägt Haut', K.traegtHaut(netz), true);
pruefe('original: eigene Karten, solange gerechnete liegen', [K.original(m).karte === eigeneKarte, K.original(m).normalen === eigeneN, K.original(m).rauheit === eigeneR], [true, true, true]);

// 4. zweites setzen (andere Haut) überschreibt die eigenen nicht
K.setzen(m, gebacken(), ablage);
pruefe('eigene Normalen nach zweitem setzen gemerkt', ablage.normalen === eigeneN, true);
K.zuruecknehmen(m, ablage);
pruefe('Normalen zurück', m.normalMap === eigeneN, true);
pruefe('Rauheit zurück', m.roughnessMap === eigeneR, true);
pruefe('trägt keine Haut mehr', K.traegtHaut(netz), false);

// 5. die eigene Karte kommt nach dem Umstellen wieder an das Material
K.setzen(m, g, ablage);
pruefe('wieder Haut', K.traegtHaut(netz), true);
m.map = eigeneKarte;
pruefe('eigene Karte am Material: keine Haut', K.traegtHaut(netz), false);
pruefe('Mehrere Materialien, keines trägt', K.traegtHaut({ material: [{ userData: {} }, m] }), false);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = KARTEN.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
