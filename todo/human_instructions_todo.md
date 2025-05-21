# Human Instructions Todo

## Critical Tasks

### 1. Create Base Structure
- [x] All human instructions and todos are now consolidated in the todo/ folder as per main_prompt.txt
- [x] Confirmed all subdirectories and instruction files are referenced in the correct place

### 2. File Operations Instructions
- [ ] Continue refining file_operations/commands.txt and related tests as new findings are revealed

### 3. System Information Instructions
- [ ] Continue refining system_info/commands.txt and related tests as new findings are revealed

### 4. Command Processing Instructions
- [ ] Continue refining command_processing/commands.txt and related tests as new findings are revealed

### 5. Multilingual Support Instructions
- [ ] Continue refining multilingual/commands.txt and related tests as new findings are revealed

### 6. Utility Instructions
- [ ] Continue refining utils/commands.txt and related tests as new findings are revealed

## Implementation Details

### File Format
Each instruction file should follow this structure:
```markdown
# [Area] Commands

## English Commands
- Pattern 1
- Pattern 2
- Pattern 3

## Arabic Commands
- Pattern 1
- Pattern 2
- Pattern 3

## Examples
1. Example 1
2. Example 2
3. Example 3

## Notes
- Important consideration 1
- Important consideration 2
```

### Priority Order
1. File Operations (highest priority)
2. System Information
3. Command Processing
4. Multilingual Support
5. Utilities

### Testing Requirements
- [ ] Create test cases for each instruction set
- [ ] Verify command pattern coverage
- [x] All todos and instructions are now in the correct folder as per main_prompt.txt

## Dependencies
- [ ] Update requirements.txt if needed
- [ ] Ensure all necessary language models are available
- [ ] Verify file system permissions

## Documentation
- [ ] Create README for human_instructions directory
- [ ] Document file format standards
- [ ] Add contribution guidelines
- [ ] Include examples of good patterns

## Review Process
- [ ] Peer review of instruction sets
- [ ] Native speaker review for Arabic patterns
- [ ] Technical review for accuracy
- [ ] User testing for clarity 