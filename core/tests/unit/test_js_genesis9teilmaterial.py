# -*- coding: utf-8 -*-
"""`Genesis9teilmaterial`: Glanz, Rauheit, Relief, Deckkraft, Feuchte je Teil (09.10.2026), geprüft in Node.

Edgar: „die Augen sind glasig / grau" (Glanz 1 bei Rauheit 0,6 legt einen Schleier über Iris und Pupille),
dann „mach mir Einstellungen, wo ich Glanz, Rauheit usw. ändern kann — auch bei Augenbrauen".

1. Die Augen haben einen eigenen Standard (Rauheit 0,1, Glanz 0,25, Feuchte 1, Tränenfilm 0,4 — die
   Glasschichten sind klar, die Deckkraft ist die Stärke der Spiegelung); die Werte des Presets (1 / 0,6)
   bleiben als `userData.teilStandard` gemerkt.
2. Die anderen Teile bleiben, wie das Preset sie lieferte, bis jemand etwas stellt.
3. `setzen` legt den Wert sofort aufs Material und in `inst.teilmaterial` (neues Objekt: die gespeicherte
   Figur hält eine flache Kopie).
4. Ein Wert gilt nach einem Neubau der Materialien wieder (`anwenden`) — und nach einem spät geladenen Bild
   (`userData.teilnach`: die Rauheitskarte setzt `roughness = 1`).
5. „Auf Standard" (`null` / `zuruecksetzen`) nimmt den eigenen Wert zurück: Augen auf 0,1 / 0,25, Haut auf 1,
   Brauen auf den gemerkten Wert.
6. Ein Wert gehört nur zu seinem Teil: Haut berührt keine Nägel, Augen nicht die Brauen.
7. Das Vorzeichen der Normalenkarte von DirectX (`normalScale.y < 0`) bleibt beim Relief.
8. `felder` meldet `verfuegbar` (ein Material ohne Glanz-Eigenschaft) und `eigen`.
9. Die Rauheit von Haut, Nägeln und Mund ist ein Faktor auf den Ausgangswert des Materials (Kopf mit Karte 1,
   Körper 0,6): 1 = wie geliefert, ein Schieber verändert beide im gleichen Verhältnis.

10. Die Brauen hängen am Netz (`userData.anhang`), nicht am Gruppennamen: `hairPhysicalShader1SG` („MB Olesia Brows Apply") und `Layer1`/`Layer2`
    (Kin) bekommen Deckkraft, Glanz und Rauheit wie `Eyebrows_…`; ein Material gleichen Namens am Körper nicht (10.10.2026).

Dazu die Deckung durch alle Schichten (Modell, Speichern, Katalog, Server): ein neues Feld, das nur an einer
Stelle fehlt, geht beim Speichern still verloren (`artefakte-benennen.md`).

Sabotage-Gegenprobe: `standard: 0.25` am Auge streichen → Fall 1 rot; in `auflegen` den Haken `teilnach`
weglassen → Fall 4 rot; das Vorzeichen in `_setzen` streichen → Fall 7 rot; `_zurueck` nicht rufen → Fall 5
rot; in `_passt` die Gruppe ignorieren → Fall 6 rot; `teilmaterial` aus `Genesis9Figur.toJSON` nehmen →
`test_teilmaterial_geht_durch_alle_schichten` rot. Nicht gelaufen (09.10.2026).
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9teilmaterial.js')

SKRIPT = """
const { Genesis9teilmaterial: T } = await import(MODUL);
const material = (gruppe, o = {}) => ({
    userData: { gruppe }, roughness: o.r ?? 0.6, specularIntensity: o.s ?? 1, opacity: o.o ?? 1,
    normalScale: { x: 1, y: o.y ?? 1, set(a, b) { this.x = a; this.y = b; } },
    roughnessMap: o.karte ? {} : null, needsUpdate: false,
});
const figur = () => {
    const m = {
        augL: material('Eye Left'), augR: material('Eye Right'),
        feuchte: material('EyeMoisture Left', { r: 0.05, s: 1, o: 0.12 }),
        traene: material('Tear', { r: 0.05, s: 1, o: 0.12 }),
        kopf: material('Head', { r: 1, karte: true }), nagel: material('Fingernails', { r: 1, karte: true }),
        koerper: material('Body', { r: 0.6 }), brauen: material('Eyebrows_Primary', { r: 0, s: 0 }),
    };
    return { m, bodyMesh: { material: [m.kopf, m.nagel, m.koerper] }, anhangNetze: {
        augen: { material: [m.feuchte, m.augL, m.augR] }, brauen: { material: [m.brauen] },
        traene: { material: [m.traene] } } };
};

// 1. Standard der Augen (klare Glasschichten: Stärke der Spiegelung), Preset-Werte gemerkt
let inst = figur(); T.anwenden(inst);
pruefe('Auge Rauheit', inst.m.augL.roughness, 0.1);
pruefe('Auge Glanz', inst.m.augR.specularIntensity, 0.25);
pruefe('Feuchte', inst.m.feuchte.opacity, 1);
pruefe('Tränenfilm', inst.m.traene.opacity, 0.4);
const gemerkt = inst.m.augL.userData.teilStandard;
pruefe('Preset gemerkt', [gemerkt.glanz, gemerkt.rauheit], [1, 0.6]);

