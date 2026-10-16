import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { money } from "../api.js";
import { useAuth } from "../context/AuthContext.jsx";
import { useCart } from "../context/CartContext.jsx";
import Message from "./Message.jsx";

function StockBadge({ stock }) {
  if (stock === 0) return <span className="badge out">Out of stock</span>;
  if (stock <= 5) return <span className="badge low">Only {stock} left</span>;
  return <span className="badge in">In stock</span>;
}

export default function ProductCard({ product }) {
  const { user } = useAuth();
  const { add } = useCart();
  const navigate = useNavigate();
  const [qty, setQty] = useState(1);
  const [msg, setMsg] = useState({ type: "", text: "" });

  const handleAdd = async () => {
    if (!user) return navigate("/login");
    try {
      await add(product.id, qty);
      setMsg({ type: "success", text: "Added to cart." });
    } catch (e) {
      setMsg({ type: "error", text: e.message });
    }
  };

  return (
    <article className="card">
      <h3>{product.name}</h3>
      <p className="muted">{product.description}</p>
      <p className="price">{money(product.price)} <StockBadge stock={product.stock} /></p>
      <div className="row">
        <input className="qty" type="number" min="1" max={product.stock} value={qty}
               onChange={(e) => setQty(Math.max(1, Number(e.target.value) || 1))} />
        <button className="btn" disabled={product.stock === 0} onClick={handleAdd}>Add to cart</button>
      </div>
      <Message type={msg.type}>{msg.text}</Message>
    </article>
  );
}
