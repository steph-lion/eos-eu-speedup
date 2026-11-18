#include <pmdsky.h>
#include <cot.h>

#define SPEED_MIN 1
#define SPEED_MAX 4
// Must match SPEED_STRING_FIRST_ID in scripts/prepare_rom.py.
#define SPEED_STRING_FIRST_ID 17298

// Explicitly placed in .data so the initial values are stored in the ROM.
__attribute__((section(".data"))) static int speed_multiplier = SPEED_MIN;
__attribute__((section(".data"))) static bool select_was_held = true;
__attribute__((section(".data"))) static bool in_input_hook = false;

__attribute__((used)) int SpeedGetMultiplier(void) {
  return speed_multiplier;
}

static void SpeedShowMessage(void) {
  struct entity* leader = GetLeader();
  if (leader != NULL) {
    LogMessageById(leader, SPEED_STRING_FIRST_ID + speed_multiplier - SPEED_MIN, true);
  }
}

__attribute__((used)) void SpeedOnButtonInput(void) {
  bool select_now = DUNGEON_BUTTON_INPUT.cur_held_buttons.select;
  DUNGEON_BUTTON_INPUT.cur_held_buttons.select = false;
  DUNGEON_BUTTON_INPUT.cur_pressed_buttons.select = false;
  DUNGEON_BUTTON_INPUT.field_0x4.select = false;

  if (in_input_hook) {
    return;
  }
  in_input_hook = true;

  bool just_pressed = select_now && !select_was_held;
  select_was_held = select_now;
  if (just_pressed) {
    speed_multiplier = (speed_multiplier >= SPEED_MAX) ? SPEED_MIN : speed_multiplier + 1;
    SpeedShowMessage();
  }

  in_input_hook = false;
}