// 2. Die anderen Teile bleiben
pruefe('Kopf unberührt', inst.m.kopf.roughness + '/' + inst.m.kopf.specularIntensity, '1/1');
pruefe('Brauen unberührt', inst.m.brauen.roughness + '/' + inst.m.brauen.opacity, '0/1');

// 3. setzen
T.setzen(inst, 'augen', 'glanz', 0.6);
pruefe('Glanz gestellt', inst.m.augL.specularIntensity + '/' + inst.m.augR.specularIntensity, '0.6/0.6');
pruefe('im Speicher', inst.teilmaterial, { augen: { glanz: 0.6 } });
const vorher = inst.teilmaterial.augen;
T.setzen(inst, 'augen', 'rauheit', 0.3);
pruefe('neues Objekt', vorher === inst.teilmaterial.augen, false);

// 4. Neubau: frische Materialien, gleiche Figur
const frisch = figur(); frisch.teilmaterial = inst.teilmaterial; T.anwenden(frisch);
pruefe('nach Neubau', frisch.m.augL.specularIntensity + '/' + frisch.m.augL.roughness, '0.6/0.3');
T.setzen(frisch, 'haut', 'rauheit', 0.5);
frisch.m.kopf.roughness = 1;                      // das Rauheitsbild kommt spät und setzt 1
frisch.m.kopf.userData.teilnach();
pruefe('nach spätem Bild', frisch.m.kopf.roughness, 0.5);

// 5. Auf Standard
T.setzen(frisch, 'haut', 'rauheit', null);
pruefe('Haut zurück', frisch.m.kopf.roughness, 1);
T.setzen(frisch, 'brauen', 'deckkraft', 0.4);
pruefe('Brauen gestellt', frisch.m.brauen.opacity, 0.4);
T.setzen(frisch, 'brauen', 'deckkraft', null);
pruefe('Brauen zurück', frisch.m.brauen.opacity, 1);
T.zuruecksetzen(frisch, 'augen');
pruefe('Augen zurück', frisch.m.augL.specularIntensity + '/' + frisch.m.augL.roughness, '0.25/0.1');
pruefe('Speicher leer', frisch.teilmaterial, {});

// 6. Ein Wert gehört nur zu seinem Teil
inst = figur(); T.anwenden(inst);
T.setzen(inst, 'haut', 'glanz', 0.2);
pruefe('Haut', inst.m.kopf.specularIntensity, 0.2);
pruefe('Nägel unberührt', inst.m.nagel.specularIntensity, 1);
pruefe('Augen unberührt', inst.m.augL.specularIntensity, 0.25);
T.setzen(inst, 'naegel', 'glanz', 0.7);
pruefe('Nägel', inst.m.nagel.specularIntensity, 0.7);

// 7. Relief behält das Vorzeichen der DirectX-Normalen
inst = figur(); inst.m.kopf.normalScale.set(1, -1); T.anwenden(inst);
T.setzen(inst, 'haut', 'relief', 1.5);
pruefe('Relief mit Vorzeichen', inst.m.kopf.normalScale.x + '/' + inst.m.kopf.normalScale.y, '1.5/-1.5');

// 8. felder
inst = figur(); T.anwenden(inst);
const f = Object.fromEntries(T.felder(inst, 'augen').map(x => [x.feld, x]));
pruefe('Standard im Feld', f.glanz.wert + '/' + f.glanz.standard + '/' + f.glanz.eigen, '0.25/0.25/false');
T.setzen(inst, 'augen', 'glanz', 0.9);
pruefe('eigen im Feld', T.felder(inst, 'augen').find(x => x.feld === 'glanz').eigen, true);
delete inst.m.augL.specularIntensity; delete inst.m.augR.specularIntensity;
pruefe('ohne Glanz-Eigenschaft', T.felder(inst, 'augen').find(x => x.feld === 'glanz').verfuegbar, false);
pruefe('Teil ohne Netz', T.felder({ anhangNetze: {} }, 'brauen').every(x => !x.verfuegbar), true);

// 9. Rauheit der Haut = FAKTOR auf den Ausgangswert: Kopf (Karte, 1) und Körper (0,6) behalten den Abstand
inst = figur(); T.anwenden(inst);
const rauh = () => T.felder(inst, 'haut').find(x => x.feld === 'rauheit');
pruefe('Faktor Standard', [rauh().standard, rauh().wert, rauh().eigen], [1, 1, false]);
T.setzen(inst, 'haut', 'rauheit', 0.5);
pruefe('Faktor 0,5', [inst.m.kopf.roughness, inst.m.koerper.roughness], [0.5, 0.3]);
T.setzen(inst, 'haut', 'rauheit', 2);
pruefe('Faktor 2', [inst.m.kopf.roughness, inst.m.koerper.roughness], [2, 1.2]);
T.setzen(inst, 'haut', 'rauheit', null);
pruefe('Faktor zurück', [inst.m.kopf.roughness, inst.m.koerper.roughness], [1, 0.6]);

