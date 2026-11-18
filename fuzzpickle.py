import sys
import click
import os
import subprocess
import json
from datetime import datetime, timedelta
import shutil
from report_engine import build_report
from audit import run_scanner

# ==========================================
# CUSTOM HELP MENU
# ==========================================
def print_custom_help():
    help_text = """
============================================================
 FUZZPICKLE: The AI Model Scanner Auditor
============================================================
Find blind spots, crashes, and bypasses in top AI security scanners.

USAGE:
  python fuzzpickle.py [COMMAND] [OPTIONS]

COMMANDS:
  1. scan      Fuzz random files and test 15 custom parser payloads.
  2. attack    Test 15 real-world evasion techniques (auto_map, 7z, etc).
  3. delete    Clean up old scan history to save disk space.
  4. demo      Run a quick 60-second demonstration.

HOW TO USE (Examples):
  - Run a basic fuzz scan of 100 files:
      python fuzzpickle.py scan --samples 100

  - Test the full 15-attack arsenal:
      python fuzzpickle.py attack --technique all

  - Delete a specific old scan report:
      python fuzzpickle.py delete --id scan_2026-11-15_1030

WANT TO LEARN MORE?
  We don't just break scanners; we teach you how they break.
  Use the --example flag on any command to see the exact CVEs, 
  research papers, and bypass techniques we use.

  Try this to see the 15 Scan Types:
      python fuzzpickle.py scan --example

  Try this to see the 15 Attack Techniques:
      python fuzzpickle.py attack --example
============================================================
"""
    click.echo(help_text)

# ==========================================
# EXAMPLE DICTIONARIES
# ==========================================
def print_scan_examples():
    click.secho("\n============================================================", fg="cyan")
    click.secho("  FUZZPICKLE SCAN ARSENAL (15 Parser Logic Bypasses)", fg="cyan", bold=True)
    click.secho("============================================================\n", fg="cyan")
    click.echo("Here are the 15 specific payloads generated when you run a scan.\n")
    click.secho("[01] STACK_GLOBAL Index 0 Bypass", bold=True)
    click.echo("     - How it works: Hides the dangerous function at position 0.")
    click.echo("     - Search Term: 'USENIX pickle scanner STACK_GLOBAL bypass'\n")
    click.secho("[02] Exception-Directed Programming (EDP)", bold=True)
    click.echo("     - How it works: Triggers a parser crash to default to SAFE.")
    click.echo("     - Search Term: 'USENIX EDP pickle scanner bypass'\n")
    click.secho("[03] Magic Number Spoofing", bold=True)
    click.echo("     - How it works: Fakes the file header to blind the scanner.")
    click.echo("     - Search Term: 'magic number spoofing malware detection'\n")
    click.secho("[04] Secondary File Parameter", bold=True)
    click.echo("     - How it works: Hides payload in a file the scanner ignores.")
    click.echo("     - Search Term: 'PyTorch secondary file pickle load'\n")
    click.secho("[05] pydoc.locate Gadget", bold=True)
    click.echo("     - How it works: Uses benign built-ins to achieve RCE.")
    click.echo("     - Search Term: 'pydoc locate RCE gadget chain'\n")
    click.secho("... and 10 more dynamic execution payloads (eval, subprocess, ctypes, etc).", fg="yellow")
    click.secho("Run 'python fuzzpickle.py scan --samples 10' to generate and test all 15.\n")

def print_attack_examples():
    click.secho("\n============================================================", fg="cyan")
    click.secho("  FUZZPICKLE ATTACK ARSENAL (15 Real-World Framework Attacks)", fg="cyan", bold=True)
    click.secho("============================================================\n", fg="cyan")
    click.echo("Here are the 15 bypasses tested when you run an attack.\n")
    click.secho("[01] 7z NullifAI Bypass", bold=True)
    click.echo("     - How it works: Compresses payload in 7z to skip ModelScan.")
    click.echo("     - Search Term: 'nullifAI 7z bypass Hugging Face'\n")
    click.secho("[02] AutoMap SafeTensors", bold=True)
    click.echo("     - How it works: Model is safe, config.json executes remote code.")
    click.echo("     - Search Term: 'Hugging Face auto_map trust_remote_code RCE'\n")
    click.secho("[03] MLflow statsmodels", bold=True)
    click.echo("     - How it works: CVE-2026-96804. Bypasses pickle flags.")
    click.echo("     - Search Term: 'CVE-2026-96804 MLflow RCE'\n")
    click.secho("... and 12 more framework bypasses (Keras, TFLite, Joblib, FastAI, ONNX).", fg="yellow")
    click.secho("Run 'python fuzzpickle.py attack --technique all' to test all 15.\n")

