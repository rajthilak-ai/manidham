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
}

export default function RestaurantForm() {
  const [form, setForm] = useState(initial)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [restaurantId, setRestaurantId] = useState(null)
  const [foodForm, setFoodForm] = useState({ description: '', quantity: '' })

  const update = (field, value) => setForm((prev) => ({ ...prev, [field]: value }))

  const handleEnroll = async (event) => {
    event.preventDefault()
    setLoading(true)
    setStatus(null)
    try {
      const result = await api.createRestaurant(form)
      setRestaurantId(result.restaurant.id)
      setStatus({ type: 'success', message: 'Restaurant enrolled! You can now log surplus food below.' })
    } catch (error) {
      setStatus({ type: 'error', message: error.message })
    } finally {
      setLoading(false)
    }
  }

  const handleFoodLog = async (event) => {
    event.preventDefault()
    if (!restaurantId) return
    setLoading(true)
    try {
      const result = await api.logFood({ restaurant_id: restaurantId, ...foodForm })
      setStatus({
        type: 'success',
        message: `Food logged! ${result.notifications_sent} institution(s) notified in your area.`,
      })
      setFoodForm({ description: '', quantity: '' })
    } catch (error) {
      setStatus({ type: 'error', message: error.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <FadeIn>
      <form className="form-card" onSubmit={handleEnroll}>
        <h3>Restaurant / Hotel Enrollment</h3>
        <p>Register to coordinate surplus food redistribution to nearby care homes.</p>

        <div className="form-grid">
          <label>
            Restaurant / Hotel Name
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
        </div>

        {status && <div className={`form-status ${status.type}`}>{status.message}</div>}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Enrolling...' : 'Enroll Restaurant'}
        </button>
      </form>

      {restaurantId && (
        <form className="form-card food-log-card" onSubmit={handleFoodLog}>
          <h3>Log Surplus Food</h3>
          <p>Notify orphanages and old age homes when food is available for pickup.</p>
          <div className="form-grid">
            <label className="full-width">
              Food Description
              <input
                required
                placeholder="e.g. 50 vegetarian meals, rice and dal"
                value={foodForm.description}
                onChange={(e) => setFoodForm({ ...foodForm, description: e.target.value })}
              />
            </label>
            <label>
              Quantity
              <input
                required
                placeholder="e.g. 50 meals"
                value={foodForm.quantity}
                onChange={(e) => setFoodForm({ ...foodForm, quantity: e.target.value })}
              />
            </label>
          </div>
          <button type="submit" className="btn btn-secondary" disabled={loading}>
            {loading ? 'Notifying...' : 'Notify Nearby Institutions'}
          </button>
        </form>
      )}
    </FadeIn>
  )
}
