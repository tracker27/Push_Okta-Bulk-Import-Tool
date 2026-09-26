import React, { useState, useEffect } from 'react';
import './App.css';
import FileUploader from './components/FileUploader';
import ResultsDisplay from './components/ResultsDisplay';

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [currentFlow, setCurrentFlow] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('');

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/groups`);
      const data = await response.json();
      if (data.success) {
        setGroups(data.groups);
      }
    } catch (error) {
      console.error('Error fetching groups:', error);
      alert('Failed to fetch groups. Check backend connection.');
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;

    setLoading(true);
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      let endpoint = '';

      if (currentFlow === 'new-users') {
        endpoint = `${API_BASE_URL}/import/users`;
      } else if (currentFlow === 'group-assignment') {
        if (!selectedGroup) {
          alert('Please select a group');
          setLoading(false);
          return;
        }
        endpoint = `${API_BASE_URL}/import/groups`;
        formData.append('group_name', selectedGroup);
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        setResults(data.results);
      } else {
        alert('Import failed: ' + data.detail);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const resetApp = () => {
    setCurrentFlow(null);
    setResults(null);
    setSelectedGroup('');
  };

  if (results) {
    return (
      <div className="app-container">
        <header className="header">
          <h1>Okta Bulk Import Tool</h1>
        </header>
        <ResultsDisplay
          results={results}
          flow={currentFlow}
          onReset={resetApp}
        />
      </div>
    );
  }

  if (!currentFlow) {
    return (
      <div className="app-container">
        <header className="header">
          <h1>Okta Bulk Import Tool</h1>
        </header>
        <div className="flow-selector">
          <h2>Select Import Type</h2>
          <div className="flow-buttons">
            <button
              className="flow-button"
              onClick={() => setCurrentFlow('new-users')}
            >
              <span className="icon">👥</span>
              <span className="title">New User Onboarding</span>
              <span className="description">Create new users in Okta</span>
            </button>
            <button
              className="flow-button"
              onClick={() => setCurrentFlow('group-assignment')}
            >
              <span className="icon">👨‍💼</span>
              <span className="title">Add to Group</span>
              <span className="description">Add existing users to groups</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>Okta Bulk Import Tool</h1>
        <button className="back-btn" onClick={() => setCurrentFlow(null)}>← Back</button>
      </header>

      <div className="content">
        <div className="flow-info">
          {currentFlow === 'new-users' ? (
            <>
              <h2>New User Onboarding</h2>
              <p>Upload a CSV file to create new users in Okta</p>
            </>
          ) : (
            <>
              <h2>Add Existing Users to Group</h2>
              <p>Upload a CSV file with user emails to add them to a group</p>
            </>
          )}
        </div>

        {currentFlow === 'group-assignment' && (
          <div className="group-selector">
            <label htmlFor="group-select">Select Group:</label>
            <select
              id="group-select"
              value={selectedGroup}
              onChange={(e) => setSelectedGroup(e.target.value)}
            >
              <option value="">-- Choose a group --</option>
              {groups.map(group => (
                <option key={group.id} value={group.name}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>
        )}

        <FileUploader
          onFileUpload={handleFileUpload}
          loading={loading}
          flow={currentFlow}
        />
      </div>
    </div>
  );
}

export default App;
