// EU addresses only, checked by scripts/check_addresses.py.
// Each block replaces "bl GetSpeedOption; cmp r0, #0; ... movne r1, #2; ... moveq r1, #1"
// with "bl SpeedGetMultiplier; mov r1, r0", turning the conditional moves into nops.

.nds
.include "symbols.asm"

.open "overlay29.bin", overlay29_start
  .org 0x2305778
    bl SpeedGetMultiplier
    mov r1, r0
    nop
  .org 0x2305788
    nop

  .org 0x2305800
    bl SpeedGetMultiplier
    mov r1, r0
    nop
  .org 0x2305810
    nop

  .org 0x2305A28
    bl SpeedGetMultiplier
    mov r1, r0
  .org 0x2305A34
    nop
  .org 0x2305A3C
    nop

  .org GetAndStoreButtonInput
    b SpeedButtonInputHook

  // WaitUntilAlertBoxPauseIsOver: "cmp r0, #180" against a speed-dependent threshold.
  .org 0x234C67C
    bl SpeedAlertPauseCompare
.close

// Text renderer: characters revealed per step ("ldreq r0, [r4, #100]") scaled by the speed.
.open "arm9.bin", arm9_start
  .org 0x2021028
    bleq SpeedTextSpeedHook
  .org 0x2021B04
    bleq SpeedTextSpeedHook

  .org UpdateAlertBox
    b SpeedUpdateAlertBox
.close
