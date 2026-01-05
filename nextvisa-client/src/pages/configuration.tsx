import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faSave,
  faSpinner,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";
import {
  useConfiguration,
  useUpdateConfiguration,
} from "../hooks/useConfiguration";
import { type Configuration as configObject } from "../types/configuration";
import { toast } from "react-toastify";
import { useForm } from "@tanstack/react-form";
import "../styles/configuration.css";

interface ConfigurationFormProps {
  config: configObject;
}

const ConfigurationForm: React.FC<ConfigurationFormProps> = ({ config }) => {
  const updateMutation = useUpdateConfiguration();

  const form = useForm({
    defaultValues: {
      base_url: config.base_url,
      hub_address: config.hub_address,
      sleep_time: config.sleep_time,
      push_token: config.push_token,
      push_user: config.push_user,
      df_msg: config.df_msg,
    },
    onSubmit: async ({ value }) => {
      try {
        await updateMutation.mutateAsync(
          {
            id: config.id,
            data: value,
          },
          {
            onSuccess: () => {
              toast.success("Configuration updated successfully");
            },
            onError: (error) => {
              console.error("Failed to update configuration:", error);
              toast.error("Failed to update configuration");
            },
          }
        );
      } catch (error) {
        console.error("Failed to update configuration:", error);
      }
    },
  });

  return (
    <div className="configuration-content">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          e.stopPropagation();
          form.handleSubmit();
        }}
        className="configuration-form"
      >
        <div className="form-section">
          <h3>API Settings</h3>
          <div className="form-grid">
            <form.Field
              name="base_url"
              validators={{
                onBlur: ({ value }) =>
                  !value.trim() ? "Base URL is required" : undefined,
              }}
              children={(field) => (
                <div className="form-group">
                  <label htmlFor={field.name}>Base URL *</label>
                  <input
                    type="text"
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className={`form-input ${
                      field.state.meta.errors.length > 0 ? "error" : ""
                    }`}
                    disabled={updateMutation.isPending}
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
              name="hub_address"
              validators={{
                onBlur: ({ value }) =>
                  !value.trim() ? "Hub Address is required" : undefined,
              }}
              children={(field) => (
                <div className="form-group">
                  <label htmlFor={field.name}>Hub Address *</label>
                  <input
                    type="text"
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className={`form-input ${
                      field.state.meta.errors.length > 0 ? "error" : ""
                    }`}
                    disabled={updateMutation.isPending}
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
              name="sleep_time"
              validators={{
                onBlur: ({ value }) => {
                  if (!value || value < 1) {
                    return "Sleep time must be at least 1 second";
                  }
                  return undefined;
                },
              }}
              children={(field) => (
                <div className="form-group">
                  <label htmlFor={field.name}>Sleep Time (seconds) *</label>
                  <input
                    type="number"
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) =>
                      field.handleChange(parseFloat(e.target.value))
                    }
                    className={`form-input ${
                      field.state.meta.errors.length > 0 ? "error" : ""
                    }`}
                    min="1"
                    step="5"
                    disabled={updateMutation.isPending}
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
        </div>

        <div className="form-section">
          <h3>Push Notification Settings</h3>
          <div className="form-grid">
            <form.Field
              name="push_token"
              validators={{
                onBlur: ({ value }) =>
                  !value.trim() ? "Push Token is required" : undefined,
              }}
              children={(field) => (
                <div className="form-group">
                  <label htmlFor={field.name}>Push Token *</label>
                  <input
                    type="text"
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className={`form-input ${
                      field.state.meta.errors.length > 0 ? "error" : ""
                    }`}
                    disabled={updateMutation.isPending}
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
              name="push_user"
              validators={{
                onBlur: ({ value }) =>
                  !value.trim() ? "Push User is required" : undefined,
              }}
              children={(field) => (
                <div className="form-group">
                  <label htmlFor={field.name}>Push User *</label>
                  <input
                    type="text"
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className={`form-input ${
                      field.state.meta.errors.length > 0 ? "error" : ""
                    }`}
                    disabled={updateMutation.isPending}
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
        </div>

        <div className="form-section">
          <h3>Default Message</h3>
          <form.Field
            name="df_msg"
            validators={{
              onBlur: ({ value }) =>
                !value.trim() ? "Default Message is required" : undefined,
            }}
            children={(field) => (
              <div className="form-group">
                <label htmlFor={field.name}>Default Message *</label>
                <textarea
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => field.handleChange(e.target.value)}
                  className={`form-input ${
                    field.state.meta.errors.length > 0 ? "error" : ""
                  }`}
                  rows={2}
                  disabled={updateMutation.isPending}
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
          <h1>Configuration</h1>
          <p>Manage application settings for the re-scheduler</p>
        </div>
      </div>

      <ConfigurationForm config={config} key={config.id} />
    </div>
  );
};

export default Configuration;
