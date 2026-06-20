import { useState, useCallback } from 'react';
import { citasApi } from '../servicios/citasApi';

export const useDisponibilidad = () => {
    const [slots, setSlots] = useState([]);
    const [bloques, setBloques] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchSlots = useCallback(async (psicologoId, fecha) => {
        setLoading(true);
        setError(null);
        try {
            const response = await citasApi.getSlots(psicologoId, fecha);
            setSlots(response.data.slots);
            return response.data.slots;
        } catch (err) {
            setError('No pudimos cargar los horarios en este momento. Inténtalo de nuevo más tarde.');
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
            setBloques(response.data);
            return response.data;
        } catch (err) {
            setError('No logramos cargar tu configuración de disponibilidad en este momento.');
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
        fetchBloques
    };
};
