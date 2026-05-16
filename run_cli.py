import sys
import os
from agents.analyzer_agent import analyze_impacted_modules
from agents.test_mapper import map_tests
from agents.risk_agent import predict_risk
from agents.playwright_runner import run_tests

def main():
    # GitHub actions passes the files as a space-separated string in the environment
    changed_files_text = os.environ.get("CHANGED_FILES", "")
    if not changed_files_text:
        print("No changed files provided. Exiting.")
        sys.exit(0)
        
    # Replace spaces with newlines for easier reading by Gemini
    changed_files_text = changed_files_text.replace(" ", "\n")
    
    print("\n--- 🚀 Triggering TestPilot AI CLI Pipeline ---")
    print(f"Changed Files:\n{changed_files_text}\n")
    
    # 1. Analyze Impact
    modules = analyze_impacted_modules(changed_files_text)
    print(f"Impacted Modules: {modules}")
    
    # 2. Map Tests
    tests = map_tests(modules)
    print(f"Tests to Run: {tests}")
    
    # 3. Predict Risk
    risk = predict_risk(modules)
    print(f"Risk Profile: {risk}")
    
    # 4. Run Playwright Tests
    test_results = run_tests(tests)
    print(f"Test Results: {test_results}\n")

    # 5. Generate Markdown Report for GitHub PR Comment
    report = f"### 🚀 TestPilot AI QA Report\n\n"
    report += f"**Impacted Modules:** {', '.join(modules).title() if modules else 'None'}\n\n"
    report += f"**Risk Level:** {risk['level']} (Score: {risk['score']}%)\n"
    report += f"**Recommendation:** {risk['recommendation']}\n\n"
    report += "**Targeted Test Results:**\n"
    
    if not test_results:
        report += "- No targeted tests required.\n"
    else:
        for t, status in test_results.items():
            icon = "✅" if status == "PASSED" else "❌"
            report += f"- {icon} `{t}`: **{status}**\n"
        
    # Write report to a file so GitHub Actions can read it and post it
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print("Report successfully generated to report.md")
    
    # Fail the GitHub Action if there is high risk or if a test failed
    if risk['level'] == 'HIGH' or any(status != "PASSED" for status in test_results.values()):
        print("\n🚨 Pipeline failed due to high risk or test failures.")
        sys.exit(1)

if __name__ == "__main__":
    main()
