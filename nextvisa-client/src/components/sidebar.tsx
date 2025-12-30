import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome, faUsers, faSignOutAlt, faCalendarAlt, faCog } from '@fortawesome/free-solid-svg-icons';
import { useAuth } from '../contexts/useAuth';
import qvIcon from '../assets/QV Icon.png';
import '../styles/sidebar.css';

interface SidebarProps {
    className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ className = '' }) => {
    const location = useLocation();
    const navigate = useNavigate();
    const { signOut } = useAuth();

    const menuItems = [
        {
            id: 'home',
            label: 'Home',
            icon: faHome,
            path: '/'
        },
        {
            id: 'applicants',
            label: 'Applicants',
            icon: faUsers,
            path: '/applicants'
        },
        {
            id: 're-schedules',
            label: 'Re-Schedules',
            icon: faCalendarAlt,
            path: '/re-schedules'
        },
        {
            id: 'configuration',
            label: 'Configuration',
            icon: faCog,
            path: '/configuration'
        }
    ];

    const isActive = (path: string) => location.pathname === path;

    const handleLogout = async () => {
        await signOut();
        navigate('/login');
    };

    return (
        <aside className={`sidebar ${className}`}>
            <div className="sidebar-header">
                <div className="sidebar-logo">
                    <img src={qvIcon} alt="NextVisa Logo" className="logo-icon" />
                    <span className="logo-text">NextVisa</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                {menuItems.map((item) => (
                    <Link
                        key={item.id}
                        to={item.path}
                        className={`sidebar-item ${isActive(item.path) ? 'active' : ''}`}
                    >
                        <FontAwesomeIcon icon={item.icon} className="sidebar-icon" />
                        <span className="sidebar-label">{item.label}</span>
                    </Link>
                ))}
            </nav>

            <div className="sidebar-footer">
                <button onClick={handleLogout} className="sidebar-item logout-btn">
                    <FontAwesomeIcon icon={faSignOutAlt} className="sidebar-icon" />
                    <span className="sidebar-label">Logout</span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
