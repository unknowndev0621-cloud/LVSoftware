#Requires AutoHotkey v2.0
CoordMode "Mouse", "Screen"

; ── 토글 상태 전역 변수
epixToggle    := false
machineToggle := false
sniperToggle  := false



Epix() {
    global epixToggle, UpdateStatus
    if !epixToggle {
        Send("{RButton down}")
        Send("{LButton down}")
        epixToggle := true
        if IsSet(UpdateStatus)
            UpdateStatus("Epix", true)
    } else {
        Send("{RButton up}")
        Send("{LButton up}")
        epixToggle := false
        if IsSet(UpdateStatus)
            UpdateStatus("Epix", false)
    }
}

MachineGun() {
    global machineToggle, UpdateStatus
    machineToggle := !machineToggle
    if (machineToggle) {
        Send("{Space down}")
        SetTimer(AmmoClick_MG, 5000)          ; 5초마다 좌클릭 (MG 전용)
        if IsSet(UpdateStatus)
            UpdateStatus("MachineGun", true)
    } else {
        Send("{Space up}")
        SetTimer(AmmoClick_MG, 0)
        if IsSet(UpdateStatus)
            UpdateStatus("MachineGun", false)
    }
}
AmmoClick_MG() {
    Click(1343, 385)                           ; v2 문법
}

Sniper() {
    global sniperToggle, UpdateStatus
    sniperToggle := !sniperToggle
    if (sniperToggle) {
        Send("{RButton down}")                  ; 우클릭 홀드
        SetTimer(LeftClickOnce, 1000)          ; 1초마다 우클릭
                ; 5초마다 (1343,385) 좌클릭
        if IsSet(UpdateStatus)
            UpdateStatus("Sniper", true)
    } else {
        Send("{RButton up}")
        SetTimer(LeftClickOnce, 0)
        
        if IsSet(UpdateStatus)
            UpdateStatus("Sniper", false)
    }
}
LeftClickOnce() {
    Click                                  ; 현재 위치에서 우클릭 1회
}

