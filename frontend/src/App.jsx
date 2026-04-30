import { useState } from "react";
import { api } from "./api";
import AuthPanel from "./AuthPanel";
import {
  Plane,
  MapPin,
  Send,
  Sparkles,
  Search,
  CloudSun,
  Database,
  Bot,
} from "lucide-react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [runId, setRunId] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [toolSources, setToolSources] = useState([]);
  const [cost, setCost] = useState(null);

  const [user, setUser] = useState(() => {
    const email = localStorage.getItem("user_email");
    return email ? { email } : null;
  });

  async function handleAskAgent(e) {
    e.preventDefault();

    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");
    setRunId(null);
    setStatus("");
    setToolSources([]);
    setCost(null);

    try {
      const response = await api.post("/agent/ask", {
        question,
      });

      setAnswer(response.data.answer);
      setRunId(response.data.run_id);
      setStatus(response.data.status);

      setCost(
        typeof response.data.total_cost_usd === "number"
          ? response.data.total_cost_usd
          : null
      );

      const sourceMatches = response.data.answer.match(/RAG retrieved: (.*?)\./);

      if (sourceMatches?.[1]) {
        setToolSources(sourceMatches[1].split(",").map((item) => item.trim()));
      }
    } catch (error) {
      setAnswer(
        "Something went wrong. Make sure you are logged in and the FastAPI backend is running."
      );
      setStatus("error");
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_email");
    setUser(null);
    setAnswer("");
    setRunId(null);
    setStatus("");
    setToolSources([]);
    setCost(null);
  }

  return (
    <main className="app-shell">
      {!user ? (
        <AuthPanel onLogin={setUser} />
      ) : (
        <>
          <section className="hero">
            <div className="hero-badge">
              <Sparkles size={16} />
              AI Travel Planner
            </div>

            <h1>VoyageAI</h1>

            <p>
              Ask for a trip idea and the assistant will use RAG, stored
              destination knowledge, ML classification, and live weather data to
              build a travel recommendation.
            </p>

            <button
              type="button"
              className="logout-button"
              onClick={handleLogout}
            >
              Logout
            </button>
          </section>

          <section className="layout">
            <div className="chat-card">
              <div className="card-header">
                <div>
                  <h2>Plan a trip</h2>
                  <p>
                    Describe your budget, dates, weather preference, and
                    activities.
                  </p>
                </div>
                <Plane className="header-icon" />
              </div>

              <form onSubmit={handleAskAgent} className="chat-form">
                <label>
                  Travel question
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Example: I want somewhere warm with hiking and fewer crowds."
                  />
                </label>

                <button type="submit" disabled={loading}>
                  {loading ? "Planning..." : "Ask Agent"}
                  <Send size={18} />
                </button>
              </form>

              <div className="answer-box">
                <div className="answer-title">
                  <Bot size={18} />
                  Agent Answer
                </div>

                {answer ? (
                  <>
                    <p style={{ whiteSpace: "pre-line" }}>{answer}</p>

                    {typeof cost === "number" && (
                      <p className="cost">
                        Estimated Cost: ${cost.toFixed(6)}
                      </p>
                    )}
                  </>
                ) : (
                  <p className="muted">
                    Your travel plan will appear here after you ask the agent.
                  </p>
                )}

                {runId && (
                  <div className="run-meta">
                    <span>Run ID: {runId}</span>
                    <span>Status: {status}</span>
                  </div>
                )}
              </div>
            </div>

            <aside className="tools-panel">
              <h2>Tool Activity</h2>

              <div className="tool-card active">
                <Database size={22} />
                <div>
                  <h3>RAG Retrieval</h3>
                  <p>Searches stored destination documents.</p>
                </div>
              </div>

              <div className="tool-card active">
                <CloudSun size={22} />
                <div>
                  <h3>Live Weather</h3>
                  <p>Checks current weather for the selected destination.</p>
                </div>
              </div>

              <div className="tool-card active">
                <Search size={22} />
                <div>
                  <h3>ML Classifier</h3>
                  <p>Classifies the travel style of the recommendation.</p>
                </div>
              </div>

              <div className="sources">
                <h3>
                  <MapPin size={17} />
                  Retrieved Sources
                </h3>

                {toolSources.length > 0 ? (
                  toolSources.map((source) => (
                    <span key={source}>{source}</span>
                  ))
                ) : (
                  <p className="muted">
                    Sources are stored in the backend logs.
                  </p>
                )}
              </div>
            </aside>
          </section>
        </>
      )}
    </main>
  );
}

export default App;