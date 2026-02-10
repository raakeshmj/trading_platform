import { useEffect, useRef, useState } from "react";
import { api } from "../../services/api";

export default function OrderBook({ symbol }) {
    const [bids, setBids] = useState([]);
    const [asks, setAsks] = useState([]);
    const ws = useRef(null);

    useEffect(() => {
        // Initial Snapshot
        // Ideally we fetch snapshot via API or wait for WS snapshot
        // For simplicity, let's just use WS

        // Connect WS
        ws.current = new WebSocket(`ws://localhost:8000/api/v1/ws/${symbol}`);

        ws.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'snapshot') {
                setBids(message.data.bids);
                setAsks(message.data.asks);
            } else if (message.type === 'orderbook') {
                // Full update or delta? Backend sends full depth snapshot currently
                setBids(message.data.bids);
                setAsks(message.data.asks);
            }
        };

        return () => {
            if (ws.current) ws.current.close();
        };
    }, [symbol]);

    // Render max 10 rows
    const renderRow = (item, type) => {
        // Calculate width relative to max quantity? 
        // For now simple table
        return (
            <div key={item.price} className="flex justify-between text-sm py-1 font-mono">
                <span className={type === 'bid' ? 'text-success' : 'text-danger'}>
                    {item.price.toFixed(2)}
                </span>
                <span className="text-muted">{item.qty}</span>
            </div>
        );
    };

    return (
        <div className="card h-full">
            <h3 className="text-lg mb-4">Order Book <span className="text-muted text-sm">({symbol})</span></h3>

            <div className="flex gap-md">
                <div className="flex-1">
                    <h4 className="text-sm text-muted mb-2 text-center">Bids (Buy)</h4>
                    <div className="flex flex-col">
                        {bids.length === 0 && <div className="text-center text-muted text-sm py-4">No Bids</div>}
                        {bids.map(b => renderRow(b, 'bid'))}
                    </div>
                </div>

                <div className="flex-1">
                    <h4 className="text-sm text-muted mb-2 text-center">Asks (Sell)</h4>
                    <div className="flex flex-col">
                        {asks.length === 0 && <div className="text-center text-muted text-sm py-4">No Asks</div>}
                        {asks.map(a => renderRow(a, 'ask'))}
                    </div>
                </div>
            </div>
        </div>
    );
}
