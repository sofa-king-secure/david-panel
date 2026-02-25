#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║              MIR // UNIVERSAL GIT MANAGER                     ║
║   Solo version tracking & GitHub sync for any project         ║
╚═══════════════════════════════════════════════════════════════╝

Usage:
  python git_manager.py              Smart mode — figures out what you need
  python git_manager.py --setup      Configure workspace & GitHub identity
  python git_manager.py --new        Create a new tracked project
  python git_manager.py --push       Push current project changes
  python git_manager.py --log        Pretty version history
  python git_manager.py --projects   List all tracked projects
  python git_manager.py --status     Status of all projects at once
"""

import subprocess
import sys
import os
import json
import argparse
import shutil
from datetime import datetime
from pathlib import Path

# ── CONFIG FILE — stored in user's home dir, never in a repo ─────────────────
CONFIG_PATH = Path.home() / ".mir_git_manager.json"

DEFAULT_WORKSPACE = Path.home() / "Projects"

# ── FIND GIT EXECUTABLE ───────────────────────────────────────────────────────
def find_git():
    """Find git.exe on Windows, handling cases where it's not on Python's PATH."""
    # 1. Already on PATH (Linux/Mac/some Windows setups)
    found = shutil.which("git")
    if found:
        return found

    # 2. Common Windows Git install locations
    candidates = [
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Git\bin\git.exe"),
        os.path.expanduser(r"~\scoop\shims\git.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c

    # 3. Try reading from registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SOFTWARE\GitForWindows")
        install_path, _ = winreg.QueryValueEx(key, "InstallPath")
        candidate = os.path.join(install_path, "bin", "git.exe")
        if os.path.exists(candidate):
            return candidate
    except Exception:
        pass

    return None

GIT_EXE = find_git()

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG LOAD / SAVE
# ─────────────────────────────────────────────────────────────────────────────

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

def get(cfg, key, default=None):
    return cfg.get(key, default)

# ─────────────────────────────────────────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

GREEN  = "\033[92m"
AMBER  = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def banner():
    print(f"""
{GREEN}╔═══════════════════════════════════════════════════════════════╗
║              MIR // UNIVERSAL GIT MANAGER  v1.0               ║
╚═══════════════════════════════════════════════════════════════╝{RESET}""")

def header(text):
    print(f"\n{CYAN}{'─'*60}{RESET}")
    print(f"{BOLD}  {text}{RESET}")
    print(f"{CYAN}{'─'*60}{RESET}")

def ok(msg):   print(f"  {GREEN}✓{RESET} {msg}")
def info(msg): print(f"  {CYAN}·{RESET} {msg}")
def warn(msg): print(f"  {AMBER}⚠{RESET}  {msg}")
def err(msg):  print(f"  {RED}✗{RESET} {msg}")
def dim(msg):  print(f"  {DIM}{msg}{RESET}")

def ask(prompt, default=None):
    """Prompt user, show default in brackets, return input or default."""
    if default:
        display = f"  {AMBER}?{RESET} {prompt} {DIM}[{default}]{RESET}: "
    else:
        display = f"  {AMBER}?{RESET} {prompt}: "
    val = input(display).strip()
    return val if val else (default or "")

def confirm(prompt, default=True):
    """Yes/no prompt. Returns bool."""
    yn = "Y/n" if default else "y/N"
    val = input(f"  {AMBER}?{RESET} {prompt} {DIM}({yn}){RESET}: ").strip().lower()
    if not val:
        return default
    return val.startswith("y")

def choose(prompt, options, default=None):
    """Numbered menu. Returns chosen string."""
    print(f"\n  {AMBER}?{RESET} {prompt}")
    for i, opt in enumerate(options, 1):
        marker = f" {DIM}← default{RESET}" if opt == default else ""
        print(f"    {CYAN}{i}{RESET}) {opt}{marker}")
    while True:
        raw = input(f"  Enter number{f' [{options.index(default)+1}]' if default in options else ''}: ").strip()
        if not raw and default in options:
            return default
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        warn("Please enter a valid number.")

# ─────────────────────────────────────────────────────────────────────────────
# GIT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def run(cmd, capture=False, check=True, cwd=None):
    # Ensure git's own bin dir is on PATH for subprocesses
    env = os.environ.copy()
    if GIT_EXE:
        git_bin = os.path.dirname(GIT_EXE)
        if git_bin not in env.get("PATH", ""):
            env["PATH"] = git_bin + os.pathsep + env.get("PATH", "")

    result = subprocess.run(
        cmd, shell=True, text=True,
        capture_output=True,
        cwd=cwd, env=env
    )
    if check and result.returncode != 0:
        error_text = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Command failed: {cmd}\n{error_text}")
    if capture:
        return result.stdout.strip()
    return result.returncode == 0

def git(cmd, capture=False, check=True, cwd=None):
    """Run a git command using the detected git executable."""
    if not GIT_EXE:
        err("Git executable not found!")
        print(f"""
  Git is installed but Python can't find it. Fix options:

  Option A — Add git to system PATH:
    1. Search Windows for 'Environment Variables'
    2. Edit PATH → Add: C:\\Program Files\\Git\\bin
    3. Restart PowerShell and re-run this script

  Option B — Run this once in PowerShell to fix permanently:
    [Environment]::SetEnvironmentVariable(
      'PATH',
      $env:PATH + ';C:\\Program Files\\Git\\bin',
      'User'
    )
