import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChartLine, faUsers, faFileAlt, faClock } from '@fortawesome/free-solid-svg-icons';

const Dashboard: React.FC = () => {
    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <h1>Dashboard</h1>
                <p>Welcome to QuickVisa - Your visa application management system</p>
            </div>

            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #FF5757, #E84C5E)' }}>
                        <FontAwesomeIcon icon={faUsers} />
                    </div>
                    <div className="stat-content">
                        <h3>Total Applicants</h3>
                        <p className="stat-number">0</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #5A5AA6, #2D6BB3)' }}>
                        <FontAwesomeIcon icon={faFileAlt} />
                    </div>
                    <div className="stat-content">
                        <h3>Pending Applications</h3>
                        <p className="stat-number">0</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #9B4F8C, #5A5AA6)' }}>
                        <FontAwesomeIcon icon={faClock} />
                    </div>
                    <div className="stat-content">
                        <h3>In Progress</h3>
                        <p className="stat-number">0</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #2D6BB3, #5A5AA6)' }}>
                        <FontAwesomeIcon icon={faChartLine} />
                    </div>
                    <div className="stat-content">
                        <h3>Completed</h3>
                        <p className="stat-number">0</p>
                    </div>
                </div>
            </div>

            <div className="dashboard-content">
                <div className="content-section">
                    <h2>Recent Activity</h2>
                    <div className="empty-state">
                        <FontAwesomeIcon icon={faChartLine} className="empty-icon" />
                        <p>No recent activity to display</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
