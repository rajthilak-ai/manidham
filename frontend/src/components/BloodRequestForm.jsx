import { useState } from 'react'
import { FadeIn } from './Animated'
import { api } from '../api'
import { BLOOD_GROUPS } from '../constants/images'

const initial = {
  patient_name: '',
  blood_group: 'O+',
  city: '',
  district: '',
  contact_phone: '',
  hospital: '',
  urgency: 'urgent',
}

export default function BloodRequestForm() {
  const [form, setForm] = useState(initial)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const update = (field, value) => setForm((prev) => ({ ...prev, [field]: value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setStatus(null)
    try {
      const result = await api.createBloodRequest(form)
      setStatus({
        type: 'success',
        message: `Request submitted. ${result.notifications_sent} matching donor(s) notified.`,
      })
      setForm(initial)
    } catch (error) {
      setStatus({ type: 'error', message: error.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <FadeIn delay={0.15}>
      <form className="form-card urgent-card" onSubmit={handleSubmit}>
        <h3>Urgent Blood Request</h3>
        <p>Submit a request to automatically notify matching donors in the area.</p>

        <div className="form-grid">
          <label>
            Patient Name
            <input required value={form.patient_name} onChange={(e) => update('patient_name', e.target.value)} />
          </label>
          <label>
            Blood Group Needed
            <select value={form.blood_group} onChange={(e) => update('blood_group', e.target.value)}>
              {BLOOD_GROUPS.map((group) => (
                <option key={group} value={group}>{group}</option>
              ))}
            </select>
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
            Contact Phone
            <input required value={form.contact_phone} onChange={(e) => update('contact_phone', e.target.value)} />
          </label>
          <label>
            Hospital (optional)
            <input value={form.hospital} onChange={(e) => update('hospital', e.target.value)} />
          </label>
        </div>

        {status && <div className={`form-status ${status.type}`}>{status.message}</div>}
        <button type="submit" className="btn btn-danger" disabled={loading}>
          {loading ? 'Sending alerts...' : 'Notify Matching Donors'}
        </button>
      </form>
    </FadeIn>
  )
}
