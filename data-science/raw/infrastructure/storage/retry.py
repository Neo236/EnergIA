"""Retry con backoff exponencial para operaciones de storage.

Wrappea cualquier operacion (callable) que pueda fallar por errores
transitorios (red, throttling). Reintenta N veces con backoff creciente.

NO cambia el resultado final: si la operacion tiene exito, retorna su
resultado. Si falla tras N intentos, propaga la ultima excepcion.
"""

from __future__ import annotations

import logging
import random
import time
from typing import Callable, TypeVar

log = logging.getLogger(__name__)

T = TypeVar("T")

DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_INITIAL_BACKOFF_S = 1.0
DEFAULT_BACKOFF_MULTIPLIER = 2.0
DEFAULT_MAX_BACKOFF_S = 30.0


def with_retry(
    op: Callable[[], T],
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    initial_backoff_s: float = DEFAULT_INITIAL_BACKOFF_S,
    backoff_multiplier: float = DEFAULT_BACKOFF_MULTIPLIER,
    max_backoff_s: float = DEFAULT_MAX_BACKOFF_S,
    op_name: str = "storage_op",
    retryable: tuple[type[BaseException], ...] = (Exception,),
) -> T:
    """Ejecuta `op` con reintentos y backoff exponencial + jitter.

    Args:
        op: callable sin args que realiza la operacion.
        max_attempts: numero maximo de intentos (incluye el primero).
        initial_backoff_s: espera antes del segundo intento.
        backoff_multiplier: factor de crecimiento por intento.
        max_backoff_s: tope al backoff para evitar esperas absurdas.
        op_name: nombre para logging.
        retryable: tupla de excepciones que disparan retry. Por defecto
            cualquier Exception (transitorio o no). Para OCI conviene
            restringir a (ConnectionError, TimeoutError, ServiceError 5xx).
    """
    last_exc: BaseException | None = None
    backoff = initial_backoff_s
    for attempt in range(1, max_attempts + 1):
        try:
            return op()
        except retryable as e:
            last_exc = e
            if attempt == max_attempts:
                log.error(
                    "%s fallo tras %d intentos: %s",
                    op_name, max_attempts, e,
                )
                raise
            # Jitter +/- 20% para evitar thundering herd
            jitter = backoff * (0.8 + 0.4 * random.random())
            log.warning(
                "%s intento %d/%d fallo: %s. Reintentando en %.1fs",
                op_name, attempt, max_attempts, e, jitter,
            )
            time.sleep(jitter)
            backoff = min(backoff * backoff_multiplier, max_backoff_s)
    # unreachable
    assert last_exc is not None
    raise last_exc