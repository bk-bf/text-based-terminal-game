# No Terminal Command Execution Policy

## Manual Command Execution Only

You are NOT allowed to execute terminal commands directly using the executeBash or controlBashProcess tools. Instead, you must propose commands and wait for manual execution by the user.

## What You MUST Do

### ✅ Propose Commands
```
Please run the following command:
`python fantasy_rpg/inventory.py`

Then paste the output here so I can verify the results.
```

### ✅ Wait for User Input
- Always wait for the user to run the command and provide output
- Do not proceed until you receive the actual command output
- Use the provided output to make decisions and continue work

### ✅ Explain Command Purpose
```
To test the inventory system, please run:
`python fantasy_rpg/inventory.py`

This will verify that:
- Weight tracking works correctly
- Item stacking functions properly
- Encumbrance calculations are accurate
```

## What You MUST NOT Do

### ❌ Never Execute Commands Directly
- Do not use `executeBash` tool for running scripts or tests
- Do not use `controlBashProcess` for starting processes
- Do not run any terminal commands automatically

### ❌ Never Assume Command Results
- Do not proceed without actual command output
- Do not guess what the output might be
- Do not make up example outputs

## Exceptions

The following file operations are still allowed:
- `fsWrite` - Creating and writing files
- `fsAppend` - Appending to files
- `strReplace` - Modifying file contents
- `readFile` - Reading file contents
- `listDirectory` - Listing directory contents
- `deleteFile` - Deleting files when necessary

## Workflow

1. **Propose Command**: Clearly state what command to run and why
2. **Wait for Output**: Do not continue until user provides actual output
3. **Analyze Results**: Use the real output to make decisions
4. **Next Steps**: Based on actual results, propose next actions

## Example Interaction

**You**: "To test the character creation system, please run:
`python fantasy_rpg/character.py`

This will verify that character stats are calculated correctly."

**User**: [Runs command and pastes output]

**You**: "Great! I can see from the output that the character creation is working. The STR modifier calculation shows +2 for STR 15, which is correct. Now let's test the equipment system..."

## Remember

This policy ensures:
- User maintains full control over their system
- No unexpected processes are started
- All command execution is transparent and intentional
- User can review commands before running them