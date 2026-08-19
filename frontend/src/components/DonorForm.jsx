import { useState } from 'react'
import { FadeIn } from './Animated'
import { api } from '../api'
import { BLOOD_GROUPS } from '../constants/images'

const initialDonor = {
  name: '',
  blood_group: 'O+',
  phone: '',
  email: '',
  age: '',
  date_of_birth: '',
  city: '',
  district: '',
  country: 'India',
  is_international: false,
}

export default function DonorForm() {
  const [form, setForm] = useState(initialDonor)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const update = (field, value) => setForm((prev) => ({ ...prev, [field]: value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setStatus(null)
    try {
      await api.createDonor({ ...form, age: Number(form.age) })
      setStatus({ type: 'success', message: 'Thank you! You are now enrolled as a blood donor.' })
      setForm(initialDonor)
    } catch (error) {
      setStatus({ type: 'error', message: error.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <FadeIn>
      <form className="form-card" onSubmit={handleSubmit}>
        <h3>Donor Enrollment</h3>
        <p>Register to save lives. International donors are welcome.</p>

        <div className="form-grid">
          <label>
            Full Name
            <input required value={form.name} onChange={(e) => update('name', e.target.value)} />
          </label>
          <label>
            Blood Group
            <select value={form.blood_group} onChange={(e) => update('blood_group', e.target.value)}>
              {BLOOD_GROUPS.map((group) => (
                <option key={group} value={group}>{group}</option>
              ))}
            </select>
          </label>
          <label>
            Phone Number
            <input required value={form.phone} onChange={(e) => update('phone', e.target.value)} />
          </label>
          <label>
            Email ID
            <input required type="email" value={form.email} onChange={(e) => update('email', e.target.value)} />
          </label>
          <label>
            Age
            <input required type="number" min="18" max="65" value={form.age} onChange={(e) => update('age', e.target.value)} />
          </label>
          <label>
            Date of Birth
            <input required type="date" value={form.date_of_birth} onChange={(e) => update('date_of_birth', e.target.value)} />
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
            Country
            <input required value={form.country} onChange={(e) => update('country', e.target.value)} />
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={form.is_international}
              onChange={(e) => update('is_international', e.target.checked)}
            />
            International Donor (enrolling from abroad)
          </label>
        </div>

        {status && <div className={`form-status ${status.type}`}>{status.message}</div>}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Enrolling...' : 'Enroll as Donor'}
        </button>
      </form>
    </FadeIn>
  )
}
