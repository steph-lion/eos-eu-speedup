#include <pmdsky.h>
#include <cot.h>

#define SPEED_MIN 1
#define SPEED_MAX 4
// Must match SPEED_STRING_FIRST_ID in scripts/prepare_rom.py.
#define SPEED_STRING_FIRST_ID 17298

// Explicitly placed in .data so the initial values are stored in the ROM.
__attribute__((used, section(".data"))) int SpeedMultiplier = SPEED_MIN;
__attribute__((section(".data"))) static bool select_was_held = true;
__attribute__((section(".data"))) static bool in_input_hook = false;

// LogMessage sets the alert box timer to 240 and WaitUntilAlertBoxPauseIsOver blocks
// until it drops below 180, so the blocking pause lasts 60 frames at 1x.
#define ALERT_BOX_TIMER_START 240
static const int alert_box_pause_frames[SPEED_MAX] = {60, 30, 20, 15};
__attribute__((used, section(".data"))) int SpeedAlertPauseThreshold = ALERT_BOX_TIMER_START - 60;

__attribute__((used)) int SpeedGetMultiplier(void) {
  return SpeedMultiplier;
}

static void SpeedSetMultiplier(int multiplier) {
  SpeedMultiplier = multiplier;
  SpeedAlertPauseThreshold = ALERT_BOX_TIMER_START - alert_box_pause_frames[multiplier - SPEED_MIN];
}

#define ALERT_BOX_STATE_PRINTING 2
#define ALERT_BOX_STATE_SCROLLING 3

extern void SpeedOrigUpdateAlertBox(struct window* window);

// Scrolling moves the lines by 2 pixels per update, so extra updates per frame speed it up.
__attribute__((used)) void SpeedUpdateAlertBox(struct window* window) {
  SpeedOrigUpdateAlertBox(window);
  struct alert_box* alert_box = window->params.contents.alert_box;
  for (int i = SPEED_MIN; i < SpeedMultiplier; i++) {
    if (alert_box->state != ALERT_BOX_STATE_PRINTING && alert_box->state != ALERT_BOX_STATE_SCROLLING) {
      break;
    }
    SpeedOrigUpdateAlertBox(window);
  }
}

static void SpeedShowMessage(void) {
  struct entity* leader = GetLeader();
  if (leader != NULL) {
    LogMessageById(leader, SPEED_STRING_FIRST_ID + SpeedMultiplier - SPEED_MIN, true);
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
    SpeedSetMultiplier((SpeedMultiplier >= SPEED_MAX) ? SPEED_MIN : SpeedMultiplier + 1);
    SpeedShowMessage();
  }

  in_input_hook = false;
}
