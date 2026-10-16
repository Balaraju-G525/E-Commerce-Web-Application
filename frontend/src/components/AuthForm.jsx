import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Message from "./Message.jsx";

// Reused by both the Login and Register pages
export default function AuthForm({ title, submitLabel, onSubmit, altText, altLink, altLabel }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await onSubmit(email, password);
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form className="auth" onSubmit={handleSubmit}>
      <h1>{title}</h1>
      <Message>{error}</Message>
      <label>Email
        <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
      </label>
      <label>Password
        <input type="password" required minLength={8} value={password}
               onChange={(e) => setPassword(e.target.value)} />
      </label>
      <button className="btn">{submitLabel}</button>
      <p className="muted">{altText} <Link to={altLink}>{altLabel}</Link></p>
    </form>
  );
}
