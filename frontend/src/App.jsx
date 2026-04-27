import { useState } from "react";
import axios from "axios";
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

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [userId, setUserId] = useState(1);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [runId, setRunId] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [toolSources, setToolSources] = useState([]);

  async function handleAskAgent(e) {
    e.preventDefault();

    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");
    setRunId(null);
    setStatus("");
    setToolSources([]);

    try {
      const response = await axios.post(`${API_BASE_URL}/agent/ask`, {
        user_id: Number(userId),
        question,
      });

      setAnswer(response.data.answer);
      setRunId(response.data.run_id);
      setStatus(response.data.status);

      const sourceMatches = response.data.answer.match(/documents are: (.*?)\./);
      if (sourceMatches?.[1]) {
        setToolSources(sourceMatches[1].split(",").map((item) => item.trim()));
      }
    } catch (error) {
      setAnswer("Something went wrong. Make sure the FastAPI backend is running.");
      setStatus("error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div className="hero-badge">
          <Sparkles size={16} />
          AI Travel Planner
        </div>

        <h1>Smart Travel Planner</h1>
        <p>
          Ask for a trip idea and the assistant will use RAG, stored destination
          knowledge, and live weather data to build a travel recommendation.
        </p>
      </section>

      <section className="layout">
        <div className="chat-card">
          <div className="card-header">
            <div>
              <h2>Plan a trip</h2>
              <p>Describe your budget, dates, weather preference, and activities.</p>
            </div>
            <Plane className="header-icon" />
          </div>

          <form onSubmit={handleAskAgent} className="chat-form">
            <label>
              User ID
              <input
                type="number"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                min="1"
              />
            </label>

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
              <p>{answer}</p>
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

          <div className="tool-card">
            <Search size={22} />
            <div>
              <h3>ML Classifier</h3>
              <p>Will classify destination travel style.</p>
            </div>
          </div>

          <div className="sources">
            <h3>
              <MapPin size={17} />
              Retrieved Sources
            </h3>

            {toolSources.length > 0 ? (
              toolSources.map((source) => <span key={source}>{source}</span>)
            ) : (
              <p className="muted">No sources retrieved yet.</p>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

export default App;