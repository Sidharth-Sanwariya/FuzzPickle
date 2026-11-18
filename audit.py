import os
import subprocess
import json
import sys

def verify_execution(filepath):
    import py7zr
    import tempfile
    import shutil
    
    proof_file = "/tmp/fuzzpickle_pwned"
    if os.path.exists(proof_file):
        os.remove(proof_file)
        
    try:
        # SCENARIO 1: The 7z Container Bypass
        if filepath.endswith('.7z'):
            # Create a temp directory to unzip the file
            temp_dir = tempfile.mkdtemp()
            with py7zr.SevenZipFile(filepath, mode='r') as z:
                z.extractall(path=temp_dir)
            
            # Find the inner pickle and execute it
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.pkl'):
                        inner_pkl = os.path.join(root, file)
                        cmd = f"python -c \"import pickle; pickle.load(open('{inner_pkl}', 'rb'))\""
                        subprocess.run(cmd, shell=True, timeout=5, capture_output=True)
            
            # Clean up
            shutil.rmtree(temp_dir)

        # SCENARIO 2: The auto_map / SafeTensors Bypass
        elif filepath.endswith('.safetensors'):
            folder = os.path.dirname(filepath)
            py_files = [f for f in os.listdir(folder) if f.endswith('.py')]
            if py_files:
                cmd = f"python {os.path.join(folder, py_files[0])}"
                subprocess.run(cmd, shell=True, timeout=5, capture_output=True)
                
        # SCENARIO 3: Standard Pickle Execution
        else:
            cmd = f"python -c \"import pickle; data = open('{filepath}', 'rb').read(); pickle.loads(data[4:])\""
            subprocess.run(cmd, shell=True, timeout=5, capture_output=True)
            
    except Exception:
        pass
        
    if os.path.exists(proof_file):
        os.remove(proof_file)
        return "EXECUTED"
    return "NOT_EXECUTED"

def run_scanner(scanner_name, command):
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=15
        )
        output = result.stdout + result.stderr
        output_lower = output.lower()
        
        if "no issues found" in output_lower and "skipped" in output_lower:
            return "SAFE (BYPASSED)", output.strip()
            
        if result.returncode != 0:
            return "CRASH", output.strip()
        
        if scanner_name == "PickleScan":
            if "infected files: 0" not in output_lower and "infected files" in output_lower:
                return "DANGEROUS", output.strip()
            if "dangerous globals: 0" not in output_lower and "dangerous globals" in output_lower:
                return "DANGEROUS", output.strip()
            return "SAFE", output.strip()

        if "dangerous" in output_lower or "malicious" in output_lower or "suspicious" in output_lower:
            return "DANGEROUS", output.strip()
        else:
            return "SAFE", output.strip()

    except KeyboardInterrupt:
        print("\n[!] Audit stopped by user.")
        sys.exit(0)
            
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "Scanner hung."
    except Exception as e:
        return "ERROR", str(e)

def main(fuzz_dir, output_json):
    results = []
    
    if not os.path.exists(fuzz_dir):
        print(f"[-] Error: Folder {fuzz_dir} not found.")
        return

    files = [f for f in os.listdir(fuzz_dir) if f.endswith(('.pkl', '.pt', '.bin', '.p', '.npy', '.txt'))]
    
    for filename in files:
        filepath = os.path.join(fuzz_dir, filename)
        print(f"[*] Analyzing {filename}...")
        
        file_result = {"file": filename}
        
        # PickleScan
        ps_cmd = f"python -m picklescan -p {filepath}"
        file_result["picklescan"], _ = run_scanner("PickleScan", ps_cmd)
        
        # ModelScan
        ms_cmd = f"{os.path.expanduser('~')}/.pyenv/versions/3.12.8/bin/modelscan -p {filepath}"
        file_result["modelscan"], _ = run_scanner("ModelScan", ms_cmd)
        
        # Fickling
        fk_cmd = f"python -m fickling {filepath}"
        fk_res = run_scanner("Fickling", fk_cmd)
        if fk_res[0] == "CRASH" and "dangerous" in fk_res[1].lower():
             file_result["fickling"] = "DANGEROUS"
        else:
             file_result["fickling"] = fk_res[0]
             
        # Verify if the payload actually executes
        file_result["execution_proof"] = verify_execution(filepath)
        
        results.append(file_result)

    with open(output_json, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"[+] Audit complete! Data saved to {output_json}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("[-] Error: Missing arguments. Usage: python audit.py <directory_to_scan> <output_json_path>")
        sys.exit(1)
    
    fuzz_dir = sys.argv[1]
    output_json = sys.argv[2]
    main(fuzz_dir, output_json)
