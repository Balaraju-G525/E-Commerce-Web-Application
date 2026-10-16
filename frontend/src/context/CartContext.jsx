import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "../api.js";
import { useAuth } from "./AuthContext.jsx";

const EMPTY = { items: [], total: "0", count: 0 };
const CartContext = createContext(null);
export const useCart = () => useContext(CartContext);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState(EMPTY);

  const refresh = useCallback(async () => {
    setCart(user ? await api("/cart/") : EMPTY);
  }, [user]);

  useEffect(() => { refresh().catch(() => setCart(EMPTY)); }, [refresh]);

  const add = async (product_id, quantity = 1) =>
    setCart(await api("/cart/", { method: "POST", body: { product_id, quantity } }));
  const update = async (product_id, quantity) =>
    setCart(await api(`/cart/${product_id}/`, { method: "PATCH", body: { quantity } }));
  const remove = async (product_id) =>
    setCart(await api(`/cart/${product_id}/`, { method: "DELETE" }));

  return (
    <CartContext.Provider value={{ cart, refresh, add, update, remove }}>
      {children}
    </CartContext.Provider>
  );
}
