import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSave, faSpinner, faExclamationCircle, faCog } from '@fortawesome/free-solid-svg-icons';
import { useConfiguration, useUpdateConfiguration } from '../hooks/useConfiguration';
import type { Configuration } from '../types/configuration';
import './configuration.css';

interface ConfigurationFormProps {
    config: Configuration;
}

const ConfigurationForm: React.FC<ConfigurationFormProps> = ({ config }) => {
    const updateMutation = useUpdateConfiguration();
    const [successMessage, setSuccessMessage] = useState('');

    const [formData, setFormData] = useState({
        base_url: config.base_url,
        hub_address: config.hub_address,
        sleep_time: config.sleep_time,
        push_token: config.push_token,
        push_user: config.push_user,
        df_msg: config.df_msg
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSuccessMessage('');

        try {
            await updateMutation.mutateAsync({
                id: config.id,
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

    return (
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
    );
};

const Configuration: React.FC = () => {
    const { data: config, isLoading, isError } = useConfiguration();

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

            <ConfigurationForm config={config} key={config.id} />
        </div>
    );
};

export default Configuration;
