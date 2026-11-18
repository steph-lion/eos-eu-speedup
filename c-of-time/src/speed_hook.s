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