// 10. Die Brauen hängen am NETZ, nicht am Gruppennamen (10.10.2026, Edgar: bei „MB Olesia Brows Apply" wirken Deckkraft und Glanz nicht —
// die Gruppe heißt `hairPhysicalShader1SG`, bei Kins Brauen `Layer1`/`Layer2`; Karten und Fasern heißen `Eyebrows_…`)
inst = figur();
inst.m.olesia = material('hairPhysicalShader1SG', { r: 0.95, s: 1, o: 0.85 });
inst.m.layer = material('Layer1', { r: 0.9, s: 1, o: 1 });
inst.m.fremd = material('hairPhysicalShader1SG', { r: 0.7 });                    // derselbe Name AM KÖRPER: gehört nicht zu den Brauen
inst.anhangNetze.brauen = { material: [inst.m.olesia, inst.m.layer] };
inst.bodyMesh.material.push(inst.m.fremd);
T.anwenden(inst);
const bf = Object.fromEntries(T.felder(inst, 'brauen').map(x => [x.feld, x]));
pruefe('Brauenfelder verfügbar', [bf.deckkraft.verfuegbar, bf.glanz.verfuegbar, bf.rauheit.verfuegbar], [true, true, true]);
T.setzen(inst, 'brauen', 'deckkraft', 0.3);
pruefe('Deckkraft auf beiden Brauenmaterialien', [inst.m.olesia.opacity, inst.m.layer.opacity], [0.3, 0.3]);
T.setzen(inst, 'brauen', 'glanz', 0.2);
pruefe('Glanz', [inst.m.olesia.specularIntensity, inst.m.layer.specularIntensity], [0.2, 0.2]);
T.setzen(inst, 'brauen', 'rauheit', 1.4);
pruefe('Rauheit', [inst.m.olesia.roughness, inst.m.layer.roughness], [1.4, 1.4]);
pruefe('gleicher Name am Körper unberührt', [inst.m.fremd.opacity, inst.m.fremd.specularIntensity, inst.m.fremd.roughness], [1, 1, 0.7]);
T.zuruecksetzen(inst, 'brauen');
pruefe('Brauen zurück', [inst.m.olesia.opacity, inst.m.olesia.roughness, inst.m.layer.opacity], [0.85, 0.95, 1]);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9teilmaterialTest(SimpleTestCase):
    databases = set()

    def test_glanz_rauheit_je_teil_standard_neubau_und_zurueck(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_teilmaterial_geht_durch_alle_schichten(self):
        u"""Modell lesen, Figur speichern, Katalog laden (Studio/Theatre), Server — überall dasselbe Feld."""
        web = Path(settings.BASE_DIR)
        orte = {
            'Modell (Konstruktor)': web / 'static/viewer/gemeinsam/genesis9modell.js',
            'Figur.toJSON': web / 'static/viewer/charakter/genesis9/genesis9figur.js',
            'Vorgabe aus dem Katalog': web / 'static/viewer/gemeinsam/genesis9vorgabe.js',
        }
        for ort, datei in orte.items():
            text = datei.read_text(encoding='utf-8')
            self.assertIn('teilmaterial', text, '%s: Feld teilmaterial fehlt' % ort)
        server = (web / 'core/api/g9figur.py').read_text(encoding='utf-8')
        self.assertIn("'teilmaterial': dict(eintrag.get('teilmaterial')", server)
        self.assertIn("'teilmaterial': figur.get('teilmaterial')", server)

    def test_der_neubau_legt_die_werte_wieder_auf(self):
        u"""`koerperAufbauen` ruft `Genesis9teilmaterial.anwenden`, der Bild-Rückruf den Haken `teilnach`."""
        web = Path(settings.BASE_DIR) / 'static/viewer/gemeinsam'
        lies = {n: (web / n).read_text(encoding='utf-8') for n in ('genesis9modell.js', 'genesis9texturen.js',
                                                                   'genesis9netz.js')}
        self.assertIn('Genesis9teilmaterial.anwenden(this)', lies['genesis9modell.js'])
        self.assertIn('teilnach', lies['genesis9texturen.js'])
        self.assertIn('Eye (Left|Right)', lies['genesis9netz.js'])

    def test_brauenmaterial_ist_einstellbar_und_weich_auch_ohne_eyebrows_im_namen(self):
        u"""`Genesis9netz` baut das Material eines Brauennetzes immer als Physical-Material (Glanz) mit weicher Deckkraft —
        „MB Olesia Brows Apply" (`hairPhysicalShader1SG`, nur `farbe`) war ein Standard-Material ohne `specularIntensity`.
        Das Netz kennt Three.js, im Test wird der Quelltext gelesen."""
        text = (Path(settings.BASE_DIR) / 'static/viewer/gemeinsam/genesis9netz.js').read_text(encoding='utf-8')
        self.assertIn('Genesis9netz.material(gruppe, brauen)', text)
        self.assertIn('static material(gruppe, brauen = false)', text)
        self.assertIn('Genesis9netz.haut(brauen || ', text)
        self.assertIn('if (brauen || Genesis9netz.WEICH.some(', text)
