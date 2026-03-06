Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap(2194, 1234)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, $bmp.Size)
$bmp.Save("A:\3DTools\HumanBodyWeb\blender_screenshot.png")
$g.Dispose()
$bmp.Dispose()
Write-Host "Screenshot saved"
