import os
import requests
import base64
import time
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def setup_demo():
    if not TOKEN:
        print("GITHUB_TOKEN not found in .env")
        return

    print("Fetching GitHub user info...")
    user_res = requests.get("https://api.github.com/user", headers=HEADERS)
    user_res.raise_for_status()
    user = user_res.json()["login"]
    repo_name = "testpilot-ai-demo"

    # 1. Create Repo
    print(f"Creating repository: {user}/{repo_name}...")
    repo_res = requests.post("https://api.github.com/user/repos", headers=HEADERS, json={
        "name": repo_name,
        "description": "Demo repository for TestPilot AI PR Analysis",
        "private": False,
        "auto_init": True
    })
    
    if repo_res.status_code == 422:
        print("Repository already exists. Using existing one.")
        repo_res = requests.get(f"https://api.github.com/repos/{user}/{repo_name}", headers=HEADERS)
        repo_res.raise_for_status()
    else:
        repo_res.raise_for_status()
        time.sleep(3)  # Wait for GitHub to initialize the repo
        
    default_branch = repo_res.json().get("default_branch", "main")

    # 2. Get base branch SHA
    refs_res = requests.get(f"https://api.github.com/repos/{user}/{repo_name}/git/refs/heads/{default_branch}", headers=HEADERS)
    refs_res.raise_for_status()
    base_sha = refs_res.json()["object"]["sha"]

    # 3. Create a new branch
    branch_name = f"feature/update-core-{int(time.time())}"
    print(f"Creating branch: {branch_name}...")
    requests.post(f"https://api.github.com/repos/{user}/{repo_name}/git/refs", headers=HEADERS, json={
        "ref": f"refs/heads/{branch_name}",
        "sha": base_sha
    }).raise_for_status()

    # 4. Commit a file (payment.js)
    print("Committing changes to payment.js...")
    payment_content = """
function processPayment(amount) {
    console.log(`Processing payment of $${amount}`);
    // BUG FIX: Added Stripe integration
    stripe.charge(amount);
    
    // Feature: Trigger risk validation before auth
    validateRiskProfile();
}
"""
    encoded_payment = base64.b64encode(payment_content.encode()).decode()
    requests.put(f"https://api.github.com/repos/{user}/{repo_name}/contents/payment.js", headers=HEADERS, json={
        "message": "Update payment processor with Stripe and Risk Validation",
        "content": encoded_payment,
        "branch": branch_name
    }).raise_for_status()

    # 5. Commit another file (wallet.py)
    print("Committing changes to wallet.py...")
    wallet_content = """
def update_wallet_balance(user_id, amount):
    print(f"Updating wallet for {user_id} by {amount}")
    # FEATURE: Deduct platform fees
    fee = amount * 0.02
    net_amount = amount - fee
    db.execute("UPDATE wallets SET balance = balance + ? WHERE user = ?", (net_amount, user_id))
"""
    encoded_wallet = base64.b64encode(wallet_content.encode()).decode()
    requests.put(f"https://api.github.com/repos/{user}/{repo_name}/contents/wallet.py", headers=HEADERS, json={
        "message": "Apply platform fees to wallet balance",
        "content": encoded_wallet,
        "branch": branch_name
    }).raise_for_status()

    # 6. Create Pull Request
    print("Creating Pull Request...")
    pr_res = requests.post(f"https://api.github.com/repos/{user}/{repo_name}/pulls", headers=HEADERS, json={
        "title": "Enhance Payment & Wallet Services",
        "body": "This PR integrates Stripe into the payment module and adds platform fee calculations to the wallet service. Ready for TestPilot AI review.",
        "head": branch_name,
        "base": default_branch
    })
    pr_res.raise_for_status()
    pr_data = pr_res.json()
    
    print("\n" + "="*50)
    print("🎉 DEMO PR CREATED SUCCESSFULLY! 🎉")
    print("="*50)
    print(f"Repo Input:  {user}/{repo_name}")
    print(f"PR Number:   {pr_data['number']}")
    print(f"PR URL:      {pr_data['html_url']}")
    print("="*50)
    print("Copy the Repo Input and PR Number above and paste them into your TestPilot AI dashboard!")

if __name__ == "__main__":
    setup_demo()
