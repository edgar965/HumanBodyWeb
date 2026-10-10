/**
 * Engine2d3dKleidersegmentierung — die Karte „Segmentierung" auf der Auftragsseite von „2D3D Kleider" (04.10.2026).
 *
 * Edgar: „baue das ein in den 2d3dKleider jobs — optional nach der Mesh erzeugung". Der Schritt „Segmentierung" (Sapiens) zerlegt die vorbereiteten Fotos in Oberteil, Hose, Socken/Schuhe, Zubehör und Haut
 * und legt die Etiketten auf die Flächen des Netzes. Der Knopf rechnet NUR diesen Schritt (`ab = bis = segmentierung`); darunter stehen die Fotos mit den Stückfarben (`segmentierung/ueberlagerung_<stamm>.webp`,
 * `zustand.segmentiert`) mit Rolle, Anteilen je Stück und der Güte der Einpassung (Silhouetten-IoU Netz ↔ Foto). Ist die Ablage veraltet (anderes Netz, neue Vorbereitung), sagt eine Zeile es.
 *
 * Die Option „Kleidung aus der Segmentierung" baut `Meshoptionenformular` aus der Gruppe `segmentierung` (siehe `Engine2d3dKleiderseite.aufbauen`).
 */
import { Engine2d3dKleidersegmentierungsklassen } from './engine2d3dkleidersegmentierungsklassen.js';

export class Engine2d3dKleidersegmentierung {

    /** Stückfarben wie in `sapiens_klassen.py` (`Sapiensklassen.FARBEN`) — die Legende zeigt dieselben. */
    static STUECKE = [
        ['Oberteil', '#dc2828'], ['Hose / Rock', '#f08c14'], ['Socken / Schuhe', '#5a64ff'], ['Zubehör', '#ff00ff'], ['Haar', '#a06e32'], ['nicht Kleidung', '#46af5a'],
    ];

    constructor(seite) {
        this.seite = seite;
        this.liste = document.getElementById('segmentierte-fotos');
        this.legende = document.getElementById('segmentierung-legende');
        this.klassen = new Engine2d3dKleidersegmentierungsklassen(document.getElementById('segmentierung-klassen'));
        this._stand = null;
        for (const [name, farbe] of Engine2d3dKleidersegmentierung.STUECKE) {
            const punkt = document.createElement('span');
            punkt.className = 'engine2d3dkleider-segmentierung-farbe';
            punkt.style.background = farbe;
            const text = document.createElement('span');
            text.className = 'hb-hinweis';
            text.textContent = name;
            this.legende.append(punkt, text);
        }
        const zeile = document.getElementById('segmentierung-zeile');
        this.knopf = document.createElement('button');
        this.knopf.type = 'button';
        this.knopf.id = 'segmentierung-starten';
        this.knopf.className = 'btn btn-primary btn-sm';
        this.knopf.title = 'Rechnet nur den Schritt „Segmentierung“ (Sapiens auf den vorbereiteten Fotos, Etiketten auf die Flächen des Netzes). Braucht das Netz aus dem Schritt „Netz“. ' +
            'Läuft ausdrücklich gestartet immer, auch bei Option „Aus“ — die Kleidung hängt davon erst ab, wenn die Option „An“ ist.';
        this.knopf.innerHTML = '<i class="fas fa-shirt"></i> <span>Segmentierung starten</span>';
        this.knopf.addEventListener('click', () => seite.starten('segmentierung', 'segmentierung', this.knopf));
        this.hinweis = document.createElement('span');
        this.hinweis.className = 'hb-hinweis';
        zeile.append(this.knopf, this.hinweis);
    }

    zeigen(z) {
        this.knopf.disabled = !!z.laeuft;
        this.knopf.querySelector('span').textContent = z.laeuft && z.schritt === 'segmentierung' ? 'Berechnet …' : 'Segmentierung starten';
        const s = z.segmentiert;
        this.klassen.zeigen(z.optionen?.segmentierung, s?.kennzahlen);
        const stand = JSON.stringify([s, z.optionen?.segmentierung?.verwenden, z.optionen?.segmentierung?.haar]);
        if (stand === this._stand) return;
        this._stand = stand;
        this.liste.innerHTML = '';
        if (!s || !s.bilder.length) {
            this.hinweis.textContent = 'Noch nicht gerechnet.';
            return;
        }
        const wann = s.stand ? new Date(s.stand).toLocaleString('de-DE') : '';
        const name = String(s.kennzahlen?.modell || '');      // '1b' … oder 'sapiens2-0.4b' (09.10.2026)
        const modell = name ? (name.startsWith('sapiens2-') ? `Sapiens2-${name.slice(9).toUpperCase()}. ` : `Sapiens-${name.toUpperCase()}. `) : '';
        this.hinweis.textContent = s.veraltet
            ? `Stand ${wann} — passt nicht mehr zu Netz, Fotos oder Einstellungen (${s.grund}); „Segmentierung starten“ rechnet neu. ${Engine2d3dKleidersegmentierung.kleidungssatz(s)}`
            : `Stand ${wann}. ${modell}${Engine2d3dKleidersegmentierung.flaechensatz(s)} ${Engine2d3dKleidersegmentierung.kleidungssatz(s)} ${Engine2d3dKleidersegmentierung.haarsatz(s)}`;
        this.hinweis.classList.toggle('hb-schlecht', !!s.veraltet);
        for (const bild of s.bilder) this.liste.appendChild(this._karte(bild, s));
    }

