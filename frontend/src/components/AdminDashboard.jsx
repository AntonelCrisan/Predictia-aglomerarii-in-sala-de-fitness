import { useEffect, useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "./AuthContext";
import "./Admin.css";

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { user, logout } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const [gyms, setGyms] = useState([]);
  const [newGym, setNewGym] = useState({ nume: "", localitate: "", judet: "", adresa: "" });
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (user?.rol !== 'administrator' && user?.rol !== 'admin') {
      navigate('/');
      return;
    }

    fetch("http://localhost:8000/admin/users", {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    })
    .then(res => res.json())
    .then(data => setUsers(Array.isArray(data) ? data : []))
    .catch(err => { console.error('Error fetching users:', err); setUsers([]); });

    fetch("http://localhost:8000/admin/sali", {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    })
    .then(res => res.json())
    .then(data => setGyms(Array.isArray(data) ? data : []))
    .catch(err => { console.error('Error fetching gyms:', err); setGyms([]); });
  }, [user, navigate, token]);

  async function deleteUser(id) {
    const res = await fetch(`http://localhost:8000/admin/delete/${id}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (res.ok) {
      setUsers(users.filter(u => u.id !== id));
    } else {
      alert("Eroare la ștergere");
    }
  }

  async function updateUserRole(id, newRole) {
    const res = await fetch(`http://localhost:8000/admin/users/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ rol: newRole })
    });

    if (res.ok) {
      setUsers(users.map(u => u.id === id ? { ...u, rol: newRole } : u));
      alert("Rol actualizat cu succes!");
    } else {
      alert("Eroare la actualizare rol");
    }
  }

  async function addGym() {
    if (!newGym.nume || !newGym.localitate || !newGym.judet || !newGym.adresa) {
      alert("Completează toate câmpurile!");
      return;
    }

    const res = await fetch("http://localhost:8000/admin/sali", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(newGym)
    });

    if (res.ok) {
      const data = await res.json();
      setGyms([...gyms, { id: data.id, ...newGym }]);
      setNewGym({ nume: "", localitate: "", judet: "", adresa: "" });
      alert("Sală adăugată cu succes!");
    } else {
      alert("Eroare la adăugare");
    }
  }

  async function deleteGym(id) {
    const res = await fetch(`http://localhost:8000/admin/sali/${id}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (res.ok) {
      setGyms(gyms.filter(g => g.id !== id));
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
              <td>
                <select
                  value={u.rol}
                  onChange={(e) => updateUserRole(u.id, e.target.value)}
                  style={{ padding: '5px', borderRadius: '4px' }}
                >
                  <option value="cursant">Cursant</option>
                  <option value="antrenor">Antrenor personal</option>
                  <option value="administrator">Administrator</option>
                </select>
              </td>
              <td>
                <button className="btn-delete" onClick={() => deleteUser(u.id)}>
                  Șterge
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Gestionare săli de fitness</h3>

      <div className="add-gym-form">
        <h4>Adaugă sală nouă</h4>
        <input
          type="text"
          placeholder="Nume sală"
          value={newGym.nume}
          onChange={(e) => setNewGym({ ...newGym, nume: e.target.value })}
        />
        <input
          type="text"
          placeholder="Localitate"
          value={newGym.localitate}
          onChange={(e) => setNewGym({ ...newGym, localitate: e.target.value })}
        />
        <input
          type="text"
          placeholder="Județ"
          value={newGym.judet}
          onChange={(e) => setNewGym({ ...newGym, judet: e.target.value })}
        />
        <input
          type="text"
          placeholder="Adresă"
          value={newGym.adresa}
          onChange={(e) => setNewGym({ ...newGym, adresa: e.target.value })}
        />
        <button onClick={addGym}>Adaugă sală</button>
      </div>

      <table className="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nume</th>
            <th>Localitate</th>
            <th>Județ</th>
            <th>Adresă</th>
            <th>Acțiuni</th>
          </tr>
        </thead>
        <tbody>
          {gyms.map(g => (
            <tr key={g.id}>
              <td>{g.id}</td>
              <td>{g.nume}</td>
              <td>{g.localitate}</td>
              <td>{g.judet}</td>
              <td>{g.adresa}</td>
              <td>
                <button className="btn-delete" onClick={() => deleteGym(g.id)}>
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
