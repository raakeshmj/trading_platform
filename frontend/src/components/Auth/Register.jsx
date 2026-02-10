import { useState } from 'react';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.auth.register(email, password);
            alert('Registration successful! Please login.');
            navigate('/login');
        } catch (err) {
            alert('Registration failed');
        }
    };

    return (
        <div className="flex justify-center items-center" style={{ minHeight: '100vh' }}>
            <div className="card" style={{ width: '400px' }}>
                <h2 className="text-xl mb-4 text-center">Register</h2>
                <form onSubmit={handleSubmit} className="flex flex-col gap-md">
                    <div>
                        <label className="label">Email</label>
                        <input
                            className="input"
                            type="email"
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
                        Create Account
                    </button>
                </form>
                <p className="mt-4 text-center text-sm text-muted">
                    Already have an account? <a href="/login">Login</a>
                </p>
            </div>
        </div>
    );
}
