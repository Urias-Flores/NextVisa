import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "@tanstack/react-form";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faEnvelope,
  faLock,
  faSpinner,
} from "@fortawesome/free-solid-svg-icons";
import { useAuth } from "../contexts/useAuth";
import Icon from "../assets/icon.png";
import "../styles/auth.css";

const Login: React.FC = () => {
  const [authError, setAuthError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const { signIn } = useAuth();
  const navigate = useNavigate();

  const form = useForm({
    defaultValues: {
      email: "",
      password: "",
    },
    onSubmit: async (form) => {
      const { email, password } = form.value;
      setLoading(true);
      try {
        const { error } = await signIn(email, password);

        if (error) {
          setAuthError(
            error.message || "Failed to sign in. Please check your credentials."
          );
        } else {
          navigate("/dashboard");
        }
      } catch {
        setAuthError("An unexpected error occurred. Please try again.");
      } finally {
        setLoading(false);
      }
    },
  });

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <img src={Icon} alt="NextVisa" />
          </div>
          <h1>Welcome Back</h1>
          <p>
            Sign in to your <strong>Next Visa</strong> account
          </p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            form.handleSubmit();
          }}
        >
          {authError && <div className="auth-error">{authError}</div>}

          <form.Field
            name="email"
            validators={{
              onChange: (input) => {
                if (!input.value) {
                  return "Email is required";
                }
                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value)) {
                  return "Invalid email format";
                }
              },
            }}
            children={(field) => (
              <div className="form-group">
                <label htmlFor="email">
                  <FontAwesomeIcon icon={faEnvelope} />
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => field.handleChange(e.target.value)}
                  className={field.state.meta.errors.length > 0 ? "error" : ""}
                  placeholder="Enter your email"
                  disabled={loading}
                />
                {field.state.meta.errors.length > 0 && (
                  <div className="error-message">
                    {field.state.meta.errors[0]}
                  </div>
                )}
              </div>
            )}
          />

          <form.Field
            name="password"
            validators={{
              onChange: (input) => {
                if (!input.value || input.value.trim().length == 0) {
                  return "Password is required";
                }
              },
            }}
            children={(field) => (
              <div className="form-group">
                <label htmlFor="password">
                  <FontAwesomeIcon icon={faLock} />
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name={field.name}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => field.handleChange(e.target.value)}
                  className={field.state.meta.errors.length > 0 ? "error" : ""}
                  placeholder="Enter your password"
                  disabled={loading}
                />
                {field.state.meta.errors.length > 0 && (
                  <div className="error-message">
                    {field.state.meta.errors[0]}
                  </div>
                )}
              </div>
            )}
          />

          <button type="submit" className="btn" disabled={loading}>
            {loading ? (
              <>
                <FontAwesomeIcon icon={faSpinner} spin /> Signing In...
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <div className="auth-footer">
          Don't have an account? Contact your administrator
        </div>
      </div>
    </div>
  );
};

export default Login;
