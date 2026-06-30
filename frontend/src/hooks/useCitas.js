import { useState, useCallback } from 'react';
import { citasApi } from '../servicios/citasApi';

export const useCitas = () => {
    const [citas, setCitas] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchMisCitas = useCallback(async (params = {}) => {
        setLoading(true);
        setError(null);
        try {
            const response = await citasApi.getMisCitas(params);
            setCitas(response.data);
        } catch (err) {
            setError('No pudimos cargar tus citas en este momento. Por favor, intenta de nuevo más tarde.');
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchTodasLasCitas = useCallback(async (params = {}) => {
        setLoading(true);
        setError(null);
        try {
            const response = await citasApi.getTodasLasCitas(params);
            setCitas(response.data);
        } catch (err) {
            setError('No pudimos cargar las citas en este momento. Por favor, intenta de nuevo más tarde.');
        } finally {
            setLoading(false);
        }
    }, []);

    const agendarCita = async (data) => {
        setLoading(true);
        setError(null);
        try {
            const response = await citasApi.agendar(data);
            return response.data;
        } catch (err) {
            setError('Lo sentimos, hubo un problema al intentar agendar tu cita.');
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const cambiarEstado = async (id, accion, data = null) => {
        setLoading(true);
        setError(null);
        try {
            let response;
            switch(accion) {
                case 'confirmar': response = await citasApi.confirmar(id); break;
                case 'cancelar': response = await citasApi.cancelar(id, data); break;
                case 'reprogramar': response = await citasApi.reprogramar(id, data); break;
                default: throw new Error('Acción no soportada');
            }
            return response.data;
        } catch (err) {
            setError('Tuvimos un inconveniente al actualizar el estado de tu cita. Intenta nuevamente.');
            throw err;
        } finally {
            setLoading(false);
        }
    };

    return {
        citas,
        loading,
        error,
        fetchMisCitas,
        fetchTodasLasCitas,
        agendarCita,
        cambiarEstado
    };
};
