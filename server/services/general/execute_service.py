"""
HDM AI - Code Execution Service
Local execution via subprocess (Python + JavaScript via Node)
No external APIs, no Docker, no keys — works offline
"""

import subprocess
import tempfile
import os
import shutil
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from models.general.code_execution import CodeExecution


class ExecuteService:
    """Code execution using local runtimes."""

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
        """Execute code locally."""

        lang = language.lower()
        lang_config = self.SUPPORTED_LANGUAGES.get(lang)

        if not lang_config:
            return {
                "success": False,
                "error": f"Unsupported language: {language}. Supported: {', '.join(self.SUPPORTED_LANGUAGES.keys())}",
            }

        # Check if runtime is available
        if not self._check_runtime(lang_config["cmd"][0]):
            return {
                "success": False,
                "error": f"{language} runtime not found. Install it to enable local execution.",
            }

        execution = CodeExecution(
            user_id=user_id,
            language=language,
            code=code,
            stdin=stdin,
            status="processing",
        )
        await execution.insert()

        try:
            # Create temp directory
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write code to file
                filename = f"script.{lang_config['ext']}"
                filepath = os.path.join(tmpdir, filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code)

                # Run the code
                cmd = lang_config["cmd"] + [filepath]
                
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,  # 10 second timeout
                    cwd=tmpdir,
                    input=stdin if stdin else None,
                )

                stdout = process.stdout or ""
                stderr = process.stderr or ""
                exit_code = process.returncode

                execution.stdout = stdout
                execution.stderr = stderr
                execution.exit_code = exit_code
                execution.execution_time_ms = 0
                execution.status = "completed" if exit_code == 0 else "error"
                await execution.save()

                logger.info(f"Code executed locally: {language}, exit_code={exit_code}")

                return {
                    "success": True,
                    "execution_id": str(execution.id),
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": exit_code,
                    "status": execution.status,
                }

        except subprocess.TimeoutExpired:
            execution.status = "error"
            execution.stderr = "Execution timed out (10 second limit)"
            await execution.save()
            return {"success": False, "error": "Execution timed out (10 second limit)"}

        except Exception as e:
            execution.status = "error"
            execution.stderr = str(e)[:200]
            await execution.save()
            logger.error(f"Local execution failed: {e}")
            return {"success": False, "error": f"Execution failed: {str(e)[:100]}"}

    def _check_runtime(self, cmd: str) -> bool:
        """Check if a runtime is installed."""
        try:
            subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                timeout=3,
            )
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
        execution = await CodeExecution.get(execution_id)
        if not execution or execution.user_id != user_id:
            return None
        return {
            "execution_id": str(execution.id),
            "language": execution.language,
            "stdout": execution.stdout,
            "stderr": execution.stderr,
            "exit_code": execution.exit_code,
            "execution_time_ms": execution.execution_time_ms,
            "status": execution.status,
            "created_at": execution.created_at.isoformat(),
        }


execute_service = ExecuteService()