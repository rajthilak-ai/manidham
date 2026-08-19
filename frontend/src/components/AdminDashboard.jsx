import { useEffect, useState } from 'react'
import { FadeIn } from './Animated'
import { api } from '../api'

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [tab, setTab] = useState('overview')
  const [data, setData] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadAll = async () => {
    setLoading(true)
    setError(null)
    try {
      const [statsData, donors, restaurants, institutions, foodLogs, bloodRequests, notifications] =
        await Promise.all([
          api.getStats(),
          api.getDonors(),
          api.getRestaurants(),
          api.getInstitutions(),
          api.getFoodLogs(),
          api.getBloodRequests(),
          api.getNotifications(),
        ])
      setStats(statsData)
      setData({ donors, restaurants, institutions, foodLogs, bloodRequests, notifications })
    } catch {
      setStats(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAll()
  }, [])

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'donors', label: 'Donors' },
    { id: 'restaurants', label: 'Restaurants' },
    { id: 'institutions', label: 'Institutions' },
    { id: 'requests', label: 'Requests' },
    { id: 'notifications', label: 'Notifications' },
  ]

  return (
    <section id="admin" className="admin-section">
      <div className="container">
        <FadeIn>
          <div className="section-heading center">
            <span className="section-tag">Admin Dashboard</span>
            <h2>Platform Overview</h2>
            <p>Monitor enrollments, requests, and notification activity across Manidham.</p>
          </div>
        </FadeIn>

        <div className="admin-tabs">
          {tabs.map((item) => (
            <button
              key={item.id}
              type="button"
              className={tab === item.id ? 'active' : ''}
              onClick={() => setTab(item.id)}
            >
              {item.label}
            </button>
          ))}
          <button type="button" className="refresh-btn" onClick={loadAll}>Refresh</button>
        </div>

        {loading ? (
          <p className="muted center">Loading dashboard...</p>
        ) : (
          <>
            {tab === 'overview' && stats && (
              <div className="stats-grid">
                {Object.entries(stats).map(([key, value]) => (
                  <article key={key} className="admin-stat-card">
                    <strong>{value}</strong>
                    <span>{key.replace(/_/g, ' ')}</span>
                  </article>
                ))}
              </div>
            )}

            {tab === 'donors' && (
              <DataTable
                columns={['name', 'blood_group', 'phone', 'city', 'district', 'country']}
                rows={data.donors || []}
              />
            )}

            {tab === 'restaurants' && (
              <DataTable
                columns={['name', 'contact_person', 'phone', 'city', 'district']}
                rows={data.restaurants || []}
              />
            )}

            {tab === 'institutions' && (
              <DataTable
                columns={['name', 'institution_type', 'phone', 'city', 'district']}
                rows={data.institutions || []}
              />
            )}

            {tab === 'requests' && (
              <div className="admin-split">
                <div>
                  <h4>Blood Requests</h4>
                  <DataTable
                    columns={['patient_name', 'blood_group', 'city', 'contact_phone', 'urgency']}
                    rows={data.bloodRequests || []}
                  />
                </div>
                <div>
                  <h4>Food Logs</h4>
                  <DataTable
                    columns={['restaurant_name', 'description', 'quantity', 'city']}
                    rows={data.foodLogs || []}
                  />
                </div>
              </div>
            )}

            {tab === 'notifications' && (
              <div className="notification-list">
                {(data.notifications || []).map((item) => (
                  <article key={item.id} className={`notification-item ${item.is_read ? 'is-read' : ''}`}>
                    <div>
                      <strong>{item.notification_type.replace(/_/g, ' ')}</strong>
                      <p>{item.message}</p>
                    </div>
                    <div className="notification-meta">
                      <small>{new Date(item.created_at).toLocaleString()}</small>
                      {item.is_read ? (
                        <span className="tag">Read</span>
                      ) : (
                        <button type="button" className="link-btn" onClick={() => markRead(item.id)}>
                          Mark as read
                        </button>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </section>
  )
}

function DataTable({ columns, rows }) {
  if (!rows.length) return <p className="muted">No records yet.</p>

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column.replace(/_/g, ' ')}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              {columns.map((column) => (
                <td key={column}>{row[column] ?? '—'}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
