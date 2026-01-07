import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faUsers,
  faUserPlus,
  faSearch,
  faEnvelope,
  faCalendar,
  faSpinner,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";
import { useApplicants, useDeleteApplicant } from "../hooks/useApplicants";
import AddApplicantModal from "../components/ApplicantModal";
import { toast } from "react-toastify";
import Swal from "sweetalert2";
import type { Applicant } from "../types/applicantServices";

const Applicants: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [selectedApplicant, setSelectedApplicant] = useState<Applicant | null>(
    null
  );

  // Use TanStack Query to fetch applicants
  const {
    data: applicants = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useApplicants();
  const { mutate: deleteApplicant } = useDeleteApplicant();

  // Filter applicants based on search query
  const filteredApplicants = useMemo(() => {
    if (!applicants) return [];

    const query = searchQuery.toLowerCase();
    return applicants.filter(
      (applicant) =>
        applicant.name.toLowerCase().includes(query) ||
        applicant.last_name.toLowerCase().includes(query) ||
        applicant.email.toLowerCase().includes(query)
    );
  }, [applicants, searchQuery]);

  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const handleDelete = (id: number) => {
    Swal.fire({
      title: "Are you sure?",
      text: "You won't be able to revert this!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "var(--blue)",
      cancelButtonColor: "var(--red)",
      confirmButtonText: "Yes, delete it!",
    }).then((result) => {
      if (result.isConfirmed) {
        try {
          deleteApplicant(id, {
            onSuccess: () => {
              toast.success("Applicant deleted successfully");
              refetch();
            },
            onError: (error) => {
              console.error("Error deleting applicant:", error);
              toast.error("Error deleting applicant");
            },
          });
        } catch (error) {
          console.error("Error deleting applicant:", error);
        }
      }
    });
  };

  const handleAddNew = () => {
    setSelectedApplicant(null);
    setIsModalOpen(true);
  };

  const handleEdit = (applicant: Applicant) => {
    setSelectedApplicant(applicant);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedApplicant(null);
  };

  return (
    <div className="container">
      <div className="header">
        <div>
          <h1>Applicants</h1>
          <p>Manage all visa applicants and their applications</p>
        </div>
      </div>

      <div className="page-actions">
        <div className="filters">
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
        </div>

        <div className="actions">
          <button className="btn" onClick={handleAddNew}>
            <FontAwesomeIcon icon={faUserPlus} />
            <span>Add Applicant</span>
          </button>
        </div>
      </div>

      <div className="content">
        {isLoading ? (
          <div className="loading-state">
            <FontAwesomeIcon icon={faSpinner} className="spinner" spin />
            <p>Loading applicants...</p>
          </div>
        ) : isError ? (
          <div className="error-state">
            <FontAwesomeIcon
              icon={faExclamationCircle}
              className="error-icon"
            />
            <h3>Error Loading Applicants</h3>
            <p>
              {(error as Error)?.message ||
                "Failed to load applicants. Please try again."}
            </p>
            <button className="retry-btn" onClick={() => refetch()}>
              Try Again
            </button>
          </div>
        ) : filteredApplicants.length === 0 ? (
          <div className="empty-state">
            <FontAwesomeIcon icon={faUsers} className="empty-icon" />
            <h3>{searchQuery ? "No Applicants Found" : "No Applicants Yet"}</h3>
            <p>
              {searchQuery
                ? "Try adjusting your search criteria"
                : "Start by adding your first applicant  to the system"}
            </p>
            {!searchQuery && (
              <button className="add-btn-secondary" onClick={handleAddNew}>
                <FontAwesomeIcon icon={faUserPlus} />
                <span>Add Your First Applicant</span>
              </button>
            )}
          </div>
        ) : (
          <div className="table-container">
            <table className="table">
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
                      <div className="table-name">
                        {applicant.name} {applicant.last_name}
                      </div>
                    </td>
                    <td>
                      <div className="table-email">
                        <FontAwesomeIcon icon={faEnvelope} />
                        <span>{applicant.email}</span>
                      </div>
                    </td>
                    <td>
                      <div className="table-date">
                        <FontAwesomeIcon icon={faCalendar} />
                        <span>
                          {applicant.schedule_date || "Not scheduled"}
                        </span>
                      </div>
                    </td>
                    <td>{formatDate(applicant.created_at)}</td>
                    <td>
                      <div className="table-actions">
                        <button
                          className="btn"
                          onClick={() => handleEdit(applicant)}
                        >
                          Edit
                        </button>
                        <button
                          className="btn"
                          onClick={() =>
                            navigate(`/applicants/${applicant.id}`)
                          }
                        >
                          View
                        </button>
                        <button
                          className="btn btn-danger"
                          onClick={() => handleDelete(applicant.id)}
                        >
                          Delete
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
        onClose={handleCloseModal}
        applicant={selectedApplicant}
      />
    </div>
  );
};

export default Applicants;
