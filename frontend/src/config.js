function isLocalHostname(hostname) {
  return ['localhost', '127.0.0.1', '::1'].includes(hostname)
}

function isLocalUrl(value) {
  if (!value) return false

  try {
    return isLocalHostname(new URL(value).hostname)
  } catch {
    return false
  }
}

function resolveBackendUrl(value) {
  const configuredUrl = value?.trim()
  const pageIsLocal = isLocalHostname(window.location.hostname)

  if (configuredUrl && (pageIsLocal || !isLocalUrl(configuredUrl))) {
    return configuredUrl
  }

  if (pageIsLocal) {
    return `${window.location.protocol}//${window.location.hostname}:5000`
  }

  return window.location.origin
}

export const API_BASE = resolveBackendUrl(import.meta.env.VITE_API_BASE)
export const SOCKET_URL = resolveBackendUrl(import.meta.env.VITE_SOCKET_URL || API_BASE)
export const HAS_PRODUCTION_LOCALHOST_BACKEND = (
  !isLocalHostname(window.location.hostname) &&
  (isLocalUrl(import.meta.env.VITE_API_BASE) || isLocalUrl(import.meta.env.VITE_SOCKET_URL))
)
