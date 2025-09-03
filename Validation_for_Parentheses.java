package Interview_Other_program;

import java.util.Stack;

public class Validation_for_Parentheses {
	public static void main(String[] args) {

	}

	public static boolean isValidBrackets(String s) {
		Stack<Character> stack = new Stack<>();
		for (char ch : s.toCharArray()) {
			if ("([{".indexOf(ch) != -1) {
				stack.push(ch);
			} else if (")]}".indexOf(ch) != -1) {
				if (stack.isEmpty())
					return false;
				char open = stack.pop();
				if ((open == '(' && ch != ')') || (open == '[' && ch != ']') || (open == '{' && ch != '}'))
					return false;
			}
		}
		return stack.isEmpty();

	}
}
