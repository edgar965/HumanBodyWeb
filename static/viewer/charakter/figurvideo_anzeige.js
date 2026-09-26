/**
 * Figurvideoanzeige — Balken, Meldung und Ergebnis des Videobereichs.
 *
 * Beide Rechenwege (`figurvideo.js` Server, `videoaufnahme.js` Szene)
 * schreiben in dieselben Elemente; hier steht, WIE. Ohne Zustand, damit
 * die Texte (`kurz`, `lang`, `HINWEIS`) in Node prüfbar bleiben.
 *
 * Der Balken zeigt den Anteil UND die Zahl: Ein Balken allein bei 97 %
 * liest sich wie „hängt", die Zahl daneben sagt, dass er noch läuft.
 */
export class Figurvideoanzeige {

    /** So lange steht die Meldung Pfad kopiert statt des Pfads. */
    static KOPIERT_MS = 1200;

    /** Klartext je Rechenweg — steht UNTER der Auswahl, nicht im Tooltip.
     *  Edgar (11.09.2026): „da steht Server und Browser?? Mach das eindeutig". */
    static HINWEIS = {
        szene: 'Nimmt die Szene auf, wie sie hier zu sehen ist — mit Texturen, '
            + 'Licht und Kamera. Der Tab muss dabei offen bleiben; '
            + 'etwa eine Minute je 3 Sekunden Video.',
        server: 'Rechnet Figur, Kleider und Weichgewebe in Python und rendert '
            + 'ohne Texturen (einfarbige Flächen). Läuft auch weiter, wenn '
            + 'Sie den Tab wechseln; etwa 70 Sekunden je 3 Sekunden Video.',
    };

    static hinweisZeigen(weg) {
        const feld = document.getElementById('figurvideo-weg-hinweis');
        if (feld) feld.textContent = Figurvideoanzeige.HINWEIS[weg] || '';
    }

    // ------------------------------------------------------------ Stand

    static zeigen(text, anteil) {
        document.getElementById('figurvideo-stand')?.classList.remove('hb-versteckt');
        const prozent = Math.round(Math.min(Math.max(anteil, 0), 1) * 100);
        const balken = document.getElementById('figurvideo-anteil');
        if (balken) balken.style.width = `${prozent}%`;
        const zahl = document.getElementById('figurvideo-prozent');
        if (zahl) zahl.textContent = `${prozent} %`;
        const phase = document.getElementById('figurvideo-phase');
        if (phase) { phase.textContent = text; phase.style.color = ''; }
        Figurvideoanzeige.sperren(true);
    }

    static melden(text, fehler = false) {
        Figurvideoanzeige.zeigen(text, 0);
        const phase = document.getElementById('figurvideo-phase');
        if (phase) phase.style.color = fehler ? 'var(--danger, #d44)' : '';
        if (fehler) Figurvideoanzeige.sperren(false);
    }

    static sperren(zu) {
        const knopf = document.getElementById('figurvideo-start');
        if (knopf) knopf.disabled = zu;
    }

    // --------------------------------------------------------- Ergebnis

    /**
     * Das MP4 einbetten, Pfad und Bilanz dazu.
     * @param {object} e  {url, download, pfad, ablageFehler, kurz, lang}
     */
    static ergebnis(e) {
        const video = document.getElementById('figurvideo-video');
        const laden = document.getElementById('figurvideo-laden');
        if (video) video.src = e.url;
        if (laden) { laden.href = e.url; laden.download = e.download; }
        const pfad = document.getElementById('figurvideo-pfad');
        if (pfad) {
            pfad.textContent = e.pfad ? `Gespeichert: ${e.pfad}`
                : (e.ablageFehler ? `Kopie in die Ablage fehlgeschlagen: ${e.ablageFehler}` : '');
            pfad.dataset.pfad = e.pfad || '';
        }
        const bilanz = document.getElementById('figurvideo-bilanz');
        if (bilanz) { bilanz.textContent = e.kurz || ''; bilanz.title = e.lang || ''; }
        document.getElementById('figurvideo-ergebnis')?.classList.remove('hb-versteckt');
    }

    /** „Abspielen": in einem eigenen Tab, in voller Größe. Das kleine
     *  Vorschaufenster im Bedienfeld spielt daneben weiter. */
    static abspielen() {
        const video = document.getElementById('figurvideo-video');
        if (video?.src) window.open(video.src, '_blank');
    }

    /** Klick auf den Pfad kopiert ihn — wer ihn im Explorer öffnen will,
     *  muss ihn nicht abtippen. */
    static async pfadKopieren() {
        const feld = document.getElementById('figurvideo-pfad');
        const pfad = feld?.dataset.pfad;
        if (!pfad || !navigator.clipboard) return;
        try {
            await navigator.clipboard.writeText(pfad);
            const war = feld.textContent;
            feld.textContent = 'Pfad kopiert.';
            setTimeout(() => { feld.textContent = war; }, Figurvideoanzeige.KOPIERT_MS);
        } catch {
            // stumm gewollt: ohne Zwischenablage-Berechtigung bleibt der Pfad sichtbar stehen, der Nutzer kopiert von Hand
        }
    }

    // ------------------------------------------------------ Bilanztexte

    static kurz(b) {
        const koerper = b.teile?.[0];
        const stuecke = (b.teile || []).slice(1);
        const teile = [`${b.bilder} Bilder`];
        if (koerper?.zuschlag_mm) teile.push(`Weichgewebe ${koerper.zuschlag_mm} mm`);
        // Die Stueckzahl IMMER, auch null: „nur Koerper" ist ein Befund,
        // den man sehen muss.
        teile.push(stuecke.length === 1 ? '1 Stück' : `${stuecke.length} Stücke`);
        return teile.join(' · ');
    }

    static lang(b) {
        const zeilen = [`Wurzelweg ${(b.wurzelweg_m || 0).toFixed(2)} m, `
            + `Quelle ${Math.round(b.quell_fps || 0)} fps, Zeitschritt ${b.schritt}`];
        for (const t of b.teile || []) {
            let z = `${t.name}: ${t.punkte} Punkte, Ruheprobe ${t.ruheprobe_mm} mm`;
            if (t.sitz_mm != null) z += `, Sitz ${t.sitz_mm} mm`;
            if (t.gleichlauf_mm) z += `, zur Haut ${t.gleichlauf_mm.join(' / ')} mm`;
            if (t.zuschlag_mm != null) z += `, Zuschlag ${t.zuschlag_mm} mm`;
            if (t.stoff_im_koerper_prozent != null) {
                z += `, im Körper ${t.stoff_im_koerper_prozent} %`;
            }
            zeilen.push(z);
        }
        return zeilen.join('\n');
    }
}
