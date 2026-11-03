param(
    [ValidateSet('Build','Rebuild','Clean')][string]$Action = 'Build',
    [string]$Assembler = $env:ZMAC_EXE
)
$ErrorActionPreference = 'Stop'
$buildRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'build'))
# Only the fixed build directory inside this checkout may be removed.
if ($buildRoot -ne [IO.Path]::Combine([IO.Path]::GetFullPath($PSScriptRoot), 'build')) {
    throw 'Unexpected build directory'
}
if ($Action -in @('Clean','Rebuild') -and (Test-Path -LiteralPath $buildRoot)) {
    if ((Get-Item -LiteralPath $buildRoot).Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw 'Refusing to clean a linked build directory'
    }
    Remove-Item -LiteralPath $buildRoot -Recurse -Force
}
if ($Action -eq 'Clean') { return }
if (-not $Assembler) { $Assembler = Join-Path $PSScriptRoot 'tools/zmac.exe' }
if (-not (Test-Path -LiteralPath $Assembler)) {
    throw 'Set ZMAC_EXE to zmac.exe, pass -Assembler PATH, or place it in tools/zmac.exe. See BUILDING.txt.'
}
$Assembler = (Resolve-Path -LiteralPath $Assembler).Path
$source = Join-Path $buildRoot 'src'
$destination = Join-Path $buildRoot 'SD-CARD'
New-Item -ItemType Directory -Force -Path $source,(Join-Path $destination 'SYS') | Out-Null
# Assemble a fresh source copy so build products never modify tracked sources.
Copy-Item -Path (Join-Path $PSScriptRoot 'SYS/SRC/*.z') -Destination $source -Force
$targets = @(@('BOOT.z','lst,cim,cmd'),@('SYS0P.z','lst,cmd'),@('SYS0F.z','lst,cmd'),@('keyboard.z','lst,cmd'))
foreach ($letter in @('b','c','d','e','f','g','h','l','o')) {
    $targets += ,@("overlay$letter.z",'lst,cim')
}
Push-Location $source
try {
    foreach ($target in $targets) {
        & $Assembler --zmac --oo $target[1] $target[0]
        if ($LASTEXITCODE -ne 0) { throw "Assembly failed: $($target[0])" }
    }
    $copies = @{
        'boot.cim'='SYS/BOOT.SYS'; 'boot.cmd'='frehd.rom';
        'sys0p.cmd'='SYS/SYSP.sys'; 'sys0f.cmd'='SYS/SYS0.sys';
        'keyboard.cmd'='SYS/KEYBOARD.CMD'
    }
    foreach ($letter in @('b','c','d','e','f','g','h','l','o')) {
        $copies["overlay$letter.cim"]="SYS/overlay$letter.sys"
    }
    foreach ($entry in $copies.GetEnumerator()) {
        Copy-Item -LiteralPath (Join-Path $source "zout/$($entry.Key)") -Destination (Join-Path $destination $entry.Value)
    }
} finally { Pop-Location }
Write-Output "Built $($targets.Count) targets. SD-card binaries: $destination"
