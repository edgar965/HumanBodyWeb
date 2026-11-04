/**
 * Modellpruefunghaar — Haarkarten ohne Deckkraft, Teil der Klasse „haare“ des Modell Checks (`Modellpruefung`; aus `modellpruefung.js` abgeteilt 02.11.2026 abends).
 * Ein Material mit Bild, aber ohne Alpha, Schnitt, Durchsicht, Alpha-to-Coverage oder Linien lässt auf Haarkarten den Kartengrund als Blöcke stehen (Amala charm_hair,
 * Birne sallymae_hair, 02.11.2026). Ein geschlossenes Haarnetz trägt sein Bild ohne Deckkraft zu Recht — bis 02.11.2026 abends zählte jedes Netz, das Haar von
 * „Edgar 2d-3d-AI“ (2d-3d-AI) fiel mit 100 % durch. Karten = das größte zusammenhängende Stück trägt weniger als KARTEN_ANTEIL der Dreiecke; gemessen 02.11.2026 im
 * MCP-Tab (Netze aus `/api/character/genesis9-figur/garderobe/<id>/netz/`): edgar_2d_3d_ai_haar 92 %, aldora_hair 37, sallymae_hair 11, charm_hair 10, toulouse_hair 5,
 * hs_viola_hair_g9 0; die Kappe der g9_base_dforce_pixie_hair (eigenes Netz) 100. Der Anteil der Randkanten trennte nicht (edgar 3,1 %, aldora 3,4, sallymae 4,9).
 * Gezählt werden nur Dreiecke mit UV-Fläche (`mitBild`): eigen_herrenhaar (Strähnen als Bänder, ~30.000 Stücke) zeigt je Dreieck mit allen drei Ecken auf die Mitte
 * eines Farbfelds (`core/dienste/herrenhaarstueck.py`, `flaechen_uv = [nummer] * 3`) — ein Bildpunkt je Dreieck, kein Kartengrund; es fiel mit 100 % durch
 * (Edgar, Modell Check an „Edgar“, 02.11.2026 spätabends: „warum ist das Haar rot“).
 */
export class Modellpruefunghaar {

    static KARTEN_ANTEIL = 0.5;
    static UV_FLAECHE = 1e-9;               // doppelte Dreiecksfläche in UV-Einheiten²; darunter zeigt das Dreieck einen Bildpunkt

    /** Anteil der Frisur-Dreiecke auf Haarkarten (`karten`), deren Material ein Bild trägt, aber keine Deckkraft. */
    static ohneDeckkraft(netze) {
        let alle = 0, ohne = 0;
        for (const o of netze) {
            const stoffe = [o.material].flat(), g = o.geometry, zahl = g.index ? g.index.count : g.attributes.position.count;
            const gruppen = g.groups.length ? g.groups : [{ start: 0, count: zahl, materialIndex: 0 }];
            let kart = null;
            for (const gr of gruppen) {
                const m = stoffe[gr.materialIndex] || stoffe[0];
                alle += gr.count;
                if (!(m?.map && !m.alphaMap && !(m.alphaTest > 0) && !m.transparent && !m.alphaToCoverage && !m.wireframe)) continue;
                kart ??= Modellpruefunghaar.karten(o);
                if (kart) ohne += Modellpruefunghaar.mitBild(g, gr.start, Math.min(gr.count, zahl - gr.start));
            }
        }
        return alle ? +(ohne / alle).toFixed(3) : 0;
    }

    /** Indexplätze (3 je Dreieck) im Bereich `start … start + zahl`, deren Dreieck eine UV-Fläche hat — nur dort kann der Kartengrund stehen. */
    static mitBild(g, start, zahl) {
        const uv = g.attributes.uv, idx = g.index ? g.index.array : null;
        if (!uv) return 0;
        let mit = 0;
        for (let t = start; t + 2 < start + zahl; t += 3) {
            const a = idx ? idx[t] : t, b = idx ? idx[t + 1] : t + 1, c = idx ? idx[t + 2] : t + 2;
            const ux = uv.getX(b) - uv.getX(a), uy = uv.getY(b) - uv.getY(a), vx = uv.getX(c) - uv.getX(a), vy = uv.getY(c) - uv.getY(a);
            if (Math.abs(ux * vy - uy * vx) > Modellpruefunghaar.UV_FLAECHE) mit += 3;
        }
        return mit;
    }

    /** Sind es Haarkarten? Punkte gleicher Lage verschweißt (three.js trennt sie an UV-Nähten), dann die Stücke über die Dreiecke vereinigt. */
    static karten(o) {
        const g = o.geometry, pos = g.attributes.position.array, m = pos.length / 3, idx = g.index ? g.index.array : Uint32Array.from({ length: m }, (_, i) => i);
        const nummer = new Map(), eltern = [], neu = new Int32Array(m);
        for (let i = 0; i < m; i++) {
            const s = `${Math.round(pos[3 * i] * 1e5)},${Math.round(pos[3 * i + 1] * 1e5)},${Math.round(pos[3 * i + 2] * 1e5)}`;
            if (!nummer.has(s)) { nummer.set(s, eltern.length); eltern.push(eltern.length); }
            neu[i] = nummer.get(s);
        }
        const finde = (x) => { while (eltern[x] !== x) { eltern[x] = eltern[eltern[x]]; x = eltern[x]; } return x; };
        for (let t = 0; t < idx.length; t += 3) { const a = finde(neu[idx[t]]); eltern[finde(neu[idx[t + 1]])] = a; eltern[finde(neu[idx[t + 2]])] = a; }
        const groesse = new Map();
        for (let t = 0; t < idx.length; t += 3) { const r = finde(neu[idx[t]]); groesse.set(r, (groesse.get(r) || 0) + 1); }
        let groesste = 0;
        for (const z of groesse.values()) groesste = Math.max(groesste, z);
        return groesste < Modellpruefunghaar.KARTEN_ANTEIL * idx.length / 3;
    }
}
