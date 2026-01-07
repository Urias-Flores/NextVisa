import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faArrowLeft,
  faSpinner,
  faExclamationCircle,
  faCheckCircle,
  faInfoCircle,
  faExclamationTriangle,
  faTimesCircle,
} from "@fortawesome/free-solid-svg-icons";
import { useReScheduleLogs } from "../hooks/useReScheduleLogs";
import { useReSchedule } from "../hooks/useReSchedules";
import { useApplicant } from "../hooks/useApplicants";
import { LogState } from "../types/reScheduleLog";
import { formatDate } from "../utils/dateFormatter";

const ReScheduleDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const reScheduleId = parseInt(id || "0");

  const {
    data: reSchedule,
    isLoading: isLoadingReSchedule,
    isError: isErrorReSchedule,
  } = useReSchedule(reScheduleId);

  const {
    data: logs,
    isLoading: isLoadingLogs,
    isError: isErrorLogs,
  } = useReScheduleLogs(reScheduleId);

  const { data: applicant, isLoading: isLoadingApplicant } = useApplicant(
    reSchedule?.applicant || 0
  );

  const getLogIcon = (state: LogState) => {
    switch (state) {
      case "ERROR":
        return (
          <FontAwesomeIcon icon={faTimesCircle} className="log-icon error" />
        );
      case "WARNING":
        return (
          <FontAwesomeIcon
            icon={faExclamationTriangle}
            className="log-icon warning"
          />
        );
      case "SUCCESS":
        return (
          <FontAwesomeIcon icon={faCheckCircle} className="log-icon success" />
        );
      case "INFO":
      default:
        return (
          <FontAwesomeIcon icon={faInfoCircle} className="log-icon info" />
        );
    }
  };

  if (isLoadingReSchedule || isLoadingLogs || isLoadingApplicant) {
    return (
      <div className="loading-state">
        <FontAwesomeIcon icon={faSpinner} className="spinner" spin />
        <p>Loading re-schedule details...</p>
      </div>
    );
  }

  if (isErrorReSchedule || isErrorLogs || !reSchedule) {
    return (
      <div className="error-state">
        <FontAwesomeIcon icon={faExclamationCircle} className="error-icon" />
        <h3>Failed to Load Re-Schedule Details</h3>
        <p>Unable to load re-schedule information. Please try again later.</p>
        <button onClick={() => navigate(-1)} className="btn-secondary">
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="details-container">
      <div className="page-header">
        <button onClick={() => navigate(-1)} className="back-link">
          <FontAwesomeIcon icon={faArrowLeft} />
          <span>Back to Details</span>
        </button>
        <h1>Re-Schedule Process Details</h1>
      </div>

      <div className="re-schedules-details-grid">
        {/* Re-Schedule Information */}
        <div className="info-card">
          <h2>Re-Schedule Information</h2>
          <div className="info-row">
            <span className="info-label">Status:</span>
            <span className={`status-badge ${reSchedule.status.toLowerCase()}`}>
              {reSchedule.status.replace("_", " ")}
            </span>
          </div>
          <div className="info-row">
            <span className="info-label">Start Date:</span>
            <span className="info-value">
              {formatDate(reSchedule.start_datetime)}
            </span>
          </div>
          {reSchedule.end_datetime && (
            <div className="info-row">
              <span className="info-label">End Date:</span>
              <span className="info-value">
                {formatDate(reSchedule.end_datetime)}
              </span>
            </div>
          )}
          {reSchedule.error && (
            <div className="info-row">
              <span className="info-label">Error:</span>
              <span className="info-value error-text">{reSchedule.error}</span>
            </div>
          )}
          <div className="info-row">
            <span className="info-label">Created:</span>
            <span className="info-value">
              {formatDate(reSchedule.created_at)}
            </span>
          </div>
        </div>

        {/* Applicant Information */}
        {applicant && (
          <div className="info-card">
            <h2>Applicant Information</h2>
            <div className="info-row">
              <span className="info-label">Name:</span>
              <span className="info-value">
                {applicant.name} {applicant.last_name}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label">Email:</span>
              <span className="info-value">{applicant.email}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Schedule Number:</span>
              <span className="info-value">{applicant.schedule}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Date Range:</span>
              <span className="info-value">
                {applicant.min_date} to {applicant.max_date}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Logs Timeline */}
      <div className="logs-section">
        <h2>Process Logs</h2>
        {isErrorLogs ? (
          <div className="error-message">
            <FontAwesomeIcon icon={faExclamationCircle} />
            <span>Failed to load logs</span>
          </div>
        ) : !logs || logs.length === 0 ? (
          <div className="empty-state">
            <p>No logs available for this re-schedule process</p>
          </div>
        ) : (
          <div className="logs-timeline">
            {logs.map((log) => (
              <div
                key={log.id}
                className={`log-entry ${log.state.toLowerCase()}`}
              >
                <div className="log-icon-wrapper">{getLogIcon(log.state)}</div>
                <div className="log-content">
                  <div className="log-header">
                    <span className={`log-state ${log.state.toLowerCase()}`}>
                      {log.state}
                    </span>
                    <span className="log-time">
                      {formatDate(log.created_at)}
                    </span>
                  </div>
                  <p className="log-message">{log.content}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReScheduleDetails;
