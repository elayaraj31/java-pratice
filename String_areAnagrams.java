package String_program;

public class String_areAnagrams {
	
	public static void main(String[] args) {
		String s1 = "car";
		String s2 = "rac";
		
		//System.out.println(areAnagrams(s1, s2) ? "true" : "false");
		
		if (areAnagrams(s1, s2))
            System.out.println("true");
        else
            System.out.println("false");
		}
	 static boolean areAnagrams(String s1, String s2) {
		if(s1.length() != s2.length()) return false;
		
		int [] freq = new int [26];
		
		for(int i = 0; i< s1.length();i++)
			freq[s1.charAt(i) - 'a']++;
		
		for(int i = 0; i< s2.length();i++)
			freq[s1.charAt(i) - 'a']--;
		
		for(int count : freq) {
			if(count != 0)
				return false;
		}
		return true;
	 }
}
