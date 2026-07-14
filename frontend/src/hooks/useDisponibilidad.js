import { useState, useCallback } from 'react';
import { citasApi } from '../servicios/citasApi';

const mensajeError = (err, defecto) =>
    err.response?.data?.mensaje || err.response?.data?.message || defecto;

export const useDisponibilidad = () => {
    const [slots, setSlots] = useState([]);
    const [bloques, setBloques] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const limpiarSlots = useCallback(() => {
        setSlots([]);
        setError(null);
    }, []);

    const fetchSlots = useCallback(async (psicologoId, fecha) => {
        setLoading(true);
        setError(null);
        setSlots([]);
        try {
            const response = await citasApi.getSlots(psicologoId, fecha);
            const nuevosSlots = response.data?.slots || [];
            setSlots(nuevosSlots);
            return nuevosSlots;
        } catch (err) {
            const mensaje = mensajeError(
                err,
                'No pudimos cargar los horarios en este momento. Inténtalo nuevamente.'
            );
            setError(mensaje);
            return [];
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchBloques = useCallback(async (psicologoId) => {
        setLoading(true);
        setError(null);
        try {
            const response = await citasApi.getDisponibilidad(psicologoId);
            const nuevosBloques = response.data || [];
            setBloques(nuevosBloques);
            return nuevosBloques;
        } catch (err) {
            setError(mensajeError(err, 'No logramos cargar la disponibilidad.'));
            return [];
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        slots,
        bloques,
        loading,
        error,
        fetchSlots,
        fetchBloques,
        limpiarSlots,
    };
};
