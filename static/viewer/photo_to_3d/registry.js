/**
 * Photo To 3D — Function registry to avoid circular imports.
 * Each module registers its public functions here after defining them.
 * Consumers call fn.someFunction() instead of direct imports.
 */
export const fn = {};