    _karte(bild, s) {
        const karte = document.createElement('div');
        karte.className = 'mesh-fotokarte engine2d3dkleider-vorbereitet-karte' + (s.veraltet ? ' engine2d3dkleider-vorbereitet-veraltet' : '');
        const bildfeld = document.createElement('img');
        bildfeld.className = 'mesh-vorschau engine2d3dkleider-vorbereitet-bild';
        bildfeld.loading = 'lazy';
        bildfeld.alt = bild.datei;
        bildfeld.title = `${bild.datei} — Sapiens-Etiketten`;
        bildfeld.src = `${this.seite.dateiAdresse('segmentierung', bild.ueberlagerung)}?v=${encodeURIComponent(s.stand || '')}`;
        const text = document.createElement('div');
        text.className = 'hb-hinweis';
        text.textContent = `${bild.rolle} · ${Engine2d3dKleidersegmentierung.anteile(bild.anteile)} · Netz passt zum Foto: IoU ${Number(bild.iou).toFixed(2)}`;
        karte.append(bildfeld, text);
        return karte;
    }

    /** „Oberteil 38 % · Hose 7 % …" — die Anteile an der Personenfläche, nur was vorkommt (ohne „nicht Kleidung"). */
    static anteile(a) {
        const teile = Object.entries(a || {}).filter(([name, x]) => name !== 'nicht Kleidung' && x > 0)
            .map(([name, x]) => `${name} ${x < 0.01 ? '< 1' : (x * 100).toFixed(0)} %`);
        return teile.length ? teile.join(' · ') : 'keine Kleidung erkannt';
    }

    /** „Flächen: 9.800 von 95.000 gesehen …" — wie viele Netzflächen von mindestens einem Foto gesehen werden und was sie nach den Stimmen sind. */
    static flaechensatz(s) {
        const k = s.kennzahlen;
        if (!k) return '';
        const je = Object.entries(k.stuecke || {}).filter(([name, x]) => name !== 'nicht Kleidung' && x.flaechen > 0)
            .map(([name, x]) => `${name} ${Math.round(x.cm2).toLocaleString('de-DE')} cm²`).join(' · ');
        return `Netzflächen: ${k.flaechen_gesehen.toLocaleString('de-DE')} von ${k.flaechen_gesamt.toLocaleString('de-DE')} sichtbar${je ? ' — ' + je : ''}.`;
    }

    /** Was die Haarmaske (Schritt „haar" der Körper-Kette) mit der Klasse „Hair" gemacht hat: beide Flächen, ihre Überschneidung, das Ergebnis (nur bei Option „Haar aus der Segmentierung"). */
    static haarsatz(s) {
        const h = s.haar;
        const zahl = x => Math.round(x).toLocaleString('de-DE');
        if (s.haar_quelle === 'farbe' || !s.haar_quelle) return 'Haarmaske: aus der Farbe des Netzes (Option).';
        if (!h) return `Haarmaske: Option „${s.haar_quelle}“ — der Schritt „Körper“ (Quelle „rechnen“) nimmt Sapiens beim nächsten Lauf.`;
        if (!h.verwendet) return `Haarmaske: Sapiens NICHT benutzt (${h.grund}) — die Farbe galt.`;
        return `Haarmaske (${h.quelle}): Farbe ${zahl(h.farbe.cm2)} cm², Sapiens ${zahl(h.sapiens.cm2)} cm², beide ${h.beide_flaechen.toLocaleString('de-DE')} Flächen → ${zahl(h.ergebnis.cm2)} cm² (${h.hinzu_flaechen.toLocaleString('de-DE')} dazu, ${h.weg_flaechen.toLocaleString('de-DE')} weg).`;
    }

    /** Was der Schritt „kleidung" der Körper-Kette mit den Etiketten gemacht hat (nur bei Quelle „rechnen"). */
    static kleidungssatz(s) {
        const k = s.kleidung;
        if (s.verwenden !== 'an') return 'Die Kleidungsmaske nutzt sie nicht (Option „Aus“).';
        if (!k) return 'Option „An“: der Schritt „Körper“ (Quelle „rechnen“) nimmt sie beim nächsten Lauf für die Kleidungsmaske.';
        if (!k.verwendet) return `Kleidungsmaske: Etiketten NICHT benutzt (${k.grund}) — Farbe und Lage galten.`;
        return `Kleidungsmaske aus den Etiketten: ${k.flaechen_geaendert.toLocaleString('de-DE')} Flächen anders als nach Farbe und Lage.`;
    }
}
