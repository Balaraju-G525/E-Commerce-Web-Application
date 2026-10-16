import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, money } from "../api.js";
import CartItem from "../components/CartItem.jsx";
import Message from "../components/Message.jsx";
import { useCart } from "../context/CartContext.jsx";

export default function Cart() {
  const { cart, refresh, update, remove } = useCart();
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const guard = (fn) => async (...args) => {
    setError("");
    try { await fn(...args); } catch (e) { setError(e.message); }
  };

  const checkout = guard(async () => {
    try {
      await api("/checkout/", { method: "POST" });
      await refresh();
      navigate("/orders");
    } catch (e) {
      await refresh(); // stock may have changed - show fresh numbers
      throw e;
    }
  });

  if (cart.items.length === 0)
    return <><h1>Your cart</h1><p>Your cart is empty. <Link to="/">Keep shopping</Link></p></>;

  return (
    <>
      <h1>Your cart</h1>
      <Message>{error}</Message>
      <table>
        <thead><tr><th>Product</th><th>Price</th><th>Qty</th><th>Subtotal</th><th /></tr></thead>
        <tbody>
          {cart.items.map((i) => (
            <CartItem key={i.product_id} item={i} onUpdate={guard(update)} onRemove={guard(remove)} />
          ))}
          <tr className="total"><td colSpan="3">Total</td><td colSpan="2">{money(cart.total)}</td></tr>
        </tbody>
      </table>
      <button className="btn" onClick={checkout}>Place order</button>
    </>
  );
}
