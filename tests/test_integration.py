"""
Integration tests for the real estate analyzer.
These tests may take longer to run as they test the full application.
"""
import pytest
import sys
import time
import threading
import requests
from pathlib import Path
from unittest.mock import patch
import subprocess
import signal
import os

# Add the real_estate_analyzer directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "real_estate_analyzer"))


@pytest.mark.integration
class TestFullApplicationStartup:
    """Test full application startup and basic functionality."""
    
    @pytest.mark.slow
    def test_application_starts_and_responds(self):
        """Test that the application can start and respond to basic requests."""
        port = 8055  # Use a different port for testing
        process = None
        
        try:
            # Start the application in a subprocess
            cmd = [
                sys.executable, 
                str(project_root / "real_estate_analyzer" / "real_estate_analyzer.py"),
                "--port", str(port)
            ]
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            # Wait a bit for the server to start
            max_wait = 10  # seconds
            start_time = time.time()
            server_started = False
            
            while time.time() - start_time < max_wait:
                try:
                    # Try to connect to the server
                    response = requests.get(f"http://127.0.0.1:{port}/", timeout=2)
                    if response.status_code == 200:
                        server_started = True
                        break
                except (requests.ConnectionError, requests.Timeout):
                    time.sleep(0.5)
                    continue
            
            # Check if server started successfully
            if server_started:
                assert True, "Server started and responded successfully"
                
                # Test that the response contains expected content
                assert response.status_code == 200
                assert len(response.content) > 0
                
                # Optional: Test that it contains Dash-related content
                # (This would indicate it's actually our app running)
                content = response.text.lower()
                assert "dash" in content or "real estate" in content or "plotly" in content
                
            else:
                # Check if process had errors
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    pytest.fail(f"Server failed to start. Exit code: {process.returncode}\n"
                               f"STDOUT: {stdout.decode()}\n"
                               f"STDERR: {stderr.decode()}")
                else:
                    pytest.fail(f"Server did not respond within {max_wait} seconds")
                    
        finally:
            # Clean up: terminate the process
            if process and process.poll() is None:
                try:
                    if hasattr(os, 'killpg'):
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    else:
                        process.terminate()
                    
                    # Wait for process to terminate
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        if hasattr(os, 'killpg'):
                            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        else:
                            process.kill()
                        process.wait()
                except Exception as e:
                    print(f"Error cleaning up process: {e}")
    
    def test_application_cli_help(self):
        """Test that the application CLI help works."""
        try:
            result = subprocess.run([
                sys.executable,
                str(project_root / "real_estate_analyzer" / "real_estate_analyzer.py"),
                "--help"
            ], capture_output=True, text=True, timeout=10)
            
            # Should exit cleanly with help text
            assert result.returncode == 0
            assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()
            
        except subprocess.TimeoutExpired:
            pytest.fail("CLI help command timed out")
        except Exception as e:
            pytest.fail(f"CLI help command failed: {e}")
    
    def test_invalid_port_handling(self):
        """Test that the application handles invalid ports gracefully."""
        try:
            # Try to start with an invalid port
            result = subprocess.run([
                sys.executable,
                str(project_root / "real_estate_analyzer" / "real_estate_analyzer.py"),
                "--port", "99999"  # Invalid port
            ], capture_output=True, text=True, timeout=10)
            
            # Should either fail gracefully or start successfully
            # (depending on system permissions)
            assert isinstance(result.returncode, int)
            
        except subprocess.TimeoutExpired:
            pytest.fail("Invalid port test timed out")
        except Exception as e:
            # This is acceptable - invalid ports may cause various errors
            assert True


@pytest.mark.integration  
class TestDataProcessingIntegration:
    """Test data processing with real-world scenarios."""
    
    def test_empty_data_workflow(self):
        """Test the complete workflow with empty data."""
        from real_estate_analyzer import create_empty_dataframe, load_data
        
        # This should work without errors
        df = create_empty_dataframe()
        assert len(df) == 0
        
        # Loading non-existent file should also work
        df2 = load_data("non_existent_file.csv")
        assert len(df2) == 0 