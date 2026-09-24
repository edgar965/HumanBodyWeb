// `export *` durch ein CJS-Paket ist nicht zuverlässig statisch auflösbar
// (Rollup kennt CJS-Exporte erst zur Laufzeit) — deshalb explizit benannt,
// genau die zwei Namen, die `theatrejs_editor.js` tatsächlich braucht.
export { getProject, types } from '@theatre/core';
