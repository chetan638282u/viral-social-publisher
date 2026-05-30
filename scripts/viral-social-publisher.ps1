param(
    [ValidateSet("draft", "telegram-request", "telegram-bot", "post-instagram", "save-package")]
    [string]$Command = "telegram-request"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$OutputDir = Join-Path $Root "output"
$DraftPath = Join-Path $OutputDir "draft-powershell.json"
$StatePath = Join-Path $OutputDir "telegram-state-powershell.json"

function Load-Env {
    $envPath = Join-Path $Root ".env"
    if (!(Test-Path $envPath)) { return }
    Get-Content $envPath | ForEach-Object {
        if ($_ -match "^\s*#" -or $_ -notmatch "=") { return }
        $parts = $_ -split "=", 2
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
    }
}

function Get-EnvValue([string]$Name, [string]$Default = "") {
    $value = [Environment]::GetEnvironmentVariable($Name, "Process")
    if ([string]::IsNullOrWhiteSpace($value)) { return $Default }
    return $value
}

function New-Draft {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    $story = Get-Story
    $post = New-PostText $story
    $imagePath = Join-Path $OutputDir "post-powershell.png"
    New-PostImage $post.hook $imagePath

    $draft = [ordered]@{
        topic = $post.topic
        hook = $post.hook
        caption = $post.caption
        hashtags = $post.hashtags
        image_path = $imagePath
        source_title = $story.title
        source_url = $story.url
        created_at = (Get-Date).ToString("o")
    }
    $draft | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $DraftPath -Encoding UTF8
    return $draft
}

function Get-Story {
    $feeds = @(
        "https://news.google.com/rss/search?q=AI%20technology%20India&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=technology%20gaming%20viral&hl=en-IN&gl=IN&ceid=IN:en"
    )
    foreach ($feed in $feeds) {
        try {
            $rss = Invoke-RestMethod -Uri $feed -TimeoutSec 20
            $item = @($rss.rss.channel.item)[0]
            if ($item) {
                return @{
                    title = [string]$item.title
                    url = [string]$item.link
                    source = "Google News RSS"
                }
            }
        } catch {
            continue
        }
    }
    return @{
        title = "New AI tools are changing how creators work"
        url = "https://news.google.com/search?q=AI%20technology"
        source = "Fallback"
    }
}

function New-PostText($Story) {
    $openRouterKey = Get-EnvValue "OPENROUTER_API_KEY"
    if ($openRouterKey) {
        try {
            $prompt = @"
Create an original social media post from this research note. Do not copy the headline.
Return strict JSON with topic, hook, caption, hashtags.
Research note: $($Story.title)
Source URL: $($Story.url)
Style: India audience, short, punchy, factual, no unverified claims, no clickbait lies.
Use plain ASCII text only. No emoji, curly quotes, or fancy dashes.
"@
            $body = @{
                model = (Get-EnvValue "OPENROUTER_MODEL" "openrouter/free")
                messages = @(@{ role = "user"; content = $prompt })
            } | ConvertTo-Json -Depth 6
            $response = Invoke-RestMethod -Method Post -Uri "https://openrouter.ai/api/v1/chat/completions" -Headers @{
                Authorization = "Bearer $openRouterKey"
                "Content-Type" = "application/json"
                "HTTP-Referer" = "https://github.com/chetan638282u/viral-social-publisher"
                "X-Title" = "Viral Social Publisher"
            } -Body $body -TimeoutSec 45
            $text = [string]$response.choices[0].message.content
            $jsonText = [regex]::Match($text, "\{[\s\S]*\}").Value
            if ($jsonText) {
                $parsed = $jsonText | ConvertFrom-Json
                return @{
                    topic = Clean-Ascii ([string]$parsed.topic)
                    hook = Clean-Ascii ([string]$parsed.hook)
                    caption = Clean-Ascii ([string]$parsed.caption)
                    hashtags = Clean-Ascii ([string]$parsed.hashtags)
                }
            }
        } catch {
            # Fallback below.
        }
    }

    $topic = "AI and tech update"
    $hook = "This tech shift is worth watching today"
    $caption = "$hook`n`nA fresh signal from today's tech news: $($Story.title)`n`nThe important part is not hype. It is how fast tools, creators, and businesses are adapting.`n`nSource: $($Story.url)"
    return @{
        topic = $topic
        hook = $hook
        caption = $caption
        hashtags = "#AI #Technology #India #ViralBriefIndia #TechNews"
    }
}

function Clean-Ascii([string]$Text) {
    if ($null -eq $Text) { return "" }
    $clean = $Text -replace "[\u2018\u2019]", "'" -replace "[\u201C\u201D]", '"' -replace "[\u2013\u2014]", "-"
    return [regex]::Replace($clean, "[^\u0009\u000A\u000D\u0020-\u007E]", "")
}

function New-PostImage([string]$Hook, [string]$Path) {
    Add-Type -AssemblyName System.Drawing
    if (Test-Path $Path) { Remove-Item -LiteralPath $Path -Force }
    $dir = Split-Path -Parent $Path
    if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $bitmap = New-Object Drawing.Bitmap 1080, 1080
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.Clear([Drawing.Color]::FromArgb(12, 15, 22))

    $accent = New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(0, 220, 190))
    $white = New-Object Drawing.SolidBrush ([Drawing.Color]::White)
    $muted = New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(180, 190, 205))
    $fontTitle = New-Object Drawing.Font "Arial", 58, ([Drawing.FontStyle]::Bold)
    $fontSmall = New-Object Drawing.Font "Arial", 28, ([Drawing.FontStyle]::Regular)

    $graphics.FillRectangle($accent, 0, 0, 1080, 28)
    $graphics.DrawString("VIRAL BRIEF INDIA", $fontSmall, $muted, 80, 90)
    $rect = New-Object Drawing.RectangleF 80, 250, 920, 520
    $graphics.DrawString($Hook, $fontTitle, $white, $rect)
    $graphics.DrawString("AI | Tech | Gaming | Culture", $fontSmall, $accent, 80, 880)
    $graphics.DrawString("@viralbriefindia", $fontSmall, $muted, 80, 930)

    $bitmap.Save($Path, [Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
}

function Send-TelegramRequest {
    $draft = New-Draft
    $token = Get-EnvValue "TELEGRAM_BOT_TOKEN"
    $chatId = Get-EnvValue "TELEGRAM_CHAT_ID"
    if (!$token -or !$chatId) { throw "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required." }

    $text = "Approval needed`n`nHook: $($draft.hook)`n`nCaption:`n$($draft.caption)`n`n$($draft.hashtags)"
    $keyboard = @{
        inline_keyboard = @(
            @(@{ text = "Save package"; callback_data = "save_latest" }, @{ text = "Direct post"; callback_data = "post_latest" }),
            @(@{ text = "Reject"; callback_data = "reject_latest" })
        )
    } | ConvertTo-Json -Compress -Depth 5
    Invoke-Telegram "sendMessage" @{ chat_id = $chatId; text = $text; reply_markup = $keyboard } | Out-Null
    Send-TelegramFile "sendPhoto" $draft.image_path "photo" @{ chat_id = $chatId; caption = "Preview image draft" } | Out-Null
    @{ status = "pending"; last_update_id = 0; draft_path = $DraftPath } | ConvertTo-Json | Set-Content $StatePath -Encoding UTF8
    Write-Host "Telegram approval request sent."
}

function Run-TelegramBot {
    $token = Get-EnvValue "TELEGRAM_BOT_TOKEN"
    if (!$token) { throw "TELEGRAM_BOT_TOKEN is required." }
    $offset = 0
    if (Test-Path $StatePath) {
        $state = Get-Content -Raw $StatePath | ConvertFrom-Json
        $offset = [int]$state.last_update_id + 1
    }
    Write-Host "Telegram bot running. Press Ctrl+C to stop."
    while ($true) {
        $updates = Invoke-Telegram "getUpdates" @{ timeout = 30; offset = $offset }
        foreach ($update in @($updates.result)) {
            $offset = [int]$update.update_id + 1
            if ($update.callback_query) {
                Handle-Callback $update.callback_query
            }
            @{ last_update_id = ([int]$update.update_id) } | ConvertTo-Json | Set-Content $StatePath -Encoding UTF8
        }
    }
}

function Handle-Callback($Callback) {
    $token = Get-EnvValue "TELEGRAM_BOT_TOKEN"
    $chatId = $Callback.message.chat.id
    if ($Callback.data -eq "reject_latest") {
        Invoke-Telegram "answerCallbackQuery" @{ callback_query_id = $Callback.id; text = "Rejected. Nothing posted." } | Out-Null
        return
    }
    if ($Callback.data -eq "save_latest") {
        Invoke-Telegram "answerCallbackQuery" @{ callback_query_id = $Callback.id; text = "Saved package sent." } | Out-Null
        Send-SavedPackage $chatId
        return
    }
    if ($Callback.data -eq "post_latest") {
        try {
            $result = Publish-Instagram
            Invoke-Telegram "answerCallbackQuery" @{ callback_query_id = $Callback.id; text = "Posted." } | Out-Null
            Invoke-Telegram "sendMessage" @{ chat_id = $chatId; text = "Instagram result:`n$($result | ConvertTo-Json -Depth 5)" } | Out-Null
        } catch {
            Invoke-Telegram "sendMessage" @{ chat_id = $chatId; text = "Direct post failed:`n$($_.Exception.Message)" } | Out-Null
        }
    }
}

function Send-SavedPackage($ChatId) {
    $draft = Get-Content -Raw $DraftPath | ConvertFrom-Json
    Invoke-Telegram "sendMessage" @{ chat_id = $ChatId; text = "Saved package:`n`n$($draft.caption)`n`n$($draft.hashtags)" } | Out-Null
    Send-TelegramFile "sendPhoto" $draft.image_path "photo" @{ chat_id = $ChatId; caption = "Image for manual upload" } | Out-Null
}

function Publish-Instagram {
    $draft = Get-Content -Raw $DraftPath | ConvertFrom-Json
    $token = Get-EnvValue "INSTAGRAM_ACCESS_TOKEN" (Get-EnvValue "META_ACCESS_TOKEN")
    $accountId = Get-EnvValue "INSTAGRAM_BUSINESS_ACCOUNT_ID"
    $version = Get-EnvValue "META_GRAPH_VERSION" "v25.0"
    if (!$token -or !$accountId) { throw "Instagram token and account ID are required." }
    $publicImageUrl = Get-EnvValue "PUBLIC_IMAGE_URL"
    if (!$publicImageUrl) {
        $publicImageUrl = Upload-GitHubMedia $draft.image_path "images"
    }
    $caption = "$($draft.caption)`n`n$($draft.hashtags)"
    $create = Invoke-RestMethod -Method Post -Uri "https://graph.instagram.com/$version/$accountId/media" -Body @{
        image_url = $publicImageUrl
        caption = $caption
        access_token = $token
    } -TimeoutSec 60
    $publish = Invoke-RestMethod -Method Post -Uri "https://graph.instagram.com/$version/$accountId/media_publish" -Body @{
        creation_id = $create.id
        access_token = $token
    } -TimeoutSec 60
    return @{ platform = "instagram"; status = "posted"; response = $publish }
}

function Upload-GitHubMedia([string]$Path, [string]$Prefix) {
    $githubToken = Get-EnvValue "GITHUB_TOKEN"
    if (!$githubToken) { throw "GITHUB_TOKEN is required to upload media publicly for Instagram." }
    $repository = Get-EnvValue "GITHUB_REPOSITORY" "chetan638282u/viral-social-publisher"
    $branch = Get-EnvValue "GITHUB_MEDIA_BRANCH" "main"
    $basePath = Get-EnvValue "GITHUB_MEDIA_PATH" "media"
    $file = Get-Item $Path
    $repoPath = "$basePath/$Prefix/$($file.Name)"
    $bytes = [IO.File]::ReadAllBytes($file.FullName)
    $content = [Convert]::ToBase64String($bytes)
    $headers = @{
        Authorization = "Bearer $githubToken"
        Accept = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    $apiUrl = "https://api.github.com/repos/$repository/contents/$repoPath"
    $sha = $null
    try {
        $existing = Invoke-RestMethod -Method Get -Uri "$apiUrl`?ref=$branch" -Headers $headers -TimeoutSec 30
        $sha = $existing.sha
    } catch {}
    $body = @{ message = "Upload generated media $($file.Name)"; content = $content; branch = $branch }
    if ($sha) { $body.sha = $sha }
    Invoke-RestMethod -Method Put -Uri $apiUrl -Headers $headers -Body ($body | ConvertTo-Json -Depth 5) -ContentType "application/json" -TimeoutSec 60 | Out-Null
    return "https://raw.githubusercontent.com/$repository/$branch/$repoPath"
}

function Invoke-Telegram([string]$Method, [hashtable]$Body) {
    $token = Get-EnvValue "TELEGRAM_BOT_TOKEN"
    return Invoke-RestMethod -Method Post -Uri "https://api.telegram.org/bot$token/$Method" -Body $Body -TimeoutSec 60
}

function Send-TelegramFile([string]$Method, [string]$Path, [string]$Field, [hashtable]$Body) {
    $token = Get-EnvValue "TELEGRAM_BOT_TOKEN"
    Add-Type -AssemblyName System.Net.Http
    $client = New-Object System.Net.Http.HttpClient
    $multipart = New-Object System.Net.Http.MultipartFormDataContent
    foreach ($key in $Body.Keys) {
        $multipart.Add((New-Object System.Net.Http.StringContent([string]$Body[$key])), $key)
    }
    $stream = [IO.File]::OpenRead((Resolve-Path $Path))
    try {
        $fileContent = New-Object System.Net.Http.StreamContent($stream)
        $multipart.Add($fileContent, $Field, (Split-Path -Leaf $Path))
        $response = $client.PostAsync("https://api.telegram.org/bot$token/$Method", $multipart).Result
        $text = $response.Content.ReadAsStringAsync().Result
        if (!$response.IsSuccessStatusCode) { throw $text }
        return $text | ConvertFrom-Json
    } finally {
        $stream.Dispose()
        $client.Dispose()
        $multipart.Dispose()
    }
}

Load-Env
switch ($Command) {
    "draft" { New-Draft | ConvertTo-Json -Depth 5 }
    "telegram-request" { Send-TelegramRequest }
    "telegram-bot" { Run-TelegramBot }
    "post-instagram" { Publish-Instagram | ConvertTo-Json -Depth 5 }
    "save-package" { Send-SavedPackage (Get-EnvValue "TELEGRAM_CHAT_ID") }
}
