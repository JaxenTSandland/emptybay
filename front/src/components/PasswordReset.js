import React, { useState } from 'react';
import axios from 'axios';
import './Auth.css';

function PasswordReset() {
  const [step, setStep] = useState('request'); // 'request' or 'confirm'
  const [username, setUsername] = useState('');
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await axios.post('/password-reset/request', { username });
      if (response.data.reset_token) {
        setToken(response.data.reset_token);
        setStep('confirm');
        setMessage('Reset token generated. Please check your email or use the token below.');
      } else {
        setMessage('Password reset request submitted.');
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to request password reset');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post('/password-reset/confirm', {
        username,
        token,
        new_password: newPassword
      });
      
      setMessage('Password reset successful! You can now login with your new password.');
      setStep('request');
      setUsername('');
      setToken('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to confirm password reset');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setStep('request');
    setUsername('');
    setToken('');
    setNewPassword('');
    setConfirmPassword('');
    setMessage('');
    setError('');
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Password Reset</h1>
          <p>{step === 'request' ? 'Request a password reset' : 'Confirm password reset'}</p>
        </div>
        
        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}
        
        {step === 'request' ? (
          <form onSubmit={handleRequestReset} className="auth-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Enter your username"
              />
            </div>
            
            <button 
              type="submit" 
              className="auth-button"
              disabled={loading}
            >
              {loading ? 'Requesting...' : 'Request Reset'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleConfirmReset} className="auth-form">
            <div className="form-group">
              <label htmlFor="reset-token">Reset Token</label>
              <input
                type="text"
                id="reset-token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                required
                placeholder="Enter reset token"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="new-password">New Password</label>
              <input
                type="password"
                id="new-password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                placeholder="Enter new password"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="confirm-password">Confirm New Password</label>
              <input
                type="password"
                id="confirm-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                placeholder="Confirm new password"
              />
            </div>
            
            <button 
              type="submit" 
              className="auth-button"
              disabled={loading}
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}
        
        <div className="auth-footer">
          <button onClick={resetForm} className="auth-link" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            {step === 'request' ? 'Back to Login' : 'Start Over'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default PasswordReset; 