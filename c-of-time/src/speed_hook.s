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

