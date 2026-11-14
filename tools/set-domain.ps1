#Requires -Version 7.0
<#
.SYNOPSIS
    把站点中的 __SITE_DOMAIN__ 占位符一次性替换成正式访问地址，并生成 CNAME。

.DESCRIPTION
    站点所有 canonical、og:url、JSON-LD、sitemap.xml、robots.txt 中都使用
    同一枚占位符 __SITE_DOMAIN__。注册好域名后运行本脚本即可全站生效，
    不需要手工逐页修改。

    支持两种部署形态：
      1) 自定义域名 / 用户主页   -> 传域名本身，例如 www.gxyoushang.com
      2) GitHub 项目页（子路径） -> 传 用户名.github.io/仓库名
         此时不会生成 CNAME（项目页不能使用 CNAME）。

.PARAMETER Domain
    正式访问地址，可带或不带 https://，结尾斜杠会被自动去掉。

.PARAMETER Backup
    替换前把将被修改的文件复制到 _backup/domain-<时间戳>/ 下。

.EXAMPLE
    pwsh tools/set-domain.ps1 -Domain www.gxyoushang.com -Backup

.EXAMPLE
    pwsh tools/set-domain.ps1 -Domain yourname.github.io/guanxiang-youshang-site
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Domain,

    [switch]$Backup
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path -LiteralPath (Join-Path $root 'index.html'))) {
    throw "没有找到站点根目录：$root —— 本脚本应放在站点的 tools/ 目录下运行。"
}

$raw = $Domain.Trim()
$raw = $raw -replace '^(?i)https?://', ''
$raw = $raw.TrimEnd('/').ToLower()

$pattern = '^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+(/[a-z0-9._~-]+)*$'
if ($raw -notmatch $pattern) {
    throw "地址格式不正确：$Domain`n示例：www.gxyoushang.com 或 yourname.github.io/guanxiang-youshang-site"
}

$base = "https://$raw"
$hasPath = $raw.Contains('/')
$token = '__SITE_DOMAIN__'
$utf8 = New-Object Text.UTF8Encoding($false)

# 上一次生效的地址。首次运行没有该文件；以后换域名时用它做旧值替换，
# 这样占位符已经消失的情况下仍可整站改域名。
$siteBaseFile = Join-Path $root '.site-base'
$oldBase = $null
if (Test-Path -LiteralPath $siteBaseFile) {
    $oldBase = [IO.File]::ReadAllText($siteBaseFile, [Text.Encoding]::UTF8).Trim()
}
if ($oldBase -eq $base) {
    Write-Host "全站地址已经是 $base，无需替换。"
    return
}

$files = Get-ChildItem -LiteralPath $root -Recurse -File -Force |
    Where-Object {
        $_.Extension -in '.html', '.xml', '.txt' -and
        $_.FullName -notmatch '\\_backup\\' -and
        $_.FullName -notmatch '\\\.git\\'
    }

if ($Backup) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $bak = Join-Path $root ("_backup\domain-" + $stamp)
    foreach ($f in $files) {
        $rel = $f.FullName.Substring($root.Length).TrimStart('\')
        $dest = Join-Path $bak $rel
        New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force | Out-Null
        Copy-Item -LiteralPath $f.FullName -Destination $dest
    }
    Write-Host "已备份 $($files.Count) 个文件 → $bak"
}

$rows = @()
$total = 0

foreach ($f in $files) {
    $rel = $f.FullName.Substring($root.Length).TrimStart('\')
    $text = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8)
    $count = ([regex]::Matches($text, [regex]::Escape($token))).Count
    $legacy = 0
    if ($oldBase -and $oldBase -ne $base) {
        $legacy = ([regex]::Matches($text, [regex]::Escape($oldBase))).Count
    }
    if ($count -gt 0 -or $legacy -gt 0) {
        $newText = $text.Replace($token, $base)
        if ($legacy -gt 0) { $newText = $newText.Replace($oldBase, $base) }
        [IO.File]::WriteAllText($f.FullName, $newText, $utf8)
        $total += $count + $legacy
    }
    $rows += [pscustomobject]@{ 文件 = $rel; 替换处数 = $count + $legacy }
}

[IO.File]::WriteAllText($siteBaseFile, "$base`n", $utf8)

if ($total -eq 0) {
    Write-Warning "没有发现需要替换的地址（既无 $token 占位符，也没有旧地址命中）。"
}

$cnamePath = Join-Path $root 'CNAME'
if ($hasPath) {
    Write-Host "检测到子路径部署（$raw）：不生成 CNAME。"
    if (Test-Path -LiteralPath $cnamePath) {
        Write-Warning "站点根目录已存在 CNAME，子路径部署时应当删除它，否则 GitHub Pages 会尝试用该域名提供服务。"
    }
}
else {
    [IO.File]::WriteAllText($cnamePath, "$raw`n", $utf8)
    Write-Host "已写入 CNAME → $raw"
}

$rows | Where-Object { $_.替换处数 -gt 0 } | Format-Table -AutoSize | Out-String | Write-Host
Write-Host "合计替换 $total 处，基准地址：$base"
Write-Host "请再核对 sitemap.xml / robots.txt 中的地址，确认无误后提交推送。"
