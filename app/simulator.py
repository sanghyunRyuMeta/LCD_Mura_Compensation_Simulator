import subprocess
from app.config import SIMULATOR_DIR, ENC_EXE, DEC_EXE


class Simulator:
    def __init__(self, log_callback):
        self._log = log_callback

    def run_encoder(self, panel: str, reg: str):
        cmd = [ENC_EXE, panel, reg]
        self._execute("ENC", cmd)

    def run_decoder(self, panel: str, reg: str, mode: str, last_arg: str):
        cmd = [DEC_EXE, panel, reg, mode, last_arg]
        self._execute("DEC", cmd)

    def run_both(self, panel: str, reg: str, mode: str, last_arg: str):
        self.run_encoder(panel, reg)
        self.run_decoder(panel, reg, mode, last_arg)

    def _execute(self, label: str, command: list[str]):
        self._log(f"\n{'='*60}\n[{label}] Running: {' '.join(command)}\n{'='*60}\n")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=SIMULATOR_DIR,
            )
            if result.stdout:
                self._log(f"[{label}] stdout:\n{result.stdout}\n")
            if result.stderr:
                self._log(f"[{label}] stderr:\n{result.stderr}\n")
            self._log(f"[{label}] Finished (return code {result.returncode})\n")
        except FileNotFoundError:
            self._log(f"[{label}] ERROR: Executable not found. Check Simulator folder.\n")
        except Exception as e:
            self._log(f"[{label}] ERROR: {e}\n")
