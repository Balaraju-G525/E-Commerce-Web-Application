import { useEffect, useState } from "react";
import { api } from "../api.js";
import ProductCard from "../components/ProductCard.jsx";
import Message from "../components/Message.jsx";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [q, setQ] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      api(`/products/?q=${encodeURIComponent(q)}`)
        .then((d) => { setProducts(d.products); setError(""); })
        .catch((e) => setError(e.message));
    }, 250); // debounce typing
    return () => clearTimeout(timer);
  }, [q]);

  return (
    <>
      <input className="search" placeholder="Search products…" value={q}
             onChange={(e) => setQ(e.target.value)} />
      <Message>{error}</Message>
      <div className="grid">
        {products.map((p) => <ProductCard key={p.id} product={p} />)}
      </div>
      {products.length === 0 && !error && <p>No products found.</p>}
    </>
  );
}
