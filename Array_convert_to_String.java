package String_program;

import java.util.Arrays;

public class Array_convert_to_String {

	public static void main(String[] args) {
		
		// Array to String Number 
		
	/*	int[] intArray = {1, 2, 3, 4, 5};
        String arrayAsString = Arrays.toString(intArray);
        System.out.println(arrayAsString); */
        
        // Array to String Method 1
        String[] stringArray = {"apple", "banana", "cherry"};
//        String stringArrayAsString = Arrays.toString(stringArray);
//        System.out.println(stringArrayAsString);  
        
        // Mthod 2
        String joinedString = String.join(" ", stringArray); // Join with space
        System.out.println(joinedString); 
        
        // Revers the String 
        
         String Copy = "";
		   for(int i = joinedString.length()-1;i>=0;i--) {
			Copy += joinedString.charAt(i);	
		}
		System.out.println(Copy);

	}

}
