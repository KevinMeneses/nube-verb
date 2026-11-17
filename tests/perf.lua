-- CPU: render de 60 s sin plugin y con 10 instancias (peor caso: Catedral, 16 líneas, shimmer, anti-eses, filtros, ducking, gate).
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local AUDIO = os.getenv("HOME") .. "/Music/ClaudeBeats/Master/Nube baja (master X20).wav"
local f = io.open(OUT .. "/perf.txt", "w")
reaper.Main_OnCommand(40859, 0)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.AddMediaItemToTrack(tr); local take = reaper.AddTakeToMediaItem(item)
reaper.SetMediaItemTake_Source(take, reaper.PCM_Source_CreateFromFile(AUDIO))
reaper.SetMediaItemInfo_Value(item, "D_LENGTH", 60)
local function render(name, nfx, setup)
  while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
  for k = 1, nfx do local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Verb/nube_verb.jsfx", false, -1); setup(fx) end
  os.remove(OUT .. "/" .. name .. ".wav")
  reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true); reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true); reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
  local t0 = reaper.time_precise(); reaper.Main_OnCommand(42230, 0); return reaper.time_precise() - t0
end
local t_empty = render("perf_vacio", 0, function() end)
local function worst(fx, eco)
  for p, v in pairs({[0] = 4, [1] = 30, [17] = 6, [18] = 6, [21] = -40, [23] = 30, [29] = eco}) do reaper.TrackFX_SetParam(tr, fx, p, v) end
  reaper.TrackFX_SetParamNormalized(tr, fx, 15, 0.3); reaper.TrackFX_SetParamNormalized(tr, fx, 16, 0.6)
end
local t_full = render("perf_todo", 10, function(fx) worst(fx, 0) end)
local t_eco = render("perf_eco", 10, function(fx) worst(fx, 1) end)
local t_basic = render("perf_basico", 10, function(fx) end)
f:write(string.format("sin plugin %.2f s | 10 instancias (60 s de audio): peor caso %.2f s, eco %.2f s, por defecto %.2f s\n", t_empty, t_full, t_eco, t_basic))
f:write(string.format("por instancia (%% de un nucleo): peor %.1f, eco %.1f, defecto %.1f\n", (t_full - t_empty) / 600 * 100, (t_eco - t_empty) / 600 * 100, (t_basic - t_empty) / 600 * 100))
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_perf.rpp", 0); reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_perf.rpp"); reaper.Main_OnCommand(40860, 0)
f:write("done\n"); f:close()
