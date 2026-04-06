const defaultBackendUrl = 'http://localhost:5000'

export const API_BASE = import.meta.env.VITE_API_BASE || defaultBackendUrl
export const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || API_BASE
