$commandHelperCommands = @(
    'update'
    'import-localized'
    'extract'
    'apply'
    'merge'
    'override'
    'pack'
    'pack-riviera'
    'godmode-extract'
    'godmode-override'
    'godmode-apply'
    'godmode-pack'
)

function tswloc {
    python (Join-Path $PSScriptRoot '..\command_helper.py') @args
}

Set-Alias -Name tl -Value tswloc

Register-ArgumentCompleter -CommandName tswloc, tl -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $commandHelperCommands |
        Where-Object { $_ -like "$wordToComplete*" } |
        ForEach-Object {
            [System.Management.Automation.CompletionResult]::new(
                $_, $_, 'ParameterName', $_
            )
        }
}

Register-ArgumentCompleter -CommandName python, py -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $elements = @($commandAst.CommandElements | ForEach-Object { $_.Extent.Text.Trim('"') })
    $helperIndex = for ($index = 0; $index -lt $elements.Count; $index++) {
        if ((Split-Path -Leaf $elements[$index]) -eq 'command_helper.py') {
            $index
            break
        }
    }
    if ($null -eq $helperIndex) {
        return
    }

    $arguments = if ($helperIndex -ge 0) {
        @($elements | Select-Object -Skip ($helperIndex + 1))
    } else {
        @()
    }

    if ($arguments.Count -eq 0 -or ($arguments.Count -eq 1 -and $wordToComplete -ne '')) {
        $commandHelperCommands |
            Where-Object { $_ -like "$wordToComplete*" } |
            ForEach-Object {
                [System.Management.Automation.CompletionResult]::new(
                    $_, $_, 'ParameterName', $_
                )
            }
        return
    }

    $command = $arguments[0]
    if ($command -notin @('update', 'import-localized')) {
        return
    }

    $filePrefix = Split-Path -Leaf $wordToComplete
    $pathPrefix = if ($wordToComplete -match '^[.][\\/]') { '.\' } else { '' }
    Get-ChildItem -Path . -Filter '*.pak' -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "$filePrefix*" } |
        ForEach-Object {
            $completionText = $pathPrefix + $_.Name
            [System.Management.Automation.CompletionResult]::new(
                ('"' + $completionText + '"'), $_.Name, 'ParameterValue', $_.FullName
            )
        }
}

Write-Host 'Command helper PowerShell completion registered for this session.'