# ==========================================
# CLI COMMANDS
# ==========================================
@click.group(invoke_without_command=True, add_help_option=False)
@click.option('--help', is_flag=True, help='Show the custom help menu.')
@click.pass_context
def cli(ctx, help):
    """FuzzPickle: The AI Model Scanner Auditor."""
    if help or ctx.invoked_subcommand is None:
        print_custom_help()

@click.command()
@click.option('--samples', type=int, help='Number of fuzz files to generate (Max: 5000).')
@click.option('--mutators', default='all', help='Fuzzing technique (memoidx, offbyone, all, etc.)')
@click.option('--json', 'json_output', is_flag=True, help='Output raw JSON instead of Markdown.')
@click.option('--example', is_flag=True, help='Show details about the 15 scan types.')
def scan(samples, mutators, json_output, example):
    """Fuzz files, scan them, and generate the report instantly."""
    
    if example:
        print_scan_examples()
        return

    if not samples:
        click.secho("[-] Error: --samples is required. Use --example to learn more.", fg="red")
        return

    if samples > 5000:
        click.secho("[-] Error: Maximum sample limit is 5000 to prevent disk exhaustion.", fg="red", bold=True)
        return
    elif samples <= 0:
        click.secho("[-] Error: Samples must be greater than 0.", fg="red", bold=True)
        return

    scan_id = datetime.now().strftime("scan_%Y-%m-%d_%H%M")
    scan_dir = os.path.join("scan_history", "scans", scan_id)
    report_dir = os.path.join(scan_dir, "reports")
    os.makedirs(report_dir, exist_ok=True)
   
    json_path = os.path.join(report_dir, "raw_data.json")
    report_path = os.path.join(report_dir, "report.md")

    click.echo(f"[*] Generating {samples} random fuzz files...")
    cmd = f"./pickle-fuzzer/target/release/pickle-fuzzer -d fuzz_output -s {samples} --mutators {mutators}"
    subprocess.run(cmd, shell=True, capture_output=True)

    click.echo("[*] Generating targeted parser bypass payloads...")
    subprocess.run(["python", "scan_generator.py", "fuzz_files/scan_payloads"], check=True)

    click.echo("[*] Auditing random files against scanners...")
    subprocess.run(["python", "audit.py", "fuzz_output", json_path], check=True)
   
    click.echo("[*] Auditing targeted payloads against scanners...")
    subprocess.run(["python", "audit.py", "fuzz_files/scan_payloads", json_path + ".tmp"], check=True)
   
    with open(json_path, "r") as f:
        random_results = json.load(f)
    with open(json_path + ".tmp", "r") as f:
        targeted_results = json.load(f)
    with open(json_path, "w") as f:
        json.dump(random_results + targeted_results, f, indent=4)
    os.remove(json_path + ".tmp")
   
    if json_output:
        with open(json_path, "r") as f:
            print(json.dumps(json.load(f), indent=4))
        return

    click.echo("[*] Generating Markdown report...")
    vuln_count = build_report(json_path, report_path, scan_id)
   
    click.secho(f"\n=========================================", fg="green")
    click.secho(f" [SUCCESS] SCAN COMPLETE", fg="green", bold=True)
    click.secho(f"=========================================", fg="green")
    click.echo(f" Critical Blind Spots: {vuln_count}")
    click.echo(f" Scan ID: {scan_id}")
    click.echo(f" Report Saved: {report_path}")
    click.secho(f"=========================================\n", fg="green")


