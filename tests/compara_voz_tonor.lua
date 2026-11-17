-- Compara la cadena "Voz Tonor 6 · retorno reverb" (de-esser + EQ + ReaVerbate) con Nube Verb (parámetros en tests/out/cmp_params.txt:
-- "slider valor" por línea). Escribe tests/out/cmp/{orig,nube}_{impulse,noise_burst,vocal}.wav; analizar con tests/compara_voz_tonor.py
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out/cmp"; os.execute('mkdir -p "' .. OUT .. '"')
local logf = io.open(OUT .. "/log.txt", "w")
local params = {}
for line in io.lines(ROOT .. "/out/cmp_params.txt") do local k, v = line:match("(%d+)%s+([%-%d%.]+)"); if k then params[tonumber(k)] = tonumber(v) end end
local LOGP = {[5] = {0.1, 20, 2}, [11] = {0.05, 5, 0.6}, [12] = {0.25, 4, 1}, [13] = {50, 1000, 250}, [14] = {0.1, 2, 0.5},
              [15] = {1000, 16000, 4000}, [16] = {20, 1000, 150}, [17] = {1000, 20000, 5000}, [20] = {50, 2000, 300}}
local function to_norm(s, v) local mn, mx, mid = table.unpack(LOGP[s]); local sr = (mx - mn) / (mid - mn) - 1; local r = sr * sr
  return math.log((v - mn) / (mx - mn) * (r - 1) + 1) / math.log(r) end
reaper.Main_OnCommand(40859, 0)
reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true); reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.AddMediaItemToTrack(tr); local take = reaper.AddTakeToMediaItem(item)
reaper.SetMediaItemInfo_Value(item, "D_FADEINLEN", 0); reaper.SetMediaItemInfo_Value(item, "D_FADEOUTLEN", 0)
local only = io.open(OUT .. "/only_nube") ~= nil
for _, which in ipairs({"orig", "nube"}) do
  if which == "nube" or not only then
  for _, sig in ipairs({"impulse", "noise_burst", "vocal"}) do
    local path = ROOT .. "/signals/" .. sig .. ".wav"
    local s = reaper.PCM_Source_CreateFromFile(path); reaper.SetMediaItemTake_Source(take, s)
    reaper.SetMediaItemInfo_Value(item, "D_LENGTH", (reaper.GetMediaSourceLength(s))); reaper.UpdateItemInProject(item)
    while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
    if which == "orig" then
      reaper.TrackFX_AddByName(tr, "Claude/Voz Tonor 6 · retorno reverb.RfxChain", false, -1)
    else
      local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Verb/nube_verb.jsfx", false, -1)
      for k, v in pairs(params) do if LOGP[k] then reaper.TrackFX_SetParamNormalized(tr, fx, k - 1, to_norm(k, v)) else reaper.TrackFX_SetParam(tr, fx, k - 1, v) end end
    end
    logf:write(which, " ", sig, " fx=", reaper.TrackFX_GetCount(tr), "\n")
    local name = which .. "_" .. sig; os.remove(OUT .. "/" .. name .. ".wav")
    reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true); reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
    reaper.GetSetProjectInfo(0, "RENDER_SRATE", 48000, true); reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
    reaper.GetSetProjectInfo(0, "RENDER_TAILFLAG", 0, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true); reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
    reaper.Main_OnCommand(42230, 0)
  end
  end
end
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp.rpp", 0); reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp.rpp"); reaper.Main_OnCommand(40860, 0)
logf:write("done\n"); logf:close()
