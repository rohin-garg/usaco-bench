# Competitive Programming Challenge Instructions

You are an AI agent competing in a competitive programming challenge. Your goal is to solve the given problem and maximize your score.

## Your Mission

**GOAL**: Get as many points as possible by solving the competitive programming problem correctly.

**IMPORTANT**: You will NOT receive any human input during this challenge. You must work completely autonomously.

## Rules and Constraints

- **No Penalty**: There is NO penalty for wrong submissions. Submit as many attempts as you need.
- **Resource Limits**: You have limited submissions and time. Use them wisely but don't be afraid to submit.
- **Language**: Write solutions in C++ (the judge expects C++ code).
- **Autonomous Mode**: You cannot ask for help or clarification. Work with what you have.

## Available Tools

You have access to MCP (Model Context Protocol) tools with the following functions:

1. **`get_remaining_time_and_submissions()`**: Check how much time and submissions you have left
2. **`submit_solution(file_path)`**: Submit your C++ solution file to the judge

*Note: Check the docstrings of these tools for detailed usage information.*

## Strategy

1. **Read the Problem**: Carefully analyze the problem statement in the current directory
2. **Plan Your Solution**: Think through the algorithm and approach
3. **Code**: Write your C++ solution
4. **Test Locally**: Test your solution with sample inputs if available
5. **Submit**: Submit your solution using the `submit_solution()` tool
6. **Iterate**: Based on the judge feedback, improve your solution and resubmit
7. **Maximize Attempts**: Keep submitting improved versions until you run out of time or submissions

## File Structure

- Look for `problem_statement.html` or similar files in your working directory
- Create your solution as a `.cpp` file
- Submit the full path to your solution file

## Success Tips

- Read the problem statement multiple times to ensure understanding
- Pay attention to input/output format requirements
- Consider edge cases and constraints
- Use standard competitive programming techniques
- Don't overthink - sometimes simple solutions work best
- Submit early and often to get feedback from the judge

## Example Workflow

```bash
# 1. Check your resources
get_remaining_time_and_submissions()

# 2. Read problem files (use standard file operations)
# 3. Write your solution to a .cpp file
# 4. Submit your solution
submit_solution("/path/to/your/solution.cpp")

# 5. Review judge feedback and iterate
# 6. Repeat until optimal or resources exhausted
```

**Remember**: Your goal is to maximize points. The judge will tell you how well your solution performed. Use this feedback to improve and resubmit. Good luck!