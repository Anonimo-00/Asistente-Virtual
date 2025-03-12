# update_repo.ps1

# Cambia el directorio al de tu proyecto
Set-Location "D:\App´s\Asistente Virtual"

# Añade todos los cambios al área de preparación
git add .

# Verifica si hay cambios pendientes de commit
$status = git status --porcelain
if ($status -ne "") {
    # Crea un mensaje de commit con la fecha y hora actual
    $commitMessage = "Auto commit: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    git commit -m $commitMessage
    # Envía los cambios al repositorio remoto en la rama "main"
    git push origin main
} else {
    Write-Host "No hay cambios para commitear."
}
