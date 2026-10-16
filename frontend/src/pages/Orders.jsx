import { useEffect, useState } from "react";
import { api, money } from "../api.js";
import Message from "../components/Message.jsx";

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/orders/").then((d) => setOrders(d.orders)).catch((e) => setError(e.message));
  }, []);

  return (
    <>
      <h1>Your orders</h1>
      <Message>{error}</Message>
      {orders.length === 0 && !error && <p>No orders yet.</p>}
      {orders.map((o) => (
        <section className="card" key={o.id}>
          <h3>Order #{o.id} — {money(o.total)}{" "}
            <span className="muted">{new Date(o.created_at).toLocaleString()}</span></h3>
          <ul>{o.items.map((it, idx) => (
            <li key={idx}>{it.quantity} × {it.name} @ {money(it.unit_price)}</li>
          ))}</ul>
        </section>
      ))}
    </>
  );
}
