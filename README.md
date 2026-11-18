
# FuzzPickle 🥒

**An automated stress-testing and evasion framework for AI model scanners.**

FuzzPickle tests the most popular open-source pickle scanners (PickleScan, ModelScan, Fickling) against 15 targeted parser bypasses and 15 real-world framework exploits. It doesn't just find bugs—it proves execution via a built-in sandbox and generates a Threat Intelligence dashboard.

## 🚨 Why FuzzPickle?
Companies rely on scanners to check AI models downloaded from Hugging Face. But what happens when the scanner says "SAFE" and the model is actually malicious? 
FuzzPickle proves that current scanner stacks are highly vulnerable to **Full Blind Spots** and **Real-World Remote Code Execution (RCE)**.

## 📊 Key Findings (From our latest audit)
*   **6 Confirmed RCEs:** Payloads successfully executed in the sandbox after bypassing the scanners.
*   **Full Blind Spots:** Multiple attack techniques (like `auto_map` and `TorchScript`) were completely missed by all three scanners.
*   **Availability Bugs:** ModelScan crashed on almost every malformed or dynamic payload thrown at it.

## 🛠️ Features
*   **15 Parser Bypasses:** Fuzzed payloads (STACK_GLOBAL, Exception-Directed, Magic Number Spoofing, etc).
*   **15 Real-World Exploits:** CVE-correlated attacks (nullifAI 7z, Pluto Security auto_map, MLflow CVEs, TorchScript).
*   **Sandbox Execution Proof:** Proves if a payload actually runs (RCE).
*   **Interactive HTML Dashboard:** Beautiful, themeable UI with charts, heatmaps, and clickable threat intelligence.
*   **CI/CD Ready:** JSON output for automated pipelines.

## ⚙️ Installation

1. **Clone the repository:**
   ```bashSet up the Python environment:

bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
   git clone https://github.com/YOUR_USERNAME/FuzzPickle.git
   cd FuzzPickle


2.Install the Rust Fuzzer (Required for Scan Mode):
bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
git clone https://github.com/cisco-ai-defense/pickle-fuzzer.git
cd pickle-fuzzer
cargo build --release
cd ..


🚀 Usage

1. The Attack Arsenal (Recommended)
Test the 15 real-world exploits against the scanners:
bash
- python fuzzpickle.py attack --technique all

2. The Fuzz Scan
Generate random malformed files and test parser logic:
bash
- python fuzzpickle.py scan --samples 50

3. Learn About the Attacks
Don't know what an attack does? Use the --example flag:
bash
- python fuzzpickle.py attack --example

4. CI/CD Integration (JSON)
Output raw JSON for your pipelines:
- python fuzzpickle.py attack --technique all --json


📁 Outputs
After every run, FuzzPickle generates a folder in scan_history/:
- raw_data.json: The raw scanner verdicts and execution proofs.
- report.md: A Markdown report with Threat Intelligence.
- report.html: The Interactive Dashboard (open in any browser).

⚖️ Disclaimer
This tool is for educational and defensive security purposes only. The payloads generated are proof-of-concept (PoC) and only write a harmless file (/tmp/fuzzpickle_pwned) to prove execution. Do not use this on systems you do not own.

   
