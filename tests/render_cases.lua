-- Carga Nube Verb en una pestaña nueva, renderiza cada caso y cierra la pestaña.
-- Uso: REAPER -nonewinst tests/render_cases.lua   (escribe tests/out/*.wav y tests/out/log.txt)
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
os.execute('mkdir -p "' .. OUT .. '"')
local logf = io.open(OUT .. "/log.txt", "w")
local function log(...) local t = {} for _, v in ipairs({...}) do t[#t+1] = tostring(v) end logf:write(table.concat(t, " "), "\n") logf:flush() end

-- slider N (1..31) = parámetro N-1. Los sliders con forma :log=mid van normalizados 0..1
local LOGP = {[5] = {0.1, 20, 2}, [11] = {0.05, 5, 0.6}, [12] = {0.25, 4, 1}, [13] = {50, 1000, 250}, [14] = {0.1, 2, 0.5},
              [15] = {1000, 16000, 4000}, [16] = {20, 1000, 150}, [17] = {1000, 20000, 5000}, [20] = {50, 2000, 300}}
local function to_norm(s, v)
  local mn, mx, mid = table.unpack(LOGP[s])
  local sr = (mx - mn) / (mid - mn) - 1; local r = sr * sr
  return math.log((v - mn) / (mx - mn) * (r - 1) + 1) / math.log(r)
end
-- base: Sala, envío (100 % húmeda), sin tempranas, sin pre-delay, sin modulación, decay plano
local function W(t)
  local r = {[1] = 3, [28] = 1, [8] = 0, [3] = 0, [10] = 0, [12] = 1, [14] = 1, [5] = 2}
  for k, v in pairs(t) do r[k] = v end
  return r
end
local function with(a, b) local r = {} for k, v in pairs(a) do r[k] = v end for k, v in pairs(b) do r[k] = v end return r end

local CASES = {
  {"mix0",        "sine1k.wav",      {[2] = 0}},
  {"mix50",       "sine1k.wav",      {[2] = 50, [3] = 500}},
  {"out_m6",      "sine1k.wav",      {[2] = 0, [29] = -6}},
  {"envio",       "impulse.wav",     {[28] = 1, [3] = 50}},
  {"rt05",        "impulse.wav",     W{[5] = 0.5}},
  {"rt2",         "impulse.wav",     W{[5] = 2}},
  {"rt6",         "impulse.wav",     W{[5] = 6}},
  {"rt2_eco",     "impulse.wav",     W{[5] = 2, [30] = 1}},
  {"rt2_mod",     "impulse.wav",     W{[5] = 2, [10] = 100}},
  {"rt2_low2",    "impulse.wav",     W{[5] = 2, [12] = 2, [13] = 300}},
  {"rt2_high03",  "impulse.wav",     W{[5] = 2, [14] = 0.3, [15] = 2000}},
  {"pre100",      "impulse.wav",     W{[3] = 100, [8] = 50}},
  {"sync18",      "impulse.wav",     W{[4] = 7, [8] = 50}},
  {"width0",      "impulse.wav",     W{[9] = 0, [8] = 50}},
  {"width100",    "impulse.wav",     W{[9] = 100, [8] = 50}},
  {"lc_off",      "noise_burst.wav", W{}},
  {"lc500",       "noise_burst.wav", W{[16] = 500}},
  {"hc2k",        "noise_burst.wav", W{[17] = 2000}},
  {"era70",       "noise_burst.wav", W{[26] = 2}},
  {"duck_off",    "noise_burst.wav", W{[5] = 3}},
  {"duck12",      "noise_burst.wav", W{[5] = 3, [19] = 12, [21] = -40, [20] = 200}},
  {"gate_off",    "short_burst.wav", W{[5] = 3}},
  {"gate",        "short_burst.wav", W{[5] = 3, [22] = -40, [23] = 200}},
  {"shim_off",    "sine440_burst.wav", W{[5] = 4}},
  {"shim60",      "sine440_burst.wav", W{[5] = 4, [24] = 60}},
  {"shim_max",    "impulse.wav",     W{[5] = 20, [24] = 100, [14] = 2, [12] = 4}},
  {"shim_down",   "sine440_burst.wav", W{[5] = 4, [24] = 60, [25] = 5}},
  {"ess_off",     "ess.wav",         W{[5] = 1.5}},
  {"ess12",       "ess.wav",         W{[5] = 1.5, [18] = 12}},
  {"vowel_off",   "vowel.wav",       W{[5] = 1.5}},
  {"vowel12",     "vowel.wav",       W{[5] = 1.5, [18] = 12}},
  {"freeze",      "noise_burst.wav", W{[5] = 2}, {27, 1.5, 1}},
  {"big_mod_max", "impulse.wav",     W{[5] = 20, [6] = 100, [1] = 4, [10] = 100, [11] = 5, [12] = 4, [14] = 2}},
  {"tiny",        "impulse.wav",     W{[5] = 0.1, [6] = 0, [1] = 1}},
}
for m = 0, 5 do CASES[#CASES + 1] = {"mode" .. m, "impulse.wav", W{[1] = m, [8] = 50, [7] = 80}} end
for p = 1, 27 do CASES[#CASES + 1] = {"preset" .. p, "noise_burst.wav", {[31] = p}} end

reaper.Main_OnCommand(40859, 0) -- nueva pestaña
reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true)
reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
reaper.SetCurrentBPM(0, 120, false)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.AddMediaItemToTrack(tr)
local take = reaper.AddTakeToMediaItem(item)
reaper.SetMediaItemInfo_Value(item, "D_POSITION", 0)
reaper.SetMediaItemInfo_Value(item, "D_FADEINLEN", 0); reaper.SetMediaItemInfo_Value(item, "D_FADEOUTLEN", 0)
local only = os.getenv("NUBE_CASE")

for _, c in ipairs(CASES) do
  local name, src, params, env = c[1], c[2], c[3], c[4]
  if not only or name:find(only) then
    local s = reaper.PCM_Source_CreateFromFile(ROOT .. "/signals/" .. src)
    reaper.SetMediaItemTake_Source(take, s)
    reaper.SetMediaItemInfo_Value(item, "D_LENGTH", (reaper.GetMediaSourceLength(s)))
    reaper.UpdateItemInProject(item)
    while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
    local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Verb/nube_verb.jsfx", false, -1)
    if fx < 0 or reaper.TrackFX_GetNumParams(tr, fx) < 31 then log("ERROR no cargó el FX") break end
    if params[31] then reaper.TrackFX_SetParam(tr, fx, 30, params[31]) end
    for s_, v in pairs(params) do
      if s_ ~= 31 then
        if LOGP[s_] then reaper.TrackFX_SetParamNormalized(tr, fx, s_ - 1, to_norm(s_, v))
        else reaper.TrackFX_SetParam(tr, fx, s_ - 1, v) end
      end
    end
    if env then  -- {slider, tiempo, valor}: envolvente de un paso
      local e = reaper.GetFXEnvelope(tr, fx, env[1] - 1, true)
      reaper.InsertEnvelopePoint(e, 0, 0, 1, 0, false, true)
      reaper.InsertEnvelopePoint(e, env[2], env[3], 1, 0, false, true)
      reaper.Envelope_SortPoints(e)
    end
    local file = OUT .. "/" .. name .. ".wav"
    os.remove(file)
    reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true)
    reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
    reaper.GetSetProjectInfo(0, "RENDER_SRATE", 48000, true)
    reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
    reaper.GetSetProjectInfo(0, "RENDER_TAILFLAG", 0, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
    local t0 = reaper.time_precise()
    reaper.Main_OnCommand(42230, 0)
    local vals = {}
    for _, k in ipairs({1, 2, 3, 5, 6, 8, 12, 14, 16, 17, 19, 22, 24, 28}) do local _, v = reaper.TrackFX_GetFormattedParamValue(tr, fx, k - 1, ""); vals[#vals + 1] = v end
    log("caso", name, string.format("%.2fs", reaper.time_precise() - t0), table.concat(vals, " | "))
  end
end
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_test.rpp", 0)
reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_test.rpp")
reaper.Main_OnCommand(40860, 0) -- cerrar pestaña
log("done")
logf:close()
