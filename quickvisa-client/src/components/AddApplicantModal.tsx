import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes, faSpinner, faUser, faEnvelope, faCalendar } from '@fortawesome/free-solid-svg-icons';
import { useForm } from '@tanstack/react-form';
import { useCreateApplicant } from '../hooks/useApplicants';
import type { ApplicantCreate } from '../types/applicantServices';
import '../styles/modal.css';

interface AddApplicantModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const AddApplicantModal: React.FC<AddApplicantModalProps> = ({ isOpen, onClose }) => {
    const [isClosing, setIsClosing] = useState(false);
    const { mutate: createApplicant, isPending, isError, error } = useCreateApplicant();

    const form = useForm({
        defaultValues: {
            name: '',
            last_name: '',
            email: '',
            password: '',
            confirmPassword: '',
            schedule_date: '',
            min_date: '',
            max_date: '',
            schedule: '',
        },
        onSubmit: async ({ value }) => {
            const { ...applicantData } = value;
            createApplicant(applicantData as ApplicantCreate, {
                onSuccess: () => {
                    form.reset();
                    handleClose();
                },
            });
        },
    });

    const handleClose = () => {
        if (!isPending) {
            setIsClosing(true);
            setTimeout(() => {
                form.reset();
                setIsClosing(false);
                onClose();
            }, 250);
        }
    };

    if (!isOpen) return null;

    return (
        <div className={`modal-overlay ${isClosing ? 'closing' : ''}`} onClick={handleClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>
                        <FontAwesomeIcon icon={faUser} />
                        Add New Applicant
                    </h2>
                    <button className="modal-close-btn" onClick={handleClose} disabled={isPending}>
                        <FontAwesomeIcon icon={faTimes} />
                    </button>
                </div>

                <form onSubmit={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    form.handleSubmit();
                }} className="modal-form">
                    <div className="form-row">
                        <form.Field
                            name="name"
                            validators={{
                                onChange: ({ value }) =>
                                    !value.trim() ? 'First name is required' : undefined,
                            }}
                            children={(field) => (
                                <div className="form-group">
                                    <label htmlFor={field.name}>
                                        <FontAwesomeIcon icon={faUser} />
                                        First Name *
                                    </label>
                                    <input
                                        type="text"
                                        id={field.name}
                                        name={field.name}
                                        value={field.state.value}
                                        onBlur={field.handleBlur}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        className={field.state.meta.errors.length > 0 ? 'error' : ''}
                                        disabled={isPending}
                                    />
                                    {field.state.meta.errors.length > 0 && (
                                        <span className="error-message">{field.state.meta.errors[0]}</span>
                                    )}
                                </div>
                            )}
                        />

                        <form.Field
                            name="last_name"
                            validators={{
                                onChange: ({ value }) =>
                                    !value.trim() ? 'Last name is required' : undefined,
                            }}
                            children={(field) => (
                                <div className="form-group">
                                    <label htmlFor={field.name}>
                                        <FontAwesomeIcon icon={faUser} />
                                        Last Name *
                                    </label>
                                    <input
                                        type="text"
                                        id={field.name}
                                        name={field.name}
                                        value={field.state.value}
                                        onBlur={field.handleBlur}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        className={field.state.meta.errors.length > 0 ? 'error' : ''}
                                        disabled={isPending}
                                    />
                                    {field.state.meta.errors.length > 0 && (
                                        <span className="error-message">{field.state.meta.errors[0]}</span>
                                    )}
                                </div>
                            )}
                        />
                    </div>

                    <form.Field
                        name="email"
                        validators={{
                            onChange: ({ value }) => {
                                if (!value.trim()) {
                                    return 'Email is required';
                                }
                                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                                    return 'Invalid email format';
                                }
                                return undefined;
                            },
                        }}
                        children={(field) => (
                            <div className="form-group">
                                <label htmlFor={field.name}>
                                    <FontAwesomeIcon icon={faEnvelope} />
                                    Email Address *
                                </label>
                                <input
                                    type="email"
                                    id={field.name}
                                    name={field.name}
                                    value={field.state.value}
                                    onBlur={field.handleBlur}
                                    onChange={(e) => field.handleChange(e.target.value)}
                                    className={field.state.meta.errors.length > 0 ? 'error' : ''}
                                    disabled={isPending}
                                />
                                {field.state.meta.errors.length > 0 && (
                                    <span className="error-message">{field.state.meta.errors[0]}</span>
                                )}
                            </div>
                        )}
                    />