""")
        sys.exit(1)
    # Replace 'git ' prefix with actual executable path
    actual_cmd = cmd
    if cmd.startswith("git ") or cmd == "git":
        actual_cmd = f'"{GIT_EXE}" ' + cmd[4:]
    elif not cmd.startswith('"'):
        actual_cmd = f'"{GIT_EXE}" {cmd}'
    return run(actual_cmd, capture=capture, check=check, cwd=cwd)

def is_git_repo(path):
    return (Path(path) / ".git").exists()

def has_remote(cwd=None):
    try:
        result = git("remote get-url origin", capture=True, cwd=cwd)
        return bool(result)
    except:
        return False

def get_current_branch(cwd=None):
    try:
        return git("branch --show-current", capture=True, cwd=cwd)
    except:
        return "main"

def get_repo_status(path):
    """Returns dict with status info for a repo path."""
    if not is_git_repo(path):
        return None
    try:
        dirty = git("status --porcelain", capture=True, cwd=path)
        branch = get_current_branch(cwd=path)
        last_commit = git('log -1 --format="%h %s" --date=short', capture=True, cwd=path)
        last_date = git('log -1 --format="%cr"', capture=True, cwd=path)
        remote = has_remote(cwd=path)
        return {
            "dirty": bool(dirty),
            "changes": len(dirty.splitlines()) if dirty else 0,
            "branch": branch,
            "last_commit": last_commit,
            "last_date": last_date,
            "remote": remote,
        }
    except:
        return None

# ─────────────────────────────────────────────────────────────────────────────
# GITHUB HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def check_gh_cli():
    """Check if GitHub CLI (gh) is installed."""
    return shutil.which("gh") is not None

def create_github_repo(username, repo_name, private=False, description=""):
    """Try to create repo via gh CLI, fallback to instructions."""
    if check_gh_cli():
        vis = "--private" if private else "--public"
        desc_flag = f'--description "{description}"' if description else ""
        try:
            run(f'gh repo create {username}/{repo_name} {vis} {desc_flag}')
            ok(f"GitHub repo created: github.com/{username}/{repo_name}")
            return True
        except Exception as e:
            warn(f"gh CLI failed: {e}")

    # Manual fallback
    print(f"""
  {AMBER}Manual step required:{RESET}
  1. Go to {CYAN}https://github.com/new{RESET}
  2. Repository name: {BOLD}{repo_name}{RESET}
  3. Set to {'Private' if private else 'Public'}
  4. {RED}Leave everything else UNCHECKED{RESET} (no README, no .gitignore)
  5. Click Create repository

  Then press Enter here to continue...
""")
    input()
    return True

# ─────────────────────────────────────────────────────────────────────────────
# WORKSPACE SETUP
# ─────────────────────────────────────────────────────────────────────────────

def setup_workspace(cfg):
    """First-time or re-run workspace + identity configuration."""
    header("WORKSPACE SETUP")

    # ── Verify git works before asking anything ───────────────────────────
    try:
        ver = git("--version", capture=True)
        ok(f"Git detected: {ver}")
    except Exception as e:
        err(f"Git check failed: {e}")
        sys.exit(1)

    # ── GitHub identity ───────────────────────────────────────────────────
    print(f"\n  {BOLD}Step 1 — GitHub Identity{RESET}")

    saved_username = get(cfg, "github_username", "")
    username = ask("GitHub username", default=saved_username or None)
    if not username:
        err("Username required.")
        sys.exit(1)

    saved_email = get(cfg, "github_email", "")
    email = ask("GitHub email", default=saved_email or None)

    # Set git global identity
    git(f'config --global user.name "{username}"')
    if email:
        git(f'config --global user.email "{email}"')

    cfg["github_username"] = username
    if email:
        cfg["github_email"] = email
    ok(f"Identity set: {username}" + (f" <{email}>" if email else ""))

    # ── Workspace location ────────────────────────────────────────────────
    print(f"\n  {BOLD}Step 2 — Project Workspace Location{RESET}")
    print(f"""
  {DIM}A workspace is a single folder on your machine where all your
  git projects live as subfolders. This makes it easy to find
  everything and run status checks across all projects at once.

  Best practice default: {DEFAULT_WORKSPACE}{RESET}
