#Include functions.ahk

#Requires AutoHotkey v2.0

STR:='F1: Melee weapon (Toggle)`n`nF2: Semi guns(marksman & semi automatic) (Toggle)`n`nF3: Machine gun turret (Toggle)'

g := Gui("+AlwaysOnTop","Raid Macro -Unknown-")    

DESCRIPTION := g.Add("Text", "xm ym w400 +0x80", STR)
statusLbl := g.Add("Text", "xm y+8 w400", "Current Macro: None")
statusLbl.SetFont("cRed","Arial")
       
g.Show("w330 h100 Center")
global UpdateStatus := UpdateStatusFn
UpdateStatusFn(name := "", on := false) {
    
    global statusLbl, epixToggle, machineToggle, sniperToggle

    anyOn := epixToggle || machineToggle || sniperToggle

    if anyOn {
        
        current := epixToggle ? "Epix"
                : machineToggle ? "MachineGun"
                : sniperToggle ? "Sniper"
                : "None"

        statusLbl.Text := "Current Macro: " (on ? name : current)
        statusLbl.SetFont("cGreen")   
    } else {
        statusLbl.Text := "Current Macro: None"
        statusLbl.SetFont("cRed")     
    }
}
F1::Epix()
F2::Sniper()
F3::MachineGun()