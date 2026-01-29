import subprocess
import os

# Path to clamscan.exe (update if not in PATH)
CLAMSCAN_PATH = os.environ.get('CLAMSCAN_PATH', 'clamscan')

def scan_file_with_clamav(file_path):
    """
    Scan a file using ClamAV's clamscan command-line tool.
    Returns (is_clean, output):
        is_clean: True if no virus found, False if infected or error
        output: clamscan output string
    """
    try:
        result = subprocess.run([
            CLAMSCAN_PATH,
            '--no-summary',
            file_path
        ], capture_output=True, text=True, timeout=60)
        output = result.stdout.strip() + '\n' + result.stderr.strip()
        if 'OK' in output and 'FOUND' not in output:
            return True, output
        else:
            return False, output
    except Exception as e:
        return False, f'Error running clamscan: {e}'
