import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUsers, faUserPlus, faSearch, faEnvelope, faCalendar, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { useApplicants } from '../hooks/useApplicants';
import AddApplicantModal from '../components/AddApplicantModal';

const Applicants: React.FC = () => {
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

    // Use TanStack Query to fetch applicants
    const { data: applicants = [], isLoading, isError, error, refetch } = useApplicants();

    // Filter applicants based on search query
    const filteredApplicants = useMemo(() => {
        if (!applicants) return [];

        const query = searchQuery.toLowerCase();
        return applicants.filter((applicant) =>
            applicant.name.toLowerCase().includes(query) ||
            applicant.last_name.toLowerCase().includes(query) ||
            applicant.email.toLowerCase().includes(query)
        );
    }, [applicants, searchQuery]);

    const formatDate = (dateString: string) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    return (
        <div className="applicants-container">
            <div className="applicants-header">
                <div>
                    <h1>Applicants</h1>
                    <p>Manage all visa applicants and their applications</p>
                </div>
                <button className="add-btn" onClick={() => setIsModalOpen(true)}>
                    <FontAwesomeIcon icon={faUserPlus} />
                    <span>Add Applicant</span>
                </button>
            </div>

            <div className="search-bar">
                <FontAwesomeIcon icon={faSearch} className="search-icon" />
                <input
                    type="text"
                    placeholder="Search applicants..."
                    className="search-input"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
            </div>

            <div className="applicants-content">
                {isLoading ? (
                    <div className="loading-state">
                        <FontAwesomeIcon icon={faSpinner} className="spinner" spin />
                        <p>Loading applicants...</p>
                    </div>
                ) : isError ? (
                    <div className="error-state">
                        <div className="error-icon">⚠️</div>
                        <h3>Error Loading Applicants</h3>
                        <p>{(error as Error)?.message || 'Failed to load applicants. Please try again.'}</p>
                        <button className="retry-btn" onClick={() => refetch()}>
                            Try Again
                        </button>
                    </div>
                ) : filteredApplicants.length === 0 ? (
                    <div className="empty-state">
                        <FontAwesomeIcon icon={faUsers} className="empty-icon" />
                        <h3>{searchQuery ? 'No Applicants Found' : 'No Applicants Yet'}</h3>
                        <p>
                            {searchQuery
                                ? 'Try adjusting your search criteria'
                                : 'Start by adding your first applicant  to the system'}
                        </p>
                        {!searchQuery && (
                            <button className="add-btn-secondary" onClick={() => setIsModalOpen(true)}>
                                <FontAwesomeIcon icon={faUserPlus} />
                                <span>Add Your First Applicant</span>
                            </button>
                        )}
                    </div>
                ) : (
                    <div className="applicants-table-container">
                        <table className="applicants-table">
                            <thead className="table-header">
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Schedule Date</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredApplicants.map((applicant) => (
                                    <tr key={applicant.id}>
                                        <td>
                                            <div className="applicant-name">
                                                {applicant.name} {applicant.last_name}
                                            </div>
                                        </td>
                                        <td>
                                            <div className="applicant-email">
                                                <FontAwesomeIcon icon={faEnvelope} />
                                                <span>{applicant.email}</span>
                                            </div>
                                        </td>
                                        <td>
                                            <div className="applicant-date">
                                                <FontAwesomeIcon icon={faCalendar} />
                                                <span>{applicant.schedule_date || 'Not scheduled'}</span>
                                            </div>
                                        </td>
                                        <td>{formatDate(applicant.created_at)}</td>
                                        <td>
                                            <div className="table-actions">
                                                <button className="action-btn edit">Edit</button>
                                                <button
                                                    className="action-btn view"
                                                    onClick={() => navigate(`/applicants/${applicant.id}`)}
                                                >
                                                    View
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <AddApplicantModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
            />
        </div>
    );
};

export default Applicants;
