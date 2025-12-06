import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import PredictorCard from "./components/PredictorCard";
import GymsList from "./components/GymList";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<GymsList />} />
        <Route path="/predict" element={<PredictorCard />} />
      </Routes>
    </Router>
  );
}

export default App;
