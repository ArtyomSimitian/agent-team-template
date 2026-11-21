<#
.SYNOPSIS
  Start the agent mission-control dashboard at http://localhost:8501 (only reachable from this PC).
  If the project has its own Streamlit app, run that on port 8502.
#>
Set-Location (Split-Path $PSScriptRoot -Parent)
& .\.venv\Scripts\python.exe -m streamlit run ops\monitor.py --server.address localhost --server.port 8501
