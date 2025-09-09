package Interview_Other_program;

import java.util.Scanner;

public class Recursive_and_iterative {
	
	public static void main(String[] args) {
		//System.out.println(factorialRecursive(5)); // 120
		
		Scanner n = new Scanner(System.in);
		int val =n.nextInt();
		System.out.println("Factorial num  "+factorialIterative(val)); // 1205

		
	}
	public static long factorialIterative(int n) {
	    long result = 1;
	    for (int i = 2; i <= n; i++) {
	        result *= i; // Multiply result by each number from 2 to n
	    }
	    return result;
	}
	
//	public static long factorialRecursive(int n) {
//	    if (n <= 1) {
//	        return 1; // Base case: factorial of 0 or 1 is 1
//	    }
//	    return n * factorialRecursive(n - 1); // Recursive call
//	}

}
