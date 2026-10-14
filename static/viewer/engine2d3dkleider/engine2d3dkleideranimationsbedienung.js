/**
 * Engine2d3dKleideranimationsbedienung — Knöpfe und Tasten der Animationsleiste (aus `Engine2d3dKleideranimation` herausgelöst,
 * 01.10.2026).
 *
 * Edgar (01.10.2026): „es fehlt die Stopptaste bei der Animation, das komplette rewind nach hinten, vorne, die
 * Pfeiltasten sollen um einen Frame verschieben" — dazu Play/Pause per Leertaste.
 *
 *     ⏮ Anfang   ◀ ein Bild zurück   ▶/⏸ Play/Pause   ⏹ Stopp (Ruhehaltung)   ▶ ein Bild vor   ⏭ Ende
 *     Tasten: Leertaste Play/Pause · ← → ein Bild · Pos1/Ende an Anfang/Ende — nicht, solange ein Eingabefeld den
 *     Fokus hat.
 */
export class Engine2d3dKleideranimationsbedienung {
    static TASTEN = {
        Space: a => a.umschalten(),
        ArrowLeft: a => a.bild(-1),
        ArrowRight: a => a.bild(1),
        Home: a => a.springen(false),
        End: a => a.springen(true),
    };

    constructor(animation) {
        this.a = animation;
        // Jeder Befehl geht durch `bedienen`: baut die Seite dafür erst die Figur um (Mesh-3D: „Haltung“ aus), läuft er danach von selbst.
        const knopf = (id, tun) => document.getElementById(id)?.addEventListener('click', () => this.a.bedienen(tun));
        knopf('anim-anfang', () => this.a.springen(false));
        knopf('anim-zurueck', () => this.a.bild(-1));
        knopf('anim-play', () => this.a.umschalten());
        knopf('anim-stopp', () => this.a.stoppen());
        knopf('anim-vor', () => this.a.bild(1));
        knopf('anim-ende', () => this.a.springen(true));
        const schieber = this.a.scrubber;
        schieber.addEventListener('input', () => this.a.bedienen(() => this.a.gezogen()));
        schieber.addEventListener('mousedown', () => { this.a._ziehen = true; });
        schieber.addEventListener('touchstart', () => { this.a._ziehen = true; }, { passive: true });
        const loslassen = () => { this.a._ziehen = false; };
        schieber.addEventListener('mouseup', loslassen);
        schieber.addEventListener('touchend', loslassen);
        document.addEventListener('keydown', ereignis => this.taste(ereignis));
    }

    taste(ereignis) {
        const tun = Engine2d3dKleideranimationsbedienung.TASTEN[ereignis.code];
        if (!tun || this.a.karte.hidden) return;
        const ziel = ereignis.target;
        const art = ziel && ziel.tagName;
        // Ein Schieber nimmt Pfeile, Pos1 und Ende selbst, die Leertaste aber nicht (13.10.2026: sie scrollte die Seite); Eingabefelder und Knöpfe behalten ihre Tasten.
        const schieber = art === 'INPUT' && ziel.type === 'range';
        if (ziel && (ziel.isContentEditable || /^(TEXTAREA|SELECT|BUTTON)$/.test(art) || (art === 'INPUT' && !schieber))) return;
        if (schieber && ereignis.code !== 'Space') return;
        // Auch solange die Bewegung noch nicht (wieder) geladen ist: solange die Leiste da ist, scrollt die Leertaste die Seite nicht (Edgar, 13.10.2026: „Play mit Pause-Taste … scrollt die Seite“).
        // Ohne Bewegung entscheidet `bedienen`: Mesh-3D rechnet sie dann (`ohneBewegung`), die anderen Seiten tun nichts (alle Befehle prüfen `action`).
        ereignis.preventDefault();
        this.a.bedienen(() => tun(this.a));
    }
}
