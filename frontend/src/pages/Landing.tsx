import React from "react";
import { Link } from "react-router-dom";

const steps = [
  { n: "01", title: "Create event", text: "Admin spins up an event and adds shooters by email." },
  { n: "02", title: "Team uploads", text: "Crew batch-uploads selects straight from the floor." },
  { n: "03", title: "Admin selects", text: "Lead curates keepers for the final gallery." },
  { n: "04", title: "Publish + PIN", text: "One click generates a shareable link and a 6-digit PIN." },
  { n: "05", title: "Customer views", text: "Clients open the link, enter the PIN. No account, no friction." },
];

const testimonials = [
  { quote: "We delivered a 1,200-photo wedding gallery the same night. The couple had their link before the afterparty ended.", name: "Meera K.", role: "Lead Photographer, Lumen Weddings", img: "https://picsum.photos/seed/trizen-face1/160/160" },
  { quote: "My second shooters just upload. I pick keepers, hit publish, and send one link with a PIN. That is the whole workflow.", name: "Arjun S.", role: "Studio Owner, Framehouse", img: "https://picsum.photos/seed/trizen-face2/160/160" },
  { quote: "Clients love that there is no login. They tap the link, type the PIN, and relive the day.", name: "Priya R.", role: "Event Lead, Aura Films", img: "https://picsum.photos/seed/trizen-face3/160/160" },
];

const Landing: React.FC = () => {
  return (
    <div>
      <div className="band">
        <img className="bg" src="https://picsum.photos/seed/trizen-hero/1600/900" alt="Wedding celebration captured by an event photographer" />
        <div className="scrim">
          <div className="kicker">Trizen Photos // Event Darkroom</div>
          <h1>Beautiful events,<br />delivered beautifully.</h1>
          <p className="lead">
            The photo-sharing platform for event teams. Upload together, curate the
            keepers, and deliver PIN-protected galleries your customers will actually open.
          </p>
          <div className="cta-row" style={{ justifyContent: "flex-start" }}>
            <Link to="/register" className="btn">Get started</Link>
            <Link to="/login" className="btn btn-ghost" style={{ color: "#fff", borderColor: "rgba(255,255,255,0.4)" }}>Enter studio</Link>
          </div>
        </div>
      </div>

      <div className="stats-strip">
        <div className="stat"><b>1,250</b><span>photos per event</span></div>
        <div className="stat"><b>600</b><span>curated selects</span></div>
        <div className="stat"><b>6-digit</b><span>PIN protection</span></div>
        <div className="stat"><b>0</b><span>accounts for clients</span></div>
      </div>

      <h2>How it works</h2>
      <div className="workflow">
        {steps.map((s) => (
          <div key={s.n} className="step">
            <b>{s.n}</b>
            <h4>{s.title}</h4>
            <p className="muted">{s.text}</p>
          </div>
        ))}
      </div>

      <div className="band">
        <img className="bg" src="https://picsum.photos/seed/trizen-team/1600/800" alt="Photography team at work during an event" loading="lazy" />
        <div className="scrim">
          <div className="kicker">For the whole crew</div>
          <h2>Everyone shoots. One gallery ships.</h2>
          <p>Second shooters upload straight from the floor while the lead curates from anywhere.</p>
        </div>
      </div>

      <h2>Loved by event crews</h2>
      <div className="testimonials">
        {testimonials.map((t) => (
          <figure key={t.name} className="testimonial">
            <blockquote>"{t.quote}"</blockquote>
            <figcaption>
              <img className="avatar" src={t.img} alt={`Portrait of ${t.name}`} loading="lazy" />
              <span><strong>{t.name}</strong><br /><span className="role">{t.role}</span></span>
            </figcaption>
          </figure>
        ))}
      </div>

      <div className="band">
        <img className="bg" src="https://picsum.photos/seed/trizen-couple/1600/800" alt="Happy couple viewing their wedding gallery" loading="lazy" />
        <div className="scrim" style={{ textAlign: "center", alignItems: "center" }}>
          <h2>Your next event deserves a beautiful delivery</h2>
          <p>Gallery link plus PIN, in one click. No client accounts, ever.</p>
          <p className="pin-demo">Gallery URL: /gallery/abc123 &nbsp;|&nbsp; Access PIN: shared privately with your client</p>
          <div className="cta-row">
            <Link to="/register" className="btn">Start free as a studio</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Landing;
