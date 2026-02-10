import { useAuth } from '../context/AuthContext';
import { Link, Outlet, useNavigate } from 'react-router-dom';

export default function Layout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <>
            <header style={{
                height: 'var(--header-height)',
                borderBottom: '1px solid var(--border-color)',
                backgroundColor: 'var(--bg-color)',
                display: 'flex',
                alignItems: 'center',
                padding: '0 var(--spacing-lg)',
                justifyContent: 'space-between',
                position: 'sticky',
                top: 0,
                zIndex: 10
            }}>
                <div className="flex items-center gap-md">
                    <Link to="/" className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                        CryptoTrade
                    </Link>
                    <nav className="flex gap-md">
                        <Link to="/" className="text-sm text-muted hover:text-primary">Dashboard</Link>
                        <Link to="/markets" className="text-sm text-muted hover:text-primary">Markets</Link>
                    </nav>
                </div>

                <div className="flex items-center gap-md">
                    {user && (
                        <div className="text-sm text-muted">
                            Balance: <span className="text-success font-mono">${parseFloat(user.cash_balance).toFixed(2)}</span>
                        </div>
                    )}
                    <button onClick={handleLogout} className="btn btn-outline text-sm">
                        Logout
                    </button>
                </div>
            </header>

            <main className="container flex-grow py-8">
                <Outlet />
            </main>
        </>
    );
}
