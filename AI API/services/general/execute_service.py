# ====================================================================================================
# HDM AI Engine - Code Execution Service
# Local execution via subprocess | No DB, stateless
# ====================================================================================================

import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
from loguru import logger
import uuid


class ExecuteService:
    """Code execution using local runtimes. No DB — MERN logs if needed."""

    SUPPORTED_LANGUAGES = {
        "python": {"ext": "py", "cmd": ["python"], "check": "python --version"},
        "javascript": {"ext": "js", "cmd": ["node"], "check": "node --version"},
        "bash": {"ext": "sh", "cmd": ["bash"], "check": "bash --version"},
    }

    async def execute(
        self,
        user_id: str,
        language: str,
        code: str,
        stdin: str = "",
    ) -> Dict[str, Any]:
        """Execute code locally. Returns result, no DB save."""

        lang = language.lower()
        lang_config = self.SUPPORTED_LANGUAGES.get(lang)

        if not lang_config:
            return {
                "success": False,
                "error": f"Unsupported language: {language}. Supported: {', '.join(self.SUPPORTED_LANGUAGES.keys())}",
            }

        if not self._check_runtime(lang_config["cmd"][0]):
            return {
                "success": False,
                "error": f"{language} runtime not found. Install it to enable local execution.",
            }

        execution_id = str(uuid.uuid4())[:8]

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                filename = f"script.{lang_config['ext']}"
                filepath = os.path.join(tmpdir, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code)

                cmd = lang_config["cmd"] + [filepath]

                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=tmpdir,
                    input=stdin if stdin else None,
                )

                stdout = process.stdout or ""
                stderr = process.stderr or ""
                exit_code = process.returncode

                logger.info(f"Code executed: {language}, exit={exit_code}")

                return {
                    "success": True,
                    "execution_id": execution_id,
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": exit_code,
                    "status": "completed" if exit_code == 0 else "error",
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution timed out (10 second limit)"}

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {"success": False, "error": f"Execution failed: {str(e)[:100]}"}

    def _check_runtime(self, cmd: str) -> bool:
        """Check if a runtime is installed."""
        try:
            subprocess.run([cmd, "--version"], capture_output=True, timeout=3)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages with availability."""
        languages = []
        for name, config in self.SUPPORTED_LANGUAGES.items():
            available = self._check_runtime(config["cmd"][0])
            languages.append({
                "name": name,
                "available": available,
                "status": "ready" if available else "not installed",
            })
        return {"languages": languages}

    async def get_execution(self, execution_id: str, user_id: str) -> Optional[Dict]:
        """Execution history is managed by MERN. Returns None if not in cache."""
        return None


execute_service = ExecuteService()