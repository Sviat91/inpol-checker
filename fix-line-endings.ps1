$content = Get-Content docker-entrypoint -Raw
$content = $content -replace "`r`n", "`n"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("$PSScriptRoot\docker-entrypoint", $content, $utf8NoBom)
Write-Host "Fixed line endings in docker-entrypoint (CRLF -> LF)"