@click.command()
@click.option('--technique', type=click.Choice(['all', '7z', 'automap']), help='Real-world attack technique.')
@click.option('--json', 'json_output', is_flag=True, help='Output raw JSON instead of Markdown.')
@click.option('--example', is_flag=True, help='Show details about the 15 attack types.')
def attack(technique, json_output, example):
    """Run specific real-world bypass techniques (V2)."""
    
    if example:
        print_attack_examples()
        return

    if not technique:
        click.secho("[-] Error: --technique is required. Use --example to learn more.", fg="red")
        return
   
    attack_id = datetime.now().strftime(f"attack_{technique}_%Y-%m-%d_%H%M")
    attack_dir = os.path.join("scan_history", "attacks", attack_id)
    report_dir = os.path.join(attack_dir, "reports")
    os.makedirs(report_dir, exist_ok=True)
   
    json_path = os.path.join(report_dir, "raw_data.json")
    report_path = os.path.join(report_dir, "report.md")

    if technique == 'all':
        click.echo("[*] Generating the full 15-attack arsenal...")
        subprocess.run(["python", "attack_generator.py", "fuzz_files/attack_payloads"], check=True)
       
        click.echo("[*] Auditing all 15 attacks against scanners...")
        subprocess.run(["python", "attack_engine.py", "fuzz_files/attack_payloads", json_path], check=True)
        
        if not os.path.exists(json_path):
            click.secho("[-] Error: The attack engine failed to produce raw_data.json.", fg="red", bold=True)
            return
       
    elif technique == '7z':
        click.echo("[-] Please use --technique all for now.")
        return

    if json_output:
        with open(json_path, "r") as f:
            print(json.dumps(json.load(f), indent=4))
        return

    click.echo("[*] Generating Markdown report...")
    
    try:
        vuln_count = build_report(json_path, report_path, attack_id)
    except Exception as e:
        click.secho(f"[-] Error generating report: {e}", fg="red", bold=True)
        return
   
    click.secho(f"\n=========================================", fg="green")
    click.secho(f" [SUCCESS] {technique.upper()} ATTACK COMPLETE", fg="green", bold=True)
    click.secho(f"=========================================", fg="green")
    click.echo(f" Critical Bypasses (RCE Confirmed): {vuln_count}")
    click.echo(f" Scan ID: {attack_id}")
    click.echo(f" Report Saved: {report_path}")
    click.secho(f"=========================================\n", fg="green")


@click.command()
@click.option('--id', help='Delete a specific scan or attack by its folder ID.')
@click.option('--older-than', type=int, help='Delete all reports older than X days.')
@click.option('--all', 'delete_all', is_flag=True, help='Delete ALL scan and attack history.')
def delete(id, older_than, delete_all):
    """Delete old scan and attack reports to free up disk space."""
    flags_used = sum([bool(id), bool(older_than), bool(delete_all)])
    if flags_used == 0:
        click.secho("[-] Error: You must provide --id, --older-than, or --all.", fg="red")
        return
    if flags_used > 1:
        click.secho("[-] Error: Please use only one delete method at a time.", fg="red")
        return

    if id:
        found = False
        for category in ["scans", "attacks"]:
            path = os.path.join("scan_history", category, id)
            if os.path.exists(path):
                shutil.rmtree(path)
                click.secho(f"[+] Deleted: {path}", fg="green")
                found = True
        if not found:
            click.secho(f"[-] Error: Folder '{id}' not found in scans or attacks.", fg="red")

    elif older_than:
        cutoff_date = datetime.now() - timedelta(days=older_than)
        deleted_count = 0
        for category in ["scans", "attacks"]:
            base_dir = os.path.join("scan_history", category)
            if not os.path.exists(base_dir): continue
            for folder in os.listdir(base_dir):
                folder_path = os.path.join(base_dir, folder)
                if not os.path.isdir(folder_path): continue
                try:
                    date_str = folder.split("_")[1]
                    folder_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if folder_date < cutoff_date:
                        shutil.rmtree(folder_path)
                        deleted_count += 1
                except (IndexError, ValueError):
                    continue
        click.secho(f"[+] Deleted {deleted_count} reports older than {older_than} days.", fg="green")

    elif delete_all:
        click.secho(f"⚠️  WARNING: This will permanently delete ALL scan and attack history!", fg="yellow", bold=True)
        if click.confirm("Are you sure you want to proceed?"):
            deleted_count = 0
            for category in ["scans", "attacks"]:
                base_dir = os.path.join("scan_history", category)
                if not os.path.exists(base_dir): continue
                for folder in os.listdir(base_dir):
                    folder_path = os.path.join(base_dir, folder)
                    if os.path.isdir(folder_path):
                        shutil.rmtree(folder_path)
                        deleted_count += 1
            click.secho(f"[+] Successfully deleted all {deleted_count} history folders.", fg="green")
        else:
            click.secho("[-] Deletion cancelled.", fg="red")

cli.add_command(scan)
cli.add_command(attack)
cli.add_command(delete)

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        click.secho("\n\n[!] Scan interrupted by user. Exiting gracefully.", fg="yellow", bold=True)
        sys.exit(0)
