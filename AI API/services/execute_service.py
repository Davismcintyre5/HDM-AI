# ====================================================================================================
# HDM AI Engine — Execute Service (/v1/execute)
# Local code execution | No external API
# ====================================================================================================

import subprocess
import tempfile
import os
import uuid
from typing import Dict, Any
from loguru import logger


class ExecuteService:
    SUPPORTED = {
        "python": {"ext": "py", "cmd": ["python"]},
        "javascript": {"ext": "js", "cmd": ["node"]},
        "bash": {"ext": "sh", "cmd": ["bash"]},
    }

    async def execute(self, user_id: str, language: str, code: str, stdin: str = "") -> Dict[str, Any]:
        lang = language.lower()
        cfg = self.SUPPORTED.get(lang)
        if not cfg:
            return {"success": False, "error": f"Unsupported: {language}"}
        if not self._has_runtime(cfg["cmd"][0]):
            return {"success": False, "error": f"{language} runtime not installed."}

        execution_id = str(uuid.uuid4())[:8]

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                path = os.path.join(tmpdir, f"script.{cfg['ext']}")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(code)

                proc = subprocess.run(
                    cfg["cmd"] + [path], capture_output=True, text=True,
                    timeout=10, cwd=tmpdir, input=stdin or None,
                )

                logger.info(f"Executed {language} — exit {proc.returncode}")
                return {
                    "success": True,
                    "execution_id": execution_id,
                    "stdout": proc.stdout or "",
                    "stderr": proc.stderr or "",
                    "exit_code": proc.returncode,
                    "status": "completed" if proc.returncode == 0 else "error",
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution timed out (10s limit)"}
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {"success": False, "error": str(e)[:100]}

    def _has_runtime(self, cmd: str) -> bool:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, timeout=3)
            return True
        except Exception:
            return False

    async def get_languages(self) -> Dict[str, Any]:
        langs = []
        for name, cfg in self.SUPPORTED.items():
            available = self._has_runtime(cfg["cmd"][0])
            langs.append({"name": name, "available": available, "status": "ready" if available else "not installed"})
        return {"languages": langs}


execute_service = ExecuteService()