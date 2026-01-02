import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEnvelope, faLock, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { useAuth } from '../contexts/useAuth';
import Icon from '../assets/icon.png';
import '../styles/auth.css';

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
    const [authError, setAuthError] = useState<string>('');
    const [loading, setLoading] = useState(false);

    const { signIn } = useAuth();
    const navigate = useNavigate();

    const validateForm = (): boolean => {
        const newErrors: { email?: string; password?: string } = {};

        if (!email.trim()) {
            newErrors.email = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            newErrors.email = 'Invalid email format';
        }

        if (!password) {
            newErrors.password = 'Password is required';
        } else if (password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setAuthError('');

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            const { error } = await signIn(email, password);

            if (error) {
                setAuthError(error.message || 'Failed to sign in. Please check your credentials.');
            } else {
                // Successfully signed in, navigate to dashboard
                navigate('/dashboard');
            }
        } catch {
            setAuthError('An unexpected error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <div className="auth-logo">
                        <img src={Icon} alt="NextVisa" />
                    </div>
                    <h1>Welcome Back</h1>
                    <p>Sign in to your NextVisa account</p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    {authError && (
                        <div className="auth-error">
                            ⚠️ {authError}
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="email">
                            <FontAwesomeIcon icon={faEnvelope} />
                            Email Address
                        </label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => {
                                setEmail(e.target.value);
                                if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }));
                            }}
                            className={errors.email ? 'error' : ''}
                            placeholder="Enter your email"
                            disabled={loading}
                        />
                        {errors.email && <span className="error-message">{errors.email}</span>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">
                            <FontAwesomeIcon icon={faLock} />
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => {
                                setPassword(e.target.value);
                                if (errors.password) setErrors((prev) => ({ ...prev, password: undefined }));
                            }}
                            className={errors.password ? 'error' : ''}
                            placeholder="Enter your password"
                            disabled={loading}
                        />
                        {errors.password && <span className="error-message">{errors.password}</span>}
                    </div>

                    <button type="submit" className="submit-btn" disabled={loading}>
                        {loading ? (
                            <>
                                <FontAwesomeIcon icon={faSpinner} spin /> Signing In...
                            </>
                        ) : (
                            'Sign In'
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
