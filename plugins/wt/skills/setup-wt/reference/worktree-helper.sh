# b3oy1 worktree helper —— cd 进 .fiber/worktrees/<slug>/ 并打开 lazygit
# 由 setup-wt 追加到 shell rc；<repo-root> 会在安装时替换为仓库绝对路径
wt() {
  local slug="$1"
  if [[ -z "$slug" ]]; then
    echo "用法: wt <slug>   # slug 见 .fiber/worktrees.md 路由表" >&2
    return 1
  fi
  local dir="<repo-root>/.fiber/worktrees/$slug"
  if [[ ! -d "$dir" ]]; then
    echo "worktree 不存在: $dir（查 .fiber/worktrees.md 路由表）" >&2
    return 1
  fi
  cd "$dir" && lazygit
}
