import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes, faSpinner, faExclamationCircle } from '@fortawesome/free-solid-svg-icons';
import { useCreateReSchedule } from '../hooks/useReSchedules';
import { ScheduleStatus } from '../types/reSchedule';

interface AddReScheduleModalProps {
    isOpen: boolean;
    onClose: () => void;
    applicantId: number;
}

const AddReScheduleModal: React.FC<AddReScheduleModalProps> = ({ isOpen, onClose, applicantId }) => {
    const [startDateTime, setStartDateTime] = useState('');
    const [endDateTime, setEndDateTime] = useState('');
    const [formError, setFormError] = useState('');

    const createReScheduleMutation = useCreateReSchedule();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError('');

        if (!applicantId) {
            setFormError('Invalid applicant ID');
            return;
        }

        try {
            await createReScheduleMutation.mutateAsync({
                applicant: applicantId,
                start_datetime: startDateTime || undefined,
                end_datetime: endDateTime || undefined,
                status: ScheduleStatus.PENDING,
            });

            // Reset form and close
            setStartDateTime('');
            setEndDateTime('');
            setFormError('');
            onClose();
        } catch (err) {
            setFormError('Failed to create re-schedule. Please try again.');
            console.error(err);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h2>Add Re-Schedule</h2>
                    <button className="close-btn" onClick={onClose}>
                        <FontAwesomeIcon icon={faTimes} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="modal-form">
                    {formError && (
                        <div className="error-message">
                            <FontAwesomeIcon icon={faExclamationCircle} />
                            <span>{formError}</span>
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="startDateTime">Start Date & Time</label>
                        <div className="input-wrapper">
                            <input
                                type="datetime-local"
                                id="startDateTime"
                                value={startDateTime}
                                onChange={(e) => setStartDateTime(e.target.value)}
                                className="form-input"
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="endDateTime">End Date & Time</label>
                        <div className="input-wrapper">
                            <input
                                type="datetime-local"
                                id="endDateTime"
                                value={endDateTime}
                                onChange={(e) => setEndDateTime(e.target.value)}
                                className="form-input"
                                required
                            />
                        </div>
                    </div>

                    <div className="modal-actions">
                        <button type="button" className="cancel-btn" onClick={onClose}>
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="submit-btn"
                            disabled={createReScheduleMutation.isPending}
                        >
                            {createReScheduleMutation.isPending ? (
                                <>
                                    <FontAwesomeIcon icon={faSpinner} spin />
                                    <span>Creating...</span>
                                </>
                            ) : (
                                'Create Re-Schedule'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddReScheduleModal;
