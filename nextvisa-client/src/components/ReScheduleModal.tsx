import React, { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTimes,
  faSpinner,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";
import { useForm } from "@tanstack/react-form";
import { useCreateReSchedule } from "../hooks/useReSchedules";
import { ScheduleStatus } from "../types/reSchedule";
import { toast } from "react-toastify";

interface ReScheduleModalProps {
  isOpen: boolean;
  onClose: () => void;
  applicantId: number;
}

const ReScheduleModal: React.FC<ReScheduleModalProps> = ({
  isOpen,
  onClose,
  applicantId,
}) => {
  const [isClosing, setIsClosing] = useState(false);
  const createReScheduleMutation = useCreateReSchedule();

  const form = useForm({
    defaultValues: {
      start_datetime: "",
      end_datetime: "",
    },
    onSubmit: async ({ value }) => {
      if (!applicantId) {
        toast.error("Invalid applicant ID");
        return;
      }

      try {
        await createReScheduleMutation.mutateAsync({
          applicant: applicantId,
          start_datetime: value.start_datetime || undefined,
          end_datetime: value.end_datetime || undefined,
          status: ScheduleStatus.PENDING,
        });

        toast.success("Re-schedule created successfully");
        form.reset();
        handleClose();
      } catch (err) {
        toast.error("Failed to create re-schedule. Please try again.");
        console.error(err);
      }
    },
  });

  const handleClose = () => {
    if (!createReScheduleMutation.isPending) {
      setIsClosing(true);
      setTimeout(() => {
        setIsClosing(false);
        form.reset();
        onClose();
      }, 250);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={`modal-overlay ${isClosing ? "closing" : ""}`}>
      <div className="modal-container modal-container-small">
        <div className="modal-header">
          <h2>Add Re-Schedule</h2>
          <button className="modal-close-btn" onClick={handleClose}>
            <FontAwesomeIcon icon={faTimes} />
          </button>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            form.handleSubmit();
          }}
          className="modal-form"
        >
          <form.Field
            name="start_datetime"
            validators={{
              onBlur: ({ value }) => {
                if (!value) {
                  return "Start date and time is required";
                }
                return undefined;
              },
            }}
          >
            {(field) => (
              <div className="form-group">
                <label htmlFor={field.name}>Start Date & Time</label>
                <div className="input-wrapper">
                  <input
                    type="datetime-local"
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className="form-input"
                  />
                </div>
                {field.state.meta.errors.length > 0 && (
                  <div className="error-message">
                    <FontAwesomeIcon icon={faExclamationCircle} />
                    <span>{field.state.meta.errors[0]}</span>
                  </div>
                )}
              </div>
            )}
          </form.Field>

          <form.Field
            name="end_datetime"
            validators={{
              onBlur: ({ value, fieldApi }) => {
                if (!value) {
                  return "End date and time is required";
                }
                const startDateTime =
                  fieldApi.form.getFieldValue("start_datetime");
                if (
                  startDateTime &&
                  new Date(value) <= new Date(startDateTime)
                ) {
                  return "End date must be after start date";
                }
                return undefined;
              },
            }}
          >
            {(field) => (
              <div className="form-group">
                <label htmlFor={field.name}>End Date & Time</label>
                <div className="input-wrapper">
                  <input
                    type="datetime-local"
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className="form-input"
                  />
                </div>
                {field.state.meta.errors.length > 0 && (
                  <div className="error-message">
                    <FontAwesomeIcon icon={faExclamationCircle} />
                    <span>{field.state.meta.errors[0]}</span>
                  </div>
                )}
              </div>
            )}
          </form.Field>

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleClose}
              disabled={createReScheduleMutation.isPending}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn"
              disabled={createReScheduleMutation.isPending}
            >
              {createReScheduleMutation.isPending ? (
                <>
                  <FontAwesomeIcon icon={faSpinner} spin />
                  <span>Creating...</span>
                </>
              ) : (
                "Create Re-Schedule"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReScheduleModal;
