import React, { useState, useEffect, createContext, useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import "./App.css";

// Context pour l'authentification
const AuthContext = createContext();

// Configuration API
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configuration Axios
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Hook pour utiliser le contexte d'authentification
const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Provider d'authentification
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setUser(JSON.parse(userData));
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        username,
        password
      });
      
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Erreur de connexion' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Component de connexion
const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(username, password);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-blue-600 to-blue-700 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-500 p-3 rounded-full">
              <div className="flex space-x-1">
                <div className="text-white text-2xl">🚛</div>
                <div className="text-white text-2xl">🚗</div>
              </div>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Connexion</h1>
          <p className="text-xl font-semibold text-blue-600">ABOU GENI</p>
          <p className="text-gray-600">Gestionnaire de Documents Véhicules</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Nom d'utilisateur
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Entrez votre nom d'utilisateur"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Mot de passe
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Entrez votre mot de passe"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition duration-200"
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600 text-center">
            Compte par défaut: <strong>admin / admin123</strong>
          </p>
        </div>
      </div>
    </div>
  );
};

// Component pour les routes protégées
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  return user ? children : <Navigate to="/login" />;
};

// Navigation component
const Navigation = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-3">
            <div className="flex space-x-1">
              <span className="text-2xl">🚛</span>
              <span className="text-2xl">🚗</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">ABOU GENI</h1>
              <p className="text-sm opacity-90">Gestion de Documents Véhicules</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm">Bonjour, {user?.username}</span>
            <button
              onClick={logout}
              className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded transition duration-200"
            >
              Déconnexion
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

// Dashboard component
const Dashboard = () => {
  const [stats, setStats] = useState({
    vehicles_count: 0,
    documents_count: 0,
    alerts_count: 0,
    expiring_documents: 0
  });
  const [vehicles, setVehicles] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsRes, vehiclesRes, documentsRes, alertsRes] = await Promise.all([
        axios.get(`${API}/statistics`),
        axios.get(`${API}/vehicles`),
        axios.get(`${API}/documents`),
        axios.get(`${API}/alerts`)
      ]);

      setStats(statsRes.data);
      setVehicles(vehiclesRes.data);
      setDocuments(documentsRes.data);
      setAlerts(alertsRes.data);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-xl">Chargement du tableau de bord...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="text-3xl mr-4">🚗</div>
            <div>
              <p className="text-2xl font-bold text-gray-800">{stats.vehicles_count}</p>
              <p className="text-gray-600">Véhicules</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="text-3xl mr-4">📄</div>
            <div>
              <p className="text-2xl font-bold text-gray-800">{stats.documents_count}</p>
              <p className="text-gray-600">Documents</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="text-3xl mr-4">🔔</div>
            <div>
              <p className="text-2xl font-bold text-red-600">{stats.alerts_count}</p>
              <p className="text-gray-600">Alertes actives</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="text-3xl mr-4">⏰</div>
            <div>
              <p className="text-2xl font-bold text-orange-600">{stats.expiring_documents}</p>
              <p className="text-gray-600">Expirent bientôt</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">🔔 Alertes actives</h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {alerts.slice(0, 5).map((alert) => (
                <div key={alert.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <div>
                    <p className="font-medium text-red-800">{alert.message}</p>
                    <p className="text-sm text-red-600">
                      Type: {alert.type_alert} | {new Date(alert.date_alert).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-2xl">⚠️</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recent Vehicles */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">🚗 Véhicules récents</h2>
        </div>
        <div className="p-6">
          {vehicles.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              Aucun véhicule enregistré. Commencez par ajouter un véhicule !
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {vehicles.slice(0, 6).map((vehicle) => (
                <div key={vehicle.id} className="border rounded-lg p-4 hover:shadow-md transition duration-200">
                  <div className="flex items-center mb-2">
                    <div className="text-2xl mr-3">
                      {vehicle.type_vehicule === 'camion' ? '🚛' : 
                       vehicle.type_vehicule === 'bus' ? '🚌' : 
                       vehicle.type_vehicule === 'mini_bus' ? '🚐' : '🚗'}
                    </div>
                    <div>
                      <h3 className="font-semibold">{vehicle.marque} {vehicle.modele}</h3>
                      <p className="text-sm text-gray-600">{vehicle.immatriculation}</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">Propriétaire: {vehicle.proprietaire}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Main App component
const AppContent = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {user && <Navigation />}
      
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </div>
  );
};

// Main App with Router
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;