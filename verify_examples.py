import os
import subprocess
import sys

def run_example(example_path):
    print(f"Running {example_path}...")
    try:
        # Run the example in its own directory to handle relative paths if any
        example_dir = os.path.dirname(example_path)
        example_file = os.path.basename(example_path)
        # Add src to PYTHONPATH
        env = os.environ.copy()
        src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
        env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")

        result = subprocess.run(
            [sys.executable, example_file],
            cwd=example_dir,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        if result.returncode == 0:
            print(f"✅ {example_path} passed")
            return True
        else:
            print(f"❌ {example_path} failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏳ {example_path} timed out")
        return False
    except Exception as e:
        print(f"🔥 {example_path} failed with exception: {e}")
        return False

def find_examples(base_dir):
    examples = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == "example.py":
                examples.append(os.path.join(root, file))
    return sorted(examples)

def main():
    examples_dir = "examples"
    examples = find_examples(examples_dir)
    if not examples:
        print("No examples found.")
        return

    failed = []
    for example in examples:
        if not run_example(example):
            failed.append(example)

    print("\n" + "="*40)
    if not failed:
        print("🎉 All examples passed!")
    else:
        print(f"🔴 {len(failed)} examples failed:")
        for f in failed:
            print(f"  - {f}")
        sys.exit(1)

if __name__ == "__main__":
    main()
