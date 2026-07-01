[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }

$loginJson = '{"correo":"antonio@bytered.es","contrasena":"admin1234A"}'
$loginFile = [System.IO.Path]::GetTempFileName()
Set-Content -Path $loginFile -Value $loginJson -Encoding ASCII
$loginResult = curl.exe -s -X POST "https://byteredapp.onrender.com/api/v1/auth/login" -H "Content-Type: application/json" -d "@${loginFile}"
Remove-Item -Path $loginFile
$token = ($loginResult | ConvertFrom-Json).access_token

$tareas = Get-Content "tareas.json" | ConvertFrom-Json
$i = 0
foreach ($t in $tareas) {
    $i++
    $jsonTarea = $t | ConvertTo-Json
    $tmpFile = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $tmpFile -Value $jsonTarea -Encoding ASCII
    $result = curl.exe -s -X POST "https://byteredapp.onrender.com/api/v1/scrum/tareas" -H "Content-Type: application/json" -H "Authorization: Bearer $token" -d "@${tmpFile}"
    Remove-Item -Path $tmpFile
    Write-Host "$i. $($t.titulo) -> $result"
}
