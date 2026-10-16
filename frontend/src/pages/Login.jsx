import AuthForm from "../components/AuthForm.jsx";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const { login } = useAuth();
  return <AuthForm title="Log in" submitLabel="Log in" onSubmit={login}
                   altText="No account?" altLink="/register" altLabel="Register" />;
}
