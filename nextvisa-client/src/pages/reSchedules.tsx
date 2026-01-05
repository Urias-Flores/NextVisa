import React, { useMemo, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faCalendarAlt,
  faSearch,
  faFilter,
  faSpinner,
  faExclamationTriangle,
  faCheckCircle,
  faClock,
  faTimesCircle,
  faQuestionCircle,
  faCalendarPlus,
} from "@fortawesome/free-solid-svg-icons";
import { useReSchedules } from "../hooks/useReSchedules";
import { useApplicants } from "../hooks/useApplicants";
import { ScheduleStatus } from "../types/reSchedule";

const ReSchedules: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [applicantFilter, setApplicantFilter] = useState<string>("ALL");

  // Fetch re-schedules
  const {
    data: reSchedules = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useReSchedules();

  // Fetch applicants for filter
  const { data: applicants = [] } = useApplicants();

  // Filter re-schedules
  const filteredReSchedules = useMemo(() => {
    if (!reSchedules) return [];

    return reSchedules.filter((item) => {
      const matchesStatus =
        statusFilter === "ALL" || item.status === statusFilter;
      const matchesApplicant =
        applicantFilter === "ALL" ||
        item.applicant === parseInt(applicantFilter);
      return matchesStatus && matchesApplicant;
    });
  }, [reSchedules, statusFilter, applicantFilter]);

  const formatDate = (dateString?: string) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
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
      default:
        return (
          <FontAwesomeIcon
            icon={faExclamationTriangle}
            className="status-icon unknown"
          />
        );
    }
  };

  const getApplicantName = (applicantId: number) => {
    const applicant = applicants.find((a) => a.id === applicantId);
    return applicant
      ? `${applicant.name} ${applicant.last_name}`
      : `ID: ${applicantId}`;
  };

  return (
    <div className="container">
      <div className="header">
        <div>
          <h1>Re-Schedules</h1>
          <p>Monitor and manage appointment re-scheduling attempts</p>
        </div>
      </div>

      <div className="page-actions">
        <div className="filters">
          <div className="filter-group">
            <FontAwesomeIcon icon={faFilter} className="search-icon" />
            <select
              className="search-input"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              {Object.values(ScheduleStatus).map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <FontAwesomeIcon icon={faSearch} className="search-icon" />
            <select
              className="search-input"
              value={applicantFilter}
              onChange={(e) => setApplicantFilter(e.target.value)}
            >
              <option value="ALL">All Applicants</option>
              {applicants.map((applicant) => (
                <option key={applicant.id} value={applicant.id}>
                  {applicant.name} {applicant.last_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="actions">
          <button className="btn">
            <FontAwesomeIcon icon={faCalendarPlus} />
            <span>Add Re-Schedule</span>
          </button>
        </div>
      </div>

      <div className="applicants-content">
        {isLoading ? (
          <div className="loading-state">
            <FontAwesomeIcon icon={faSpinner} className="spinner" spin />
            <p>Loading re-schedules...</p>
          </div>
        ) : isError ? (
          <div className="error-state">
            <div className="error-icon">⚠️</div>
            <h3>Error Loading Data</h3>
            <p>{(error as Error)?.message || "Failed to load re-schedules."}</p>
            <button className="retry-btn" onClick={() => refetch()}>
              Try Again
            </button>
          </div>
        ) : filteredReSchedules.length === 0 ? (
          <div className="empty-state">
            <FontAwesomeIcon icon={faCalendarAlt} className="empty-icon" />
            <h3>No Re-Schedules Found</h3>
            <p>Try adjusting your filters or check back later.</p>
          </div>
        ) : (
          <div className="applicants-table-container">
            <table className="applicants-table">
              <thead>
                <tr>
                  <th>Applicant</th>
                  <th>Status</th>
                  <th>Start Time</th>
                  <th>End Time</th>
                  <th>Error</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {filteredReSchedules.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div className="applicant-name">
                        {getApplicantName(item.applicant)}
                      </div>
                    </td>
                    <td>
                      <div
                        className={`status-badge ${item.status.toLowerCase()}`}
                      >
                        {getStatusIcon(item.status)}
                        <span>{item.status}</span>
                      </div>
                    </td>
                    <td>{formatDate(item.start_datetime)}</td>
                    <td>{formatDate(item.end_datetime)}</td>
                    <td className="error-text">
                      {item.error ? (
                        <span title={item.error}>
                          {item.error.length > 30
                            ? item.error.substring(0, 30) + "..."
                            : item.error}
                        </span>
                      ) : (
                        "-"
                      )}
                    </td>
                    <td>{formatDate(item.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <style>{`
                .filter-group {
                    display: flex;
                    align-items: center;
                    position: relative;
                }
                .status-badge {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.25rem 0.75rem;
                    border-radius: 999px;
                    font-size: 0.85rem;
                    font-weight: 500;
                    width: fit-content;
                }
                .status-badge.completed { background: #dcfce7; color: #166534; }
                .status-badge.processing { background: #dbeafe; color: #1e40af; }
                .status-badge.pending { background: #fef9c3; color: #854d0e; }
                .status-badge.failed { background: #fee2e2; color: #991b1b; }
                .status-badge.not_found { background: #f3f4f6; color: #374151; }
                
                .error-text {
                    color: #ef4444;
                    font-size: 0.9rem;
                }
            `}</style>
    </div>
  );
};

export default ReSchedules;
