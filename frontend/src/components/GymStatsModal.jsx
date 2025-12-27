import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, CartesianGrid
} from "recharts";
import "./GymStats.css";

export default function GymStatsModal({ gym, onClose }) {
  if (!gym?.stats) return null;

  const { kpi, daily, hourly } = gym.stats;

  return (
    <div className="stats-overlay" onClick={onClose}>
      <div className="stats-modal" onClick={(e) => e.stopPropagation()}>
        <button className="stats-close" onClick={onClose}>×</button>

        <h2>{gym.nume} – Statistici</h2>

        {/* KPI */}
        <div className="kpi-grid">
          <div className="kpi-card">
            <span>Medie zilnică</span>
            <strong>{kpi.medie}</strong>
          </div>
          <div className="kpi-card">
            <span>Maxim înregistrat</span>
            <strong>{kpi.maxim}</strong>
          </div>
        </div>

        {/* Evoluție zilnică */}
        <div className="chart-block">
          <h4>Evoluție zilnică</h4>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={daily}>
              <XAxis dataKey="data" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="medie" stroke="#76c893" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Medie pe ore */}
        <div className="chart-block">
          <h4>Medie pe ore</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={hourly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="ora" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="medie" fill="#52b788" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