                    <div className="form-row">
                        <form.Field
                            name="password"
                            validators={{
                                onChange: ({ value }) => {
                                    if (!value) {
                                        return 'Password is required';
                                    }
                                    if (value.length < 8) {
                                        return 'Password must be at least 8 characters';
                                    }
                                    return undefined;
                                },
                            }}
                            children={(field) => (
                                <div className="form-group">
                                    <label htmlFor={field.name}>
                                        🔒 Password *
                                    </label>
                                    <input
                                        type="password"
                                        id={field.name}
                                        name={field.name}
                                        value={field.state.value}
                                        onBlur={field.handleBlur}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        className={field.state.meta.errors.length > 0 ? 'error' : ''}
                                        disabled={isPending}
                                        placeholder="Min. 8 characters"
                                    />
                                    {field.state.meta.errors.length > 0 && (
                                        <span className="error-message">{field.state.meta.errors[0]}</span>
                                    )}
                                </div>
                            )}
                        />

                        <form.Field
                            name="confirmPassword"
                            validators={{
                                onChangeListenTo: ['password'],
                                onChange: ({ value, fieldApi }) => {
                                    if (!value) {
                                        return 'Please confirm password';
                                    }
                                    const password = fieldApi.form.getFieldValue('password');
                                    if (value !== password) {
                                        return 'Passwords do not match';
                                    }
                                    return undefined;
                                },
                            }}
                            children={(field) => (
                                <div className="form-group">
                                    <label htmlFor={field.name}>
                                        🔒 Confirm Password *
                                    </label>
                                    <input
                                        type="password"
                                        id={field.name}
                                        name={field.name}
                                        value={field.state.value}
                                        onBlur={field.handleBlur}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        className={field.state.meta.errors.length > 0 ? 'error' : ''}
                                        disabled={isPending}
                                        placeholder="Re-enter password"
                                    />
                                    {field.state.meta.errors.length > 0 && (
                                        <span className="error-message">{field.state.meta.errors[0]}</span>
                                    )}
                                </div>
                            )}
                        />
                    </div>

                    <form.Field
                        name="schedule_date"
                        children={(field) => (
                            <div className="form-group">
                                <label htmlFor={field.name}>
                                    <FontAwesomeIcon icon={faCalendar} />
                                    Schedule Date
                                </label>
                                <input
                                    type="date"
                                    id={field.name}
                                    name={field.name}
                                    value={field.state.value}
                                    onBlur={field.handleBlur}
                                    onChange={(e) => field.handleChange(e.target.value)}
                                    disabled={isPending}
                                />
                            </div>
                        )}
                    />

                    <div className="form-row">
                        <form.Field
                            name="min_date"
                            children={(field) => (
                                <div className="form-group">
                                    <label htmlFor={field.name}>
                                        <FontAwesomeIcon icon={faCalendar} />
                                        Minimum Date
                                    </label>
                                    <input
                                        type="date"
                                        id={field.name}
                                        name={field.name}
                                        value={field.state.value}
                                        onBlur={field.handleBlur}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        disabled={isPending}
                                    />
                                </div>
                            )}
                        />

                        <form.Field
                            name="max_date"
                            children={(field) => (
                                <div className="form-group">
                                    <label htmlFor={field.name}>
                                        <FontAwesomeIcon icon={faCalendar} />
                                        Maximum Date
                                    </label>
                                    <input
                                        type="date"
                                        id={field.name}
                                        name={field.name}
                                        value={field.state.value}
                                        onBlur={field.handleBlur}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        disabled={isPending}
                                    />
                                </div>
                            )}
                        />
                    </div>

                    {isError && (
                        <div className="form-error">
                            <span>❌ {String(error.message) || 'Failed to create applicant. Please try again.'}</span>
                        </div>
                    )}

                    <div className="modal-footer">
                        <button
                            type="button"
                            className="btn-secondary"
                            onClick={handleClose}
                            disabled={isPending}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn-primary"
                            disabled={isPending}
                        >
                            {isPending ? (
                                <>
                                    <FontAwesomeIcon icon={faSpinner} spin />
                                    Creating...
                                </>
                            ) : (
                                'Create Applicant'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddApplicantModal;
