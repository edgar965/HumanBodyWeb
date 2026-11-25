/**
 * Genesis9stueckstand — mit welchen Reglern ein Stück gebaut wurde und worauf seine Schieber stehen (25.11.2026, für `Genesis9stueckzug`). Ohne Importe: `Genesis9kleidung` merkt den Stand
 * beim Bau, `Genesis9stueckzug` (der seinerseits `Genesis9kleidung` braucht) liest ihn.
 */
export class Genesis9stueckstand {

    static GRUPPE = 'stueckregler';
    /** Figur → Map(Kennung → Map(Regler → {wert, vorgabe})) */
    static _wuensche = new WeakMap();

    /** Die Reglerwerte, mit denen dieses Netz gebaut ist — die Wünsche, die er erfüllt, sind erledigt. */
    static merken(inst, kennung, netz, regler) {
        if (netz?.geometry) netz.geometry.userData.stueckstand = { ...(regler || {}) };
        const je = Genesis9stueckstand._wuensche.get(inst)?.get(kennung);
        for (const [name, { wert, vorgabe }] of je || []) if (((regler || {})[name] ?? vorgabe) === wert) je.delete(name);
    }

    static wunsch(inst, kennung, name, wert, vorgabe) {
        if (!Genesis9stueckstand._wuensche.has(inst)) Genesis9stueckstand._wuensche.set(inst, new Map());
        const je = Genesis9stueckstand._wuensche.get(inst);
        if (!je.has(kennung)) je.set(kennung, new Map());
        je.get(kennung).set(name, { wert, vorgabe });
    }

    static wuensche(inst, kennung) {
        const je = Genesis9stueckstand._wuensche.get(inst)?.get(kennung);
        return je?.size ? je : null;
    }
}
