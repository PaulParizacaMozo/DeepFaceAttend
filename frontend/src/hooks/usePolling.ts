import { useEffect, useRef } from 'react';

export const usePolling = (
  callback: () => Promise<void>, 
  interval: number, 
  enabled: boolean = true
) => {
  const savedCallback = useRef<() => Promise<void> | null>(null);
  const intervalId = useRef<ReturnType<typeof setInterval> | null>(null);

  // Actualizar el callback ref cuando cambia
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled || interval <= 0) return;

    const tick = async () => {
      if (savedCallback.current) {
        try {
          await savedCallback.current();
        } catch (error) {
          console.error('Error en polling:', error);
        }
      }
    };

    // Ejecutar inmediatamente y luego cada intervalo
    tick();
    intervalId.current = setInterval(tick, interval);

    // Cleanup
    return () => {
      if (intervalId.current) {
        clearInterval(intervalId.current);
      }
    };
  }, [interval, enabled]);
};