import React, { useState } from 'react';
import styled from 'styled-components';
import { User, Mail, Phone, MapPin, CreditCard, ArrowRight, ArrowLeft, CheckCircle, Lock } from 'lucide-react';
import MercadoPagoCheckout from '../MercadoPagoCheckout/MercadoPagoCheckout';

// Interfaces
interface CustomerData {
  name: string;
  email: string;
  phone: string;
  cpf: string;
  zipCode: string;
  city: string;
  state: string;
}

interface Course {
  id: string;
  name: string;
  description: string;
  price: number;
}

interface TwoStepCheckoutProps {
  courseId: string;
  course: Course;
  onSuccess?: (paymentData: any) => void;
  onError?: (error: string) => void;
}

// Styled Components
const CheckoutContainer = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  max-width: 600px;
  margin: 0 auto;
`;

const StepIndicator = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
`;

const Step = styled.div<{ $active: boolean; $completed: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-weight: 600;
  transition: all 0.3s ease;
  
  ${props => {
    if (props.$completed) {
      return `
        background: #4caf50;
        color: white;
        border: 2px solid #4caf50;
      `;
    } else if (props.$active) {
      return `
        background: #2196f3;
        color: white;
        border: 2px solid #2196f3;
      `;
    } else {
      return `
        background: rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.6);
        border: 2px solid rgba(255, 255, 255, 0.2);
      `;
    }
  }}
`;

const StepConnector = styled.div<{ $completed: boolean }>`
  width: 60px;
  height: 2px;
  background: ${props => props.$completed ? '#4caf50' : 'rgba(255, 255, 255, 0.2)'};
  transition: all 0.3s ease;
`;

const StepTitle = styled.h2`
  text-align: center;
  color: #ffffff;
  margin-bottom: 2rem;
  font-size: 1.5rem;
`;

const FormContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
`;

const Input = styled.input<{ $hasError?: boolean }>`
  padding: 0.75rem 1rem;
  border: 2px solid ${props => props.$hasError ? '#f44336' : 'rgba(255, 255, 255, 0.2)'};
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-size: 1rem;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #2196f3;
    background: rgba(255, 255, 255, 0.1);
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const Select = styled.select<{ $hasError?: boolean }>`
  padding: 0.75rem 1rem;
  border: 2px solid ${props => props.$hasError ? '#f44336' : 'rgba(255, 255, 255, 0.2)'};
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-size: 1rem;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #2196f3;
    background: rgba(255, 255, 255, 0.1);
  }
  
  option {
    background: #1a1a2e;
    color: #ffffff;
  }
`;

const ErrorMessage = styled.span`
  color: #f44336;
  font-size: 0.8rem;
  margin-top: 0.25rem;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  gap: 1rem;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  ${props => props.variant === 'secondary' ? `
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.8);
    
    &:hover {
      background: rgba(255, 255, 255, 0.2);
    }
  ` : `
    background: linear-gradient(135deg, #2196f3, #00bcd4);
    color: white;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3);
    }
  `}
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const PaymentContainer = styled.div`
  margin-top: 1rem;
`;

const CustomerSummary = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const SummaryTitle = styled.h3`
  color: #ffffff;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const SummaryItem = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  
  .label {
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.9rem;
  }
  
  .value {
    color: #ffffff;
    font-weight: 500;
    font-size: 0.9rem;
  }
`;

/**
 * Componente de checkout em duas etapas
 * Etapa 1: Captura dados do comprador
 * Etapa 2: Processa pagamento com Mercado Pago
 */
