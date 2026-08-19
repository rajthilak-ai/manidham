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
          {[
            [IMAGES.community, 'Volunteers coordinating community outreach', 'Volunteers'],
            [IMAGES.restaurant, 'Partner restaurant dining hall', 'Restaurant Partners'],
            [IMAGES.orphanage, 'Child smiling while painting at an orphanage', 'Orphanages'],
            [IMAGES.oldAge, 'Elderly resident enjoying a quiet afternoon', 'Old Age Homes'],
          ].map(([src, alt, caption]) => (
            <figure key={caption}>
              <img src={src} alt={alt} loading="lazy" />
              <figcaption>{caption}</figcaption>
            </figure>
          ))}
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
