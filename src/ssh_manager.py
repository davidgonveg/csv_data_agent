import paramiko
import os
import io
import stat
from typing import List, Tuple, Optional

class SSHManager:
    def __init__(self):
        self.host = os.getenv("SSH_HOST")
        self.user = os.getenv("SSH_USER")
        self.password = os.getenv("SSH_PASSWORD")
        self.client = None

    def connect(self):
        """Establishes SSH connection."""
        if not all([self.host, self.user, self.password]):
            raise ValueError("SSH credentials missing in environment variables.")
        
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=self.host,
                username=self.user,
                password=self.password,
                timeout=10
            )
        except Exception as e:
            self.client = None
            raise ConnectionError(f"Failed to connect to {self.host}: {e}")

    def list_files(self, remote_dir: str, pattern: str = "*.csv") -> List[str]:
        """Lists files matching a pattern in a remote directory."""
        if not self.client:
            self.connect()
        
        try:
            # Use find to get only files
            stdin, stdout, stderr = self.client.exec_command(f"find {remote_dir} -maxdepth 1 -name '{pattern}' -type f")
            files = stdout.read().decode().splitlines()
            # Return only basenames
            return [os.path.basename(f) for f in files if f.strip()]
        except Exception as e:
            raise RuntimeError(f"Error listing files: {e}")

    def get_file(self, remote_path: str) -> io.BytesIO:
        """Downloads a remote file into memory."""
        if not self.client:
            self.connect()
            
        try:
            sftp = self.client.open_sftp()
            file_obj = io.BytesIO()
            sftp.getfo(remote_path, file_obj)
            file_obj.seek(0)
            sftp.close()
            # attribute name for app.py logic
            file_obj.name = os.path.basename(remote_path) 
            return file_obj
        except Exception as e:
            raise RuntimeError(f"Error downloading file {remote_path}: {e}")

    def get_mtime(self, remote_path: str) -> float:
        """Gets modification time of remote file."""
        if not self.client:
            self.connect()
            
        try:
            sftp = self.client.open_sftp()
            attr = sftp.stat(remote_path)
            sftp.close()
            return attr.st_mtime
        except Exception as e:
             # Fallback using command execution if sftp stat fails?
            return 0.0

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
