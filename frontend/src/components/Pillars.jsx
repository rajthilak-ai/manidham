import { FadeIn, ParallaxSection, TiltCard } from './Animated'
import { IMAGES } from '../constants/images'

const pillars = [
  {
    id: 'education',
    title: 'Education for Every Child',
    label: 'Pillar One · Education',
    image: IMAGES.education,
    accent: 'education',
    description:
      'We bridge the gap for underprivileged children with scholarships, learning materials, and mentorship programs that unlock their full potential.',
    points: ['School enrollment support', 'Digital learning access', 'Mentorship & tutoring'],
  },
  {
    id: 'blood',
    title: 'Direct Blood Donation',
    label: 'Pillar Two · Blood',
    image: IMAGES.blood,
    accent: 'blood',
    description:
      'Our platform connects verified blood donors directly with patients—no middlemen, no delays. Search by area and blood group for urgent matches.',
    points: ['Area-based donor search', 'Instant urgent alerts', 'International donor support'],
  },
  {
    id: 'food',
    title: 'Food Waste to Hope',
    label: 'Pillar Three · Food',
    image: IMAGES.food,
    accent: 'food',
    description:
      'Hotels and restaurants register surplus food; orphanages and old age homes in the same area receive instant notifications to collect nourishing meals.',
    points: ['Hotel surplus logging', 'Local institution matching', 'Zero-waste redistribution'],
  },
]

export default function Pillars() {
  return (
    <>
      {pillars.map((pillar, index) => (
        <section key={pillar.id} id={pillar.id} className={`pillar pillar-${pillar.accent}`}>
          <div className={`container pillar-grid ${index % 2 === 1 ? 'reverse' : ''}`}>
            <FadeIn delay={0.1}>
              <div className="pillar-copy">
                <span className="section-tag">{pillar.label}</span>
                <h2>{pillar.title}</h2>
                <p>{pillar.description}</p>
                <ul>
                  {pillar.points.map((point) => (
                    <li key={point}>{point}</li>
                  ))}
                </ul>
              </div>
            </FadeIn>

            <FadeIn delay={0.2}>
              <TiltCard className={`pillar-image-wrap image-${pillar.accent}`}>
                <img src={pillar.image} alt={pillar.title} loading="lazy" />
                <div className="image-glow" />
              </TiltCard>
            </FadeIn>
          </div>
        </section>
      ))}

      <ParallaxSection image={IMAGES.mission} className="mission-banner">
        <FadeIn>
          <h2>One platform. Three lifelines. Infinite compassion.</h2>
          <p>
            Manidham brings together donors, restaurants, and care institutions into a single
            ecosystem designed for speed, dignity, and measurable community impact.
          </p>
        </FadeIn>
      </ParallaxSection>
    </>
  )
}
