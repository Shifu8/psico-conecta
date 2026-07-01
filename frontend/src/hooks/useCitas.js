import { useState, useCallback } from 'react';
import { citasApi } from '../servicios/citasApi';
import { registrarEventoAuditoria } from '../servicios/servicioAutenticacion';

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
            console.error('Error al cargar mis citas:', err);
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
            console.error('Error al cargar todas las citas:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    const agendarCita = async (data) => {
        setLoading(true);
        setError(null);
        try {
            const response = await citasApi.agendar(data);
            try {
                await registrarEventoAuditoria({
                    event_type: "cita_scheduled",
                    category: "citas",
                    status: "success",
                    modulo: "citas",
                    descripcion: `Cita agendada para el psicólogo ID ${data.psicologo_id} en fecha/hora: ${data.fecha_hora_inicio}.`
                });
            } catch (auditErr) {
                console.warn('Error al registrar auditoría:', auditErr);
            }
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
            try {
                const eventType = accion === 'confirmar' ? 'cita_confirmed' : 'cita_cancelled';
                const desc = accion === 'confirmar' 
                    ? `Cita ID ${id} confirmada por el profesional.`
                    : `Cita ID ${id} cancelada. Motivo: ${data?.motivo || 'No especificado'}.`;
                await registrarEventoAuditoria({
                    event_type: eventType,
                    category: "citas",
                    status: "success",
                    modulo: "citas",
                    descripcion: desc
                });
            } catch (auditErr) {
                console.warn('Error al registrar auditoría:', auditErr);
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
