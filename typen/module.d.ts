// Ambient-Deklarationen für den Language Server (Hilfe → Werkzeug Language Server,
// `tsc --checkJs`). Die Seiten laden Theatre.js über die Import-Map in
// `_importmap.html`; tsc kennt die Karte nicht. Three.js dagegen ist als
// devDependency installiert (package.json: three + @types/three in der Fassung
// der Import-Map), damit die JSDoc-Typen `{THREE.Mesh}` etwas bedeuten.
// (12.09.2026)
declare module '@theatre/core';
declare module '@theatre/studio';
