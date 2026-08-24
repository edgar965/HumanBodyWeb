/**
 * Körpermaterialien — die Materialtabelle des HumanBody-Netzes.
 *
 * WARUM DIESES MODUL (Umbau 17.08.2026): Diese Tabelle stand SECHSMAL im
 * Projekt — in animation/material.js, character_core.js,
 * photo_to_3d/helpers.js, scene/state.js, viewer/state.js und
 * TheatreJS/src/asset-loader.js. Fünf Fassungen waren Byte für Byte gleich, die
 * sechste dieselben Werte ohne die Kommentare. Gefunden vom Werkzeug
 * `doppelcode` (Kriterium 6).
 *
 * Sechs Kopien heißen: Wer die Hautrauheit ändert, ändert sie an einer Stelle
 * und wundert sich, warum die Szene anders aussieht als die Foto-Seite.
 *
 * DIE REIHENFOLGE IST DER VERTRAG: Der Index ist die Materialgruppe, die
 * `humanbody_core.mesh` beim Laden aus `face_materials` mitgibt (HB_Skin,
 * HB_Censor, HB_Eyelash, …). Wer hier eine Zeile einfügt, verschiebt alle
 * folgenden Gruppen — dann trägt das Auge plötzlich Nagel-Material.
 *
 * Die alten Fundstellen exportieren aus diesem Modul weiter, damit die
 * Aufrufstellen unverändert bleiben — dasselbe Vorgehen wie bei
 * `kodierung.js`.
 */

/** Index = Materialgruppe aus `face_materials`. Nicht umsortieren. */
export const BODY_MATERIALS = [
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },  // 0 Skin
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },  // 1 Censor
    { color: 0x111111, roughness: 0.8,  metalness: 0.0 },  // 2 Eyelash
    { color: 0x0a0a0a, roughness: 0.1,  metalness: 0.0 },  // 3 Pupil
    { color: 0xf4f0e8, roughness: 0.2,  metalness: 0.0 },  // 4 Sclera
    { color: 0xf4f0e8, roughness: 0.05, metalness: 0.0, opacity: 0.3, transparent: true },  // 5 Cornea
    { color: 0x4a7a9b, roughness: 0.15, metalness: 0.0 },  // 6 Iris
    { color: 0xb55a6a, roughness: 0.7,  metalness: 0.0 },  // 7 Tongue
    { color: 0xf0ece0, roughness: 0.3,  metalness: 0.0 },  // 8 Teeth
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },  // 9 Nails Hand
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },  // 10 Nails Feet
];
