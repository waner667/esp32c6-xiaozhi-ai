# 编译成功后把 5 个固件文件更新到烧录包 —— 用法：& "<repo>\pack_flash.ps1"
$src = '<repo>\me\xiaozhi-esp32-2.5.2\build'
$dst = '<repo>\flash_c6_tf1990'
$log = '<repo>\flash_pack.log'

New-Item -ItemType Directory -Path $dst -Force | Out-Null
$files = @('bootloader\bootloader.bin','partition_table\partition-table.bin','ota_data_initial.bin','xiaozhi.bin','generated_assets.bin')
$out = @('=== ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ===')
$missing = 0

foreach ($f in $files) {
  $p = Join-Path $src $f
  $leaf = Split-Path $f -Leaf
  if (Test-Path -LiteralPath $p) {
    Copy-Item -LiteralPath $p -Destination $dst -Force
    $i = Get-Item (Join-Path $dst $leaf)
    $out += ('OK      {0,-24} {1,9}  {2}' -f $leaf, $i.Length, $i.LastWriteTime)
  } else {
    $out += ('MISSING ' + $f)
    $missing++
  }
}

# 显示关键日志判定
$blog = '<repo>\build_final8.log'
if (Test-Path -LiteralPath $blog) {
  $c = Get-Content $blog
  $hit = $c | Select-String -Pattern 'BUILD_EXIT|Successfully created|error:|ninja: build stopped' | Select-Object -Last 5
  $out += '--- build_final8 判定 ---'
  if ($hit) { $out += ($hit | ForEach-Object { $_.Line }) } else { $out += '(无关键行，编译未完成)' }
}

$out += ('PACK_MISSING=' + $missing)
$out | Out-File -FilePath $log -Encoding utf8
$out | Write-Output