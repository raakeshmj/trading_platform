import { useState, useEffect } from 'react';
import { api } from '../services/api';
import Ticker from '../components/Market/Ticker';
import OrderBook from '../components/Market/OrderBook';
import OrderForm from '../components/Market/OrderForm';

export default function Dashboard() {
    const [instruments, setInstruments] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState('AAPL');

    useEffect(() => {
        fetchInstruments();
    }, []);

    const fetchInstruments = async () => {
        try {
            const data = await api.instruments.list();
            setInstruments(data);
            if (data.length > 0 && !selectedSymbol) {
                setSelectedSymbol(data[0].symbol);
            }
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="flex flex-col gap-lg">
            <div className="flex justify-between items-center">
                <h1 className="text-xl">Trading Dashboard</h1>

                <select
                    className="input"
                    style={{ width: '200px' }}
                    value={selectedSymbol}
                    onChange={(e) => setSelectedSymbol(e.target.value)}
                >
                    {instruments.map(inst => (
                        <option key={inst.id} value={inst.symbol}>
                            {inst.symbol} - {inst.name}
                        </option>
                    ))}
                    {!instruments.length && <option>Loading...</option>}
                </select>
            </div>

            {selectedSymbol && (
                <div className="flex flex-col gap-lg">
                    <Ticker symbol={selectedSymbol} />

                    <div className="flex gap-lg" style={{ height: '500px' }}>
                        <div className="flex-1">
                            <OrderBook symbol={selectedSymbol} />
                        </div>
                        <div style={{ width: '350px' }}>
                            <OrderForm
                                symbol={selectedSymbol}
                                onOrderPlaced={() => {
                                    // Ideally refresh account balance here
                                }}
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
