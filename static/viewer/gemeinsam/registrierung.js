/**
 * Registrierung — das Funktionsverzeichnis, mit dem sich Module gegenseitig
 * erreichen, ohne sich zu importieren.
 *
 * Jedes Modul traegt nach seiner Definition ein, was andere brauchen
 * (`fn.updateProperties = …`), und die Aufrufer nehmen `fn.updateProperties()`.
 * Das bricht die Kreise, die sonst zwischen Zeitleiste, Eigenschaften und
 * Spuren entstehen wuerden.
 *
 * WARUM eine Datei statt fuenf (Umbau 16.08.2026): Es gab
 * bvh_studio/registry.js, scene/registry.js, viewer/registry.js,
 * photo_to_3d/registry.js und result_character/registry.js — inhaltlich
 * dieselbe Zeile, unterschiedlich nur in der Seitenbezeichnung im Kommentar.
 *
 * Dass sich die Seiten den Namensraum jetzt teilen, ist unkritisch: Jede Seite
 * laedt genau ihren eigenen Modulsatz, in einem Dokument ist immer nur einer
 * davon aktiv.
 */
export const fn = {};
