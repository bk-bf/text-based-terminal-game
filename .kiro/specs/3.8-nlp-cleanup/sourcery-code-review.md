Please address the comments from this code review:

## Overall Comments
- The massive if/elif chain in _log_main_result makes it hard to maintain—consider using a dispatch table or splitting handlers into smaller methods.
- There are several raw print statements (especially in log_equipment_event) that should be removed or replaced with a proper logging framework at debug level.
- ActionLogger has grown large with NLP concerns—think about extracting the NLP logging methods into a separate class or module to keep responsibilities clear.

## Individual Comments

### Comment 1
<location> `fantasy_rpg/actions/action_logger.py:899-908` </location>
<code_context>
+        print(f"[DEBUG ActionLogger] log_equipment_event called: event_type={event_type}, kwargs={kwargs}")
</code_context>

<issue_to_address>
**suggestion:** Remove debug print statements from log_equipment_event for production.

These print statements should be removed or controlled by a debug flag to prevent unnecessary log output in production environments.

Suggested implementation:

```python
        # Debug print statements removed for production use.

```

```python
            # Debug print statement removed for production use.

```
</issue_to_address>

### Comment 2
<location> `fantasy_rpg/game/object_interaction_system.py:312` </location>
<code_context>
-    def _handle_unlock(self, obj: Dict, properties: Dict) -> Tuple[bool, str]:
+    def _handle_unlock(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
         """Handle unlocking/lockpicking objects"""
         if not properties.get("can_unlock"):
-            return False, f"The {obj.get('name')} cannot be unlocked."
+            return self._make_result(False, f"The {obj.get('name')} cannot be unlocked.")
</code_context>

<issue_to_address>
**suggestion:** Consider including skill check metadata in unlock/disarm results.

Including skill check details in the result dict for unlock and disarm actions will improve consistency and support better logging and UI feedback.

Suggested implementation:

```python
    def _handle_unlock(self, obj: Dict, properties: Dict) -> Dict[str, Any]:
        """Handle unlocking/lockpicking objects"""
        skill_check_metadata = {
            "skill": "lockpicking",
            "dc": properties.get("lock_dc", 15),  # Default DC 15 if not specified
        }

        if not properties.get("can_unlock"):
            skill_check_metadata.update({
                "success": False,
                "roll": None,
                "reason": "Object cannot be unlocked"
            })
            return self._make_result(
                False,
                f"The {obj.get('name')} cannot be unlocked.",
                skill_check=skill_check_metadata
            )

        # Check if already unlocked
        if obj.get("unlocked", False):
            skill_check_metadata.update({
                "success": False,
                "roll": None,
                "reason": "Object already unlocked"
            })
            return self._make_result(
                False,
                f"The {obj.get('name')} is already unlocked.",
                skill_check=skill_check_metadata
            )

        # Make lockpicking check
        roll = random.randint(1, 20)
        skill_check_metadata["roll"] = roll
        dc = skill_check_metadata["dc"]
        if self.game_engine.time_system:
            time_result = self.game_engine.time_system.perform_activity("lockpick", duration_override=1.0)

```

```python
        # Make lockpicking check
        # (continued from above)
        if roll >= dc:
            skill_check_metadata["success"] = True
            return self._make_result(
                True,
                f"You successfully unlock the {obj.get('name')} (Roll: {roll}, DC: {dc}).",
                skill_check=skill_check_metadata
            )
        else:
            skill_check_metadata["success"] = False
            return self._make_result(
                False,
                f"You fail to unlock the {obj.get('name')} (Roll: {roll}, DC: {dc}).",
                skill_check=skill_check_metadata
            )

```

1. The `_make_result` method must be updated to accept and include the `skill_check` parameter in the returned dict. For example:
```python
def _make_result(self, success: bool, message: str, skill_check: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    result = {"success": success, "message": message}
    if skill_check is not None:
        result["skill_check"] = skill_check
    return result
```
2. If other methods (e.g., disarm) use similar skill checks, apply the same pattern for consistency.
</issue_to_address>

### Comment 3
<location> `fantasy_rpg/actions/character_handler.py:67-72` </location>
<code_context>
+                item = inv_item
+                break
+        
+        if not item:
+            return ActionResult(False, f"Item '{item_id}' not found in inventory.")
+        
</code_context>

<issue_to_address>
**suggestion (bug_risk):** Item lookup in inventory may be case-sensitive.

Consider normalizing item_id case during lookup to prevent mismatches due to casing inconsistencies.

```suggestion
        # Find item in inventory (case-insensitive)
        item = None
        normalized_item_id = item_id.lower()
        for inv_item in character.inventory.items:
            if inv_item.item_id.lower() == normalized_item_id:
                item = inv_item
                break
```
</issue_to_address>

### Comment 4
<location> `tests/test_message_manager.py:251-257` </location>
<code_context>
+    # Should return a fallback, not crash
+
+
+def test_missing_template_variable():
+    """Test that missing template variables are handled gracefully."""
+    manager = MessageManager()
+    # Call with missing required template variable
+    msg = manager.get_equipment_message('armor_equipped')  # Missing armor_name
+    assert msg is not None
+    # Message should still be returned (with template markers or graceful handling)
+
+
</code_context>

<issue_to_address>
**suggestion (testing):** Missing template variable test does not assert on fallback behavior.

Add an assertion to verify that the returned message includes the unsubstituted template marker or is otherwise handled gracefully, confirming robust fallback behavior.

```suggestion
def test_missing_template_variable():
    """Test that missing template variables are handled gracefully."""
    manager = MessageManager()
    # Call with missing required template variable
    msg = manager.get_equipment_message('armor_equipped')  # Missing armor_name
    assert msg is not None
    # Message should still be returned (with template markers or graceful handling)
    # Assert that the unsubstituted template marker is present in the message
    assert '{armor_name}' in msg or 'armor_name' in msg, "Fallback behavior not confirmed: unsubstituted template marker missing"
```
</issue_to_address>

### Comment 5
<location> `tests/test_message_manager.py:241-248` </location>
<code_context>
+    assert len(msg) > 0
+
+
+def test_empty_message_array():
+    """Test behavior when a message pool exists but is empty."""
+    manager = MessageManager()
+    # This would require modifying the JSON, so we test the fallback logic
+    # by testing an event that might not have messages
+    msg = manager.get_survival_message('NONEXISTENT_triggered')
+    assert msg is not None
+    # Should return a fallback, not crash
+
+
</code_context>

<issue_to_address>
**suggestion (testing):** Empty message array test does not assert on fallback content.

Add an assertion to verify that the returned message contains fallback content, such as 'experience' or 'unknown event', to confirm the fallback logic is triggered.

```suggestion
def test_empty_message_array():
    """Test behavior when a message pool exists but is empty."""
    manager = MessageManager()
    # This would require modifying the JSON, so we test the fallback logic
    # by testing an event that might not have messages
    msg = manager.get_survival_message('NONEXISTENT_triggered')
    assert msg is not None
    # Should return a fallback, not crash
    assert 'experience' in msg or 'unknown event' in msg
```
</issue_to_address>

### Comment 6
<location> `tests/test_action_logger_nlp.py:106-115` </location>
<code_context>
+    assert '{weapon_name}' not in message
+
+
+def test_log_equipment_event_armor_removed():
+    """Test logging armor removed event"""
+    logger = ActionLogger()
+    logger.log_equipment_event("armor_removed", armor_name="Chainmail")
+    
+    assert len(logger.message_queue) > 0
+    message = logger.message_queue[-1]['message']
+    assert "Chainmail" in message
+
+
</code_context>

<issue_to_address>
**suggestion (testing):** No test for unequipping shield or weapon events.

Please add tests for 'shield_unequipped' and 'weapon_unequipped' events to verify correct handling of all equipment removal cases.

```suggestion

def test_log_equipment_event_armor_removed():
    """Test logging armor removed event"""
    logger = ActionLogger()
    logger.log_equipment_event("armor_removed", armor_name="Chainmail")

    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "Chainmail" in message

def test_log_equipment_event_shield_unequipped():
    """Test logging shield unequipped event"""
    logger = ActionLogger()
    logger.log_equipment_event("shield_unequipped", shield_name="Kite Shield")

    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "Kite Shield" in message

def test_log_equipment_event_weapon_unequipped():
    """Test logging weapon unequipped event"""
    logger = ActionLogger()
    logger.log_equipment_event("weapon_unequipped", weapon_name="Shortsword")

    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "Shortsword" in message

```
</issue_to_address>

### Comment 7
<location> `tests/test_action_logger_nlp.py:184-193` </location>
<code_context>
+    assert '{quantity}' not in message
+
+
+def test_log_action_event_search_empty():
+    """Test logging empty search result"""
+    logger = ActionLogger()
+    logger.log_action_event("search_empty", object_name="chest")
+    
+    assert len(logger.message_queue) > 0
+    message = logger.message_queue[-1]['message']
+    assert "chest" in message.lower()
+    # Should indicate nothing found - comprehensive keywords from search_empty messages
+    assert any(word in message.lower() for word in ['empty', 'nothing', 'value', 'search', 'picked', 'find', 'remain'])
+
+
</code_context>

<issue_to_address>
**suggestion (testing):** No test for failed search (e.g., unsearchable object or already searched).

Please add a test to cover cases where a search fails due to the object being unsearchable or previously searched, ensuring the appropriate error or fallback message is logged.

Suggested implementation:

```python
def test_log_action_event_search_empty():
    """Test logging empty search result"""
    logger = ActionLogger()
    logger.log_action_event("search_empty", object_name="chest")

    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "chest" in message.lower()
    # Should indicate nothing found - comprehensive keywords from search_empty messages
    assert any(word in message.lower() for word in ['empty', 'nothing', 'value', 'search', 'picked', 'find', 'remain'])


def test_log_action_event_search_failed():
    """Test logging failed search due to unsearchable object or already searched"""
    logger = ActionLogger()
    # Simulate an unsearchable object
    logger.log_action_event("search_failed", object_name="locked chest")
    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "locked chest" in message.lower()
    # Should indicate failure - comprehensive keywords from search_failed messages
    assert any(word in message.lower() for word in ['unsearchable', 'already searched', 'cannot', 'fail', 'unable', 'locked', 'error', 'not allowed', 'forbidden'])

```

If "search_failed" is not a valid event type in your ActionLogger implementation, you may need to adjust the event type or update the logger to support it. Also, ensure that the logger generates appropriate messages for failed searches.
</issue_to_address>

### Comment 8
<location> `tests/test_action_logger_nlp.py:195-205` </location>
<code_context>
+    assert any(word in message.lower() for word in ['empty', 'nothing', 'value', 'search', 'picked', 'find', 'remain'])
+
+
+def test_log_action_event_chop_success():
+    """Test logging successful wood chopping"""
+    logger = ActionLogger()
+    logger.log_action_event("chop_success", object_name="tree", quantity=3)
+    
+    assert len(logger.message_queue) > 0
+    message = logger.message_queue[-1]['message']
+    assert "tree" in message.lower() or "wood" in message.lower()
+    assert "3" in message
+
+
</code_context>

<issue_to_address>
**suggestion (testing):** No test for chop_depleted event.

Please add a test for 'chop_depleted' to verify correct logging when attempting to chop wood from a depleted object.

```suggestion

def test_log_action_event_chop_success():
    """Test logging successful wood chopping"""
    logger = ActionLogger()
    logger.log_action_event("chop_success", object_name="tree", quantity=3)

    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "tree" in message.lower() or "wood" in message.lower()
    assert "3" in message

def test_log_action_event_chop_depleted():
    """Test logging chopping from a depleted object"""
    logger = ActionLogger()
    logger.log_action_event("chop_depleted", object_name="tree")

    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "tree" in message.lower()
    # Should indicate depletion/exhaustion
    assert any(word in message.lower() for word in ['depleted', 'empty', 'exhausted', 'no wood', 'nothing left', 'ran out'])
```
</issue_to_address>

### Comment 9
<location> `tests/test_action_logger_nlp.py:207-217` </location>
<code_context>
+    assert "3" in message
+
+
+def test_log_action_event_drink():
+    """Test logging drinking from water source"""
+    logger = ActionLogger()
+    logger.log_action_event("drink_success", object_name="well")
+    
+    assert len(logger.message_queue) > 0
+    message = logger.message_queue[-1]['message']
+    assert "well" in message.lower()
+    assert any(word in message.lower() for word in ['drink', 'water', 'thirst', 'refresh'])
+
+
</code_context>

<issue_to_address>
**suggestion (testing):** No test for drink failure (e.g., object does not provide water).

Please add a test case for when drinking fails, such as when the object does not provide water, to ensure proper error handling and messaging.

```suggestion
def test_log_action_event_drink():
    """Test logging drinking from water source"""
    logger = ActionLogger()
    logger.log_action_event("drink_success", object_name="well")

    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "well" in message.lower()
    assert any(word in message.lower() for word in ['drink', 'water', 'thirst', 'refresh'])


def test_log_action_event_drink_failure():
    """Test logging failed drinking attempt from non-water source"""
    logger = ActionLogger()
    logger.log_action_event("drink_failure", object_name="rock")

    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "rock" in message.lower()
    assert any(word in message.lower() for word in ['fail', 'unable', 'no water', 'dry', 'thirst'])
```
</issue_to_address>

### Comment 10
<location> `tests/test_action_logger_nlp.py:217-227` </location>
<code_context>
+    assert any(word in message.lower() for word in ['drink', 'water', 'thirst', 'refresh'])
+
+
+def test_log_action_event_unlock_success():
+    """Test logging successful unlock"""
+    logger = ActionLogger()
+    logger.log_action_event("unlock_success", object_name="chest")
+    
+    assert len(logger.message_queue) > 0
+    message = logger.message_queue[-1]['message']
+    assert "chest" in message.lower()
+    assert any(word in message.lower() for word in ['unlock', 'open', 'lock'])
+
+
</code_context>

<issue_to_address>
**suggestion (testing):** No test for unlock_failure event.

Please add a test for 'unlock_failure' to verify that failed unlock attempts are properly logged.

```suggestion

def test_log_action_event_unlock_success():
    """Test logging successful unlock"""
    logger = ActionLogger()
    logger.log_action_event("unlock_success", object_name="chest")

    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "chest" in message.lower()
    assert any(word in message.lower() for word in ['unlock', 'open', 'lock'])

def test_log_action_event_unlock_failure():
    """Test logging failed unlock"""
    logger = ActionLogger()
    logger.log_action_event("unlock_failure", object_name="chest")

    assert len(logger.message_queue) > 0
    message = logger.message_queue[-1]['message']
    assert "chest" in message.lower()
    assert any(word in message.lower() for word in ['fail', 'unable', 'cannot', 'locked', 'unsuccessful', 'error', 'denied', 'refused', 'blocked', 'unsuccess'])
```
</issue_to_address>

### Comment 11
<location> `tests/test_action_logger_nlp.py:167-182` </location>
<code_context>
+    assert any(word in message.lower() for word in ['cold', 'freez', 'chill', 'frost', 'ice', 'frigid'])
+
+
+def test_log_action_event_forage_success():
+    """Test logging successful forage action"""
+    logger = ActionLogger()
+    logger.log_action_event("forage_success", object_name="berry bush", item_name="berries", quantity=5)
+    
+    assert len(logger.message_queue) > 0
+    assert logger.message_queue[-1]['type'] == 'action'
+    
+    message = logger.message_queue[-1]['message']
+    assert "berries" in message.lower() or "berry" in message.lower()
+    assert "5" in message
+    # Should not have template markers
+    assert '{item_name}' not in message
+    assert '{quantity}' not in message
+
</code_context>

<issue_to_address>
**suggestion (testing):** No test for forage_depleted event.

Please add a test to ensure the 'forage_depleted' event is logged as expected when foraging is unavailable.

```suggestion
def test_log_action_event_forage_success():
    """Test logging successful forage action"""
    logger = ActionLogger()
    logger.log_action_event("forage_success", object_name="berry bush", item_name="berries", quantity=5)

    assert len(logger.message_queue) > 0
    assert logger.message_queue[-1]['type'] == 'action'

    message = logger.message_queue[-1]['message']
    assert "berries" in message.lower() or "berry" in message.lower()
    assert "5" in message
    # Should not have template markers
    assert '{item_name}' not in message
    assert '{quantity}' not in message

def test_log_action_event_forage_depleted():
    """Test logging forage depleted event when foraging is unavailable"""
    logger = ActionLogger()
    logger.log_action_event("forage_depleted", object_name="berry bush")

    assert len(logger.message_queue) > 0
    assert logger.message_queue[-1]['type'] == 'action'

    message = logger.message_queue[-1]['message']
    # Check for depletion keywords
    assert any(word in message.lower() for word in ['depleted', 'empty', 'no more', 'exhausted', 'unavailable', 'cannot forage'])
    # Should mention the object name
    assert "berry bush" in message.lower()
    # Should not have template markers
    assert '{object_name}' not in message
```
</issue_to_address>

### Comment 12
<location> `fantasy_rpg/dialogue/message_manager.py:170-174` </location>
<code_context>
        messages = self.messages.get('environmental', {}).get(event, [])

        # If not found, check beneficial_effects category
        if not messages:
            messages = self.messages.get('beneficial_effects', {}).get(event, [])

</code_context>

<issue_to_address>
**suggestion (code-quality):** Use `or` for providing a fallback value ([`use-or-for-fallback`](https://docs.sourcery.ai/Reference/Rules-and-In-Line-Suggestions/Python/Default-Rules/use-or-for-fallback))

```suggestion
        messages = self.messages.get('environmental', {}).get(event, []) or self.messages.get('beneficial_effects', {}).get(event, [])

```

<br/><details><summary>Explanation</summary>Thanks to the flexibility of Python's `or` operator, you can use a single
assignment statement, even if a variable can retrieve its value from various
sources. This is shorter and easier to read than using multiple assignments with
`if not` conditions.
</details>
</issue_to_address>

### Comment 13
<location> `tests/test_action_logger_nlp.py:73-76` </location>
<code_context>

</code_context>

<issue_to_address>
**issue (code-quality):** Avoid loops in tests. ([`no-loop-in-tests`](https://docs.sourcery.ai/Reference/Rules-and-In-Line-Suggestions/Python/Default-Rules/no-loop-in-tests))

<details><summary>Explanation</summary>Avoid complex code, like loops, in test functions.

Google's software engineering guidelines says:
"Clear tests are trivially correct upon inspection"
To reach that avoid complex code in tests:
* loops
* conditionals

Some ways to fix this:

* Use parametrized tests to get rid of the loop.
* Move the complex logic into helpers.
* Move the complex part into pytest fixtures.

> Complexity is most often introduced in the form of logic. Logic is defined via the imperative parts of programming languages such as operators, loops, and conditionals. When a piece of code contains logic, you need to do a bit of mental computation to determine its result instead of just reading it off of the screen. It doesn't take much logic to make a test more difficult to reason about.

Software Engineering at Google / [Don't Put Logic in Tests](https://abseil.io/resources/swe-book/html/ch12.html#donapostrophet_put_logic_in_tests)
</details>
</issue_to_address>

### Comment 14
<location> `tests/test_action_logger_nlp.py:122-127` </location>
<code_context>

</code_context>

<issue_to_address>
**issue (code-quality):** Avoid loops in tests. ([`no-loop-in-tests`](https://docs.sourcery.ai/Reference/Rules-and-In-Line-Suggestions/Python/Default-Rules/no-loop-in-tests))

<details><summary>Explanation</summary>Avoid complex code, like loops, in test functions.

Google's software engineering guidelines says:
"Clear tests are trivially correct upon inspection"
To reach that avoid complex code in tests:
* loops
* conditionals

Some ways to fix this:

* Use parametrized tests to get rid of the loop.
* Move the complex logic into helpers.
* Move the complex part into pytest fixtures.

> Complexity is most often introduced in the form of logic. Logic is defined via the imperative parts of programming languages such as operators, loops, and conditionals. When a piece of code contains logic, you need to do a bit of mental computation to determine its result instead of just reading it off of the screen. It doesn't take much logic to make a test more difficult to reason about.

Software Engineering at Google / [Don't Put Logic in Tests](https://abseil.io/resources/swe-book/html/ch12.html#donapostrophet_put_logic_in_tests)
</details>
</issue_to_address>

### Comment 15
<location> `tests/test_action_logger_nlp.py:442-448` </location>
<code_context>

</code_context>

<issue_to_address>
**issue (code-quality):** Avoid loops in tests. ([`no-loop-in-tests`](https://docs.sourcery.ai/Reference/Rules-and-In-Line-Suggestions/Python/Default-Rules/no-loop-in-tests))

<details><summary>Explanation</summary>Avoid complex code, like loops, in test functions.

Google's software engineering guidelines says:
"Clear tests are trivially correct upon inspection"
To reach that avoid complex code in tests:
* loops
* conditionals

Some ways to fix this:

* Use parametrized tests to get rid of the loop.
* Move the complex logic into helpers.
* Move the complex part into pytest fixtures.

> Complexity is most often introduced in the form of logic. Logic is defined via the imperative parts of programming languages such as operators, loops, and conditionals. When a piece of code contains logic, you need to do a bit of mental computation to determine its result instead of just reading it off of the screen. It doesn't take much logic to make a test more difficult to reason about.

Software Engineering at Google / [Don't Put Logic in Tests](https://abseil.io/resources/swe-book/html/ch12.html#donapostrophet_put_logic_in_tests)
</details>
</issue_to_address>

### Comment 16
<location> `tests/test_message_manager.py:44-46` </location>
<code_context>

</code_context>

<issue_to_address>
**issue (code-quality):** Avoid loops in tests. ([`no-loop-in-tests`](https://docs.sourcery.ai/Reference/Rules-and-In-Line-Suggestions/Python/Default-Rules/no-loop-in-tests))

<details><summary>Explanation</summary>Avoid complex code, like loops, in test functions.

Google's software engineering guidelines says:
"Clear tests are trivially correct upon inspection"
To reach that avoid complex code in tests:
* loops
* conditionals

Some ways to fix this:

* Use parametrized tests to get rid of the loop.
* Move the complex logic into helpers.
* Move the complex part into pytest fixtures.

> Complexity is most often introduced in the form of logic. Logic is defined via the imperative parts of programming languages such as operators, loops, and conditionals. When a piece of code contains logic, you need to do a bit of mental computation to determine its result instead of just reading it off of the screen. It doesn't take much logic to make a test more difficult to reason about.

Software Engineering at Google / [Don't Put Logic in Tests](https://abseil.io/resources/swe-book/html/ch12.html#donapostrophet_put_logic_in_tests)
</details>
</issue_to_address>

### Comment 17
<location> `tests/test_message_manager.py:107-109` </location>
<code_context>

</code_context>

<issue_to_address>
**issue (code-quality):** Avoid loops in tests. ([`no-loop-in-tests`](https://docs.sourcery.ai/Reference/Rules-and-In-Line-Suggestions/Python/Default-Rules/no-loop-in-tests))

<details><summary>Explanation</summary>Avoid complex code, like loops, in test functions.

Google's software engineering guidelines says:
"Clear tests are trivially correct upon inspection"
To reach that avoid complex code in tests:
* loops
* conditionals

Some ways to fix this:

* Use parametrized tests to get rid of the loop.
* Move the complex logic into helpers.
* Move the complex part into pytest fixtures.

> Complexity is most often introduced in the form of logic. Logic is defined via the imperative parts of programming languages such as operators, loops, and conditionals. When a piece of code contains logic, you need to do a bit of mental computation to determine its result instead of just reading it off of the screen. It doesn't take much logic to make a test more difficult to reason about.

Software Engineering at Google / [Don't Put Logic in Tests](https://abseil.io/resources/swe-book/html/ch12.html#donapostrophet_put_logic_in_tests)
</details>
</issue_to_address>

### Comment 18
<location> `tests/test_message_manager.py:266-270` </location>
<code_context>

</code_context>

<issue_to_address>
**issue (code-quality):** Avoid loops in tests. ([`no-loop-in-tests`](https://docs.sourcery.ai/Reference/Rules-and-In-Line-Suggestions/Python/Default-Rules/no-loop-in-tests))

<details><summary>Explanation</summary>Avoid complex code, like loops, in test functions.

Google's software engineering guidelines says:
"Clear tests are trivially correct upon inspection"
To reach that avoid complex code in tests:
* loops
* conditionals

Some ways to fix this:

* Use parametrized tests to get rid of the loop.
* Move the complex logic into helpers.
* Move the complex part into pytest fixtures.

> Complexity is most often introduced in the form of logic. Logic is defined via the imperative parts of programming languages such as operators, loops, and conditionals. When a piece of code contains logic, you need to do a bit of mental computation to determine its result instead of just reading it off of the screen. It doesn't take much logic to make a test more difficult to reason about.

Software Engineering at Google / [Don't Put Logic in Tests](https://abseil.io/resources/swe-book/html/ch12.html#donapostrophet_put_logic_in_tests)
</details>
</issue_to_address>

### Comment 19
<location> `fantasy_rpg/actions/action_logger.py:160` </location>
<code_context>
    def _log_main_result(self, action_result):
        """Log the main result of the action

        ============================================================================
        CRITICAL ARCHITECTURE: Message Ordering and Centralized NLP Generation
        ============================================================================

        This method is the SINGLE POINT where action messages are logged. It ensures
        correct chronological ordering: COMMAND → DICE ROLLS → MESSAGE → TIME → EFFECTS

        CORRECT PATTERN (handler returns metadata):
            1. Handler performs action logic
            2. Handler returns ActionResult with METADATA (item_equipped, search_result, etc.)
            3. UI calls action_logger.log_action_result(result, command_text="...")
            4. log_action_result() logs command FIRST ("> search chest")
            5. Then calls THIS METHOD which generates NLP message from metadata
            6. Result: "> search chest" appears BEFORE "You find treasure" ✓

        WRONG PATTERN (direct logging - DO NOT DO THIS):
            1. System calls action_logger.log_action_event() directly
            2. NLP message appears in log immediately
            3. System returns ActionResult with message
            4. UI calls action_logger.log_action_result(result, command_text="...")
            5. Command appears AFTER message already logged
            6. Result: "You find treasure" appears BEFORE "> search chest" ❌

        SUPPORTED EVENT TYPES (add metadata to ActionResult.data):
            - item_equipped/item_unequipped + item_type: Equipment NLP
            - search_success/search_empty + items_found + skill_check: Search NLP
            - forage_success/forage_depleted + object_name: Forage NLP
            - harvest_success/harvest_depleted + object_name: Harvest NLP
            - fire_started/fire_failure + object_name: Fire NLP
            - unlock_success/unlock_failure + object_name: Lockpick NLP
            - disarm_success/disarm_failure + object_name + triggered: Trap disarm NLP
            - chop_success/chop_depleted + object_name: Chop wood NLP
            - drink_success + object_name + water_quality + temperature: Drink NLP
            - (Add more as needed for combat, etc.)

        FOR NEW SYSTEMS (combat, crafting, etc.):
            1. Add metadata keys to ActionResult
            2. Add handling in this method
            3. NEVER call action_logger directly from game systems
        ============================================================================
        """
        # Handle equipment events (metadata-driven)
        if action_result.get('item_equipped'):
            item_name = action_result.get('item_equipped')
            item_type = action_result.get('item_type', 'item')

            if item_type == 'armor':
                self.log_equipment_event("armor_equipped", armor_name=item_name)
            elif item_type == 'weapon':
                self.log_equipment_event("weapon_equipped", weapon_name=item_name)
            elif item_type == 'shield':
                self.log_equipment_event("shield_equipped", shield_name=item_name)
            else:
                self.game_log.add_message(f"Equipped {item_name}")

        elif action_result.get('item_unequipped'):
            item_name = action_result.get('item_unequipped')
            item_type = action_result.get('item_type', 'item')

            if item_type == 'armor':
                self.log_equipment_event("armor_unequipped", armor_name=item_name)
            elif item_type == 'weapon':
                self.log_equipment_event("weapon_unequipped", weapon_name=item_name)
            elif item_type == 'shield':
                self.log_equipment_event("shield_unequipped", shield_name=item_name)
            else:
                self.game_log.add_message(f"Unequipped {item_name}")

        # Handle object interaction events (metadata-driven)
        elif action_result.get('event_type') == 'search_success':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("search_success", object_name=object_name)
            # Factual message about items is in action_result.message
            if action_result.message:
                self.game_log.add_message(action_result.message)

        elif action_result.get('event_type') == 'search_empty':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("search_empty", object_name=object_name)

        elif action_result.get('event_type') == 'forage_success':
            object_name = action_result.get('object_name', 'object')
            items_found = action_result.get('items_found', [])
            self.log_action_event("forage_success", object_name=object_name, items=", ".join(items_found))

        elif action_result.get('event_type') == 'forage_depleted':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("forage_depleted", object_name=object_name)

        elif action_result.get('event_type') == 'harvest_success':
            object_name = action_result.get('object_name', 'object')
            items_found = action_result.get('items_found', [])
            self.log_action_event("harvest_success", object_name=object_name, items=", ".join(items_found))

        elif action_result.get('event_type') == 'harvest_depleted':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("harvest_depleted", object_name=object_name)

        # Fire lighting events
        elif action_result.get('event_type') == 'fire_started':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("fire_started", object_name=object_name)
            # Add factual message if present (e.g., fuel consumption)
            if action_result.message:
                self.game_log.add_message(action_result.message)

        elif action_result.get('event_type') == 'fire_failure':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("fire_failure", object_name=object_name)

        # Unlock/lockpick events
        elif action_result.get('event_type') == 'unlock_success':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("unlock_success", object_name=object_name)

        elif action_result.get('event_type') == 'unlock_failure':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("unlock_failure", object_name=object_name)

        # Disarm trap events
        elif action_result.get('event_type') == 'disarm_success':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("disarm_success", object_name=object_name)

        elif action_result.get('event_type') == 'disarm_failure':
            object_name = action_result.get('object_name', 'object')
            triggered = action_result.get('triggered', False)
            self.log_action_event("disarm_failure", object_name=object_name, triggered=triggered)
            # Add factual damage message if present
            if action_result.message:
                self.game_log.add_message(action_result.message)

        # Chop wood events
        elif action_result.get('event_type') == 'chop_success':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("chop_success", object_name=object_name)

        elif action_result.get('event_type') == 'chop_depleted':
            object_name = action_result.get('object_name', 'object')
            self.log_action_event("chop_depleted", object_name=object_name)

        # Drink water events
        elif action_result.get('event_type') == 'drink_success':
            object_name = action_result.get('object_name', 'object')
            water_quality = action_result.get('water_quality', 'unknown')
            temperature = action_result.get('temperature', 'cool')
            self.log_action_event("drink_success", 
                object_name=object_name,
                water_quality=water_quality,
                temperature=temperature)

        elif action_result.message:
            # Regular messages for actions without special NLP
            self.game_log.add_message(action_result.message)

        # Handle specific action types
        self._log_movement_result(action_result)
        self._log_location_result(action_result)
        self._log_foraging_result(action_result)
        self._log_shelter_result(action_result)
        self._log_map_result(action_result)
        self._log_status_result(action_result)

</code_context>

<issue_to_address>
**issue (code-quality):** Low code quality found in ActionLogger.\_log\_main\_result - 11% ([`low-code-quality`](https://docs.sourcery.ai/Reference/Default-Rules/comments/low-code-quality/))

<br/><details><summary>Explanation</summary>The quality score for this function is below the quality threshold of 25%.
This score is a combination of the method length, cognitive complexity and working memory.

How can you solve this?

It might be worth refactoring this function to make it shorter and more readable.

- Reduce the function length by extracting pieces of functionality out into
  their own functions. This is the most important thing you can do - ideally a
  function should be less than 10 lines.
- Reduce nesting, perhaps by introducing guard clauses to return early.
- Ensure that variables are tightly scoped, so that code using related concepts
  sits together within the function rather than being scattered.</details>
</issue_to_address>

### Comment 20
<location> `fantasy_rpg/actions/action_logger.py:913-916` </location>
<code_context>
    def log_equipment_event(self, event_type: str, **kwargs):
        """Log equipment change with message variance.

        Uses MessageManager to provide varied messages for equipment actions
        with template variable substitution.

        Args:
            event_type: Event like 'armor_equipped', 'weapon_equipped', 'shield_removed'
            **kwargs: Template variables (armor_name, weapon_name, shield_name, etc)

        Example:
            action_logger.log_equipment_event("armor_equipped", 
                armor_name="Iron Breastplate",
                protection_boost=2
            )
        """
        print(f"[DEBUG ActionLogger] log_equipment_event called: event_type={event_type}, kwargs={kwargs}")
        print(f"[DEBUG ActionLogger] message_manager={self.message_manager}, game_log={self.game_log}")

        if not self.message_manager:
            # Fallback if MessageManager failed to load
            item_name = kwargs.get('armor_name') or kwargs.get('weapon_name') or kwargs.get('shield_name') or kwargs.get('item_name', 'item')
            action = event_type.replace('_', ' ').title()
            message = f"{action}: {item_name}"
            print(f"[DEBUG ActionLogger] Using fallback message: {message}")
        else:
            message = self.message_manager.get_equipment_message(event_type, **kwargs)
            print(f"[DEBUG ActionLogger] Got message from MessageManager: {message}")

        if self.game_log:
            print(f"[DEBUG ActionLogger] Adding message to game_log")
            self.game_log.add_message(message, "equipment")
        else:
            print(f"[DEBUG ActionLogger] No game_log, queueing message")
            self.message_queue.append({'type': 'equipment', 'message': message})

</code_context>

<issue_to_address>
**issue (code-quality):** Replace f-string with no interpolated values with string [×2] ([`remove-redundant-fstring`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/remove-redundant-fstring/))
</issue_to_address>

### Comment 21
<location> `fantasy_rpg/actions/character_handler.py:68` </location>
<code_context>
    def handle_equip(self, item_id: str, slot: str = None) -> ActionResult:
        """Handle equipping an item from inventory

        CRITICAL: Does NOT log directly! Returns ActionResult with metadata (item_equipped, item_type).
        The UI calls action_logger.log_action_result() which handles NLP message generation.
        This ensures proper message ordering: command appears before the action message.

        Args:
            item_id: ID of item to equip
            slot: Optional specific slot to equip to

        Returns:
            ActionResult with item_equipped metadata for ActionLogger to process
        """
        if not self.game_engine or not self.game_engine.is_initialized:
            return ActionResult(False, "Game engine not available.")

        gs = self.game_engine.game_state
        character = gs.character

        # Find item in inventory
        item = None
        for inv_item in character.inventory.items:
            if inv_item.item_id == item_id:
                item = inv_item
                break

        if not item:
            return ActionResult(False, f"Item '{item_id}' not found in inventory.")

        # Determine slot if not provided
        if not slot:
            slot = self._determine_equip_slot(item)
            if not slot:
                return ActionResult(False, f"Cannot determine equipment slot for {item.name}.")

        # Attempt to equip - character.equip_item returns bool only
        # We need to call equipment.equip_item directly to get the message
        if not character.equipment:
            from fantasy_rpg.core.equipment import Equipment
            character.equipment = Equipment()

        success, message = character.equipment.equip_item(item, slot, character)

        if success:
            # Recalculate stats after equipping
            character.recalculate_derived_stats()

            # Remove from inventory
            character.inventory.remove_item(item_id, 1)

            # Return success with metadata - UI will handle NLP logging
            return ActionResult(
                success=True,
                message="",  # Empty - equipment event handler will create NLP message
                time_passed=0.0,
                item_equipped=item.name,
                item_type=item.item_type,
                slot=slot
            )
        else:
            return ActionResult(False, message)

</code_context>

<issue_to_address>
**issue (code-quality):** We've found these issues:

- Use the built-in function `next` instead of a for-loop ([`use-next`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/use-next/))
- Hoist conditional out of nested conditional ([`hoist-if-from-if`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/hoist-if-from-if/))
</issue_to_address>

### Comment 22
<location> `fantasy_rpg/actions/character_handler.py:152` </location>
<code_context>
    def handle_unequip(self, slot: str) -> ActionResult:
        """Handle unequipping an item from a slot

        CRITICAL: Does NOT log directly! Returns ActionResult with metadata (item_unequipped, item_type).
        The UI calls action_logger.log_action_result() which handles NLP message generation.
        This ensures proper message ordering: command appears before the action message.

        Args:
            slot: The equipment slot to unequip from

        Returns:
            ActionResult with item_unequipped metadata for ActionLogger to process
        """
        if not self.game_engine or not self.game_engine.is_initialized:
            return ActionResult(False, "Game engine not available.")

        gs = self.game_engine.game_state
        character = gs.character

        # Check if equipment exists
        if not character.equipment:
            return ActionResult(False, "No equipment system initialized.")

        # Attempt to unequip - call equipment.unequip_item directly to get message
        unequipped_item, message = character.equipment.unequip_item(slot)

        if unequipped_item:
            # Recalculate stats after unequipping
            character.recalculate_derived_stats()

            # Ensure inventory exists
            if not hasattr(character, 'inventory') or character.inventory is None:
                character.initialize_inventory()

            # Add back to inventory
            if hasattr(character, 'inventory') and character.inventory is not None:
                # Ensure item has proper attributes for inventory
                if not unequipped_item.item_id:
                    import uuid
                    unequipped_item.item_id = f"{unequipped_item.name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
                unequipped_item.quantity = 1

                added = character.inventory.add_item(unequipped_item)

                if added:
                    # Return success with metadata - UI will handle NLP logging
                    return ActionResult(
                        success=True,
                        message="",  # Empty - equipment event handler will create NLP message
                        time_passed=0.0,
                        item_unequipped=unequipped_item.name,
                        item_type=unequipped_item.item_type,
                        slot=slot
                    )
                else:
                    return ActionResult(False, f"Unequipped {unequipped_item.name} but couldn't add to inventory (weight limit?)")
            else:
                return ActionResult(False, f"Unequipped {unequipped_item.name} but no inventory to return to")
        else:
            return ActionResult(False, message)

</code_context>

<issue_to_address>
**issue (code-quality):** Use named expression to simplify assignment and conditional ([`use-named-expression`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/use-named-expression/))
</issue_to_address>

### Comment 23
<location> `fantasy_rpg/actions/character_handler.py:183` </location>
<code_context>
    def _determine_equip_slot(self, item) -> str:
        """Determine which slot an item should be equipped to"""
        if not item:
            return None

        # Use item's slot property if available
        if hasattr(item, 'slot') and item.slot:
            # Map "hand" to "main_hand" for compatibility with items.json
            if item.slot == 'hand':
                return 'main_hand'
            # Handle ring slot - default to ring_1
            if item.slot == 'ring':
                return 'ring_1'
            return item.slot

        # Fallback based on item type
        if item.item_type == 'weapon':
            return 'main_hand'
        elif item.item_type == 'shield':
            return 'off_hand'
        elif item.item_type == 'armor':
            # Check armor_type if available
            if hasattr(item, 'armor_type'):
                return 'body'  # Most common armor slot
            return 'body'

        return None

</code_context>

<issue_to_address>
**issue (code-quality):** We've found these issues:

- Lift code into else after jump in control flow ([`reintroduce-else`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/reintroduce-else/))
- Replace if statement with if expression ([`assign-if-exp`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/assign-if-exp/))
- Simplify conditional into switch-like form [×2] ([`switch`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/switch/))
</issue_to_address>

### Comment 24
<location> `fantasy_rpg/actions/handler_registry.py:83` </location>
<code_context>
    def get_handler(self, handler_name: str):
        """Get a registered handler instance by name

        Args:
            handler_name: Name of the handler class (lowercase, without 'Handler' suffix)
                         e.g., 'character' for CharacterHandler, 'movement' for MovementHandler

        Returns:
            Handler instance or None if not found
        """
        for handler in self._handlers:
            class_name = handler.__class__.__name__.lower()
            # Match both 'character' and 'characterhandler'
            if class_name == f"{handler_name}handler" or class_name == handler_name:
                return handler
        return None

</code_context>

<issue_to_address>
**suggestion (code-quality):** Replace multiple comparisons of same variable with `in` operator ([`merge-comparisons`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/merge-comparisons/))

```suggestion
            if class_name in [f"{handler_name}handler", handler_name]:
```
</issue_to_address>

### Comment 25
<location> `fantasy_rpg/actions/object_interaction_handler.py:63` </location>
<code_context>
    def handle_search(self, *args) -> ActionResult:
        """Handle searching objects - delegates to ObjectInteractionSystem

        Returns ActionResult with metadata for ActionLogger to generate NLP messages.
        """
        if error := self._require_location():
            return error

        if not args:
            return ActionResult(False, "Search what? Specify an object name (e.g., 'search chest')")

        object_name = " ".join(args).lower()

        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "search")

            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')
            items_found = result.get('items_found', [])
            skill_check = result.get('skill_check')

            # Only pass time if the search actually happened
            time_passed = 0.1 if success else 0.0  # 6 minutes for successful search

            # Return ActionResult with metadata for NLP generation
            return ActionResult(
                success=success,
                message=message,  # Factual info ("You find: X")
                time_passed=time_passed,
                event_type=event_type,  # For NLP: 'search_success' or 'search_empty'
                object_name=result.get('object_name', object_name),
                items_found=items_found,
                skill_check=skill_check
            )
        except Exception as e:
            return ActionResult(False, f"Error: {str(e)}")

</code_context>

<issue_to_address>
**issue (code-quality):** Extract code out into method ([`extract-method`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/extract-method/))
</issue_to_address>

### Comment 26
<location> `fantasy_rpg/actions/object_interaction_handler.py:127` </location>
<code_context>
    def handle_forage(self, *args) -> ActionResult:
        """Handle foraging - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error

        if not args:
            return ActionResult(False, "Forage what? Specify an object name (e.g., 'forage berry bush')")

        object_name = " ".join(args).lower()

        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "forage")

            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')

            # Use time system to ensure condition effects are applied
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("forage", duration_override=0.25)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Foraging interrupted."))

            return ActionResult(
                success=success,
                message=message,
                time_passed=0.25,
                event_type=event_type,
                object_name=result.get('object_name', object_name)
            )
        except Exception as e:
            return ActionResult(False, f"Failed to forage: {str(e)}")

</code_context>

<issue_to_address>
**issue (code-quality):** Extract code out into method ([`extract-method`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/extract-method/))
</issue_to_address>

### Comment 27
<location> `fantasy_rpg/actions/object_interaction_handler.py:162` </location>
<code_context>
    def handle_harvest(self, *args) -> ActionResult:
        """Handle harvesting - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error

        if not args:
            return ActionResult(False, "Harvest what? Specify an object name (e.g., 'harvest berry bush')")

        object_name = " ".join(args).lower()

        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "harvest")

            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')

            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("forage", duration_override=0.25)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Harvesting interrupted."))

            return ActionResult(
                success=success,
                message=message,
                time_passed=0.25,
                event_type=event_type,
                object_name=result.get('object_name', object_name)
            )
        except Exception as e:
            return ActionResult(False, f"Failed to harvest: {str(e)}")

</code_context>

<issue_to_address>
**issue (code-quality):** Extract code out into method ([`extract-method`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/extract-method/))
</issue_to_address>

### Comment 28
<location> `fantasy_rpg/actions/object_interaction_handler.py:196` </location>
<code_context>
    def handle_chop(self, *args) -> ActionResult:
        """Handle chopping wood - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error

        if not args:
            return ActionResult(False, "Chop what? Specify an object name (e.g., 'chop tree')")

        object_name = " ".join(args).lower()

        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "chop")

            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')

            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("chop_wood", duration_override=1.0)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Chopping interrupted."))

            return ActionResult(
                success=success,
                message=message,
                time_passed=1.0,
                event_type=event_type,
                object_name=result.get('object_name', object_name)
            )
        except Exception as e:
            return ActionResult(False, f"Failed to chop: {str(e)}")

</code_context>

<issue_to_address>
**issue (code-quality):** Extract code out into method ([`extract-method`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/extract-method/))
</issue_to_address>

### Comment 29
<location> `fantasy_rpg/actions/object_interaction_handler.py:230` </location>
<code_context>
    def handle_drink(self, *args) -> ActionResult:
        """Handle drinking from water sources - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error

        if not args:
            return ActionResult(False, "Drink from what? Specify a water source (e.g., 'drink well')")

        object_name = " ".join(args).lower()

        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "drink")

            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')

            # Use time system
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("drink", duration_override=0.1)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Drinking interrupted."))

            return ActionResult(
                success=success,
                message=message,
                time_passed=0.1,
                action_type="survival",
                event_type=event_type,
                object_name=result.get('object_name', object_name),
                water_quality=result.get('water_quality'),
                temperature=result.get('temperature')
            )

        except Exception as e:
            return ActionResult(False, f"Failed to drink: {str(e)}")

</code_context>

<issue_to_address>
**issue (code-quality):** Extract code out into method ([`extract-method`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/extract-method/))
</issue_to_address>

### Comment 30
<location> `fantasy_rpg/actions/object_interaction_handler.py:269` </location>
<code_context>
    def handle_unlock(self, *args) -> ActionResult:
        """Handle unlocking/lockpicking - delegates to ObjectInteractionSystem"""
        if error := self._require_location():
            return error

        if not args:
            return ActionResult(False, "Unlock what? Specify an object name (e.g., 'unlock chest')")

        object_name = " ".join(args).lower()

        try:
            # Delegate to game engine's ObjectInteractionSystem (returns dict)
            result = self.game_engine.interact_with_object(object_name, "unlock")

            # Extract data from result dict
            success = result.get('success', False)
            message = result.get('message', '')
            event_type = result.get('event_type')

            # Use time system
            if success and self.game_engine.time_system:
                time_result = self.game_engine.time_system.perform_activity("lockpick", duration_override=0.5)
                if not time_result.get("success", True):
                    return ActionResult(False, time_result.get("message", "Lockpicking interrupted."))

            return ActionResult(
                success=success,
                message=message,
                time_passed=0.5,
                event_type=event_type,
                object_name=result.get('object_name', object_name)
            )

        except Exception as e:
            return ActionResult(False, f"Failed to unlock: {str(e)}")

</code_context>

<issue_to_address>
**issue (code-quality):** Extract code out into method ([`extract-method`](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/extract-method/))
</issue_to_address>