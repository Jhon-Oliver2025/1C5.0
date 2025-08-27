
// Exemplo de como usar o novo AuthContext na página de login
// Adicionar ao componente de Login

import { useAuth } from '../context/AuthContext';
import { useState } from 'react';

const LoginPage = () => {
  const { login, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLogging, setIsLogging] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLogging(true);

    try {
      const result = await login(email, password);
      
      if (result.success) {
        console.log('✅ Login realizado com sucesso!');
        // Redirecionar para dashboard ou página principal
        // navigate('/dashboard');
      } else {
        setError(result.error || 'Erro no login');
        console.error('❌ Erro no login:', result.error);
      }
    } catch (err) {
      setError('Erro de conexão');
      console.error('❌ Erro de conexão:', err);
    } finally {
      setIsLogging(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
        disabled={isLogging}
      />
      
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Senha"
        required
        disabled={isLogging}
      />
      
      <button type="submit" disabled={isLogging || loading}>
        {isLogging ? 'Entrando...' : 'Entrar'}
      </button>
    </form>
  );
};

export default LoginPage;
