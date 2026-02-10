import { useEffect, useState, useRef } from "react";

export default function Ticker({ symbol }) {
    const [price, setPrice] = useState(null);
    const [prevPrice, setPrevPrice] = useState(null);
    const ws = useRef(null);

    useEffect(() => {
        ws.current = new WebSocket(`ws://localhost:8000/api/v1/ws/${symbol}`);

        ws.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'trade') {
                setPrevPrice(price);
                setPrice(message.data.price);
            }
        };

        return () => {
            if (ws.current) ws.current.close();
        };
    }, [symbol]);

    const getColor = () => {
        if (!prevPrice || !price) return 'text-primary';
        if (price > prevPrice) return 'text-success';
        if (price < prevPrice) return 'text-danger';
        return 'text-primary';
    };

    return (
        <div className="card flex items-center justify-between">
            <div>
                <h2 className="text-xl font-bold">{symbol} / USD</h2>
                <div className="text-sm text-muted">Real-time Price</div>
            </div>
            <div className={`text-3xl font-mono font-bold ${getColor()}`}>
                {price ? `$${price.toFixed(2)}` : 'Loading...'}
            </div>
        </div>
    );
}
