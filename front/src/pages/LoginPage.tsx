import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './LoginPage.module.css';
import logo from '../assets/logo.png';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      console.log('🔄 Login: Usuário já autenticado, redirecionando...');
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const result = await login(email, password);
    if (result.success) {
      console.log('🎯 Login: Redirecionando para dashboard...');
      navigate('/dashboard', { replace: true });
    } else {
      console.error('❌ Login: Falha -', result.error);
      setError(result.error || 'Email ou senha incorretos. Por favor, tente novamente.');
    }
    setIsLoading(false);
  };

  const handleInputChange = (setter: React.Dispatch<React.SetStateAction<string>>) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setter(e.target.value);
    if (error) setError(null);
  };

  return (
    <div className={styles.loginPageContainer}>
      <div className={styles.loginCard}>
        <div className={styles.logoSection}>
          <Link to="/">
            <img src={logo} alt="CrypTen Logo" className={styles.crypTenLogo} />
          </Link>
        </div>
        <h2>Vamos Começar</h2>
        <p>Insira os seus dados para continuar</p>

        <form onSubmit={handleLogin}>
          <div className={styles.formGroup}>
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              placeholder="seuemail@exemplo.com"
              value={email}
              onChange={handleInputChange(setEmail)}
              autoComplete="username"
              disabled={isLoading}
              required
            />
          </div>
          <div className={styles.formGroup}>
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              placeholder="********"
              value={password}
              onChange={handleInputChange(setPassword)}
              autoComplete="current-password"
              disabled={isLoading}
              required
            />
          </div>
          {error && <p className={styles.errorMessage}>{error}</p>}
          <button type="submit" className={styles.loginButton} disabled={isLoading}>
            {isLoading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
        <p className={styles.registerLink}>
          Não tem uma conta? <Link to="/register">Crie sua conta aqui</Link>
        </p>
        <p className={styles.forgotPasswordLink}>
          <Link to="/forgot-password">Esqueceu sua senha?</Link>
        </p>
        <div className={styles.policyLinks}>
          <p>Ao usar este serviço, você concorda com nossos</p>
          <p>
            <Link to="/terms-of-service">Termos de Serviço</Link> e <Link to="/privacy-policy">Política de Privacidade</Link>.
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;