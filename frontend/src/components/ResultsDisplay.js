import React from 'react';
import './ResultsDisplay.css';

function ResultsDisplay({ results, flow, onReset }) {
  const getSummary = () => {
    if (flow === 'new-users') {
      return {
        success: results.created.length,
        duplicates: results.duplicates.length,
        errors: results.errors.length,
        total: results.total,
      };
    } else {
      return {
        success: results.added.length,
        already_member: results.already_member.length,
        not_found: results.not_found.length,
        errors: results.errors.length,
        total: results.total,
      };
    }
  };

  const summary = getSummary();

  return (
    <div className="results-container">
      <div className="results-header">
        <h2>Import Results</h2>
        <button className="reset-btn" onClick={onReset}>Start New Import</button>
      </div>

      <div className="summary-cards">
        {flow === 'new-users' ? (
          <>
            <div className="card success">
              <span className="count">{summary.success}</span>
              <span className="label">Created</span>
            </div>
            <div className="card warning">
              <span className="count">{summary.duplicates}</span>
              <span className="label">Duplicates</span>
            </div>
            <div className="card error">
              <span className="count">{summary.errors}</span>
              <span className="label">Errors</span>
            </div>
            <div className="card info">
              <span className="count">{summary.total}</span>
              <span className="label">Total</span>
            </div>
          </>
        ) : (
          <>
            <div className="card success">
              <span className="count">{summary.success}</span>
              <span className="label">Added</span>
            </div>
            <div className="card info">
              <span className="count">{summary.already_member}</span>
              <span className="label">Already Member</span>
            </div>
            <div className="card warning">
              <span className="count">{summary.not_found}</span>
              <span className="label">Not Found</span>
            </div>
            <div className="card error">
              <span className="count">{summary.errors}</span>
              <span className="label">Errors</span>
            </div>
          </>
        )}
      </div>

      <div className="details-section">
        {flow === 'new-users' && results.created.length > 0 && (
          <div className="details-card success-card">
            <h3>✓ Created Users ({results.created.length})</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>User ID</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {results.created.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.email}</td>
                      <td className="code">{item.user_id}</td>
                      <td>{item.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {flow === 'new-users' && results.duplicates.length > 0 && (
          <div className="details-card warning-card">
            <h3>⚠ Duplicate Users ({results.duplicates.length})</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Email</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {results.duplicates.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.row}</td>
                      <td>{item.email}</td>
                      <td>{item.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {results.errors.length > 0 && (
          <div className="details-card error-card">
            <h3>✗ Errors ({results.errors.length})</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Email/User</th>
                    <th>Error Message</th>
                  </tr>
                </thead>
                <tbody>
                  {results.errors.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.row}</td>
                      <td>{item.email}</td>
                      <td className="error-msg">{item.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {flow === 'group-assignment' && results.added.length > 0 && (
          <div className="details-card success-card">
            <h3>✓ Added to Group ({results.added.length})</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>User ID</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {results.added.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.email}</td>
                      <td className="code">{item.user_id}</td>
                      <td>{item.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {flow === 'group-assignment' && results.already_member.length > 0 && (
          <div className="details-card info-card">
            <h3>ℹ Already Member ({results.already_member.length})</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {results.already_member.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.email}</td>
                      <td>{item.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {flow === 'group-assignment' && results.not_found.length > 0 && (
          <div className="details-card warning-card">
            <h3>⚠ Not Found ({results.not_found.length})</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Email</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {results.not_found.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.row}</td>
                      <td>{item.email}</td>
                      <td>{item.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultsDisplay;
