import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import KanbanBoard from './components/KanbanBoard';
import Projects from './components/Projects';
import Calendar from './components/Calendar';
import Analytics from './components/Analytics';
import TimeTracking from './components/TimeTracking';
import Team from './components/Team';
import Settings from './components/Settings';
import Layout from './components/Layout';
import TaskDetail from './pages/TaskDetail';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
    }
    setLoading(false);
  }, []);

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route 
            path="/login" 
            element={
              !isAuthenticated ? 
                <Login onLogin={handleLogin} /> : 
                <Navigate to="/dashboard" replace />
            } 
          />
          <Route 
            path="/*" 
            element={
              isAuthenticated ? 
                <Layout user={user} onLogout={handleLogout}>
                  <Routes>
                    <Route path="/dashboard" element={<Dashboard user={user} />} />
                    <Route path="/kanban" element={<KanbanBoard user={user} />} />
                    <Route path="/projects" element={<Projects user={user} />} />
                    <Route path="/calendar" element={<Calendar user={user} />} />
                    <Route path="/analytics" element={<Analytics user={user} />} />
                    <Route path="/time-tracking" element={<TimeTracking user={user} />} />
                    <Route path="/team" element={<Team user={user} />} />
                    <Route path="/settings" element={<Settings user={user} />} />
                    <Route path="/tasks/:taskId" element={<TaskDetail user={user} />} />
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </Layout> : 
                <Navigate to="/login" replace />
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;