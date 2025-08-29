import React, { useState } from 'react';
import styled from 'styled-components';
import { checkDeviceSupport } from '../../utils/pwaChecker';

/**
 * Componente que mostra instruções visuais de instalação do PWA
 * Específico para cada plataforma (Android, iOS, Desktop)
 */
const PWAInstallInstructions: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const deviceSupport = checkDeviceSupport();

  /**
   * Renderiza instruções específicas para Android
   */
  const renderAndroidInstructions = () => (
    <InstructionsContent>
      <InstructionTitle>📱 Como Instalar no Android</InstructionTitle>
      
      <StepsList>
        <Step>
          <StepNumber>1</StepNumber>
          <StepContent>
            <StepTitle>Abra o Menu do Navegador</StepTitle>
            <StepDescription>
              Toque nos três pontos (⋮) no canto superior direito do Chrome
            </StepDescription>
          </StepContent>
        </Step>
        
        <Step>
          <StepNumber>2</StepNumber>
          <StepContent>
            <StepTitle>Encontre "Adicionar à tela inicial"</StepTitle>
            <StepDescription>
              Role o menu e procure por "Adicionar à tela inicial" ou "Instalar app"
            </StepDescription>
          </StepContent>
        </Step>
        
        <Step>
          <StepNumber>3</StepNumber>
          <StepContent>
            <StepTitle>Confirme a Instalação</StepTitle>
            <StepDescription>
              Toque em "Adicionar" ou "Instalar" para confirmar
            </StepDescription>
          </StepContent>
        </Step>
        
        <Step>
          <StepNumber>4</StepNumber>
          <StepContent>
            <StepTitle>Acesse o App</StepTitle>
            <StepDescription>
              O ícone do 1Crypten aparecerá na sua tela inicial
            </StepDescription>
          </StepContent>
        </Step>
      </StepsList>
      
      <TipBox>
        <TipIcon>💡</TipIcon>
        <TipText>
          <strong>Dica:</strong> Se não aparecer a opção "Adicionar à tela inicial", 
          certifique-se de estar usando o Chrome e que o site está carregado completamente.
        </TipText>
      </TipBox>
    </InstructionsContent>
  );

  /**
   * Renderiza instruções específicas para iOS
   */
  const renderiOSInstructions = () => (
    <InstructionsContent>
      <InstructionTitle>🍎 Como Instalar no iPhone/iPad</InstructionTitle>
      
      <StepsList>
        <Step>
          <StepNumber>1</StepNumber>
          <StepContent>
            <StepTitle>Abra no Safari</StepTitle>
            <StepDescription>
              Certifique-se de estar usando o Safari (não Chrome ou outros navegadores)
            </StepDescription>
          </StepContent>
        </Step>
        
        <Step>
          <StepNumber>2</StepNumber>
          <StepContent>
            <StepTitle>Toque no Botão de Compartilhar</StepTitle>
            <StepDescription>
              Toque no ícone de compartilhar (□↗) na parte inferior da tela
            </StepDescription>
          </StepContent>
        </Step>
        
        <Step>
          <StepNumber>3</StepNumber>
          <StepContent>
            <StepTitle>Encontre "Adicionar à Tela de Início"</StepTitle>
            <StepDescription>
              Role para baixo no menu e toque em "Adicionar à Tela de Início"
            </StepDescription>
          </StepContent>
        </Step>
        
        <Step>
          <StepNumber>4</StepNumber>
          <StepContent>
            <StepTitle>Confirme a Instalação</StepTitle>
            <StepDescription>
              Toque em "Adicionar" no canto superior direito
            </StepDescription>
          </StepContent>
        </Step>
      </StepsList>
      
      <TipBox>
        <TipIcon>💡</TipIcon>
        <TipText>
          <strong>Dica:</strong> O Safari é obrigatório no iOS. 
          Se estiver usando outro navegador, copie o link e abra no Safari.
        </TipText>
      </TipBox>
    </InstructionsContent>
  );

  /**
   * Renderiza instruções específicas para Desktop
   */
  const renderDesktopInstructions = () => (
    <InstructionsContent>
      <InstructionTitle>💻 Como Instalar no Desktop</InstructionTitle>
      
      <StepsList>
        <Step>
          <StepNumber>1</StepNumber>
          <StepContent>
            <StepTitle>Procure o Ícone de Instalação</StepTitle>
            <StepDescription>
              Olhe na barra de endereços por um ícone de instalação (⊕ ou 📱)
            </StepDescription>
          </StepContent>
        </Step>
        
        <Step>
          <StepNumber>2</StepNumber>
          <StepContent>
            <StepTitle>Ou Use o Menu do Navegador</StepTitle>
            <StepDescription>
              Chrome: Menu (⋮) → "Instalar 1Crypten..."<br/>
              Edge: Menu (⋯) → "Aplicativos" → "Instalar este site como um aplicativo"
            </StepDescription>
          </StepContent>
        </Step>
        
        <Step>
          <StepNumber>3</StepNumber>
          <StepContent>
            <StepTitle>Atalho de Teclado</StepTitle>
            <StepDescription>
              Chrome: Pressione <kbd>Ctrl + Shift + A</kbd> (Windows) ou <kbd>Cmd + Shift + A</kbd> (Mac)
            </StepDescription>
          </StepContent>
        </Step>
        
        <Step>
          <StepNumber>4</StepNumber>
          <StepContent>
            <StepTitle>Confirme a Instalação</StepTitle>
            <StepDescription>
              Clique em "Instalar" na janela que aparecer
            </StepDescription>
          </StepContent>
        </Step>
      </StepsList>
      
      <TipBox>
        <TipIcon>💡</TipIcon>
        <TipText>
          <strong>Dica:</strong> Após instalar, o 1Crypten aparecerá como um aplicativo 
          separado na sua área de trabalho e menu iniciar.
        </TipText>
      </TipBox>
    </InstructionsContent>
  );

  /**
   * Renderiza as instruções baseadas na plataforma detectada
   */
  const renderInstructions = () => {
    switch (deviceSupport.platform) {
      case 'android':
        return renderAndroidInstructions();
      case 'ios':
        return renderiOSInstructions();
      default:
        return renderDesktopInstructions();
    }
  };

  if (!isVisible) {
    return (
      <ShowInstructionsButton onClick={() => setIsVisible(true)}>
        📖 Ver Instruções Detalhadas de Instalação
      </ShowInstructionsButton>
    );
  }

  return (
    <InstructionsOverlay>
      <InstructionsModal>
        <CloseButton onClick={() => setIsVisible(false)}>✕</CloseButton>
        {renderInstructions()}
        
        <ActionButtons>
          <SecondaryButton onClick={() => setIsVisible(false)}>
            Fechar
          </SecondaryButton>
          <PrimaryButton onClick={() => {
            setIsVisible(false);
            // Tentar abrir instruções do navegador
            if (deviceSupport.platform === 'android' && deviceSupport.browser === 'chrome') {
              alert('Agora toque no menu (⋮) do Chrome e procure por "Adicionar à tela inicial"');
            }
          }}>
            Entendi, Vamos Instalar!
          </PrimaryButton>
        </ActionButtons>
      </InstructionsModal>
    </InstructionsOverlay>
  );
};

