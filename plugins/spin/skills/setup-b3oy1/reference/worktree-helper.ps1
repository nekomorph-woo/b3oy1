# b3oy1 worktree helper —— cd 进 .fiber/worktrees/<slug>/ 并打开 lazygit
# 由 setup-b3oy1 追加到 PowerShell $PROFILE；<repo-root> 会在安装时替换为仓库绝对路径
# 名字用 wtx：wt 与 Windows Terminal 的 wt.exe 撞名
function wtx {
  param([Parameter(Mandatory = $true)][string]$Slug)
  $dir = "<repo-root>\.fiber\worktrees\$Slug"
  if (-not (Test-Path $dir)) {
    Write-Error "worktree 不存在: $dir（查 .fiber/worktrees.md 路由表）"
    return
  }
  Set-Location $dir
  lazygit
}
