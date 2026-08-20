export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div>
          <div className="brand footer-brand">
            <img className="brand-logo footer-logo" src="/manidham-logo.png" alt="Manidham logo" />
            <span>
              <strong>Manidham Trust</strong>
              <small>Education · Blood · Food</small>
            </span>
          </div>
          <p>Building a compassionate ecosystem where no child is left behind, no patient waits for blood, and no meal goes to waste.</p>
        </div>
        <div>
          <h4>Initiatives</h4>
          <a href="#education">Education</a>
          <a href="#blood">Blood Donation</a>
          <a href="#food">Food Redistribution</a>
        </div>
        <div>
          <h4>Participate</h4>
          <a href="#get-involved">Donor Enrollment</a>
          <a href="#get-involved">Restaurant Partners</a>
          <a href="#get-involved">Care Institutions</a>
        </div>
      </div>
      <div className="footer-bottom">
        <div className="container">
          <p>© {new Date().getFullYear()} Manidham Trust. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
