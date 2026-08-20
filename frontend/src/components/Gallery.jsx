import { useEffect, useState } from 'react'
import { FadeIn } from './Animated'
import { api } from '../api'

const TOKEN_KEY = 'manidham_admin_token'
const USERNAME_KEY = 'manidham_admin_username'

const CATEGORIES = [
  { value: 'general', label: 'General' },
  { value: 'education', label: 'Education' },
  { value: 'blood', label: 'Blood Donation' },
  { value: 'food', label: 'Food Redistribution' },
]

const initialUploadForm = { caption: '', category: 'general', file: null }
const initialLoginForm = { username: '', password: '' }

export default function Gallery() {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || '')
  const [username, setUsername] = useState(() => localStorage.getItem(USERNAME_KEY) || '')
  const [showLogin, setShowLogin] = useState(false)
  const [loginForm, setLoginForm] = useState(initialLoginForm)
  const [loginStatus, setLoginStatus] = useState(null)
  const [loggingIn, setLoggingIn] = useState(false)

  const [uploadForm, setUploadForm] = useState(initialUploadForm)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [fileInputKey, setFileInputKey] = useState(0)

  const loadImages = async (category) => {
    setLoading(true)
    try {
      const data = await api.getGallery(category)
      setImages(data.images || [])
    } catch {
      setImages([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadImages(filter)
  }, [filter])

  useEffect(() => {
    if (!token) return
    api.verifyAdmin(token).catch(() => {
      setToken('')
      setUsername('')
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USERNAME_KEY)
    })
  }, [token])

  const handleLogin = async (event) => {
    event.preventDefault()
    setLoggingIn(true)
    setLoginStatus(null)
    try {
      const data = await api.adminLogin(loginForm)
      setToken(data.token)
      setUsername(data.username)
      localStorage.setItem(TOKEN_KEY, data.token)
      localStorage.setItem(USERNAME_KEY, data.username)
      setLoginForm(initialLoginForm)
      setShowLogin(false)
    } catch (error) {
      setLoginStatus({ type: 'error', message: error.message })
    } finally {
      setLoggingIn(false)
    }
  }

  const handleLogout = () => {
    setToken('')
    setUsername('')
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USERNAME_KEY)
  }

  const handleUpload = async (event) => {
    event.preventDefault()
    if (!uploadForm.file) {
      setUploadStatus({ type: 'error', message: 'Please choose a photo or video file.' })
      return
    }
    setUploading(true)
    setUploadStatus(null)
    try {
      const formData = new FormData()
      formData.append('file', uploadForm.file)
      formData.append('caption', uploadForm.caption)
      formData.append('category', uploadForm.category)
      await api.uploadGalleryImage(formData, token)
      setUploadStatus({ type: 'success', message: 'Media uploaded to the gallery.' })
      setUploadForm(initialUploadForm)
      setFileInputKey((key) => key + 1)
      loadImages(filter)
    } catch (error) {
      setUploadStatus({ type: 'error', message: error.message })
      if (error.message === 'Invalid or expired session') handleLogout()
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await api.deleteGalleryImage(id, token)
      loadImages(filter)
    } catch (error) {
      setUploadStatus({ type: 'error', message: error.message })
      if (error.message === 'Invalid or expired session') handleLogout()
    }
  }

  return (
    <section id="gallery" className="gallery-section">
      <div className="container">
        <FadeIn>
          <div className="section-heading center">
            <span className="section-tag">Gallery</span>
            <h2>Moments from the Manidham Community</h2>
            <p>Photos and videos from our education, blood donation, and food redistribution initiatives.</p>
          </div>
        </FadeIn>

        <div className="gallery-filters">
          <button type="button" className={filter === '' ? 'active' : ''} onClick={() => setFilter('')}>
            All
          </button>
          {CATEGORIES.map((category) => (
            <button
              key={category.value}
              type="button"
              className={filter === category.value ? 'active' : ''}
              onClick={() => setFilter(category.value)}
            >
              {category.label}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="muted center">Loading gallery...</p>
        ) : images.length === 0 ? (
          <p className="muted center">No media uploaded yet. Check back soon.</p>
        ) : (
          <div className="gallery-grid">
            {images.map((image) => (
              <figure key={image.id} className="gallery-item">
                {image.media_type === 'video' ? (
                  <video src={image.url} controls muted playsInline preload="metadata" />
                ) : (
                  <img src={image.url} alt={image.caption || 'Manidham Trust gallery photo'} loading="lazy" />
                )}
                {image.caption && <figcaption>{image.caption}</figcaption>}
                {token && (
                  <button
                    type="button"
                    className="gallery-delete"
                    onClick={() => handleDelete(image.id)}
                    aria-label="Remove media"
                  >
                    Remove
                  </button>
                )}
              </figure>
            ))}
          </div>
        )}

        <div className="gallery-admin">
          {!token ? (
            <div className="gallery-admin-toggle">
              <button type="button" className="btn btn-secondary" onClick={() => setShowLogin((value) => !value)}>
                Admin Login
              </button>
              {showLogin && (
                <form className="form-card admin-login-form" onSubmit={handleLogin}>
                  <h3>Admin Login</h3>
                  <p>Sign in to upload new photos to the gallery.</p>
                  <div className="form-grid">
                    <label>
                      Username
                      <input
                        required
                        value={loginForm.username}
                        onChange={(e) => setLoginForm((prev) => ({ ...prev, username: e.target.value }))}
                      />
                    </label>
                    <label>
                      Password
                      <input
                        required
                        type="password"
                        value={loginForm.password}
                        onChange={(e) => setLoginForm((prev) => ({ ...prev, password: e.target.value }))}
                      />
                    </label>
                  </div>
                  {loginStatus && <div className={`form-status ${loginStatus.type}`}>{loginStatus.message}</div>}
                  <button type="submit" className="btn btn-primary" disabled={loggingIn}>
                    {loggingIn ? 'Signing in...' : 'Sign In'}
                  </button>
                </form>
              )}
            </div>
          ) : (
            <form className="form-card admin-upload-form" onSubmit={handleUpload}>
              <div className="result-header">
                <h3>Upload Gallery Media</h3>
                <button type="button" className="btn btn-secondary" onClick={handleLogout}>
                  Logout ({username || 'admin'})
                </button>
              </div>
              <p>Signed in as admin. New photos and videos appear in the gallery immediately.</p>
              <div className="form-grid">
                <label className="full-width">
                  Photo or Video File
                  <input
                    key={fileInputKey}
                    required
                    type="file"
                    accept="image/png,image/jpeg,image/gif,image/webp,video/mp4,video/webm,video/ogg,video/quicktime"
                    onChange={(e) => setUploadForm((prev) => ({ ...prev, file: e.target.files[0] || null }))}
                  />
                  <small className="muted">Photos: PNG, JPG, GIF, WEBP. Videos: MP4, WEBM, MOV, OGG (up to 50 MB).</small>
                </label>
                <label>
                  Caption (optional)
                  <input
                    value={uploadForm.caption}
                    onChange={(e) => setUploadForm((prev) => ({ ...prev, caption: e.target.value }))}
                  />
                </label>
                <label>
                  Category
                  <select
                    value={uploadForm.category}
                    onChange={(e) => setUploadForm((prev) => ({ ...prev, category: e.target.value }))}
                  >
                    {CATEGORIES.map((category) => (
                      <option key={category.value} value={category.value}>{category.label}</option>
                    ))}
                  </select>
                </label>
              </div>
              {uploadStatus && <div className={`form-status ${uploadStatus.type}`}>{uploadStatus.message}</div>}
              <button type="submit" className="btn btn-primary" disabled={uploading}>
                {uploading ? 'Uploading...' : 'Upload Media'}
              </button>
            </form>
          )}
        </div>
      </div>
    </section>
  )
}
