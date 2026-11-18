import os
import json
import sys
from audit import run_scanner, verify_execution

def run_all_attacks(attack_dir, output_json):
    results = []
    
    if not os.path.exists(attack_dir):
        print(f"[-] Error: Directory {attack_dir} not found.")
        sys.exit(1)

    folders = sorted([f for f in os.listdir(attack_dir) if os.path.isdir(os.path.join(attack_dir, f))])
    
    for folder in folders:
        folder_path = os.path.join(attack_dir, folder)
        print(f"[*] Testing Attack: {folder}")
        
        files = os.listdir(folder_path)
        if not files:
            continue
            
        target_file = None
        for f in files:
            if f.endswith(('.7z', '.pkl', '.pt', '.h5', '.tflite', '.joblib', '.onnx', '.npy', '.safetensors')):
                target_file = f
                break
        
        if not target_file:
            continue
            
        filepath = os.path.join(folder_path, target_file)
        file_result = {"technique": folder, "file_scanned": target_file}
        
        # PickleScan
        try:
            ps_cmd = f"python -m picklescan -p {filepath}"
            file_result["picklescan"], _ = run_scanner("PickleScan", ps_cmd)
        except Exception:
            file_result["picklescan"] = "ERROR"
        
        # ModelScan
        try:
            ms_cmd = f"{os.path.expanduser('~')}/.pyenv/versions/3.12.8/bin/modelscan -p {filepath}"
            file_result["modelscan"], _ = run_scanner("ModelScan", ms_cmd)
        except Exception:
            file_result["modelscan"] = "ERROR"
        
        # Fickling
        try:
            fk_cmd = f"python -m fickling {filepath}"
            fk_res = run_scanner("Fickling", fk_cmd)
            file_result["fickling"] = fk_res[0]
        except Exception:
            file_result["fickling"] = "ERROR"
        
        # FLAW 3 FIX: Add execution verification for attacks
        try:
            file_result["execution_proof"] = verify_execution(filepath)
        except Exception:
            file_result["execution_proof"] = "NOT_EXECUTED"
             
        results.append(file_result)

    with open(output_json, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"[+] Attack audit complete! Saved to {output_json}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python attack_engine.py <attack_dir> <output_json>")
        sys.exit(1)
        
    run_all_attacks(sys.argv[1], sys.argv[2])
