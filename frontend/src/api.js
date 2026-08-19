const API_BASE = '/api'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.error || 'Something went wrong')
  }
  return data
}

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
}
