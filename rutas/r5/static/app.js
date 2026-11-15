/* app.js · Mejora progresiva de R5 (spec, «Diseño visual v2», D6).
   La aplicación funciona igual sin este archivo: el servidor calcula, valida y pone el contador inicial.
   Hace solo dos cosas:
     M2. Las tarjetas del resumen entran con un resorte sin rebote.
     M3. El contador de atractivos se actualiza al marcar y desmarcar.
   Motion (vendor/motion.js) se carga antes, también con defer, y deja el objeto global Motion. */
(function () {
  "use strict";

  // Se consulta al animar, así se respeta aunque el usuario lo cambie con la página abierta.
  const movimientoReducido = window.matchMedia("(prefers-reduced-motion: reduce)");

  // ---------- M2: entrada de las tarjetas del resumen ----------
  function animarTarjetas() {
    const tarjetas = document.querySelectorAll(".resumen .tarjeta");
    if (tarjetas.length === 0 || !window.Motion) {
      return; // página sin resultado, o Motion no cargó: las tarjetas ya están visibles
    }
    const { animate, stagger } = window.Motion;
    if (movimientoReducido.matches) {
      // Sin desplazamiento ni resorte: un fundido corto de opacidad.
      animate(tarjetas, { opacity: [0, 1] }, { duration: 0.2, ease: "linear" });
      return;
    }
    // Resorte críticamente amortiguado: llega sin pasarse. Nada se lanza con un gesto, así que no hay rebote.
    animate(
      tarjetas,
      { opacity: [0, 1], y: [8, 0] },
      { type: "spring", bounce: 0, duration: 0.4, delay: stagger(0.04) }
    );
  }

  // ---------- M3: contador de atractivos ----------
  // Mismos límites y textos que contador_elegidos() en app.py.
  const MINIMO = 6;
  const MAXIMO = 8;

  function plural(n, uno, varios) {
    return n === 1 ? uno : varios;
  }

  function estadoDe(n) {
    if (n < MINIMO) {
      return plural(MINIMO - n, "falta", "faltan") + " " + (MINIMO - n);
    }
    if (n > MAXIMO) {
      return plural(n - MAXIMO, "sobra", "sobran") + " " + (n - MAXIMO);
    }
    return "listo para calcular";
  }

  // Solo escribe si cambia: así el aria-live no repite un anuncio idéntico.
  function escribir(elemento, texto) {
    if (elemento.textContent !== texto) {
      elemento.textContent = texto; // textContent, nunca HTML
    }
  }

  function actualizarContador(contador, casillas) {
    let n = 0;
    casillas.forEach(function (casilla) {
      if (casilla.checked) {
        n += 1;
      }
    });
    const enRango = n >= MINIMO && n <= MAXIMO;
    escribir(contador.querySelector(".cuenta"), n + " " + plural(n, "elegido", "elegidos"));
    escribir(contador.querySelector(".estado"), estadoDe(n));
    escribir(contador.querySelector(".icono"), enRango ? "✓" : "!");
    contador.dataset.estado = enRango ? "en-rango" : "fuera";
  }

  function prepararContador() {
    const contador = document.getElementById("contador");
    if (!contador) {
      return; // solo existe en /itinerario
    }
    const casillas = document.querySelectorAll('input[name="atractivos"]');
    const actualizar = function () {
      actualizarContador(contador, casillas);
    };
    casillas.forEach(function (casilla) {
      casilla.addEventListener("change", actualizar);
    });
    // Al volver con «Atrás», el navegador puede restaurar las casillas marcadas: se resincroniza.
    window.addEventListener("pageshow", actualizar);
    actualizar();
  }

  animarTarjetas();
  prepararContador();
})();
