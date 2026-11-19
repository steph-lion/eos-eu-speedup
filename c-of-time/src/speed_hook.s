.align 4
.global SpeedButtonInputHook
SpeedButtonInputHook:
  push {r4, lr}
  bl   SpeedOrigGetAndStoreButtonInput
  bl   SpeedOnButtonInput
  pop  {r4, pc}

.align 4
SpeedOrigGetAndStoreButtonInput:
  push {r3, lr}
  b    GetAndStoreButtonInput+4

.align 4
.global SpeedAlertPauseCompare
SpeedAlertPauseCompare:
  push {r1, lr}
  ldr  r1, =SpeedAlertPauseThreshold
  ldr  r1, [r1]
  cmp  r0, r1
  pop  {r1, pc}
.pool

.align 4
.global SpeedTextSpeedHook
SpeedTextSpeedHook:
  push {r1, lr}
  ldr  r0, [r4, #100]
  ldr  r1, =SpeedMultiplier
  ldr  r1, [r1]
  mul  r0, r1, r0
  pop  {r1, pc}
.pool

.align 4
.global SpeedOrigUpdateAlertBox
SpeedOrigUpdateAlertBox:
  push {r3, r4, r5, r6, r7, r8, r9, lr}
  b    UpdateAlertBox+4
