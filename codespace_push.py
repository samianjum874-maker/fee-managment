import subprocess
import sys

def run_cmd(cmd, desc):
    print(f"Running: {desc}...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Error in {desc}:\n{res.stderr}")
        return False
    print(f"✓ {desc} done.")
    return True

def push_flow():
    # 1. Track all changes
    if not run_cmd("git add .", "Staging all changes"): sys.exit(1)
    
    # 2. Commit with a clear message
    commit_msg = "Update from GitHub Codespace"
    if not run_cmd(f'git commit -m "{commit_msg}"', "Committing modifications"):
        print("Note: Maybe nothing new to commit.")
    
    # 3. Detect branch and push
    branch_res = subprocess.run("git rev-parse --abbrev-ref HEAD", shell=True, capture_output=True, text=True)
    branch = branch_res.stdout.strip() or "main"
    
    run_cmd(f"git push origin {branch}", f"Pushing code to remote branch {branch}")

if __name__ == "__main__":
    push_flow()
