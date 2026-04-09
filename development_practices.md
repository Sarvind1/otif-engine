# Development Practices - OTIF Stage Calculation Engine

## Core Development Principles

### ⚠️ CRITICAL: Always Confirm Before Writing Code
- **ALWAYS ask for confirmation before writing any code**
- Present the development plan and approach first
- Wait for explicit approval before implementation
- This prevents wasted effort and ensures alignment

### 1. Iterative Development
- **Never write long pieces of code in one go**
- Use feedback-based development cycles
- Start with small, testable components
- Build incrementally with validation at each step

### 2. Code Simplicity
- Write simple, easy-to-read code
- Avoid over-engineering solutions
- Prioritize clarity over cleverness
- Use descriptive variable and function names

### 3. Debugging Support
- **Implement debug mode throughout the codebase**
- Add strategic debug prints with clear prefixes
- Easy toggle between debug and execution modes
- Example pattern:
  ```python
  def debug_print(message, data=None, debug=False):
      if debug:
          print(f"[MODULE_NAME] {message}")
          if data is not None:
              print(f"  → {data}")
  ```

### 4. Error Handling
- Graceful degradation for missing data
- Clear error messages with context
- Distinguish between warnings and critical errors
- Never fail silently

### 5. Data Handling Best Practices
- Standardize null value handling early (`fillna("")`)
- Be explicit about data type conversions
- Handle mixed date formats consistently
- Validate data existence before operations

### 6. Module Structure
- Clear separation of concerns
- One module = one responsibility
- No business logic in data fetching layers
- Configuration-driven business rules

### 7. Documentation
- Document complex logic inline
- Add docstrings to all functions
- Explain "why" not just "what"
- Keep README and brain documents updated

### 8. Performance Considerations
- Pre-compute mapping dictionaries
- Avoid iterative lookups in apply functions
- Use vectorized pandas operations where possible
- Clear intermediate dataframes when no longer needed

### 9. Testing Strategy
- **Keep tests simple and focused** - No exhaustive testing unless specifically requested
- Write minimal tests that verify core functionality works
- Test notebooks should be quick to run and easy to understand
- Example of a good test:
  ```python
  # Simple functionality test
  result = fetch_data(inputs)
  print(f"Success: {result is not None}")
  print(f"Shape: {result.shape}")
  ```
- Avoid:
  - Multiple sections of comprehensive checks
  - Testing every possible edge case
  - Long performance benchmarks
  - Exhaustive data quality reports

### 10. Code Modification Rules
- **Do not improve code if unclear on how it works**
- Ask for clarification before making assumptions
- Preserve existing functionality when refactoring
- Document any behavioral changes

## File Operations
- Use `edit_file` for modifying existing files
- Use `write_file` only for new files
- Always backup critical files before major changes

## Communication Guidelines
- **ALWAYS CONFIRM BEFORE WRITING ANY CODE** (not just large changes)
- Ask for clarification when requirements are unclear
- Provide code snippets with explanations
- Break complex features into step-by-step instructions
- Suggest testing strategies for critical components
- When creating tests or utilities:
  - Start with the minimal viable version
  - Ask if more comprehensive testing is needed
  - Don't assume exhaustive testing is required
