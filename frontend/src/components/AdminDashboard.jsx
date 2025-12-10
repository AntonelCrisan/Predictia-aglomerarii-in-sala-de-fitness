import { useEffect, useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "./AuthContext";
import "./Admin.css";

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/admin/users")
      .then(res => res.json())
      .then(data => setUsers(data));
  }, []);

  async function deleteUser(id) {
    const res = await fetch(`http://localhost:8000/admin/users/${id}`, {
      method: "DELETE"
    });

    if (res.ok) {
      setUsers(users.filter(u => u.id !== id));
    } else {
      alert("Eroare la ștergere");
    }
  }

  const handleLogout = () => {
    logout();
    window.location.href = "/";
  };

  return (
    <div className="admin-container">
      <nav className="admin-nav">
        <div className="user-info">
          <span className="user-name">
            {user?.nume} ({user?.rol})
          </span>
          <button
            onClick={handleLogout}
            className="logout-btn"
          >
            Logout
          </button>
        </div>
      </nav>

      <h1>Panou Administrator</h1>
      <h3>Gestionare utilizatori</h3>

      <table className="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nume</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Acțiuni</th>
          </tr>
        </thead>

        <tbody>
          {users.map(u => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.nume}</td>
              <td>{u.email}</td>
              <td>{u.rol}</td>

              <td>
                <button className="btn-delete" onClick={() => deleteUser(u.id)}>
                  Șterge
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
