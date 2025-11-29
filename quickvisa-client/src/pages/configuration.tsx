import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSave, faSpinner, faExclamationCircle, faCog } from '@fortawesome/free-solid-svg-icons';
import { useConfiguration, useUpdateConfiguration } from '../hooks/useConfiguration';

const Configuration: React.FC = () => {
    const { data: config, isLoading, isError } = useConfiguration();
    const updateMutation = useUpdateConfiguration();

    const [formData, setFormData] = useState({
        base_url: '',
        hub_address: '',
        sleep_time: 15,
        push_token: '',
        push_user: '',
        df_msg: ''
    });

    const [successMessage, setSuccessMessage] = useState('');

    useEffect(() => {
        if (config) {
            setFormData({
                base_url: config.base_url,
                hub_address: config.hub_address,
                sleep_time: config.sleep_time,
                push_token: config.push_token,
                push_user: config.push_user,
                df_msg: config.df_msg
            });
        }
    }, [config]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSuccessMessage('');

        try {
            await updateMutation.mutateAsync({
                id: config!.id,
                data: formData
            });
            setSuccessMessage('Configuration updated successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (error) {
            console.error('Failed to update configuration:', error);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'sleep_time' ? parseFloat(value) : value
        }));
    };

    if (isLoading) {
        return (
            <div className="loading-state">
                <FontAwesomeIcon icon={faSpinner} className="spinner" spin />
                <p>Loading configuration...</p>
            </div>
        );
    }

    if (isError || !config) {
        return (
            <div className="error-state">
                <FontAwesomeIcon icon={faExclamationCircle} className="error-icon" />
                <h3>Failed to Load Configuration</h3>
                <p>Unable to load configuration settings. Please try again later.</p>
            </div>
        );
    }

    return (
        <div className="configuration-container">
            <div className="configuration-header">
                <div>
                    <h1>
                        <FontAwesomeIcon icon={faCog} /> Configuration
                    </h1>
                    <p>Manage application settings for the re-scheduler</p>
                </div>
            </div>

            <div className="configuration-content">
                <form onSubmit={handleSubmit} className="configuration-form">
                    {successMessage && (
                        <div className="success-message">
                            {successMessage}
                        </div>
                    )}

                    {updateMutation.isError && (
                        <div className="error-message">
                            <FontAwesomeIcon icon={faExclamationCircle} />
                            <span>Failed to update configuration. Please try again.</span>
                        </div>
                    )}

                    <div className="form-section">
                        <h3>API Settings</h3>
                        <div className="form-grid">
                            <div className="form-group">
                                <label htmlFor="base_url">Base URL</label>
                                <input
                                    type="text"
                                    id="base_url"
                                    name="base_url"
                                    value={formData.base_url}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="hub_address">Hub Address</label>
                                <input
                                    type="text"
                                    id="hub_address"
                                    name="hub_address"
                                    value={formData.hub_address}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="sleep_time">Sleep Time (seconds)</label>
                                <input
                                    type="number"
                                    id="sleep_time"
                                    name="sleep_time"
                                    value={formData.sleep_time}
                                    onChange={handleChange}
                                    className="form-input"
                                    min="1"
                                    step="0.1"
                                    required
                                />
                            </div>
                        </div>
                    </div>

                    <div className="form-section">
                        <h3>Push Notification Settings</h3>
                        <div className="form-grid">
                            <div className="form-group">
                                <label htmlFor="push_token">Push Token</label>
                                <input
                                    type="text"
                                    id="push_token"
                                    name="push_token"
                                    value={formData.push_token}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="push_user">Push User</label>
                                <input
                                    type="text"
                                    id="push_user"
                                    name="push_user"
                                    value={formData.push_user}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>
                        </div>
                    </div>

                    <div className="form-section">
                        <h3>Default Message</h3>
                        <div className="form-group">
                            <label htmlFor="df_msg">Default Message</label>
                            <textarea
                                id="df_msg"
                                name="df_msg"
                                value={formData.df_msg}
                                onChange={handleChange}
                                className="form-input"
                                rows={2}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-actions">
                        <button
                            type="submit"
                            className="btn-primary"
                            disabled={updateMutation.isPending}
                        >
                            {updateMutation.isPending ? (
                                <>
                                    <FontAwesomeIcon icon={faSpinner} spin />
                                    <span>Saving...</span>
                                </>
                            ) : (
                                <>
                                    <FontAwesomeIcon icon={faSave} />
                                    <span>Save Configuration</span>
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>

            <style>{`
                .configuration-container {
                    padding: 0;
                }

                .configuration-header {
                    margin-bottom: 1.5rem;
                }

                .configuration-header h1 {
                    margin-bottom: 0.25rem;
                    color: #1e293b;
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    font-size: 1.5rem;
                }

                .configuration-header p {
                    color: #64748b;
                    font-size: 0.95rem;
                    margin: 0;
                }

                .configuration-content {
                    background: white;
                    border-radius: 12px;
                    padding: 1.25rem 1.5rem;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                    border: 1px solid rgba(0, 0, 0, 0.06);
                }

                .configuration-form {
                    max-width: 100%;
                }

                .form-section {
                    margin-bottom: 1.25rem;
                    padding-bottom: 1.25rem;
                    border-bottom: 1px solid #e2e8f0;
                }

                .form-section:last-of-type {
                    border-bottom: none;
                    margin-bottom: 0;
                    padding-bottom: 0;
                }

                .form-section h3 {
                    margin: 0 0 0.85rem 0;
                    color: #1e293b;
                    font-size: 0.95rem;
                    font-weight: 600;
                }

                .form-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 0.85rem;
                }

                .form-group {
                    display: flex;
                    flex-direction: column;
                }

                .form-group label {
                    margin-bottom: 0.35rem;
                    color: #475569;
                    font-weight: 500;
                    font-size: 0.8rem;
                }

                .form-input {
                    width: 100%;
                    padding: 0.55rem 0.75rem;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    font-size: 0.9rem;
                    color: #1e293b;
                    transition: all 0.2s;
                }

                .form-input:focus {
                    outline: none;
                    border-color: #3b82f6;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
                }

                textarea.form-input {
                    resize: vertical;
                    min-height: 55px;
                    font-family: inherit;
                }

                .form-actions {
                    margin-top: 1.25rem;
                    display: flex;
                    justify-content: flex-end;
                }

                .success-message {
                    background: #f0fdf4;
                    color: #16a34a;
                    padding: 0.6rem 0.85rem;
                    border-radius: 8px;
                    margin-bottom: 0.85rem;
                    font-weight: 500;
                    font-size: 0.85rem;
                }
            `}</style>
        </div>
    );
};

export default Configuration;