""")

    has_workspace = confirm("Do you want a central workspace folder for all projects?", default=True)

    if has_workspace:
        saved_ws = get(cfg, "workspace", str(DEFAULT_WORKSPACE))
        ws_input = ask("Workspace path", default=saved_ws)
        workspace = Path(ws_input).expanduser().resolve()
        workspace.mkdir(parents=True, exist_ok=True)
        cfg["workspace"] = str(workspace)
        cfg["use_workspace"] = True
        ok(f"Workspace set: {workspace}")
    else:
        cfg["use_workspace"] = False
        info("No central workspace — you'll specify paths per project.")

    # ── Auth note ─────────────────────────────────────────────────────────
    print(f"""
  {BOLD}Step 3 — GitHub Authentication{RESET}

  {DIM}Git uses Windows Credential Manager for passwords/tokens.
  You will NOT be asked for a password here — it's handled
  securely by Windows the first time you push.

  The first push to GitHub will open a browser window asking
  you to authorize. After that it's stored and never asked again.{RESET}
""")
    info("Authentication handled automatically by Windows Credential Manager.")

    # ── Save ──────────────────────────────────────────────────────────────
    cfg["setup_complete"] = True
    cfg.setdefault("projects", {})
    save_config(cfg)

    ok("Configuration saved to ~/.mir_git_manager.json")
    return cfg

# ─────────────────────────────────────────────────────────────────────────────
# NEW PROJECT
# ─────────────────────────────────────────────────────────────────────────────

def new_project(cfg):
    header("NEW PROJECT")

    if not get(cfg, "setup_complete"):
        warn("Workspace not configured yet. Running setup first...")
        cfg = setup_workspace(cfg)

    username = cfg["github_username"]

    # ── What are you building? ────────────────────────────────────────────
    print(f"\n  {BOLD}What are you working on?{RESET}")
    project_name = ask("Project name (no spaces, use hyphens)")
    if not project_name:
        err("Project name required.")
        sys.exit(1)
    project_name = project_name.lower().replace(" ", "-")

    description = ask("Short description (optional)", default="")

    # ── Standalone or workspace? ──────────────────────────────────────────
    if get(cfg, "use_workspace"):
        workspace = Path(cfg["workspace"])
        print(f"""
  {BOLD}Where should this project live?{RESET}

  {DIM}1) Inside your workspace → {workspace / project_name}
  2) Somewhere else (you'll specify){RESET}
""")
        in_workspace = confirm(f"Add to your workspace at {workspace}?", default=True)
        if in_workspace:
            project_path = workspace / project_name
        else:
            custom = ask("Project folder path")
            project_path = Path(custom).expanduser().resolve()
    else:
        custom = ask("Where should this project live?",
                     default=str(Path.cwd() / project_name))
        project_path = Path(custom).expanduser().resolve()

    # ── Sync with GitHub? ─────────────────────────────────────────────────
    print(f"""
  {BOLD}GitHub sync options:{RESET}

  {DIM}Syncing to GitHub gives you:
  • Off-machine backup
  • Version history accessible from anywhere
  • Easy restore if something breaks{RESET}
""")
    sync_github = confirm("Sync this project to GitHub?", default=True)

    private = False
    if sync_github:
        private = confirm("Make the GitHub repo private?", default=True)

    # ── Create folder & init ──────────────────────────────────────────────
    project_path.mkdir(parents=True, exist_ok=True)
    ok(f"Created: {project_path}")

    if not is_git_repo(project_path):
        git("init", cwd=project_path)
        git("branch -M main", cwd=project_path)
        ok("Git repo initialized")

    # ── Generate README ───────────────────────────────────────────────────
    readme_path = project_path / "README.md"
    if not readme_path.exists():
        with open(readme_path, "w") as f:
            f.write(f"# {project_name}\n\n")
            if description:
                f.write(f"{description}\n\n")
            f.write(f"*Created: {datetime.now().strftime('%Y-%m-%d')}*\n")
        ok("README.md created")

    # ── Generate .gitignore ───────────────────────────────────────────────
    gi_path = project_path / ".gitignore"
    if not gi_path.exists():
        with open(gi_path, "w") as f:
            f.write("""# Python
__pycache__/
*.py[cod]
*.pyo
.env
venv/
.venv/
*.egg-info/

# Windows
Thumbs.db
Desktop.ini
*.lnk

# Secrets — NEVER commit these
*.key
*.pem
secrets.json
config_local.py
.env.local

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
""")
        ok(".gitignore created (with secrets protection)")

    # ── Initial commit ────────────────────────────────────────────────────
    git("add .", cwd=project_path)
    try:
        git(f'commit -m "Initial commit: {project_name}"', cwd=project_path)
        ok("Initial commit made")
    except:
        info("Nothing to commit yet (empty project)")

    # ── GitHub remote ─────────────────────────────────────────────────────
    if sync_github:
        repo_url = f"https://github.com/{username}/{project_name}.git"

        if not has_remote(cwd=project_path):
            create_github_repo(username, project_name, private=private,
                               description=description)
            git(f"remote add origin {repo_url}", cwd=project_path)
            ok(f"Remote set: {repo_url}")

        try:
            git("push -u origin main", cwd=project_path)
            ok("Pushed to GitHub!")
        except Exception as e:
            warn(f"Push failed — you may need to authenticate: {e}")
            print(f"\n  Try manually:\n    cd {project_path}\n    git push -u origin main\n")

    # ── Register project in config ────────────────────────────────────────
    cfg.setdefault("projects", {})[project_name] = {
        "path": str(project_path),
        "github": f"https://github.com/{username}/{project_name}" if sync_github else None,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "description": description,
    }
    save_config(cfg)

    # ── Summary ───────────────────────────────────────────────────────────
    header("PROJECT CREATED")
    print(f"""
  {BOLD}Name:{RESET}    {project_name}
  {BOLD}Path:{RESET}    {project_path}
  {BOLD}GitHub:{RESET}  {'https://github.com/' + username + '/' + project_name if sync_github else 'Local only'}

  {BOLD}To start working:{RESET}
    cd {project_path}

  {BOLD}To push future changes:{RESET}
    python {__file__} --push --project {project_name}
  {DIM}or just:{RESET}
    cd {project_path}
    python {__file__} --push
""")

# ─────────────────────────────────────────────────────────────────────────────
# PUSH / SYNC
# ─────────────────────────────────────────────────────────────────────────────

def push_project(cfg, project_name=None, message=None, path=None):
    header("PUSH CHANGES")

    # Determine working directory
    if path:
        cwd = Path(path).expanduser().resolve()
    elif project_name and project_name in get(cfg, "projects", {}):
        cwd = Path(cfg["projects"][project_name]["path"])
    elif is_git_repo(Path.cwd()):
        cwd = Path.cwd()
    else:
        # Try to find which registered project matches cwd
        cwd_str = str(Path.cwd())
        match = None
        for pname, pdata in get(cfg, "projects", {}).items():
            if cwd_str.startswith(pdata["path"]):
                match = pname
                cwd = Path(pdata["path"])
                break
        if not match:
            err("Not in a git repo and no project specified.")
            print(f"  Run from inside a project folder, or use: --project <name>")
            list_projects(cfg)
            sys.exit(1)

    if not is_git_repo(cwd):
        err(f"No git repo at: {cwd}")
        sys.exit(1)

    info(f"Project: {cwd.name}")

    # Check status
    status = git("status --porcelain", capture=True, cwd=cwd)
    if not status:
        ok("Nothing to commit — already up to date.")
        _print_last_commit(cwd)
        return

    # Show changes
    print(f"\n  {BOLD}Changed files:{RESET}")
    for line in status.splitlines():
        flag = line[:2].strip()
        fname = line[3:]
        color = GREEN if 'A' in flag else AMBER if 'M' in flag else RED
        print(f"    {color}{flag}{RESET}  {fname}")

    # Commit message
    if not message:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        changed_files = [l[3:].strip() for l in status.splitlines()]
        auto_msg = f"Update {ts}: {', '.join(changed_files[:3])}"
        if len(changed_files) > 3:
            auto_msg += f" +{len(changed_files)-3} more"
        message = ask("Commit message", default=auto_msg)

    # Stage all
    git("add .", cwd=cwd)
    git(f'commit -m "{message}"', cwd=cwd)
    ok(f"Committed: {message}")

    # Push if remote exists
    if has_remote(cwd=cwd):
        try:
            git("push", cwd=cwd)
            ok("Pushed to GitHub!")
        except Exception as e:
            warn(f"Push failed: {e}")
    else:
        info("No remote configured — committed locally only.")
        if confirm("Would you like to add a GitHub remote now?", default=False):
            _add_remote_interactive(cfg, cwd)

    _print_last_commit(cwd)

def _print_last_commit(cwd):
    try:
        commit = git('log -1 --format="  %h  %s  (%cr)"', capture=True, cwd=cwd)
        print(f"\n  {DIM}Latest: {commit}{RESET}")
    except:
        pass

def _add_remote_interactive(cfg, cwd):
    username = get(cfg, "github_username", "")
    if not username:
        username = ask("GitHub username")
    repo_name = ask("GitHub repo name", default=cwd.name)
    private = confirm("Make private?", default=True)
    create_github_repo(username, repo_name, private=private)
    repo_url = f"https://github.com/{username}/{repo_name}.git"
    git(f"remote add origin {repo_url}", cwd=cwd)
    git("push -u origin main", cwd=cwd)
    ok(f"Synced to github.com/{username}/{repo_name}")

# ─────────────────────────────────────────────────────────────────────────────
# LOG — pretty version history
# ─────────────────────────────────────────────────────────────────────────────

def show_log(cfg, project_name=None, limit=20):
    header("VERSION HISTORY")

    cwd = _resolve_project_path(cfg, project_name)

    print(f"\n  {BOLD}{cwd.name}{RESET}  {DIM}({cwd}){RESET}\n")

    try:
        log = git(
            f'log -{limit} --format="%h|%ad|%s|%an" --date=short',
            capture=True, cwd=cwd
        )
        if not log:
            info("No commits yet.")
            return

        print(f"  {DIM}{'HASH':<8} {'DATE':<12} {'MESSAGE':<45} AUTHOR{RESET}")
        print(f"  {'─'*75}")
        for line in log.splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                h, date, msg, author = parts
                msg_short = msg[:44] + "…" if len(msg) > 44 else msg
                print(f"  {CYAN}{h:<8}{RESET} {DIM}{date:<12}{RESET} {msg_short:<45} {DIM}{author}{RESET}")
    except Exception as e:
        err(f"Could not read log: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# LIST PROJECTS
# ─────────────────────────────────────────────────────────────────────────────

def list_projects(cfg):
    header("TRACKED PROJECTS")
    projects = get(cfg, "projects", {})

    if not projects:
        info("No projects tracked yet. Run --new to create one.")
        return

    print(f"\n  {DIM}{'NAME':<25} {'PATH':<35} GITHUB{RESET}")
    print(f"  {'─'*80}")
    for name, data in sorted(projects.items()):
        path_str = data.get("path", "?")
        github   = data.get("github") or DIM + "local only" + RESET
        exists   = "✓" if Path(path_str).exists() else RED + "✗ missing" + RESET
        print(f"  {GREEN}{name:<25}{RESET} {path_str:<35} {github}")

# ─────────────────────────────────────────────────────────────────────────────
# STATUS — all projects at once
# ─────────────────────────────────────────────────────────────────────────────

def status_all(cfg):
    header("ALL PROJECTS STATUS")
    projects = get(cfg, "projects", {})

    if not projects:
        info("No projects tracked yet.")
        return

    print()
    for name, data in sorted(projects.items()):
        path = Path(data.get("path", ""))
        if not path.exists():
            print(f"  {RED}✗{RESET} {name:<25} {DIM}path missing{RESET}")
            continue

        s = get_repo_status(path)
        if not s:
            print(f"  {AMBER}?{RESET} {name:<25} {DIM}not a git repo{RESET}")
            continue

        if s["dirty"]:
            status_icon = f"{AMBER}●{RESET}"
            status_txt  = f"{AMBER}{s['changes']} uncommitted change(s){RESET}"
        else:
            status_icon = f"{GREEN}●{RESET}"
            status_txt  = f"{DIM}clean{RESET}"

        remote_icon = f"{CYAN}↑{RESET}" if s["remote"] else f"{DIM}⊘{RESET}"
        last = f"{DIM}{s['last_date']}{RESET}" if s["last_date"] else ""

        print(f"  {status_icon} {remote_icon} {name:<25} {status_txt:<35} {last}")

    print(f"""
  {DIM}Legend: {GREEN}●{RESET}{DIM} clean  {AMBER}●{RESET}{DIM} uncommitted changes
           {CYAN}↑{RESET}{DIM} GitHub synced  ⊘ local only{RESET}
""")

# ─────────────────────────────────────────────────────────────────────────────
# SMART MODE — figure out what user needs
# ─────────────────────────────────────────────────────────────────────────────

def smart_mode(cfg):
    banner()

    # First time ever
    if not get(cfg, "setup_complete"):
        print(f"""
  {AMBER}Looks like this is your first time running MIR Git Manager.{RESET}
  Let's get your workspace and GitHub identity configured.
""")
        cfg = setup_workspace(cfg)
        print()
        if confirm("Create your first project now?", default=True):
            new_project(cfg)
        return

    # Already set up — figure out context
    header("WHAT WOULD YOU LIKE TO DO?")

    in_git_repo = is_git_repo(Path.cwd())
    has_changes = False
    if in_git_repo:
        status = git("status --porcelain", capture=True, cwd=Path.cwd())
        has_changes = bool(status)

    options = []
    if has_changes:
        options.append("Push changes in current folder")
    options += [
        "Create a new project",
        "Check status of all projects",
        "View version history of a project",
        "List all tracked projects",
        "Reconfigure workspace / identity",
    ]

    choice = choose("Select an action", options)

    if choice == "Push changes in current folder":
        push_project(cfg)
    elif choice == "Create a new project":
        new_project(cfg)
    elif choice == "Check status of all projects":
        status_all(cfg)
    elif choice == "View version history of a project":
        name = _pick_project(cfg)
        if name:
            show_log(cfg, project_name=name)
    elif choice == "List all tracked projects":
        list_projects(cfg)
    elif choice == "Reconfigure workspace / identity":
        cfg = setup_workspace(cfg)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_project_path(cfg, project_name=None):
    if project_name and project_name in get(cfg, "projects", {}):
        return Path(cfg["projects"][project_name]["path"])
    if is_git_repo(Path.cwd()):
        return Path.cwd()
    err("Can't determine project. Run from inside a project folder or use --project <name>")
    list_projects(cfg)
    sys.exit(1)

def _pick_project(cfg):
    projects = get(cfg, "projects", {})
    if not projects:
        info("No projects tracked yet.")
        return None
    names = sorted(projects.keys())
    return choose("Select project", names)

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Enable ANSI colors on Windows
    if sys.platform == "win32":
        os.system("color")

    parser = argparse.ArgumentParser(
        description="MIR Universal Git Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python git_manager.py                    Smart mode — guided menu
  python git_manager.py --setup            Configure workspace & identity
  python git_manager.py --new              Create a new tracked project
  python git_manager.py --push             Push current folder changes
  python git_manager.py --push -m "Fix"   Push with custom message
  python git_manager.py --log              Version history (current folder)
  python git_manager.py --log --project navex-irm
  python git_manager.py --projects         List all projects
  python git_manager.py --status           Status of all projects
        """
    )
    parser.add_argument("--setup",    action="store_true", help="Configure workspace & identity")
    parser.add_argument("--new",      action="store_true", help="Create a new project")
    parser.add_argument("--push",     action="store_true", help="Push changes")
    parser.add_argument("--log",      action="store_true", help="Show version history")
    parser.add_argument("--projects", action="store_true", help="List all tracked projects")
    parser.add_argument("--status",   action="store_true", help="Status of all projects")
    parser.add_argument("--project",  type=str, default=None, help="Target project name")
    parser.add_argument("-m", "--message", type=str, default=None, help="Commit message")
    parser.add_argument("--limit",    type=int, default=20, help="Log entries to show")
    args = parser.parse_args()

    cfg = load_config()
    banner()

    # Show git detection status
    if GIT_EXE:
        print(f"  {DIM}git: {GIT_EXE}{RESET}")
    else:
        err("Git not found. Install from https://git-scm.com/download/win")
        sys.exit(1)

    if args.setup:
        cfg = setup_workspace(cfg)
    elif args.new:
        new_project(cfg)
    elif args.push:
        push_project(cfg, project_name=args.project, message=args.message)
    elif args.log:
        show_log(cfg, project_name=args.project, limit=args.limit)
    elif args.projects:
        list_projects(cfg)
    elif args.status:
        status_all(cfg)
    else:
        smart_mode(cfg)
