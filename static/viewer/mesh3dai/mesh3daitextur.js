/**
 * Mesh3daitextur — Dummy-Texturen und das Matcap der Seite „Mesh3D-AI“ (14.10.2026): kleine Muster aus einer Leinwand, nur damit die Ansicht „Textur“ etwas zeigt (Haut mit Sommersprossen, gestreifter Stoff, Gewebe, Leder, Schachbrett).
 * Das sind KEINE Texturen von Ursula1 — der echte Datensatz bringt Farben und Texturen aus dem Modell (Edgar: „Nimm auch Farben und Texturen hinzu“); sobald es ihn gibt, liefert er die Karten und diese Klasse entfällt.
 * Alles ist deterministisch (kein `Math.random`) und wird je Muster und Farbe nur einmal gebaut (`_ablage`), damit zwölf Felder dieselbe Karte teilen und beim Neuzeichnen nichts verloren geht.
 */
import * as THREE from 'three';

export class Mesh3daitextur {
    /** Muster je Gruppe der Zeilen (Körper, Hände/Füße, Kleider, Gesicht); was fehlt, bekommt das Schachbrett. */
    static ART_NACH_GRUPPE = {
        Oberteil: 'streifen', Ärmel: 'streifen', rumpf: 'streifen', arm: 'streifen',
        Hose: 'gewebe', bein: 'gewebe', Schuhe: 'leder', fuss: 'leder',
        haut: 'haut', kopf: 'haut', hand: 'haut', 'Hand L': 'haut', 'Hand R': 'haut', 'Fuß L': 'haut', 'Fuß R': 'haut',
    };
    static GROESSE = 128;
    static _ablage = new Map();

    /** Zufallszahl 0…1 aus einer Ganzzahl (Hash), immer dieselbe. */
    static _z(i) {
        const x = Math.sin(i * 12.9898) * 43758.5453;
        return x - Math.floor(x);
    }

    /** Die Karte für `gruppe` in der Grundfarbe `farbe` (Zahl, z. B. 0xe0b394). */
    static fuer(gruppe, farbe) {
        const art = Mesh3daitextur.ART_NACH_GRUPPE[gruppe] ?? 'karo';
        const schluessel = `${art}:${farbe}`;
        if (!Mesh3daitextur._ablage.has(schluessel)) Mesh3daitextur._ablage.set(schluessel, Mesh3daitextur._bauen(art, farbe));
        return Mesh3daitextur._ablage.get(schluessel);
    }

    static _leinwand(zeichnen) {
        const n = Mesh3daitextur.GROESSE;
        const leinwand = document.createElement('canvas');
        leinwand.width = leinwand.height = n;
        zeichnen(leinwand.getContext('2d'), n);
        return leinwand;
    }

    static _bauen(art, farbe) {
        const z = Mesh3daitextur._z;
        const grund = `#${new THREE.Color(farbe).getHexString()}`;
        const leinwand = Mesh3daitextur._leinwand((g, n) => {
            g.fillStyle = grund;
            g.fillRect(0, 0, n, n);
            if (art === 'haut') {
                for (let i = 0; i < 500; i++) {
                    g.fillStyle = `rgba(90, 50, 30, ${0.05 + 0.07 * z(i + 2000)})`;
                    g.fillRect(z(i) * n, z(i + 1000) * n, 2, 2);
                }
                for (let i = 0; i < 14; i++) {
                    g.fillStyle = 'rgba(120, 70, 40, 0.35)';
                    g.beginPath();
                    g.arc(z(i + 5000) * n, z(i + 6000) * n, 1.8, 0, Math.PI * 2);
                    g.fill();
                }
            } else if (art === 'streifen') {
                g.fillStyle = 'rgba(255, 255, 255, 0.22)';
                for (let y = 0; y < n; y += 16) g.fillRect(0, y, n, 7);
            } else if (art === 'gewebe') {
                for (let k = -n; k < n; k += 5) {
                    g.strokeStyle = 'rgba(255, 255, 255, 0.14)';
                    g.beginPath(); g.moveTo(k, 0); g.lineTo(k + n, n); g.stroke();
                    g.strokeStyle = 'rgba(0, 0, 0, 0.18)';
                    g.beginPath(); g.moveTo(k + 2, n); g.lineTo(k + 2 + n, 0); g.stroke();
                }
            } else if (art === 'leder') {
                for (let i = 0; i < 700; i++) {
                    g.fillStyle = i % 2 ? 'rgba(255, 255, 255, 0.10)' : 'rgba(0, 0, 0, 0.12)';
                    g.fillRect(z(i + 7000) * n, z(i + 8000) * n, 2, 2);
                }
            } else {
                g.fillStyle = 'rgba(255, 255, 255, 0.2)';
                for (let y = 0; y < n; y += 16) for (let x = 0; x < n; x += 16) if (((x + y) / 16) % 2 === 0) g.fillRect(x, y, 16, 16);
            }
        });
        const karte = new THREE.CanvasTexture(leinwand);
        karte.colorSpace = THREE.SRGBColorSpace;
        karte.wrapS = karte.wrapT = THREE.RepeatWrapping;
        karte.repeat.set(3, 2);
        return karte;
    }

    /** Das Matcap (Blender: Solid mit MatCap): eine beleuchtete Kugel aus Grautönen; die Farbe des Materials färbt sie ein. */
    static matcap() {
        if (!Mesh3daitextur._ablage.has('matcap')) {
            const leinwand = Mesh3daitextur._leinwand((g, n) => {
                g.fillStyle = '#2a2a2a';
                g.fillRect(0, 0, n, n);
                const verlauf = g.createRadialGradient(n * 0.38, n * 0.32, n * 0.04, n / 2, n / 2, n * 0.5);
                verlauf.addColorStop(0, '#ffffff');
                verlauf.addColorStop(0.45, '#b5b5b5');
                verlauf.addColorStop(0.85, '#5a5a5a');
                verlauf.addColorStop(1, '#2a2a2a');
                g.fillStyle = verlauf;
                g.beginPath(); g.arc(n / 2, n / 2, n / 2, 0, Math.PI * 2); g.fill();
            });
            const karte = new THREE.CanvasTexture(leinwand);
            karte.colorSpace = THREE.SRGBColorSpace;
            Mesh3daitextur._ablage.set('matcap', karte);
        }
        return Mesh3daitextur._ablage.get('matcap');
    }
}
