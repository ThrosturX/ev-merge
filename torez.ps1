$ScriptDir = Split-Path $script:MyInvocation.MyCommand.Path

$Fname = $args[0]

$files = Get-ChildItem $Fname

foreach ($f in $files){
    $rezFile = (join-path $f.DirectoryName $f.BaseName) + ".rez"
    $txtFile = (join-path $f.DirectoryName $f.BaseName) + ".txt"
    echo    .\EV` Override\EVNEW.exe -totxt $rezFile $txtFile
    .\EV` Override\EVNEW.exe -totxt $rezFile $txtFile
}

echo 'done'

# .\EV` Override\EVNEW.exe -totxt $ScriptDir\$Fname.rez $ScriptDir\$Fname.txt
