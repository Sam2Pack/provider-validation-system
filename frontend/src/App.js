import { useState } from "react";

function App() {
  const [page, setPage] = useState("home");

  return (
    <div style={styles.app}>
      {page === "home" ? (
        <Home goToApp={() => setPage("app")} />
      ) : (
        <Validation goHome={() => setPage("home")} />
      )}
    </div>
  );
}

/* ================= HOME PAGE ================= */

function Home({ goToApp }) {
  return (
    <div style={styles.homeContainer}>
      <div style={styles.hero}>
        <h1 style={styles.title}>Provider Intelligence System</h1>
        <p style={styles.subtitle}>
          AI-powered healthcare provider validation and enrichment
        </p>

        <button style={styles.ctaButton} onClick={goToApp}>
          🚀 Start Validation
        </button>
      </div>

      {/* Feature cards */}
      <div style={styles.features}>
        <Feature title="Real-time Validation" desc="Instant NPI verification using live registry API" />
        <Feature title="Confidence Scoring" desc="Smart scoring engine with explainable results" />
        <Feature title="Doctor Insights" desc="Fetch full provider details in seconds" />
      </div>
    </div>
  );
}

function Feature({ title, desc }) {
  return (
    <div style={styles.featureCard}>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
  );
}

/* ================= VALIDATION PAGE ================= */

function Validation({ goHome }) {
  const [form, setForm] = useState({
    npi: "",
    provider_first_name: "",
    provider_last_name: "",
    provider_address: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      const data = await res.json();
      setResult(data);
    } catch {
      alert("Server error. Try again.");
    }

    setLoading(false);
  };

  const getColor = (c) => {
    if (c >= 0.8) return "#16a34a";
    if (c >= 0.5) return "#ca8a04";
    return "#dc2626";
  };

  return (
    <div style={styles.container}>
      <button style={styles.backButton} onClick={goHome}>
        ⬅ Back
      </button>

      <div style={styles.card}>
        <h2>Doctor Lookup</h2>

        <input style={styles.input} name="npi" placeholder="NPI" onChange={handleChange} />
        <input style={styles.input} name="provider_first_name" placeholder="First Name" onChange={handleChange} />
        <input style={styles.input} name="provider_last_name" placeholder="Last Name" onChange={handleChange} />
        <input style={styles.input} name="provider_address" placeholder="Address" onChange={handleChange} />

        <button style={styles.button} onClick={handleSubmit}>
          Check Confidence
        </button>

        {loading && <p>🔄 Checking...</p>}
      </div>

      {result && (
        <div style={styles.resultCard}>
          <h2>Validation Result</h2>

          <p>
            <b>Status:</b>{" "}
            <span style={{ color: getColor(result.confidence) }}>
              {result.status}
            </span>
          </p>

          <p>
            <b>Confidence:</b>{" "}
            {(result.confidence * 100).toFixed(2)}%
          </p>

          {/* Progress */}
          <div style={styles.progressBg}>
            <div
              style={{
                ...styles.progressFill,
                width: `${result.confidence * 100}%`,
                background: getColor(result.confidence),
              }}
            >
              {(result.confidence * 100).toFixed(0)}%
            </div>
          </div>

          <hr />

          <h3>Doctor Details</h3>
          <p><b>Name:</b> {result.details.full_name}</p>
          <p><b>Address:</b> {result.details.address}</p>
          <p><b>Specialization:</b> {result.details.taxonomy}</p>
          <p><b>Registered On:</b> {result.details.enumeration_date}</p>

          {result.details.full_name === "Not Found" && (
            <p style={{ color: "red" }}>
              ⚠ No record found in NPI database
            </p>
          )}
        </div>
      )}
    </div>
  );
}

/* ================= STYLES ================= */

const styles = {
  app: {
    fontFamily: "Arial",
    minHeight: "100vh",
    background: "linear-gradient(135deg, #0f172a, #1e3a8a, #2563eb)",
    color: "white",
  },

  homeContainer: {
    textAlign: "center",
    padding: "80px 20px",
  },

  hero: {
    marginBottom: "60px",
  },

  title: {
    fontSize: "48px",
    fontWeight: "bold",
    background: "linear-gradient(90deg, #38bdf8, #6366f1)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },

  subtitle: {
    color: "#cbd5f5",
    marginBottom: "30px",
    fontSize: "18px",
  },

  ctaButton: {
    padding: "14px 30px",
    background: "linear-gradient(90deg, #3b82f6, #6366f1)",
    color: "white",
    border: "none",
    borderRadius: "12px",
    fontSize: "16px",
    cursor: "pointer",
    boxShadow: "0 8px 25px rgba(99,102,241,0.5)",
  },

  features: {
    display: "flex",
    justifyContent: "center",
    gap: "25px",
    flexWrap: "wrap",
  },

  featureCard: {
    backdropFilter: "blur(12px)",
    background: "rgba(255,255,255,0.08)",
    borderRadius: "16px",
    padding: "20px",
    width: "260px",
    boxShadow: "0 8px 30px rgba(0,0,0,0.3)",
    border: "1px solid rgba(255,255,255,0.1)",
  },

  container: {
    padding: "30px",
  },

  backButton: {
    marginBottom: "20px",
    padding: "10px 15px",
    border: "none",
    background: "rgba(255,255,255,0.1)",
    color: "white",
    borderRadius: "8px",
    cursor: "pointer",
  },

  card: {
    backdropFilter: "blur(14px)",
    background: "rgba(255,255,255,0.1)",
    padding: "25px",
    borderRadius: "16px",
    maxWidth: "420px",
    margin: "auto",
    boxShadow: "0 10px 40px rgba(0,0,0,0.4)",
    border: "1px solid rgba(255,255,255,0.15)",
  },

  resultCard: {
    backdropFilter: "blur(14px)",
    background: "rgba(255,255,255,0.1)",
    padding: "25px",
    borderRadius: "16px",
    maxWidth: "500px",
    margin: "20px auto",
    boxShadow: "0 10px 40px rgba(0,0,0,0.4)",
    border: "1px solid rgba(255,255,255,0.15)",
  },

  input: {
    width: "100%",
    padding: "12px",
    marginBottom: "12px",
    borderRadius: "10px",
    border: "1px solid rgba(255,255,255,0.2)",
    background: "rgba(255,255,255,0.05)",
    color: "white",
  },

  button: {
    width: "100%",
    padding: "14px",
    borderRadius: "10px",
    border: "none",
    background: "linear-gradient(90deg, #3b82f6, #6366f1)",
    color: "white",
    fontWeight: "bold",
    cursor: "pointer",
    boxShadow: "0 6px 20px rgba(59,130,246,0.5)",
  },

  progressBg: {
    width: "100%",
    background: "rgba(255,255,255,0.1)",
    borderRadius: "10px",
    overflow: "hidden",
    marginTop: "12px",
  },

  progressFill: {
    padding: "6px",
    color: "white",
    textAlign: "center",
    fontSize: "12px",
  },
};

export default App;