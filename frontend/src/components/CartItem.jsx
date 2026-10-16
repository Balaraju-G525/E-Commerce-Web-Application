import { money } from "../api.js";

export default function CartItem({ item, onUpdate, onRemove }) {
  return (
    <tr>
      <td>{item.name}</td>
      <td>{money(item.price)}</td>
      <td>
        <input className="qty" type="number" min="0" max={item.stock} defaultValue={item.quantity}
               onBlur={(e) => Number(e.target.value) !== item.quantity &&
                              onUpdate(item.product_id, Number(e.target.value))} />
      </td>
      <td>{money(item.line_total)}</td>
      <td><button className="link" onClick={() => onRemove(item.product_id)}>Remove</button></td>
    </tr>
  );
}
