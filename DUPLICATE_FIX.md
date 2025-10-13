"""
Fix explanation for duplicate first LLM message issue.

## Problem
When running robot mode with skip_first_query=True:
1. present_action() shows the LLM response via _present_query_response()
2. _handle_robot_action() returns user_prompt
3. Main loop calls _process_ai_query(user_prompt) AGAIN
→ Response shown twice

## Solution (cli.py lines 314-316)
```python
elif action_type == 'query' and skip_input:
    # First query already shown by present_action, skip _process_ai_query
    return True, last_code_blocks, None
```

When action is 'query' and skip_input=True:
- Return should_continue=True to skip further processing
- Main loop won't call _process_ai_query()
- Response shown only once ✅

## Flow comparison

### BEFORE (duplicate output):
```
_get_user_input(is_first_query=True)
  └→ _handle_robot_action(is_first_query=True)
      └→ present_action(skip_user_input=True)
          └→ _present_query_response()  ← Shows response #1
      └→ return False, code_blocks, user_prompt

main loop:
  └→ _process_ai_query(user_prompt)    ← Shows response #2 ❌
```

### AFTER (single output):
```
_get_user_input(is_first_query=True)
  └→ _handle_robot_action(is_first_query=True)
      └→ present_action(skip_user_input=True)
          └→ _present_query_response()  ← Shows response #1
      └→ return True, code_blocks, None  ← should_continue=True

main loop:
  └→ continue (skip _process_ai_query) ✅
```

## Test verification
All 118 tests pass ✅
"""
