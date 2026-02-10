import { useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const data = await api.auth.login(email, password);
            // Backend returns { access_token, token_type }
            login(data.access_token);
            navigate('/');
        } catch (err) {
            alert('Invalid credentials');
        }
    };

    return (
        <div className="flex justify-center items-center" style={{ minHeight: '100vh' }}>
            <div className="card" style={{ width: '400px' }}>
                <h2 className="text-xl mb-4 text-center">Login</h2>
                <form onSubmit={handleSubmit} className="flex flex-col gap-md">
                    <div>
                        <label className="label">Email</label>
                        <input
                            className="input"
                            type="text"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div>
                        <label className="label">Password</label>
                        <input
                            className="input"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="btn btn-primary btn-block">
                        Sign In
                    </button>
                </form>
                <p className="mt-4 text-center text-sm text-muted">
                    Don't have an account? <a href="/register">Register</a>
                </p>
            </div>
        </div>
    );
}
