import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {
    faArrowLeft,
    faEnvelope,
    faCalendar,
    faClock,
    faSpinner,
    faCalendarAlt,
    faCheckCircle,
    faTimesCircle,
    faQuestionCircle,
    faExclamationTriangle,
    faPlus,
    faArrowCircleUp,
    faKey
} from '@fortawesome/free-solid-svg-icons';
import { useApplicant, useTestCredentials } from '../hooks/useApplicants';
import { useReSchedulesByApplicant } from '../hooks/useReSchedules';
import AddReScheduleModal from '../components/AddReScheduleModal';
import { ScheduleStatus } from '../types/reSchedule';

const ApplicantDetails: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const applicantId = parseInt(id || '0');
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);

    const {
        data: applicant,
        isLoading: isLoadingApplicant,
        isError: isErrorApplicant
    } = useApplicant(applicantId);

    const {
        data: reSchedules = [],
        isLoading: isLoadingReSchedules
    } = useReSchedulesByApplicant(applicantId);

    const testCredentialsMutation = useTestCredentials();

    const handleTestCredentials = async () => {
        const toastId = toast.info('Testing credentials...', { autoClose: false });

        try {
            const result = await testCredentialsMutation.mutateAsync(applicantId);

            toast.dismiss(toastId);

            if (result.success) {
                if (result.schedule) {
                    toast.success(`Login successful! Schedule number: ${result.schedule}`);
                } else {
                    toast.warning('Login successful but could not extract schedule number');
                }
            } else {
                toast.error(result.error || 'Login failed');
            }
        } catch {
            toast.dismiss(toastId);
            toast.error('Failed to test credentials. Please try again.');
        }
    };

    const formatDate = (dateString?: string) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getStatusIcon = (status: ScheduleStatus) => {
        switch (status) {
            case ScheduleStatus.COMPLETED: return <FontAwesomeIcon icon={faCheckCircle} className="status-icon completed" />;
            case ScheduleStatus.PROCESSING: return <FontAwesomeIcon icon={faSpinner} className="status-icon processing" spin />;
            case ScheduleStatus.PENDING: return <FontAwesomeIcon icon={faClock} className="status-icon pending" />;
            case ScheduleStatus.FAILED: return <FontAwesomeIcon icon={faTimesCircle} className="status-icon failed" />;
            case ScheduleStatus.NOT_FOUND: return <FontAwesomeIcon icon={faQuestionCircle} className="status-icon not-found" />;
            case ScheduleStatus.LOGIN_PENDING: return <FontAwesomeIcon icon={faClock} className="status-icon pending" />;
            default: return <FontAwesomeIcon icon={faExclamationTriangle} className="status-icon unknown" />;
        }
    };

    if (isLoadingApplicant) {
        return (
            <div className="loading-container">
                <FontAwesomeIcon icon={faSpinner} className="spinner" spin />
                <p>Loading applicant details...</p>
            </div>
        );
    }

    if (isErrorApplicant || !applicant) {
        return (
            <div className="error-container">
                <div className="error-state">
                    <FontAwesomeIcon icon={faExclamationTriangle} className="error-icon" />
                    <h3>Applicant Not Found</h3>
                    <p>The applicant you are looking for does not exist or could not be loaded.</p>
                    <button className="back-btn" onClick={() => navigate('/applicants')}>
                        <FontAwesomeIcon icon={faArrowLeft} />
                        Back to Applicants
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="applicant-details-container">
            <div className="details-header">
                <button className="back-link" onClick={() => navigate('/applicants')}>
                    <FontAwesomeIcon icon={faArrowLeft} />
                    <span>Back to List</span>
                </button>
                <div className="header-content">
                    <div className="applicant-title">
                        <div className="avatar-placeholder">
                            {applicant.name.charAt(0)}{applicant.last_name.charAt(0)}
                        </div>
                        <div>
                            <h1>{applicant.name} {applicant.last_name}</h1>
                            <span className="applicant-id">ID: #{applicant.id}</span>
                        </div>
                    </div>
                    <div className="header-actions">
                        <button
                            className="add-btn-small"
                            onClick={handleTestCredentials}
                            disabled={testCredentialsMutation.isPending}
                        >
                            {testCredentialsMutation.isPending ? (
                                <FontAwesomeIcon icon={faSpinner} spin />
                            ) : (
                                <FontAwesomeIcon icon={faKey} />
                            )}
                            <span>{testCredentialsMutation.isPending ? 'Testing...' : 'Test Credentials'}</span>
                        </button>
                    </div>
                </div>
            </div>

            <div className="details-grid">
                <div className="info-card">
                    <h3>Applicant Information</h3>
                    <div className="info-list">
                        <div className="info-item">
                            <div className="info-label">
                                <FontAwesomeIcon icon={faEnvelope} />
                                <span>Email</span>
                            </div>
                            <div className="info-value">{applicant.email}</div>
                        </div>
                        <div className="info-item">
                            <div className="info-label">
                                <FontAwesomeIcon icon={faCalendar} />
                                <span>Schedule Date</span>
                            </div>
                            <div className="info-value">{applicant.schedule_date || 'Not Scheduled'}</div>
                        </div>
                        <div className="info-item">
                            <div className="info-label">
                                <FontAwesomeIcon icon={faArrowCircleUp} />
                                <span>Status</span>
                            </div>
                            <div className="info-value">{applicant.re_schedule_status}</div>
                        </div>
                        <div className="info-item">
                            <div className="info-label">
                                <FontAwesomeIcon icon={faArrowCircleUp} />
                                <span>Schedule Number</span>
                            </div>
                            <div className="info-value">{applicant.schedule || 'No Schedule number'}</div>
                        </div>
                        <div className="info-item">
                            <div className="info-label">
                                <FontAwesomeIcon icon={faClock} />
                                <span>Updated At</span>
                            </div>
                            <div className="info-value">{formatDate(applicant.updated_at)}</div>
                        </div>
                    </div>
                </div>

                <div className="re-schedules-section">
                    <div className="section-header">
                        <h3>Re-Schedule History</h3>
                        <div className="section-actions">
                            <button className="add-btn-small" onClick={() => setIsAddModalOpen(true)}>
                                <FontAwesomeIcon icon={faPlus} />
                                <span>Add Re-Schedule</span>
                            </button>
                        </div>
                    </div>

                    {isLoadingReSchedules ? (
                        <div className="loading-state-small">
                            <FontAwesomeIcon icon={faSpinner} spin />
                            <span>Loading history...</span>
                        </div>
                    ) : reSchedules.length === 0 ? (
                        <div className="empty-state-small">
                            <FontAwesomeIcon icon={faCalendarAlt} className="empty-icon-small" />
                            <p>No re-schedule attempts recorded.</p>
                        </div>
                    ) : (
                        <div className="re-schedules-list">
                            {reSchedules.map((item) => (
                                <div key={item.id} className="re-schedule-card">
                                    <div className="re-schedule-header">
                                        <div className={`status-badge ${item.status.toLowerCase()}`}>
                                            {getStatusIcon(item.status)}
                                            <span>{item.status}</span>
                                        </div>
                                        <span className="re-schedule-date">{formatDate(item.created_at)}</span>
                                    </div>
                                    <div className="re-schedule-body">
                                        <div className="time-range">
                                            <div className="time-item">
                                                <span className="label">Start:</span>
                                                <span className="value">{formatDate(item.start_datetime)}</span>
                                            </div>
                                            <div className="time-item">
                                                <span className="label">End:</span>
                                                <span className="value">{formatDate(item.end_datetime)}</span>
                                            </div>
                                        </div>
                                        {item.error && (
                                            <div className="error-alert">
                                                <strong>Error:</strong> {item.error}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <AddReScheduleModal
                isOpen={isAddModalOpen}
                onClose={() => setIsAddModalOpen(false)}
                applicantId={applicantId}
            />

            <style>{`
                .applicant-details-container {
                    padding: 2rem;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                .details-header {
                    margin-bottom: 2rem;
                }
                
                .back-link {
                    background: none;
                    border: none;
                    color: #64748b;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    font-size: 0.9rem;
                    margin-bottom: 1rem;
                    padding: 0;
                }
                
                .back-link:hover {
                    color: #3b82f6;
                }
                
                .header-content {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    flex-wrap: wrap;
                    gap: 1rem;
                }
                
                .applicant-title {
                    display: flex;
                    align-items: center;
                    gap: 1.5rem;
                }
                
                .avatar-placeholder {
                    width: 64px;
                    height: 64px;
                    background: linear-gradient(135deg, #FF5757, #4A90E2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 1.5rem;
                    font-weight: 700;
                    box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
                }
                
                .applicant-title h1 {
                    margin: 0 0 0.25rem 0;
                    color: #1e293b;
                    font-size: 1.75rem;
                }
                
                .applicant-id {
                    color: #64748b;
                    font-size: 0.9rem;
                    font-family: monospace;
                    background: #f1f5f9;
                    padding: 0.2rem 0.5rem;
                    border-radius: 4px;
                }
                
                .details-grid {
                    display: grid;
                    grid-template-columns: 350px 1fr;
                    gap: 2rem;
                }
                
                @media (max-width: 1024px) {
                    .details-grid {
                        grid-template-columns: 1fr;
                    }
                }
                
                .info-card {
                    background: white;
                    border-radius: 16px;
                    padding: 1.5rem;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                    border: 1px solid rgba(0, 0, 0, 0.06);
                    height: fit-content;
                }
                
                .info-card h3 {
                    margin: 0 0 1.5rem 0;
                    color: #1e293b;
                    font-size: 1.1rem;
                    border-bottom: 1px solid #e2e8f0;
                    padding-bottom: 1rem;
                }
                
                .info-list {
                    display: flex;
                    flex-direction: column;
                    gap: 1.25rem;
                }
                
                .info-item {
                    display: flex;
                    flex-direction: column;
                    gap: 0.4rem;
                }
                
                .info-label {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    color: #64748b;
                    font-size: 0.85rem;
                    font-weight: 500;
                }
                
                .info-value {
                    color: #1e293b;
                    font-weight: 500;
                    font-size: 1rem;
                    padding-left: 1.35rem;
                    word-break: break-all;
                }
                
                .re-schedules-section {
                    background: white;
                    border-radius: 16px;
                    padding: 1.5rem;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                    border: 1px solid rgba(0, 0, 0, 0.06);
                    min-height: 400px;
                }
                
                .section-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 1.5rem;
                    padding-bottom: 1rem;
                    border-bottom: 1px solid #e2e8f0;
                }
                
                .section-header h3 {
                    margin: 0;
                    color: #1e293b;
                    font-size: 1.1rem;
                }
                
                .add-btn-small {
                    background: linear-gradient(135deg, #FF5757, #4A90E2);
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 0.85rem;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    transition: all 0.2s;
                }
                
                .add-btn-small:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
                }
                
                .add-btn-small:disabled {
                    opacity: 0.7;
                    cursor: not-allowed;
                    transform: none;
                }
                
                .re-schedules-list {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }
                
                .re-schedule-card {
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    padding: 1rem;
                    transition: all 0.2s;
                }
                
                .re-schedule-card:hover {
                    border-color: #cbd5e1;
                    background: #f8fafc;
                }
                
                .re-schedule-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 0.75rem;
                }
                
                .status-badge {
                    display: flex;
                    align-items: center;
                    gap: 0.4rem;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                }
                
                .status-badge.pending { background: #fff7ed; color: #c2410c; }
                .status-badge.processing { background: #eff6ff; color: #1d4ed8; }
                .status-badge.completed { background: #f0fdf4; color: #15803d; }
                .status-badge.failed { background: #fef2f2; color: #b91c1c; }
                
                .re-schedule-date {
                    color: #94a3b8;
                    font-size: 0.8rem;
                }
                
                .time-range {
                    display: flex;
                    gap: 1.5rem;
                    margin-bottom: 0.5rem;
                }
                
                .time-item {
                    display: flex;
                    gap: 0.5rem;
                    font-size: 0.9rem;
                    color: #475569;
                }
                
                .time-item .label {
                    font-weight: 500;
                    color: #64748b;
                }
                
                .error-alert {
                    margin-top: 0.75rem;
                    background: #fef2f2;
                    color: #ef4444;
                    padding: 0.5rem 0.75rem;
                    border-radius: 6px;
                    font-size: 0.85rem;
                }
                
                .loading-container, .error-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    min-height: 400px;
                    text-align: center;
                }
                
                .spinner {
                    font-size: 2.5rem;
                    color: #4A90E2;
                    margin-bottom: 1rem;
                }
                
                .error-icon {
                    font-size: 3rem;
                    color: #ef4444;
                    margin-bottom: 1rem;
                }
                
                .back-btn {
                    margin-top: 1.5rem;
                    background: #4A90E2;
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .loading-state-small, .empty-state-small {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 3rem 1rem;
                    color: #94a3b8;
                    gap: 0.75rem;
                }
                
                .empty-icon-small {
                    font-size: 2rem;
                    color: #cbd5e1;
                }
            `}</style>
        </div>
    );
};

export default ApplicantDetails;
