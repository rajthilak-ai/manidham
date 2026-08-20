const API_BASE = '/api'

async function request(path, options = {}) {
  const isFormData = options.body instanceof FormData
  const headers = { ...(options.headers || {}) }
  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.error || 'Something went wrong')
  }
  return data
}

const authHeaders = (token) => ({ Authorization: `Bearer ${token}` })

export const api = {
  createDonor: (payload) => request('/donors', { method: 'POST', body: JSON.stringify(payload) }),
  searchDonors: (params) => {
    const query = new URLSearchParams(params).toString()
    return request(`/donors/search?${query}`)
  },
  createRestaurant: (payload) => request('/restaurants', { method: 'POST', body: JSON.stringify(payload) }),
  createInstitution: (payload) => request('/institutions', { method: 'POST', body: JSON.stringify(payload) }),
  logFood: (payload) => request('/food-log', { method: 'POST', body: JSON.stringify(payload) }),
  createBloodRequest: (payload) => request('/blood-requests', { method: 'POST', body: JSON.stringify(payload) }),
  getStats: () => request('/admin/stats'),
  getDonors: () => request('/admin/donors'),
  getRestaurants: () => request('/admin/restaurants'),
  getInstitutions: () => request('/admin/institutions'),
  getFoodLogs: () => request('/admin/food-logs'),
  getBloodRequests: () => request('/admin/blood-requests'),
  getNotifications: () => request('/admin/notifications'),

  adminLogin: (payload) => request('/admin/login', { method: 'POST', body: JSON.stringify(payload) }),
  verifyAdmin: (token) => request('/admin/verify', { headers: authHeaders(token) }),

  getGallery: (category) => request(`/gallery${category ? `?category=${category}` : ''}`),
  uploadGalleryImage: (formData, token) =>
    request('/gallery', { method: 'POST', body: formData, headers: authHeaders(token) }),
  deleteGalleryImage: (id, token) =>
    request(`/gallery/${id}`, { method: 'DELETE', headers: authHeaders(token) }),
}
