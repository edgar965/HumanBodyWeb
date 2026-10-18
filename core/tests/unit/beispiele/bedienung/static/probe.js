// Drei Wege, ein Element zu bedienen — alle drei muss der Pruefer kennen.
document.getElementById('probe-mit-hoerer').addEventListener('click', tun);
document.querySelectorAll('.probe-sammel').forEach((k) => k.onclick = tun);
const vorsilbe = 'probe-mit-vorsilbe';
document.getElementById(`${vorsilbe}-rauheit`).addEventListener('input', tun);
// Ein Feld, das erst beim Speichern gelesen wird — gegriffen ueber `querySelector('#…')` (18.10.2026, mesh3dai_test.html).
const name = karte.querySelector('#probe-ueber-raute');
