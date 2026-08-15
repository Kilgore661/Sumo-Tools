$ErrorActionPreference = "Stop"

$script:mathFragments = [System.Collections.Generic.List[string]]::new()

function Protect-MathFragment {
    param([System.Text.RegularExpressions.Match]$Match)

    $index = $script:mathFragments.Count
    $script:mathFragments.Add($Match.Value)
    return "MATHJAXPLACEHOLDER$($index)X"
}

function Get-DocumentTitle {
    param(
        [string]$Source,
        [string]$Fallback
    )

    $heading = [regex]::Match($Source, '(?m)^#\s+(.+?)\s*$')
    if ($heading.Success) {
        return $heading.Groups[1].Value
    }

    return $Fallback
}

function Convert-StoryDocument {
    param([System.IO.FileInfo]$SourceFile)

    $source = Get-Content -Raw -LiteralPath $SourceFile.FullName
    $script:mathFragments.Clear()

    $displayPattern = [regex]::new('(?s)\\\[.*?\\\]')
    $inlinePattern = [regex]::new('(?s)\\\(.*?\\\)')
    $protected = $displayPattern.Replace($source, { param($match) Protect-MathFragment $match })
    $protected = $inlinePattern.Replace($protected, { param($match) Protect-MathFragment $match })

    $body = (ConvertFrom-Markdown -InputObject $protected).Html
    for ($index = 0; $index -lt $script:mathFragments.Count; $index++) {
        $body = $body.Replace(
            "MATHJAXPLACEHOLDER$($index)X",
            $script:mathFragments[$index]
        )
    }

    # Keep the explicitly labelled source link in README pointing to Markdown,
    # but make links among the rendered story documents stay within HTML.
    $storyLinkPattern = [regex]::new(
        '(?is)<a\s+href="(?<target>(?![a-z]+:|/|\.\./)[^"]+)\.md(?<suffix>#[^"]*)?">(?<label>.*?)</a>'
    )
    $body = $storyLinkPattern.Replace($body, {
        param($match)

        if ($match.Groups['label'].Value -match '^\s*Markdown source\s*$') {
            return $match.Value
        }

        return '<a href="' + $match.Groups['target'].Value + '.html' +
            $match.Groups['suffix'].Value + '">' +
            $match.Groups['label'].Value + '</a>'
    })

    $title = Get-DocumentTitle -Source $source -Fallback $SourceFile.BaseName
    $encodedTitle = [System.Net.WebUtility]::HtmlEncode($title)

    $head = @"
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>$encodedTitle</title>
  <style>
    :root {
      color-scheme: light dark;
      font-family: Georgia, "Times New Roman", serif;
      line-height: 1.6;
    }
    body {
      margin: 0 auto;
      max-width: 54rem;
      padding: 2rem 1.25rem 4rem;
    }
    h1, h2, h3 {
      font-family: system-ui, sans-serif;
      line-height: 1.2;
      margin-top: 1.75em;
    }
    h1 { margin-top: 0; }
    li + li { margin-top: 0.35rem; }
    mjx-container[display="true"] {
      margin: 1.25rem 0 !important;
      overflow-x: auto;
      overflow-y: hidden;
    }
  </style>
  <script>
    window.MathJax = {
      tex: {
        inlineMath: [['\\(', '\\)']],
        displayMath: [['\\[', '\\]']]
      }
    };
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
"@

    $tail = @'
</body>
</html>
'@

    $outputPath = [System.IO.Path]::ChangeExtension($SourceFile.FullName, '.html')
    $document = $head + $body + $tail
    Set-Content -LiteralPath $outputPath -Value $document -Encoding utf8
    Write-Host "Rendered $($SourceFile.Name) -> $([System.IO.Path]::GetFileName($outputPath))"
}

Get-ChildItem -LiteralPath $PSScriptRoot -File -Filter '*.md' |
    Sort-Object Name |
    ForEach-Object { Convert-StoryDocument -SourceFile $_ }
