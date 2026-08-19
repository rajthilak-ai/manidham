import { useState } from 'react'
import { FadeIn } from './Animated'
import { api } from '../api'

const initial = {
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  address: '',
  city: '',
  district: '',
  institution_type: 'orphanage',
}

export default function InstitutionForm() {
  const [form, setForm] = useState(initial)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const update = (field, value) => setForm((prev) => ({ ...prev, [field]: value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setStatus(null)
    try {
      await api.createInstitution(form)
      setStatus({
        type: 'success',
        message: 'Institution enrolled! You will receive notifications when food is available nearby.',
      })
      setForm(initial)
    } catch (error) {
      setStatus({ type: 'error', message: error.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <FadeIn delay={0.1}>
      <form className="form-card" onSubmit={handleSubmit}>
        <h3>Orphanage / Old Age Home Enrollment</h3>
        <p>Register to receive food availability alerts from restaurants in your area.</p>

        <div className="form-grid">
          <label>
            Institution Name
            <input required value={form.name} onChange={(e) => update('name', e.target.value)} />
          </label>
          <label>
            Contact Person
            <input required value={form.contact_person} onChange={(e) => update('contact_person', e.target.value)} />
          </label>
          <label>
            Phone
            <input required value={form.phone} onChange={(e) => update('phone', e.target.value)} />
          </label>
          <label>
            Email
            <input required type="email" value={form.email} onChange={(e) => update('email', e.target.value)} />
          </label>
          <label className="full-width">
            Address
            <input required value={form.address} onChange={(e) => update('address', e.target.value)} />
          </label>
          <label>
            City
            <input required value={form.city} onChange={(e) => update('city', e.target.value)} />
          </label>
          <label>
            District
            <input required value={form.district} onChange={(e) => update('district', e.target.value)} />
          </label>
          <label>
            Type
            <select
              value={form.institution_type}
              onChange={(e) => update('institution_type', e.target.value)}
            >
              <option value="orphanage">Orphanage</option>
              <option value="old_age_home">Old Age Home</option>
            </select>
          </label>
        </div>

        {status && <div className={`form-status ${status.type}`}>{status.message}</div>}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Enrolling...' : 'Enroll Institution'}
        </button>
      </form>
    </FadeIn>
  )
}
