import React, { useState } from 'react';
import { Eye, EyeOff, Lock, Mail, LogIn } from 'lucide-react';
import axios from 'axios';
import { API, getErrorMessage } from '../lib/api';

// Use the API from lib/api.js which already has the correct configuration

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: 'demo@taskflow.com',
    password: 'demo123456'
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const getErrorMessage = (err) => {
    const data = err?.response?.data;
    if (!data) return 'An error occurred';
    if (typeof data.detail === 'string') return data.detail;
    if (typeof data.error === 'string') return data.error;
    if (typeof data.message === 'string') return data.message;
    if (typeof data === 'string') return data;
    if (typeof data === 'object') {
      const firstKey = Object.keys(data)[0];
      const value = Array.isArray(data[firstKey]) ? data[firstKey][0] : data[firstKey];
      if (typeof value === 'string') return value;
    }
    return 'An error occurred';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      console.log('Auth submit', { isRegistering, API });
      if (isRegistering) {
        console.log('POST', `${API}/users/register/`, formData);
        const response = await axios.post(`${API}/users/register/`, formData);
        const accessToken = response.data.access_token || response.data.access;
        const refreshToken = response.data.refresh;
        if (accessToken) {
          localStorage.setItem('token', accessToken);
          if (refreshToken) localStorage.setItem('refresh', refreshToken);
          axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
        }
        onLogin(accessToken, response.data.user);
        return;
      }

      // Login using SimpleJWT
      console.log('POST', `${API}/token/`);
      const loginRes = await axios.post(`${API}/token/`, {
        email: formData.email,
        password: formData.password,
      });
      const accessToken = loginRes.data.access;
      const refreshToken = loginRes.data.refresh;
      if (accessToken) {
        localStorage.setItem('token', accessToken);
        if (refreshToken) localStorage.setItem('refresh', refreshToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      }

      // Fetch current user profile
      console.log('GET', `${API}/users/me/`);
      const meRes = await axios.get(`${API}/users/me/`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      onLogin(accessToken, meRes.data);
    } catch (error) {
      console.error('Auth error', error);
      // Improved error handling
      if (error.response && error.response.status === 401) {
        setError('Invalid email or password. Please try again.');
      } else if (error.message === 'Network Error') {
        setError('Network error. Please check your connection and try again.');
      } else {
        setError(getErrorMessage(error));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="absolute inset-0 opacity-40">
        <div className="w-full h-full bg-gradient-to-br from-blue-100/30 to-purple-100/30"></div>
      </div>
      
      <div className="relative w-full max-w-md">
        <div className="bg-white/70 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 p-8">
          <div className="text-center mb-8">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
              <LogIn className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">TaskFlow</h1>
            <p className="text-gray-600">Behavior-driven task management</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {isRegistering && (
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Name</label>
                <div className="relative">
                  <input
                    type="text"
                    name="name"
                    value={formData.name || ''}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white/50"
                    placeholder="Enter your name"
                    required={isRegistering}
                  />
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center">
                    <div className="w-5 h-5 text-gray-400 rounded-full bg-gray-100 flex items-center justify-center">
                      <span className="text-xs">👤</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Email</label>
              <div className="relative">
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white/50"
                  placeholder="Enter your email"
                  required
                />
                <Mail className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full pl-10 pr-12 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white/50"
                  placeholder="Enter your password"
                  required
                />
                <Lock className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3.5 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 shadow-lg"
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Please wait...</span>
                </div>
              ) : (
                isRegistering ? 'Create Account' : 'Sign In'
              )}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setIsRegistering(!isRegistering)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
              >
                {isRegistering ? 'Already have an account? Sign in' : 'Need an account? Register'}
              </button>
            </div>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              Demo credentials: demo@taskflow.com / demo123456
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;