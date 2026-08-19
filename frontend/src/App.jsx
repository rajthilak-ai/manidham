import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Pillars from './components/Pillars'
import GetInvolved from './components/GetInvolved'
import AdminDashboard from './components/AdminDashboard'
import Footer from './components/Footer'

export default function App() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Pillars />
        <GetInvolved />
        <AdminDashboard />
      </main>
      <Footer />
    </>
  )
}
