const API_URL = 'http://localhost:8000/api/v1';

const getHeaders = () => {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
};

export const api = {
    auth: {
        login: async (username, password) => {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const res = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                body: formData, // OAuth2PasswordRequestForm expects form data
            });
            if (!res.ok) throw new Error('Login failed');
            return res.json();
        },
        register: async (email, password) => {
            const res = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            if (!res.ok) throw new Error('Registration failed');
            return res.json();
        }
    },

    account: {
        get: async () => {
            const res = await fetch(`${API_URL}/accounts/me`, { headers: getHeaders() });
            return res.json();
        }
    },

    instruments: {
        list: async () => {
            const res = await fetch(`${API_URL}/instruments/`, { headers: getHeaders() });
            return res.json();
        },
        create: async (data) => {
            const res = await fetch(`${API_URL}/instruments/`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify(data)
            });
            if (!res.ok) throw new Error('Failed to create instrument');
            return res.json();
        }
    },

    orders: {
        list: async () => {
            const res = await fetch(`${API_URL}/orders/`, { headers: getHeaders() });
            return res.json();
        },
        create: async (order) => {
            const res = await fetch(`${API_URL}/orders/`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify(order)
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Order failed');
            }
            return res.json();
        },
        cancel: async (id) => {
            // TODO: Implement cancel endpoint in backend if verified
        }
    }
};
