/**
 * Engine2d3dKleiderlaufzeit — Zeitangaben der Render-Läufe als Text (04.10.2026): Dauer, Datum mit Uhrzeit, Uhrzeit. Sortiert wird nie nach dem Text, sondern nach
 * dem Rohwert in `data-sort` der Zelle (Sekunden bzw. Millisekunden), die Anzeige darf formatiert sein.
 */
export class Engine2d3dKleiderlaufzeit {

    /** `476.2` → „7 min 56 s", `37` → „37 s". */
    static dauer(sekunden) {
        const s = Math.round(Number(sekunden) || 0);
        return s >= 60 ? `${Math.floor(s / 60)} min ${String(s % 60).padStart(2, '0')} s` : `${s} s`;
    }

    /** `2026-10-04 18:42:07` → „04.10.2026 18:42:07"; was nicht so aussieht, bleibt unverändert. */
    static datum(zeit) {
        const t = /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}:\d{2}:\d{2})/.exec(String(zeit || ''));
        return t ? `${t[3]}.${t[2]}.${t[1]} ${t[4]}` : String(zeit || '');
    }

    /** `Date` → „18:42:07". */
    static uhr(datum) {
        return datum.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }

    /** `2026-10-04 18:42:07` → Millisekunden seit 1970 (Ortszeit, wie der Server sie schreibt); 0, wenn der Text kein Datum ist. */
    static millisekunden(zeit) {
        const ms = Date.parse(String(zeit || '').replace(' ', 'T'));
        return Number.isNaN(ms) ? 0 : ms;
    }
}
