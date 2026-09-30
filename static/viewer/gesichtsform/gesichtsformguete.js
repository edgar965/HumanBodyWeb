import { dbTabelle } from '/static/djangobase/js/tabelle_bauen.js';
import { tabellenBinden } from '/static/djangobase/js/tabellen_auto.js';

/**
 * Gesichtsformguete — die Zahlen der letzten Rechnung (Seite „Gesichtsform", `G9schnittvorgaben.guete`).
 *
 * Je Schnitt die größte Abweichung |Ziel − Figur| vorher und nachher und das 90-%-Quantil nachher, je
 * Kontur der mittlere Abstand von vorn — in Millimetern, gemessen auf der Ansichtsstufe mit Augäpfeln.
 * Das Maximum sitzt oft am Ovalrand, wo die Fläche steil wird; das p90 sagt, wie der Schnitt sonst liegt.
 *
 * ZWEI TABELLEN, NICHT EINE (30.09.2026): Vorher stand beides in einem `<table>` mit einer zweiten
 * Kopfzeile mitten darin — Schnitte und Konturen haben aber verschiedene Spalten (die Kontur ließ die
 * vierte leer). Sortieren hätte diese Kopfzeile mitgenommen. Jetzt baut `dbTabelle` je Block eine
 * eigene djangoBase-Tabelle: sortierbar, mit gemerkten Spaltenbreiten, und `djangobase.tests.konform`
 * sieht dieselbe Struktur wie bei einer server-gerenderten (vorher fehlten `sortable`/`data-sort-key`).
 */
export class Gesichtsformguete {

    static NAMEN = {
        auge_rechts: 'Auge rechts', auge_links: 'Auge links', braue_rechts: 'Braue rechts',
        braue_links: 'Braue links', lippen: 'Lippen außen', mund: 'Lippen innen', nase: 'Nase', oval: 'Oval',
    };

    constructor(behaelter) { this.behaelter = behaelter; }

    /** Millimeter deutsch; `null`/`undefined` als Gedankenstrich. */
    static _text(wert) {
        return (wert === null || wert === undefined) ? '–' : String(wert).replace('.', ',');
    }

    /** Grün, wenn die Abweichung kleiner wurde, rot wenn größer — sonst ohne Farbe. */
    static _klasse(vor, nach) {
        if (vor === null || nach === null || vor === undefined || nach === undefined) return '';
        return nach < vor ? 'besser' : nach > vor ? 'schlechter' : '';
    }

    /** Eine Zahlenzelle: angezeigt mit Komma, sortiert nach dem echten Wert. */
    static _zelle(wert, klasse = '') {
        return { html: Gesichtsformguete._text(wert), sort: wert ?? '', klasse };
    }

    zeigen(guete, max) {
        if (!guete) { this.behaelter.textContent = 'Noch nicht gerechnet.'; return; }
        const z = Gesichtsformguete._text;
        const k = Gesichtsformguete._klasse;
        const zelle = Gesichtsformguete._zelle;
        const schnitte = dbTabelle({
            key: 'gesichtsform-guete-schnitte',
            spalten: [{ label: 'Schnitt', key: 'schnitt' },
                      { label: 'max. vorher', key: 'vorher', num: true },
                      { label: 'max. nachher', key: 'nachher', num: true },
                      { label: 'p90 nachher', key: 'p90', num: true }],
            zeilen: (guete.schnitte || []).map(s => ({ zellen: [
                { html: `${s.art} ${z(s.lage)} mm`, sort: s.lage ?? '' },
                zelle(s.vorher_max),
                zelle(s.nachher_max, k(s.vorher_max, s.nachher_max)),
                zelle(s.nachher_p90),
            ] })),
            leer: 'keine Schnitte',
        });
        const konturen = dbTabelle({
            key: 'gesichtsform-guete-konturen',
            spalten: [{ label: 'Kontur', key: 'kontur' },
                      { label: 'vorher', key: 'vorher', num: true },
                      { label: 'nachher', key: 'nachher', num: true }],
            zeilen: Object.entries(guete.konturen || {}).map(([name, kon]) => ({ zellen: [
                { html: Gesichtsformguete.NAMEN[name] || name },
                zelle(kon.vorher_mm),
                zelle(kon.nachher_mm, k(kon.vorher_mm, kon.nachher_mm)),
            ] })),
            leer: 'keine Konturen',
        });
        this.behaelter.innerHTML = `<p>Größte Verschiebung des Morphs: ${z(max)} mm</p>`
            + schnitte + konturen;
        this.behaelter.classList.add('gf-guete');
        tabellenBinden(this.behaelter);
    }
}
