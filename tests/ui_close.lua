-- Detiene y cierra la pestaña de demo sin preguntar.
local OUT = os.getenv("HOME") .. "/Music/NubeVerb/tests/out"
reaper.OnStopButton()
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_ui.rpp", 0)
reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_ui.rpp")
reaper.Main_OnCommand(40860, 0)
