import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './LoginPage.module.css';
import logo from '../assets/logo.png';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import NavigationFix from '../utils/navigationFix';

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isAuthenticated, loading } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const hasNavigated = useRef(false);

  useEffect(() => {
    // Aguardar o carregamento inicial terminar
    if (loading) {
      console.log('⏳ Login: Aguardando carregamento da autenticação...');
      return;
    }

    // Evitar múltiplas navegações
    if (isAuthenticated && !hasNavigated.current && !NavigationFix.isNavigating()) {
      console.log('🔄 Login: Usuário já autenticado, redirecionando...');
      hasNavigated.current = true;
      
      NavigationFix.debounceNavigation(() => {
        NavigationFix.safeNavigate(navigate, '/dashboard', { replace: true });
      }, 300);
    }
  }, [isAuthenticated, loading, navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    hasNavigated.current = false;

    try {
      const result = await login(email, password);
      if (result.success) {
        console.log('🎯 Login: Login bem-sucedido, aguardando redirecionamento automático...');
        // Não navegar aqui - deixar o useEffect handle
        // O AuthContext já atualizou isAuthenticated
      } else {
        console.error('❌ Login: Falha -', result.error);
        setError(result.error || 'Email ou senha incorretos. Por favor, tente novamente.');
      }
    } catch (error) {
      console.error('❌ Login: Erro inesperado:', error);
      setError('Erro inesperado. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
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