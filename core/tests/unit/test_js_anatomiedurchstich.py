"""Anatomiedurchstich — was vom Genital außen durch den Stoff sticht (19.10.2026), geprüft in Node an einer Kunstfläche.

Edgar, 19.10.2026: „mach das auch für männliche Genitalien mit Matt0" — der Penis stach unter der Hose hervor (GC Pants Wool: 13–28 % des Stücks
sichtbar). `Anatomiedurchstich.aussen` nennt die Punkte, deren Strecke zum Anker (Mitte der Randpunkte) einen Stoff kreuzt; `Anatomieverdeckung`
blendet deren Dreiecke aus — nur unter blickdichtem Stoff (`Stoffdeckung`, eigener Test: unter Spitze sah man die Löcher).

1. Stoff als Ebene z = 0,05 vor dem Anker (0, 0, 0): ein Punkt bei z = 0,08 liegt außen, einer bei z = 0,03 innen.
2. Ein Punkt seitlich neben dem Stoffstück (Strecke kreuzt die Ebene außerhalb des Dreiecks): innen.
3. `dreiecke`: ein Dreieck mit einer äußeren und zwei bedeckten Ecken fällt; eines ohne äußere Ecke bleibt; eines mit äußerer und freier Ecke bleibt
   (sonst ein Loch an der Stoffkante — `asian_female_shorts`, dunkle Kerben im Chrome).
6. Strecke entlang der Normale: der Anker liegt seitlich auf Höhe des Punkts (z = 0,06, die Strecke zu ihm läuft neben dem Stoff her) — mit der Normale
   (0, 0, 1) liegt der Punkt außen (der Stoff 10 mm dahinter, INNEN 15 mm), ohne Normalen innen; ein Punkt 30 mm vor dem Stoff bleibt innen.
7. `lagen`: 10 mm unter dem Stoff (z = 0,04, Normale nach oben, VORN 20 mm) bedeckt, seitlich daneben (x = 0,5) frei, über ihm (z = 0,08) außen —
   mit `weite` 0,1 m zählt die Strecke zum Anker für ihn nicht (er hängt nicht über den Rand hinaus), er ist dann frei.
4. `anker`: Mitte der Randpunkte eines Fächers aus vier Dreiecken mit erhabener Mitte — das Mittel des Rands, nicht aller Punkte.
5. Ohne Stoff: kein Punkt außen.

Sabotage (gedacht, nicht gefahren): in `_kreuzt` die Prüfung `w < 1 - eps` weglassen → ein Punkt HINTER dem Stoff, dessen Strecke den Stoff erst
jenseits des Ankers träfe, zählte außen (Fall 1, dritter Punkt bei z = −0,02); die Normale nach AUSSEN statt nach innen laufen lassen → Fall 6 rot;
in `dreiecke` die freie Ecke nicht prüfen → Fall 3 rot.
Geschrieben 19.10.2026, gelaufen auf Ansage: grün.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'anatomiedurchstich.js')


class AnatomiedurchstichTest(SimpleTestCase):
    databases = set()

    def test_punkte_vor_dem_stoff_liegen_aussen(self):
        skript = """
const { Anatomiedurchstich: D } = await import(MODUL);
const fehler = [];
const pruefe = (name, ist, soll) => { if (JSON.stringify(ist) !== JSON.stringify(soll)) fehler.push(`${name}: ${JSON.stringify(ist)} statt ${JSON.stringify(soll)}`); };
// Stoff: zwei Dreiecke, Quadrat −0,1 … 0,1 in x/y bei z = 0,05
const stoff = { pos: Float32Array.from([-0.1, -0.1, 0.05, 0.1, -0.1, 0.05, 0.1, 0.1, 0.05, -0.1, 0.1, 0.05]), index: Uint32Array.from([0, 1, 2, 0, 2, 3]) };
const anker = [0, 0, 0];
// 1./2. Punkte: außen (z 0,08), innen (z 0,03), hinter dem Anker (z −0,02), seitlich neben dem Stoff (x 0,5, z 0,08)
const pos = Float32Array.from([0.01, 0.02, 0.08, 0.01, 0.02, 0.03, 0.01, 0.02, -0.02, 0.5, 0.0, 0.08]);
pruefe('außen/innen', Array.from(D.aussen(pos, anker, [stoff])), [1, 0, 0, 0]);
// 3. Dreiecke über den Lagen [außen, bedeckt, bedeckt, frei]
const lg = Uint8Array.from([D.AUSSEN, D.BEDECKT, D.BEDECKT, D.FREI]);
pruefe('Dreiecke', Array.from(D.dreiecke(Uint32Array.from([0, 1, 2, 1, 2, 3, 0, 1, 3]), lg)), [1, 0, 0]);
// 7. Lagen: unter, neben, über dem Stoff
const drei = Float32Array.from([0, 0, 0.04, 0.5, 0, 0.04, 0, 0, 0.08]), oben = Float32Array.from([0, 0, 1, 0, 0, 1, 0, 0, 1]);
pruefe('Lagen', Array.from(D.lagen(drei, anker, [stoff], oben)), [D.BEDECKT, D.FREI, D.AUSSEN]);
pruefe('Weite', Array.from(D.lagen(drei, anker, [stoff], oben, 0.1)), [D.BEDECKT, D.FREI, D.FREI]);// 6. Normale: Punkte 10 mm und 30 mm vor dem Stoff, Anker seitlich auf Höhe des ersten
const flach = Float32Array.from([0, 0, 0.06, 0.02, 0, 0.08]), auf = Float32Array.from([0, 0, 1, 0, 0, 1]), seitlich = [0.5, 0, 0.06];
pruefe('Normale', [Array.from(D.aussen(flach, seitlich, [stoff], auf)), Array.from(D.aussen(flach, seitlich, [stoff]))], [[1, 0], [0, 0]]);
// 4. Anker: Fächer mit erhabener Mitte (0, 0, 0,05) und Rand bei ±0,1 in z = 0 — das Mittel ALLER Punkte läge bei z = 0,01
const faecher = Float32Array.from([0, 0, 0.05, 0.1, 0, 0, 0, 0.1, 0, -0.1, 0, 0, 0, -0.1, 0]);
const a = D.anker(faecher, Uint32Array.from([0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 1]));
pruefe('Anker', a.map(v => Math.round(v * 1000) / 1000), [0, 0, 0]);
// 5. ohne Stoff
pruefe('ohne Stoff', Array.from(D.aussen(pos, anker, [])), [0, 0, 0, 0]);
console.log(JSON.stringify({ ok: !fehler.length, fehler }));
"""
        ausgabe = MODUL.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