// Styled Components
const ShowInstructionsButton = styled.button`
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  margin: 8px 0;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  }
`;

const InstructionsOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const InstructionsModal = styled.div`
  background: white;
  border-radius: 16px;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
`;

const CloseButton = styled.button`
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  
  &:hover {
    color: #333;
  }
`;

const InstructionsContent = styled.div`
  padding: 24px;
`;

const InstructionTitle = styled.h2`
  margin: 0 0 24px 0;
  color: #333;
  text-align: center;
  font-size: 24px;
`;

const StepsList = styled.div`
  margin-bottom: 24px;
`;

const Step = styled.div`
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
`;

const StepNumber = styled.div`
  background: linear-gradient(135deg, #646cff 0%, #747bff 100%);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 16px;
  flex-shrink: 0;
`;

const StepContent = styled.div`
  flex: 1;
`;

const StepTitle = styled.h4`
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
`;

const StepDescription = styled.p`
  margin: 0;
  color: #666;
  line-height: 1.5;
  
  kbd {
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: monospace;
    font-size: 12px;
  }
`;

const TipBox = styled.div`
  background: #f8f9ff;
  border: 1px solid #e1e5ff;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: flex-start;
  margin-bottom: 24px;
`;

const TipIcon = styled.div`
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
`;

const TipText = styled.div`
  color: #4a5568;
  line-height: 1.5;
  
  strong {
    color: #2d3748;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

const SecondaryButton = styled.button`
  background: #f7f7f7;
  color: #666;
  border: 1px solid #ddd;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #e9e9e9;
  }
`;

const PrimaryButton = styled.button`
  background: linear-gradient(135deg, #646cff 0%, #747bff 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(100, 108, 255, 0.3);
  }
`;

export default PWAInstallInstructions;