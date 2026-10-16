import AuthForm from "../components/AuthForm.jsx";
import { useAuth } from "../context/AuthContext.jsx";

export default function Register() {
  const { register } = useAuth();
  return <AuthForm title="Create account" submitLabel="Register" onSubmit={register}
                   altText="Already registered?" altLink="/login" altLabel="Log in" />;
}
