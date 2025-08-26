import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import styles from './PageUnderConstruction.module.css';

const SairPage: React.FC = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  useEffect(() => {
    const performLogout = async () => {
      await logout();
      navigate('/');
    };

    performLogout();
  }, [logout, navigate]);

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Saindo...</h1>
      <p className={styles.message}>
        Você será redirecionado para a página inicial.
      </p>
    </div>
  );
};

export default SairPage;