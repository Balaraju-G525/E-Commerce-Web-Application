export default function Message({ type = "error", children }) {
  if (!children) return null;
  return <div className={`flash ${type}`}>{children}</div>;
}
