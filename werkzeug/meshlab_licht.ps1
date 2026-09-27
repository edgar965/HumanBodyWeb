# meshlab_licht.ps1 — MeshLabs Beleuchtung auf reines Umgebungslicht stellen.
#
#   powershell -File meshlab_licht.ps1            # ambient (keine Schattierung)
#   powershell -File meshlab_licht.ps1 -Zurueck   # MeshLabs Werkswerte
#
# WOZU: MeshLab beleuchtet mit EINER gerichteten Lichtquelle (diffus 204,
# spekular 255) plus schwachem Umgebungslicht (32). Auf einem einfarbigen
# Stück — dem Kleid der Genesis-9-Figur — macht das aus der gekrümmten
# Fläche ein Muster aus hellen und dunklen Feldern, das wie ein Texturfehler
# aussieht und keiner ist (Edgar, 26.09.2026: „diese Schattierungen des
# Kleides sehen noch unnatürlich aus … ich möchte die nicht sehen").
#
# Mit Umgebungslicht 255 und Diffus/Spekular 0 zeigt jede Fläche genau ihre
# eigene Farbe bzw. Textur — flach, ohne Lichtmodell. Das ist zum PRÜFEN
# eines Exports das Richtige: man sieht die Daten, nicht die Beleuchtung.
#
# MeshLab liest diese Werte beim Start und schreibt sie beim Beenden zurück —
# das Skript darf also nur bei GESCHLOSSENEM MeshLab laufen.
param([switch]$Zurueck)

$schluessel = 'HKCU:\Software\VCG\MeshLab_64bit_fp'

$laeuft = Get-Process meshlab -ErrorAction SilentlyContinue
if ($laeuft) {
    Write-Host 'MeshLab läuft noch — erst schließen, sonst überschreibt es die Werte beim Beenden.'
    exit 1
}

# name = @(r, g, b, beschreibung)
$werte = if ($Zurueck) {
    @{
        'baseLightAmbientColor'  = @(32, 32, 32, 'MeshLab Base Light Ambient Color')
        'baseLightDiffuseColor'  = @(204, 204, 204, 'MeshLab Base Light Diffuse Color')
        'baseLightSpecularColor' = @(255, 255, 255, 'MeshLab Base Light Specular Color')
    }
} else {
    @{
        'baseLightAmbientColor'  = @(255, 255, 255, 'MeshLab Base Light Ambient Color')
        'baseLightDiffuseColor'  = @(0, 0, 0, 'MeshLab Base Light Diffuse Color')
        'baseLightSpecularColor' = @(0, 0, 0, 'MeshLab Base Light Specular Color')
    }
}

foreach ($kurz in $werte.Keys) {
    $v = $werte[$kurz]
    $name = "MeshLab::Appearance::$kurz"
    $xml = '<!DOCTYPE MeshLabSettings>' + "`r`n" +
           ('<Param g="{0}" b="{1}" a="255" type="RichColor" tooltip="" r="{2}" name="{3}" description="{4}"/>' -f
            $v[1], $v[2], $v[0], $name, $v[3]) + "`r`n"
    Set-ItemProperty -Path $schluessel -Name $name -Value $xml -Type String
    Write-Host ("{0} = r{1} g{2} b{3}" -f $kurz, $v[0], $v[1], $v[2])
}
Write-Host 'Fertig. MeshLab neu starten.'
