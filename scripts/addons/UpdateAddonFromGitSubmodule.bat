
set param=/e /r:10 /w:1 /bytes /fp
robocopy "Capsule_GIT\Capsule" "Capsule" %param%
copy "RenderBurst_GIT\RenderBurst.py" .

pause