const TwoStepCheckout: React.FC<TwoStepCheckoutProps> = ({
  courseId,
  course,
  onSuccess,
  onError
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [customerData, setCustomerData] = useState<CustomerData>({
    name: '',
    email: '',
    phone: '',
    cpf: '',
    zipCode: '',
    city: '',
    state: ''
  });
  const [errors, setErrors] = useState<Partial<CustomerData>>({});
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Lista de estados brasileiros
   */
  const brazilianStates = [
    { value: '', label: 'Selecione o estado' },
    { value: 'AC', label: 'Acre' },
    { value: 'AL', label: 'Alagoas' },
    { value: 'AP', label: 'Amapá' },
    { value: 'AM', label: 'Amazonas' },
    { value: 'BA', label: 'Bahia' },
    { value: 'CE', label: 'Ceará' },
    { value: 'DF', label: 'Distrito Federal' },
    { value: 'ES', label: 'Espírito Santo' },
    { value: 'GO', label: 'Goiás' },
    { value: 'MA', label: 'Maranhão' },
    { value: 'MT', label: 'Mato Grosso' },
    { value: 'MS', label: 'Mato Grosso do Sul' },
    { value: 'MG', label: 'Minas Gerais' },
    { value: 'PA', label: 'Pará' },
    { value: 'PB', label: 'Paraíba' },
    { value: 'PR', label: 'Paraná' },
    { value: 'PE', label: 'Pernambuco' },
    { value: 'PI', label: 'Piauí' },
    { value: 'RJ', label: 'Rio de Janeiro' },
    { value: 'RN', label: 'Rio Grande do Norte' },
    { value: 'RS', label: 'Rio Grande do Sul' },
    { value: 'RO', label: 'Rondônia' },
    { value: 'RR', label: 'Roraima' },
    { value: 'SC', label: 'Santa Catarina' },
    { value: 'SP', label: 'São Paulo' },
    { value: 'SE', label: 'Sergipe' },
    { value: 'TO', label: 'Tocantins' }
  ];

  /**
   * Valida os dados do formulário
   */
  const validateForm = (): boolean => {
    const newErrors: Partial<CustomerData> = {};

    if (!customerData.name.trim()) {
      newErrors.name = 'Nome é obrigatório';
    }

    if (!customerData.email.trim()) {
      newErrors.email = 'E-mail é obrigatório';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerData.email)) {
      newErrors.email = 'E-mail inválido';
    }

    if (!customerData.phone.trim()) {
      newErrors.phone = 'Telefone é obrigatório';
    }

    if (!customerData.cpf.trim()) {
      newErrors.cpf = 'CPF é obrigatório';
    }

    if (!customerData.zipCode.trim()) {
      newErrors.zipCode = 'CEP é obrigatório';
    }

    if (!customerData.city.trim()) {
      newErrors.city = 'Cidade é obrigatória';
    }

    if (!customerData.state.trim()) {
      newErrors.state = 'Estado é obrigatório';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Atualiza os dados do cliente
   */
  const handleInputChange = (field: keyof CustomerData, value: string) => {
    setCustomerData(prev => ({ ...prev, [field]: value }));
    
    // Limpar erro do campo quando o usuário começar a digitar
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  /**
   * Formatar CPF
   */
  const formatCPF = (value: string) => {
    const numbers = value.replace(/\D/g, '');
    return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  /**
   * Formatar telefone
   */
  const formatPhone = (value: string) => {
    const numbers = value.replace(/\D/g, '');
    if (numbers.length <= 10) {
      return numbers.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return numbers.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  };

  /**
   * Formatar CEP
   */
  const formatZipCode = (value: string) => {
    const numbers = value.replace(/\D/g, '');
    return numbers.replace(/(\d{5})(\d{3})/, '$1-$2');
  };

  /**
   * Salva dados do cliente no CRM e avança para a próxima etapa
   */
  const handleNextStep = async () => {
    if (validateForm()) {
      setIsLoading(true);
      
      try {
        // Salvar dados do cliente no CRM
        const response = await fetch('/api/customers/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: customerData.email,
            firstName: customerData.name.split(' ')[0],
            lastName: customerData.name.split(' ').slice(1).join(' '),
            phone: customerData.phone,
            identification: {
              type: 'CPF',
              number: customerData.cpf
            },
            address: {
              zip_code: customerData.zipCode,
              city: customerData.city,
              state: customerData.state
            },
            courseId: courseId,
            courseName: course.name,
            coursePrice: course.price,
            paymentMethod: 'pending',
            source: 'two_step_checkout'
          })
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log('✅ Dados salvos no CRM:', result);
          setCurrentStep(2);
        } else {
          console.warn('⚠️ Erro ao salvar no CRM, mas continuando checkout');
          setCurrentStep(2); // Continuar mesmo se falhar
        }
      } catch (error) {
        console.warn('⚠️ Erro na comunicação com CRM:', error);
        setCurrentStep(2); // Continuar mesmo se falhar
      } finally {
        setIsLoading(false);
      }
    }
  };

  /**
   * Volta para a etapa anterior
   */
  const handlePreviousStep = () => {
    setCurrentStep(1);
  };

  /**
   * Manipula sucesso do pagamento
   */
  const handlePaymentSuccess = async (paymentData: any) => {
    console.log('✅ Pagamento realizado com sucesso:', paymentData);
    console.log('👤 Dados do cliente:', customerData);
    
    try {
      // Atualizar status no CRM para 'customer' (compra confirmada)
      const response = await fetch('/api/customers/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: customerData.email,
          firstName: customerData.name.split(' ')[0],
          lastName: customerData.name.split(' ').slice(1).join(' '),
          phone: customerData.phone,
          identification: {
            type: 'CPF',
            number: customerData.cpf
          },
          address: {
            zip_code: customerData.zipCode,
            city: customerData.city,
            state: customerData.state
          },
          courseId: courseId,
          courseName: course.name,
          coursePrice: course.price,
          paymentMethod: paymentData.payment_method || 'mercado_pago',
          status: 'customer', // Status atualizado para cliente
          paymentId: paymentData.payment_id,
          source: 'two_step_checkout_completed'
        })
      });
      
      if (response.ok) {
        console.log('✅ Status atualizado no CRM para cliente');
      }
    } catch (error) {
      console.warn('⚠️ Erro ao atualizar status no CRM:', error);
    }
    
    if (onSuccess) {
      onSuccess({
        ...paymentData,
        customer: customerData
      });
    }
  };

  /**
   * Manipula erro do pagamento
   */
  const handlePaymentError = (error: string) => {
    console.error('❌ Erro no pagamento:', error);
    
    if (onError) {
      onError(error);
    }
  };

  return (
    <CheckoutContainer>
      {/* Indicador de Etapas */}
      <StepIndicator>
        <Step $active={currentStep === 1} $completed={currentStep > 1}>
          {currentStep > 1 ? <CheckCircle size={20} /> : '1'}
        </Step>
        <StepConnector $completed={currentStep > 1} />
        <Step $active={currentStep === 2} $completed={false}>
          {currentStep === 2 ? <CreditCard size={20} /> : '2'}
        </Step>
      </StepIndicator>

      {/* Etapa 1: Dados do Cliente */}
      {currentStep === 1 && (
        <>
          <StepTitle>
            <User size={24} style={{ marginRight: '0.5rem' }} />
            Seus Dados Pessoais
          </StepTitle>
          
          <FormContainer>
            {/* Nome Completo */}
            <FormGroup>
              <Label>
                <User size={16} />
                Nome Completo *
              </Label>
              <Input
                type="text"
                placeholder="Digite seu nome completo"
                value={customerData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                $hasError={!!errors.name}
              />
              {errors.name && <ErrorMessage>{errors.name}</ErrorMessage>}
            </FormGroup>

            {/* E-mail e Telefone */}
            <FormRow>
              <FormGroup>
                <Label>
                  <Mail size={16} />
                  E-mail *
                </Label>
                <Input
                  type="email"
                  placeholder="seu@email.com"
                  value={customerData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  $hasError={!!errors.email}
                />
                {errors.email && <ErrorMessage>{errors.email}</ErrorMessage>}
              </FormGroup>

              <FormGroup>
                <Label>
                  <Phone size={16} />
                  Telefone *
                </Label>
                <Input
                  type="tel"
                  placeholder="(11) 99999-9999"
                  value={customerData.phone}
                  onChange={(e) => handleInputChange('phone', formatPhone(e.target.value))}
                  $hasError={!!errors.phone}
                  maxLength={15}
                />
                {errors.phone && <ErrorMessage>{errors.phone}</ErrorMessage>}
              </FormGroup>
            </FormRow>

            {/* CPF */}
            <FormGroup>
              <Label>
                <User size={16} />
                CPF *
              </Label>
              <Input
                type="text"
                placeholder="000.000.000-00"
                value={customerData.cpf}
                onChange={(e) => handleInputChange('cpf', formatCPF(e.target.value))}
                $hasError={!!errors.cpf}
                maxLength={14}
              />
              {errors.cpf && <ErrorMessage>{errors.cpf}</ErrorMessage>}
            </FormGroup>

            {/* CEP e Cidade */}
            <FormRow>
              <FormGroup>
                <Label>
                  <MapPin size={16} />
                  CEP *
                </Label>
                <Input
                  type="text"
                  placeholder="00000-000"
                  value={customerData.zipCode}
                  onChange={(e) => handleInputChange('zipCode', formatZipCode(e.target.value))}
                  $hasError={!!errors.zipCode}
                  maxLength={9}
                />
                {errors.zipCode && <ErrorMessage>{errors.zipCode}</ErrorMessage>}
              </FormGroup>

              <FormGroup>
                <Label>
                  <MapPin size={16} />
                  Cidade *
                </Label>
                <Input
                  type="text"
                  placeholder="Digite sua cidade"
                  value={customerData.city}
                  onChange={(e) => handleInputChange('city', e.target.value)}
                  $hasError={!!errors.city}
                />
                {errors.city && <ErrorMessage>{errors.city}</ErrorMessage>}
              </FormGroup>
            </FormRow>

            {/* Estado */}
            <FormGroup>
              <Label>
                <MapPin size={16} />
                Estado *
              </Label>
              <Select
                value={customerData.state}
                onChange={(e) => handleInputChange('state', e.target.value)}
                $hasError={!!errors.state}
              >
                {brazilianStates.map(state => (
                  <option key={state.value} value={state.value}>
                    {state.label}
                  </option>
                ))}
              </Select>
              {errors.state && <ErrorMessage>{errors.state}</ErrorMessage>}
            </FormGroup>
          </FormContainer>

          <ButtonContainer>
            <div></div>
            <Button onClick={handleNextStep} disabled={isLoading}>
              {isLoading ? 'Salvando dados...' : 'Continuar para Pagamento'}
              {isLoading ? null : <ArrowRight size={20} />}
            </Button>
          </ButtonContainer>
        </>
      )}

      {/* Etapa 2: Pagamento */}
      {currentStep === 2 && (
        <>
          <StepTitle>
            <CreditCard size={24} style={{ marginRight: '0.5rem' }} />
            Finalizar Pagamento
          </StepTitle>

          {/* Resumo dos Dados do Cliente */}
          <CustomerSummary>
            <SummaryTitle>
              <CheckCircle size={20} />
              Dados Confirmados
            </SummaryTitle>
            <SummaryItem>
              <span className="label">Nome:</span>
              <span className="value">{customerData.name}</span>
            </SummaryItem>
            <SummaryItem>
              <span className="label">E-mail:</span>
              <span className="value">{customerData.email}</span>
            </SummaryItem>
            <SummaryItem>
              <span className="label">Telefone:</span>
              <span className="value">{customerData.phone}</span>
            </SummaryItem>
            <SummaryItem>
              <span className="label">Localização:</span>
              <span className="value">{customerData.city}, {customerData.state}</span>
            </SummaryItem>
          </CustomerSummary>

          {/* Componente de Pagamento */}
          <PaymentContainer>
            <MercadoPagoCheckout
              courseId={courseId}
              course={course}
              customerData={customerData}
              onSuccess={handlePaymentSuccess}
              onError={handlePaymentError}
            />
          </PaymentContainer>

          <ButtonContainer>
            <Button variant="secondary" onClick={handlePreviousStep}>
              <ArrowLeft size={20} />
              Voltar
            </Button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'rgba(255, 255, 255, 0.7)' }}>
              <Lock size={16} />
              <span style={{ fontSize: '0.9rem' }}>Pagamento 100% seguro</span>
            </div>
          </ButtonContainer>
        </>
      )}
    </CheckoutContainer>
  );
};

export default TwoStepCheckout;