import React, { useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTimes,
  faSpinner,
  faUser,
  faEnvelope,
  faCalendar,
  faLock,
} from "@fortawesome/free-solid-svg-icons";
import { useForm } from "@tanstack/react-form";
import { useCreateApplicant, useUpdateApplicant } from "../hooks/useApplicants";
import type { ApplicantCreate, Applicant } from "../types/applicantServices";
import "../styles/modal.css";
import { toast } from "react-toastify";

interface AddApplicantModalProps {
  isOpen: boolean;
  onClose: () => void;
  applicant?: Applicant | null;
}

const AddApplicantModal: React.FC<AddApplicantModalProps> = ({
  isOpen,
  onClose,
  applicant = null,
}) => {
  const [isClosing, setIsClosing] = useState(false);
  const {
    mutate: createApplicant,
    isPending: isCreating,
    isError: isCreateError,
    error: createError,
  } = useCreateApplicant();

  const {
    mutate: updateApplicant,
    isPending: isUpdating,
    isError: isUpdateError,
    error: updateError,
  } = useUpdateApplicant();

  const isEditMode = !!applicant;
  const isPending = isCreating || isUpdating;
  const isError = isCreateError || isUpdateError;
  const error = createError || updateError;

  const form = useForm({
    defaultValues: {
      name: applicant?.name || "",
      last_name: applicant?.last_name || "",
      email: applicant?.email || "",
      password: "",
      confirmPassword: "",
      schedule_date: applicant?.schedule_date || "",
      min_date: applicant?.min_date || "",
      max_date: applicant?.max_date || "",
      schedule: applicant?.schedule || "",
    },
    onSubmit: async ({ value }) => {
      const { ...applicantData } = value;

      if (isEditMode && applicant) {
        const updateData: Record<string, string> = { ...applicantData };
        if (!updateData.password) {
          delete updateData.password;
        }

        updateApplicant(
          { id: applicant.id, data: updateData },
          {
            onSuccess: () => {
              toast.success("Applicant updated successfully");
              form.reset();
              handleClose();
            },
            onError: () => {
              toast.error("Failed to update applicant");
            },
          }
        );
      } else {
        // Create new applicant
        createApplicant(applicantData as ApplicantCreate, {
          onSuccess: () => {
            toast.success("Applicant created successfully");
            form.reset();
            handleClose();
          },
          onError: () => {
            toast.error("Failed to create applicant");
          },
        });
      }
    },
  });

  // Reset form when applicant changes or modal opens/closes
  useEffect(() => {
    if (isOpen) {
      form.setFieldValue("name", applicant?.name || "");
      form.setFieldValue("last_name", applicant?.last_name || "");
      form.setFieldValue("email", applicant?.email || "");
      form.setFieldValue("password", "");
      form.setFieldValue("confirmPassword", "");
      form.setFieldValue("schedule_date", applicant?.schedule_date || "");
      form.setFieldValue("min_date", applicant?.min_date || "");
      form.setFieldValue("max_date", applicant?.max_date || "");
      form.setFieldValue("schedule", applicant?.schedule || "");
    }
  }, [applicant, isOpen, form]);

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
    <div
      className={`modal-overlay ${isClosing ? "closing" : ""}`}
      onClick={handleClose}
    >
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditMode ? "Edit Applicant" : "Add New Applicant"}</h2>
          <button
            className="modal-close-btn"
            onClick={handleClose}
            disabled={isPending}
          >
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
          <div className="form-row">
            <form.Field
              name="name"
              validators={{
                onBlur: ({ value }) =>
                  !value.trim() ? "First name is required" : undefined,
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
                    className={
                      field.state.meta.errors.length > 0 ? "error" : ""
                    }
                    disabled={isPending}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <span className="error-message">
                      {field.state.meta.errors[0]}
                    </span>
                  )}
                </div>
              )}
            />

            <form.Field
              name="last_name"
              validators={{
                onBlur: ({ value }) =>
                  !value.trim() ? "Last name is required" : undefined,
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
                    className={
                      field.state.meta.errors.length > 0 ? "error" : ""
                    }
                    disabled={isPending}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <span className="error-message">
                      {field.state.meta.errors[0]}
                    </span>
                  )}
                </div>
              )}
            />
          </div>

          <form.Field
            name="email"
            validators={{
              onBlur: ({ value }) => {
                if (!value.trim()) {
                  return "Email is required";
                }
                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                  return "Invalid email format";
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
                  className={field.state.meta.errors.length > 0 ? "error" : ""}
                  disabled={isPending}
                />
                {field.state.meta.errors.length > 0 && (
                  <span className="error-message">
                    {field.state.meta.errors[0]}
                  </span>
                )}
              </div>
            )}
          />

          <div className="form-row">
            <form.Field
              name="password"
              validators={{
                onBlur: ({ value }) => {
                  // Password is required only when creating a new applicant
                  if (!isEditMode && !value) {
                    return "Password is required";
                  }
                  // If password is provided, validate its length
                  if (value && value.length < 8) {
                    return "Password must be at least 8 characters";
                  }
                  return undefined;
                },
              }}
              children={(field) => (
                <div className="form-group">
                  <label htmlFor={field.name}>
                    <FontAwesomeIcon icon={faLock} />
                    Password{" "}
                    {isEditMode ? "(leave blank to keep current)" : "*"}
                  </label>
                  <input
                    type="password"
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className={
                      field.state.meta.errors.length > 0 ? "error" : ""
                    }
                    disabled={isPending}
                    placeholder="Min. 8 characters"
                  />
                  {field.state.meta.errors.length > 0 && (
                    <span className="error-message">
                      {field.state.meta.errors[0]}
                    </span>
                  )}
                </div>
              )}
            />

            <form.Field
              name="confirmPassword"
              validators={{
                onBlurListenTo: ["password"],
                onBlur: ({ value, fieldApi }) => {
                  const password = fieldApi.form.getFieldValue("password");
                  // Only validate if password field has value
                  if (password && !value) {
                    return "Please confirm password";
                  }
                  if (password && value !== password) {
                    return "Passwords do not match";
                  }
                  return undefined;
                },
              }}
              children={(field) => (
                <div className="form-group">
                  <label htmlFor={field.name}>
                    <FontAwesomeIcon icon={faLock} />
                    Confirm Password {isEditMode ? "" : "*"}
                  </label>
                  <input
                    type="password"
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className={
                      field.state.meta.errors.length > 0 ? "error" : ""
                    }
                    disabled={isPending}
                    placeholder="Re-enter password"
                  />
                  {field.state.meta.errors.length > 0 && (
                    <span className="error-message">
                      {field.state.meta.errors[0]}
                    </span>
                  )}
                </div>
              )}
            />
          </div>

          <form.Field
            name="schedule_date"
            validators={{
              onBlur: ({ value }) => {
                if (!value) {
                  return "Schedule date is required";
                }
              },
            }}
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
                {field.state.meta.errors.length > 0 && (
                  <span className="error-message">
                    {field.state.meta.errors[0]}
                  </span>
                )}
              </div>
            )}
          />

          <div className="form-row">
            <form.Field
              name="min_date"
              validators={{
                onBlur: ({ value }) => {
                  if (!value) {
                    return "Minimum date is required";
                  }
                },
              }}
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
                  {field.state.meta.errors.length > 0 && (
                    <span className="error-message">
                      {field.state.meta.errors[0]}
                    </span>
                  )}
                </div>
              )}
            />

            <form.Field
              name="max_date"
              validators={{
                onBlur: ({ value, fieldApi }) => {
                  if (!value) {
                    return "Maximum date is required";
                  }
                  if (value <= fieldApi.form.getFieldValue("min_date")) {
                    return "Maximum date must be greater than minimum date";
                  }
                },
              }}
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
                  {field.state.meta.errors.length > 0 && (
                    <span className="error-message">
                      {field.state.meta.errors[0]}
                    </span>
                  )}
                </div>
              )}
            />
          </div>

          {isError && error && (
            <div className="form-error">
              <span>
                {String(error.message) ||
                  "Failed to create applicant. Please try again."}
              </span>
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
            <button type="submit" className="btn" disabled={isPending}>
              {isPending ? (
                <>
                  <FontAwesomeIcon icon={faSpinner} spin />
                  {isEditMode ? "Updating..." : "Creating..."}
                </>
              ) : isEditMode ? (
                "Update Applicant"
              ) : (
                "Create Applicant"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddApplicantModal;
