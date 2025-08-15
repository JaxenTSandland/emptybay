import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

function Dashboard() {
  const { user, logout } = useAuth();
  const [systemStatus, setSystemStatus] = useState(null);
  
  // Debug logging
  console.log('Dashboard render - user:', user);
  console.log('Dashboard render - user type:', typeof user);
  console.log('Dashboard render - user keys:', user ? Object.keys(user) : 'no user');
  const [bulkCreateData, setBulkCreateData] = useState({ usernames: '', length: 12, overwrite: false });
  const [bulkCreateResult, setBulkCreateResult] = useState(null);
  const [debugUsers, setDebugUsers] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      fetchSystemStatus();
      fetchConfig();
    }
  }, [user]);

  const fetchSystemStatus = async () => {
    try {
      // Use the configured axios instance with Authorization header
      const response = await fetch('https://d3a3a15d4386.ngrok.free.app/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const fetchConfig = async () => {
    try {
      // Use the configured axios instance with Authorization header
      const response = await fetch('https://d3a3a15d4386.ngrok.free.app/.well-known/config', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      console.error('Failed to fetch config:', error);
    }
  };

  const handleBulkCreate = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const usernames = bulkCreateData.usernames.split(',').map(u => u.trim()).filter(u => u);
      // Use the configured axios instance with Authorization header
      const response = await fetch('https://d3a3a15d4386.ngrok.free.app/admin/bulk-create', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          usernames,
          length: bulkCreateData.length,
          overwrite: bulkCreateData.overwrite
        })
      });
      const data = await response.json();
      setBulkCreateResult(data);
    } catch (error) {
      console.error('Bulk create failed:', error);
      setBulkCreateResult({ error: 'Bulk create failed' });
    } finally {
      setLoading(false);
    }
  };

  const fetchDebugUsers = async () => {
    try {
      // Use the configured axios instance with Authorization header
      const response = await fetch('https://d3a3a15d4386.ngrok.free.app/debug/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setDebugUsers(data);
    } catch (error) {
      console.error('Failed to fetch debug users:', error);
    }
  };

  const handleLogout = () => {
    logout();
  };

  // Don't render anything if user is not loaded
  if (!user) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Loading...</h1>
          <p>Please wait while we load your information</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome to EmptyBay Manager</h1>
        <p>Manage your authentication system</p>
      </div>
      
      <div className="dashboard-content">
        <div className="user-info-card">
          <h2>User Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Username:</label>
              <span>{user.username}</span>
            </div>
            <div className="info-item">
              <label>Role:</label>
              <span className={`role-badge role-${user.role}`}>
                {user.role}
              </span>
            </div>
            <div className="info-item">
              <label>Status:</label>
              <span className="status-active">Active</span>
            </div>
          </div>
        </div>
        
        <div className="system-status">
          <h2>System Status</h2>
          {systemStatus && (
            <div className="status-grid">
              <div className="status-item">
                <div className="status-icon">🟢</div>
                <div className="status-text">
                  <h4>Service</h4>
                  <p>{systemStatus.service}</p>
                </div>
              </div>
              <div className="status-item">
                <div className="status-icon">🟢</div>
                <div className="status-text">
                  <h4>Version</h4>
                  <p>{systemStatus.version}</p>
                </div>
              </div>
              <div className="status-item">
                <div className="status-icon">🟢</div>
                <div className="status-text">
                  <h4>Status</h4>
                  <p>{systemStatus.note}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {user.role === 'admin' && (
          <>
            <div className="admin-section">
              <h2>Admin Tools</h2>
              
              <div className="bulk-create-section">
                <h3>Bulk Create Users</h3>
                <form onSubmit={handleBulkCreate} className="admin-form">
                  <div className="form-group">
                    <label>Usernames (comma-separated):</label>
                    <textarea
                      value={bulkCreateData.usernames}
                      onChange={(e) => setBulkCreateData({...bulkCreateData, usernames: e.target.value})}
                      placeholder="user1, user2, user3"
                      rows="3"
                    />
                  </div>
                  <div className="form-group">
                    <label>Password Length:</label>
                    <input
                      type="number"
                      value={bulkCreateData.length}
                      onChange={(e) => setBulkCreateData({...bulkCreateData, length: parseInt(e.target.value)})}
                      min="6"
                      max="20"
                    />
                  </div>
                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={bulkCreateData.overwrite}
                        onChange={(e) => setBulkCreateData({...bulkCreateData, overwrite: e.target.checked})}
                      />
                      Overwrite existing users
                    </label>
                  </div>
                  <button type="submit" className="action-btn primary" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Users'}
                  </button>
                </form>
                
                {bulkCreateResult && (
                  <div className="result-section">
                    <h4>Result:</h4>
                    {bulkCreateResult.error ? (
                      <div className="error-message">{bulkCreateResult.error}</div>
                    ) : (
                      <div>
                        <p>Created: {bulkCreateResult.created_count}</p>
                        <p>Skipped: {bulkCreateResult.skipped_existing?.length || 0}</p>
                        {bulkCreateResult.accounts && bulkCreateResult.accounts.length > 0 && (
                          <div>
                            <h5>New Accounts:</h5>
                            <div className="accounts-list">
                              {bulkCreateResult.accounts.map((acc, index) => (
                                <div key={index} className="account-item">
                                  <strong>{acc.username}</strong>: {acc.password}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="debug-section">
                <h3>Debug Tools</h3>
                <button onClick={fetchDebugUsers} className="action-btn secondary">
                  Fetch Debug Users
                </button>
                {debugUsers && (
                  <div className="debug-output">
                    <h4>Debug Users:</h4>
                    <pre>{JSON.stringify(debugUsers, null, 2)}</pre>
                  </div>
                )}
              </div>

              <div className="config-section">
                <h3>System Configuration</h3>
                {config && (
                  <div className="config-display">
                    <h4>Current Config:</h4>
                    <pre>{JSON.stringify(config, null, 2)}</pre>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
      
      <div className="dashboard-footer">
        <button onClick={handleLogout} className="logout-btn">
          Sign Out
        </button>
      </div>
    </div>
  );
}

export default Dashboard; 