import { FadeIn } from './Animated'
import { IMAGES } from '../constants/images'
import DonorForm from './DonorForm'
import DonorSearch from './DonorSearch'
import BloodRequestForm from './BloodRequestForm'
import RestaurantForm from './RestaurantForm'
import InstitutionForm from './InstitutionForm'

export default function GetInvolved() {
  return (
    <section id="get-involved" className="get-involved">
      <div className="container">
        <FadeIn>
          <div className="section-heading center">
            <span className="section-tag">Get Involved</span>
            <h2>Join the Manidham Network</h2>
            <p>Enroll as a donor, partner restaurant, or care institution. Every registration strengthens our community lifelines.</p>
          </div>
        </FadeIn>

        <div className="involved-showcase">
          <img src={IMAGES.community} alt="Community volunteers" loading="lazy" />
          <img src={IMAGES.restaurant} alt="Restaurant partner" loading="lazy" />
          <img src={IMAGES.orphanage} alt="Children at orphanage" loading="lazy" />
        </div>

        <div className="forms-layout">
          <div className="forms-column">
            <h3 className="column-title blood-title">Blood Donation</h3>
            <DonorForm />
            <DonorSearch />
            <BloodRequestForm />
          </div>

          <div className="forms-column">
            <h3 className="column-title food-title">Food Redistribution</h3>
            <RestaurantForm />
            <InstitutionForm />
          </div>
        </div>
      </div>
    </section>
  )
}
