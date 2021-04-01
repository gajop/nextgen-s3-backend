local function loadtable(scriptfile)
    local env = setmetatable({}, {__index=_G})
    local _, modinfo = pcall(setfenv(assert(loadfile(scriptfile)), env))
    setmetatable(env, nil)
    return modinfo
end

local file = arg[1]
local key = arg[2]
print(loadtable(file)[key])
