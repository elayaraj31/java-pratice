package leedCodeProblemes;

public class FindTheDuplicate_In_String {

	public static void main(String[] args) {
		
		String s ="loveleedcode";
		
		 boolean[] visited = new boolean[s.length()];	
		
		 for (int i = 0; i < s.length(); i++) 
		 {
	            if (!visited[i]) { 
	                char currentChar = s.charAt(i);
	                int count = 1; 
	                System.out.println(currentChar);
	                for (int j = i + 1; j < s.length(); j++) {
	                    if (currentChar == s.charAt(j)) {
	                        count++;
	                        visited[j] = true; 
	                    }
	                }
	                if (count > 1) {
	                    System.out.println(currentChar + " : " + count);
	                }
	            }
		 }

		
		
		
	}

}
