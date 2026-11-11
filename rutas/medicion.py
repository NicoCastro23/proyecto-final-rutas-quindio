"""Cronómetro compartido por R1-R4 (sección 6 del enunciado).

Dos modos:
  (a) medir_en_proceso: la función corre en este mismo proceso.
  (b) medir_en_hijo: la función corre en un proceso hijo que se puede terminar a los 5 min.
Reglas comunes: 5 repeticiones y mediana; si la primera pasa de 60 s se deja esa sola;
si pasa de 300 s la medición es "no completada". Tiempos en milisegundos.
"""
import multiprocessing
import platform
import statistics
import subprocess
import time
from dataclasses import dataclass, field

import psutil


@dataclass
class ResultadoMedicion:
    tiempo_ms: float | None          # mediana; None si no completada
    repeticiones: int                # 5, 1 o 0
    completada: bool
    tiempos_ms: list[float] = field(default_factory=list)
    valor: object = None             # lo que devolvió la función (solo con devolver_valor=True)


NO_COMPLETADA = ResultadoMedicion(tiempo_ms=None, repeticiones=0, completada=False, tiempos_ms=[])


def _resultado(tiempos_ms):
    """Resumen de las repeticiones: la mediana es el valor que se reporta."""
    return ResultadoMedicion(tiempo_ms=statistics.median(tiempos_ms), repeticiones=len(tiempos_ms),
                             completada=True, tiempos_ms=tiempos_ms)


def medir_en_proceso(funcion, preparar, repeticiones=5, umbral_una_s=60.0, limite_s=300.0):
    """Modo (a): mide funcion(*preparar()) en este mismo proceso.

    `preparar` se llama antes de CADA repetición y queda fuera del cronómetro (en R1 devuelve
    una copia nueva del grafo, para que ninguna repetición reciba datos ya tocados).
    En el mismo proceso no se puede interrumpir la función: si la primera repetición pasa de
    `limite_s` se reporta "no completada" cuando termina.
    """
    tiempos_ms = []
    for i in range(repeticiones):
        argumentos = preparar()                       # fuera del cronómetro
        inicio = time.perf_counter_ns()
        funcion(*argumentos)
        fin = time.perf_counter_ns()
        tiempos_ms.append((fin - inicio) / 1e6)

        if i == 0 and tiempos_ms[0] / 1000 > limite_s:
            return NO_COMPLETADA
        if i == 0 and tiempos_ms[0] / 1000 > umbral_una_s:
            break                                     # muy lenta: una sola repetición
    return _resultado(tiempos_ms)


def _procesador():
    """Nombre del procesador; en macOS platform.processor() solo dice 'arm', por eso sysctl."""
    if platform.system() == "Darwin":
        try:
            nombre = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                    capture_output=True, text=True, check=True).stdout.strip()
            if nombre:
                return nombre
        except (OSError, subprocess.CalledProcessError):
            pass
    return platform.processor() or platform.machine()


def info_maquina():
    """Datos de la máquina para el informe (sección 6)."""
    return {
        "procesador": _procesador(),
        "ram_gb": round(psutil.virtual_memory().total / 1024**3, 1),
        "so": platform.platform(),
        "python": platform.python_version(),
    }


def _cronometrar_en_hijo(funcion, args, cola, devolver_valor=False):
    """Corre en el proceso hijo. El cronómetro está DENTRO del hijo y rodea solo la llamada:
    arrancar el intérprete, importar módulos y recibir `args` no cuentan."""
    inicio = time.perf_counter_ns()
    resultado = funcion(*args)
    fin = time.perf_counter_ns()
    # Lo que se envía por la cola se manda DESPUÉS de parar el cronómetro. Es pequeño (un
    # entero, o un entero y un resultado corto): join() no se bloquea.
    cola.put((fin - inicio, resultado) if devolver_valor else fin - inicio)


def _una_repeticion_en_hijo(funcion, args, limite_s, devolver_valor=False):
    """Nanosegundos que tardó el hijo (o la pareja (nanosegundos, valor) con devolver_valor),
    o None si pasó de limite_s y hubo que terminarlo."""
    contexto = multiprocessing.get_context("spawn")   # proceso limpio, igual en macOS/Linux/Windows
    cola = contexto.Queue()
    hijo = contexto.Process(target=_cronometrar_en_hijo, args=(funcion, args, cola, devolver_valor))
    hijo.start()
    hijo.join(timeout=limite_s)
    if hijo.is_alive():                           # se pasó del límite de 5 min
        hijo.terminate()
        hijo.join()
        return None
    if hijo.exitcode != 0:                        # la función lanzó una excepción en el hijo
        raise RuntimeError(f"la función falló en el proceso hijo (código {hijo.exitcode})")
    return cola.get()


def medir_en_hijo(funcion, args=(), repeticiones=5, umbral_una_s=60.0, limite_s=300.0,
                  devolver_valor=False):
    """Modo (b): cada repetición corre en un proceso hijo nuevo que se termina a los limite_s.

    `funcion` y `args` deben poder enviarse con pickle (funciones de módulo, no lambdas).
    Cada hijo recibe su propia copia de `args`, así que no hace falta `preparar`.
    Con devolver_valor=True, ResultadoMedicion.valor es lo que devolvió la función en la
    primera repetición (sirve para verificar el resultado de lo que se midió).
    """
    tiempos_ms = []
    valor = None
    for i in range(repeticiones):
        respuesta = _una_repeticion_en_hijo(funcion, args, limite_s, devolver_valor)
        if respuesta is None:
            return NO_COMPLETADA
        if devolver_valor:
            nanosegundos, resultado = respuesta
            if i == 0:
                valor = resultado
        else:
            nanosegundos = respuesta
        tiempos_ms.append(nanosegundos / 1e6)
        if i == 0 and tiempos_ms[0] / 1000 > umbral_una_s:
            break                                 # muy lenta: una sola repetición
    resultado_medicion = _resultado(tiempos_ms)
    resultado_medicion.valor = valor
    return resultado_medicion
