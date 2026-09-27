$procs = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|py\.exe' }
foreach ($p in $procs) {
  if ($p.CommandLine -match 'gateway|hermes') {
    Write-Output ("PID=" + $p.ProcessId + " START=" + $p.CreationDate + " CMD=" + $p.CommandLine)
  }
}
