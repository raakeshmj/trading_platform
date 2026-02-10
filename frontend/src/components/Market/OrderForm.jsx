import { useState } from "react";
import { api } from "../../services/api";

export default function OrderForm({ symbol, onOrderPlaced }) {
    const [side, setSide] = useState('BUY');
    const [type, setType] = useState('LIMIT');
    const [price, setPrice] = useState('');
    const [quantity, setQuantity] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await api.orders.create({
                instrument_symbol: symbol,
                side,
                type,
                quantity: parseInt(quantity),
                price: type === 'LIMIT' ? parseFloat(price) : null
            });
            alert('Order Placed');
            setQuantity('');
            setPrice('');
            if (onOrderPlaced) onOrderPlaced();
        } catch (err) {
            alert(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="card">
            <h3 className="text-lg mb-4">Place Order</h3>

            <div className="flex bg-surface-highlight rounded-md p-1 mb-4">
                <button
                    className={`flex-1 py-1 text-sm rounded-sm font-medium transition-colors ${side === 'BUY' ? 'bg-success text-white' : 'text-muted hover:text-primary'}`}
                    onClick={() => setSide('BUY')}
                >
                    Buy
                </button>
                <button
                    className={`flex-1 py-1 text-sm rounded-sm font-medium transition-colors ${side === 'SELL' ? 'bg-danger text-white' : 'text-muted hover:text-primary'}`}
                    onClick={() => setSide('SELL')}
                >
                    Sell
                </button>
            </div>

            <form onSubmit={handleSubmit} className="flex flex-col gap-md">
                <div className="flex gap-sm">
                    <button
                        type="button"
                        className={`btn btn-sm flex-1 ${type === 'LIMIT' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setType('LIMIT')}
                    >
                        Limit
                    </button>
                    <button
                        type="button"
                        className={`btn btn-sm flex-1 ${type === 'MARKET' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setType('MARKET')}
                    >
                        Market
                    </button>
                </div>

                {type === 'LIMIT' && (
                    <div>
                        <label className="label">Price</label>
                        <input
                            className="input font-mono"
                            type="number"
                            step="0.01"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            required
                        />
                    </div>
                )}

                <div>
                    <label className="label">Quantity</label>
                    <input
                        className="input font-mono"
                        type="number"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        required
                    />
                </div>

                <button
                    type="submit"
                    className={`btn btn-block ${side === 'BUY' ? 'btn-success' : 'btn-danger'}`}
                    disabled={isLoading}
                >
                    {isLoading ? 'Processing...' : `${side} ${symbol}`}
                </button>
            </form>
        </div>
    );
}
