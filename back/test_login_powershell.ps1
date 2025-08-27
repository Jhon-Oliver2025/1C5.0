# Script PowerShell para testar login
# Função para testar o login com credenciais do Supabase

Write-Host "Iniciando teste de login via PowerShell..."

# Definir dados da requisição
$uri = "http://localhost:5000/api/auth/login"
$headers = @{
    "Content-Type" = "application/json"
}
$body = @{
    email = "jonatasprojetos2013@gmail.com"
    password = "admin123"
} | ConvertTo-Json

Write-Host "URI: $uri"
Write-Host "Body: $body"

try {
    # Fazer a requisição POST
    $response = Invoke-WebRequest -Uri $uri -Method POST -Headers $headers -Body $body -UseBasicParsing
    
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response Content:"
    Write-Host $response.Content
    
} catch {
    Write-Host "Erro na requisição:"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error Message: $($_.Exception.Message)"
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody"
    }
}

Write-Host "Teste concluído."