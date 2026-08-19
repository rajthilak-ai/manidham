import { useState } from 'react'
import { FadeIn } from './Animated'
import { api } from '../api'
import { BLOOD_GROUPS } from '../constants/images'

export default function DonorSearch() {
  const [filters, setFilters] = useState({ city: '', district: '', blood_group: 'O+' })
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const data = await api.searchDonors(filters)
      setResults(data.donors)
      setSearched(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <FadeIn delay={0.1}>
      <div className="form-card search-card">
        <h3>Find Matching Donors</h3>
        <p>Search by area and blood group for urgent patient requests.</p>

        <form className="search-bar" onSubmit={handleSearch}>
          <input
            placeholder="City"
            value={filters.city}
            onChange={(e) => setFilters({ ...filters, city: e.target.value })}
          />
          <input
            placeholder="District"
            value={filters.district}
            onChange={(e) => setFilters({ ...filters, district: e.target.value })}
          />
          <select
            value={filters.blood_group}
            onChange={(e) => setFilters({ ...filters, blood_group: e.target.value })}
          >
            {BLOOD_GROUPS.map((group) => (
              <option key={group} value={group}>{group}</option>
            ))}
          </select>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Searching...' : 'Search Donors'}
          </button>
        </form>

        {error && <div className="form-status error">{error}</div>}

        {searched && (
          <div className="results-panel">
            <h4>{results.length} donor{results.length !== 1 ? 's' : ''} available</h4>
            {results.length === 0 ? (
              <p className="muted">No donors match this criteria yet. Submit an urgent request below to notify registered donors.</p>
            ) : (
              <>
                <p className="muted privacy-note">
                  To protect our donors, contact details stay private. Submit an urgent
                  request below and every matching donor is notified immediately.
                </p>
                <div className="results-grid">
                  {results.map((donor) => (
                    <article key={donor.id} className="result-card">
                      <div className="result-header">
                        <strong>{donor.name}</strong>
                        <span className="badge">{donor.blood_group}</span>
                      </div>
                      <p>{donor.city}, {donor.district}, {donor.country}</p>
                      {donor.is_international && <span className="tag">International Donor</span>}
                    </article>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </FadeIn>
  )
}
