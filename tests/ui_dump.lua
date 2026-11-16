-- Escribe los parámetros del Nube Verb de la pista 1 (pestaña actual) en tests/out/dump.txt
local OUT = os.getenv("HOME") .. "/Music/NubeVerb/tests/out"
local f = io.open(OUT .. "/dump.txt", "w")
local tr = reaper.GetTrack(0, 0)
for p = 0, 29 do
  local _, n = reaper.TrackFX_GetParamName(tr, 0, p, ""); local _, v = reaper.TrackFX_GetFormattedParamValue(tr, 0, p, "")
  f:write(p + 1, " ", n, " = ", v, "\n")
end
f:write("done\n"); f:close()
