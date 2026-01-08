import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
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
  faKey,
  faEdit,
  faTrash,
} from "@fortawesome/free-solid-svg-icons";
import { useApplicant, useTestCredentials } from "../hooks/useApplicants";
import {
  useDeleteReSchedule,
  useReSchedulesByApplicant,
} from "../hooks/useReSchedules";
import ReScheduleModal from "../components/ReScheduleModal";
import ApplicantModal from "../components/ApplicantModal";
import { ScheduleStatus } from "../types/reSchedule";
import { formatDate, formatDateOnly } from "../utils/dateFormatter";
import "../styles/pages/applicants.css";
import Swal from "sweetalert2";

const ApplicantDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const applicantId = parseInt(id || "0");
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const {
    data: applicant,
    isLoading: isLoadingApplicant,
    isError: isErrorApplicant,
  } = useApplicant(applicantId);

  const { data: reSchedules = [], isLoading: isLoadingReSchedules } =
    useReSchedulesByApplicant(applicantId);

  const testCredentialsMutation = useTestCredentials();
  const deleteReScheduleMutation = useDeleteReSchedule();

  const handleTestCredentials = async () => {
    const toastId = toast.info("Testing credentials...", { autoClose: false });

    try {
      const result = await testCredentialsMutation.mutateAsync(applicantId);

      toast.dismiss(toastId);

      if (result.success) {
        if (result.schedule) {
          toast.success(
            `Login successful! Schedule number: ${result.schedule}`
          );
        } else {
          toast.warning(
            "Login successful but could not extract schedule number"
          );
        }
      } else {
        toast.error(result.error || "Login failed");
      }
    } catch {
      toast.dismiss(toastId);
      toast.error("Failed to test credentials. Please try again.");
    }
  };

  const handleDeleteReSchedule = async (reScheduleId: number) => {
    Swal.fire({
      title: "Are you sure you want to delete this re-schedule?",
      text: "You won't be able to revert this!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "var(--blue)",
      cancelButtonColor: "var(--red)",
      confirmButtonText: "Yes, delete it!",
    }).then((result) => {
      if (result.isConfirmed) {
        try {
          deleteReScheduleMutation.mutateAsync(reScheduleId);
          toast.success("Re-schedule deleted successfully");
        } catch {
          toast.error("Failed to delete re-schedule. Please try again.");
        }
      }
    });
  };

  const getStatusIcon = (status: ScheduleStatus) => {
    switch (status) {
      case ScheduleStatus.COMPLETED:
        return (
          <FontAwesomeIcon
            icon={faCheckCircle}
            className="status-icon completed"
          />
        );
      case ScheduleStatus.PROCESSING:
        return (
          <FontAwesomeIcon
            icon={faSpinner}
            className="status-icon processing"
            spin
          />
        );
      case ScheduleStatus.PENDING:
        return (
          <FontAwesomeIcon icon={faClock} className="status-icon pending" />
        );
      case ScheduleStatus.SCHEDULED:
        return (
          <FontAwesomeIcon icon={faClock} className="status-icon pending" />
        );
      case ScheduleStatus.FAILED:
        return (
          <FontAwesomeIcon
            icon={faTimesCircle}
            className="status-icon failed"
          />
        );
      case ScheduleStatus.NOT_FOUND:
        return (
          <FontAwesomeIcon
            icon={faQuestionCircle}
            className="status-icon not-found"
          />
        );
      case ScheduleStatus.LOGIN_PENDING:
        return (
          <FontAwesomeIcon icon={faClock} className="status-icon pending" />
        );
      default:
        return (
          <FontAwesomeIcon
            icon={faExclamationTriangle}
            className="status-icon unknown"
          />
        );
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
          <FontAwesomeIcon
            icon={faExclamationTriangle}
            className="error-icon"
          />
          <h3>Applicant Not Found</h3>
          <p>
            The applicant you are looking for does not exist or could not be
            loaded.
          </p>
          <button className="back-btn" onClick={() => navigate("/applicants")}>
            <FontAwesomeIcon icon={faArrowLeft} />
            Back to Applicants
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="details-container">
      <div className="details-header">
        <button className="back-link" onClick={() => navigate("/applicants")}>
          <FontAwesomeIcon icon={faArrowLeft} />
          <span>Back to List</span>
        </button>
        <div className="header-content">
          <div className="applicant-title">
            <div className="avatar-placeholder">
              {applicant.name.charAt(0)}
              {applicant.last_name.charAt(0)}
            </div>
            <div>
              <h1>
                {applicant.name} {applicant.last_name}
              </h1>
              <span className="applicant-id">ID: #{applicant.id}</span>
            </div>
          </div>
          <div className="header-actions">
            <button
              className="btn-small"
              onClick={handleTestCredentials}
              disabled={testCredentialsMutation.isPending}
            >
              {testCredentialsMutation.isPending ? (
                <FontAwesomeIcon icon={faSpinner} spin />
              ) : (
                <FontAwesomeIcon icon={faKey} />
              )}
              <span>
                {testCredentialsMutation.isPending
                  ? "Testing..."
                  : "Test Credentials"}
              </span>
            </button>

            <button
              className="btn-small"
              onClick={() => setIsEditModalOpen(true)}
            >
              <FontAwesomeIcon icon={faEdit} />
              <span>Edit</span>
            </button>
          </div>
        </div>
      </div>

      <div className="applicants-details-grid">
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
              <div className="info-value">
                {formatDateOnly(applicant.schedule_date) || "Not Scheduled"}
              </div>
            </div>

            <div className="info-item">
              <div className="info-label">
                <FontAwesomeIcon icon={faCalendar} />
                <span>Min - Max date re-schedule</span>
              </div>
              <div className="info-value">
                {formatDateOnly(applicant.min_date) || "Not Scheduled"} -{" "}
                {formatDateOnly(applicant.max_date) || "Not Scheduled"}
              </div>
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
              <div className="info-value">
                {applicant.schedule || "No Schedule number"}
              </div>
            </div>
            <div className="info-item">
              <div className="info-label">
                <FontAwesomeIcon icon={faClock} />
                <span>Updated At</span>
              </div>
              <div className="info-value">
                {formatDate(applicant.updated_at)}
              </div>
            </div>
          </div>
        </div>

        <div className="re-schedules-section">
          <div className="section-header">
            <h3>Re-Schedule History</h3>
            <div className="section-actions">
              <button
                className="btn-small"
                onClick={() => setIsAddModalOpen(true)}
              >
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
              <FontAwesomeIcon
                icon={faCalendarAlt}
                className="empty-icon-small"
              />
              <p>No re-schedule attempts recorded.</p>
            </div>
          ) : (
            <div className="re-schedules-list">
              {reSchedules.map((item) => (
                <div key={item.id} className="re-schedule-card">
                  <div className="re-schedule-header">
                    <div
                      className={`status-badge ${item.status.toLowerCase()}`}
                    >
                      {getStatusIcon(item.status)}
                      <span>{item.status.replace("_", " ")}</span>
                    </div>
                    <span className="re-schedule-date">
                      {formatDate(item.created_at)}
                    </span>
                  </div>
                  <div className="re-schedule-body">
                    <div className="time-range">
                      <div className="time-item">
                        <span className="label">Start:</span>
                        <span className="value">
                          {formatDate(item.start_datetime)}
                        </span>
                      </div>
                      <div className="time-item">
                        <span className="label">End:</span>
                        <span className="value">
                          {formatDate(item.end_datetime)}
                        </span>
                      </div>
                    </div>
                    {item.error && (
                      <div className="error-alert">
                        <strong>Error:</strong> {item.error}
                      </div>
                    )}

                    <div className="re-schedule-actions">
                      {(item.status === ScheduleStatus.PROCESSING ||
                        item.status === ScheduleStatus.COMPLETED ||
                        item.status === ScheduleStatus.FAILED ||
                        item.status === ScheduleStatus.NOT_FOUND ||
                        item.status === ScheduleStatus.SCHEDULED) && (
                        <>
                          <button
                            className="btn btn-small"
                            onClick={() =>
                              navigate(`/re-schedules/${item.id}/logs`)
                            }
                          >
                            Logs
                          </button>

                          <div className="separator-line"></div>
                        </>
                      )}

                      <button className="btn btn-rounded">
                        <FontAwesomeIcon icon={faEdit} />
                      </button>

                      <button
                        className="btn btn-rounded"
                        onClick={() => handleDeleteReSchedule(item.id)}
                      >
                        <FontAwesomeIcon icon={faTrash} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <ReScheduleModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        applicantId={applicantId}
      />

      <ApplicantModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        applicant={applicant}
      />
    </div>
  );
};

export default ApplicantDetails;
