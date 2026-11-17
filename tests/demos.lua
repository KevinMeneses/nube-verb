-- Renderiza la voz seca (14 s) por varios presets de Nube Verb en demos/*.wav
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/.."
local OUT = ROOT .. "/demos"
local SRC = ROOT .. "/tests/signals/vocal.wav"
local JOBS = {{0, "0 - seca"}, {1, "1 - Voz rap - placa corta"}, {3, "3 - Voz hook - sala amplia"}, {4, "4 - Voz chill - Nube oscura"},
              {5, "5 - Voz - ambiente corto"}, {12, "12 - Shimmer celestial"}, {13, "13 - Catedral"}}
reaper.Main_OnCommand(40859, 0)
reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true); reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.AddMediaItemToTrack(tr); local take = reaper.AddTakeToMediaItem(item)
local s = reaper.PCM_Source_CreateFromFile(SRC); reaper.SetMediaItemTake_Source(take, s)
reaper.SetMediaItemInfo_Value(item, "D_LENGTH", (reaper.GetMediaSourceLength(s))); reaper.UpdateItemInProject(item)
for _, j in ipairs(JOBS) do
  while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
  if j[1] > 0 then local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Verb/nube_verb.jsfx", false, -1); reaper.TrackFX_SetParam(tr, fx, 30, j[1]) end
  os.remove(OUT .. "/" .. j[2] .. ".wav")
  reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true); reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
  reaper.GetSetProjectInfo(0, "RENDER_SRATE", 48000, true); reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true); reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", j[2], true)
  reaper.Main_OnCommand(42230, 0)
end
reaper.Main_SaveProjectEx(0, ROOT .. "/tests/out/_tmp_demo.rpp", 0); reaper.Main_openProject("noprompt:" .. ROOT .. "/tests/out/_tmp_demo.rpp"); reaper.Main_OnCommand(40860, 0)
local f = io.open(OUT .. "/log.txt", "w"); f:write("done\n"); f:close()
