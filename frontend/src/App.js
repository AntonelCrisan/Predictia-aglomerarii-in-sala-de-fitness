import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./components/AuthContext";
import GymsList from "./components/GymList";
import PredictorCard from "./components/PredictorCard";
import Login from "./components/Login";
import Register from "./components/Register";
import AdminDashboard from "./components/AdminDashboard";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Pagini autentificare */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/admin-dashboard" element={<AdminDashboard />} />
          {/* Pagina principală */}
          <Route path="/" element={<GymsList />} />

          {/* Pagina predictor */}
          <Route path="/predict" element={<PredictorCard />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
