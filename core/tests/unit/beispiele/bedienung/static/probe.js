// Drei Wege, ein Element zu bedienen — alle drei muss der Pruefer kennen.
document.getElementById('probe-mit-hoerer').addEventListener('click', tun);
document.querySelectorAll('.probe-sammel').forEach((k) => k.onclick = tun);
const vorsilbe = 'probe-mit-vorsilbe';
document.getElementById(`${vorsilbe}-rauheit`).addEventListener('input', tun);
