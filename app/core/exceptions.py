class AppBaseError(Exception):
    """Base exception para a aplicação"""
    def __init__(self, message="Erro na aplicação", code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)

# Erros de Autenticação
class AuthenticationError(AppBaseError):
    def __init__(self, message="Falha na autenticação"):
        super().__init__(message, 401)


# Erros de Serviços Externos
class ExternalServiceError(AppBaseError):
    def __init__(self, message="Falha em serviço externo", code=503):
        super().__init__(message, code)

class LLMServiceError(ExternalServiceError):
    def __init__(self, message="Falha no serviço de IA/Language Model"):
        super().__init__(message, 503)

class SessionError(AppBaseError):
    def __init__(self, message="Erro na gestão de sessão"):
        super().__init__(message, 500)

class DatabaseError(ExternalServiceError):
    def __init__(self, message="Falha na operação com o banco de dados"):
        super().__init__(message, 503)

class CacheError(ExternalServiceError):
    def __init__(self, message="Falha na operação de cache"):
        super().__init__(message, 503)

# Erros de Validação e Dados
class ValidationError(AppBaseError):
    def __init__(self, message="Dados inválidos ou mal formatados"):
        super().__init__(message, 422)

class DataProcessingError(AppBaseError):
    def __init__(self, message="Erro no processamento de dados"):
        super().__init__(message, 422)

class DataCreationError(AppBaseError):
    def __init__(self, message="Falha na criação de dados"):
        super().__init__(message, 500)

class SerializationError(AppBaseError):
    def __init__(self, message="Erro na serialização de dados"):
        super().__init__(message, 500)

class NotFoundError(AppBaseError):
    def __init__(self, message="Recurso não encontrado"):
        super().__init__(message, 404)

# Erros de Autenticação e Autorização
class AuthenticationError(AppBaseError):
    def __init__(self, message="Falha na autenticação"):
        super().__init__(message, 401)

class PermissionDeniedError(AppBaseError):
    def __init__(self, message="Acesso não autorizado"):
        super().__init__(message, 403)

# Erros de Configuração
class ConfigurationError(AppBaseError):
    def __init__(self, message="Erro de configuração do sistema"):
        super().__init__(message, 500)

# Erros de Regras de Negócio
class BusinessRuleError(AppBaseError):
    def __init__(self, message="Violação de regra de negócio"):
        super().__init__(message, 400)

# Erros de Taxa Limite
class RateLimitExceededError(AppBaseError):
    def __init__(self, message="Limite de requisições excedido"):
        super().__init__(message, 429)

# Erros Genéricos HTTP
class ServiceUnavailableError(AppBaseError):
    def __init__(self, message="Serviço indisponível"):
        super().__init__(message, 503)

class InternalServerError(AppBaseError):
    def __init__(self, message="Erro interno no servidor"):
        super().__init__(message, 500)

class VerificationError(Exception):
    """Raised when WhatsApp webhook verification fails"""
    def __init__(self, message="Webhook verification failed"):
        self.message = message
        super().__init__(self.message)
