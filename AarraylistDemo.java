package Project;

import java.util.*;


public class AarraylistDemo {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		List<Integer>number=Arrays.asList(1,2,3,2,4,3,5);
		LinkedHashSet<Integer> hs = new LinkedHashSet<Integer>();
		hs.addAll(number);
		System.out.println(hs);
		System.out.println(hs.size());
		
//		Set hs = new HashSet();
//		
//		hs.add(1);
//		hs.add(2);
//		hs.add(3);
//		hs.add(2);
//		hs.add(4);
//		hs.add(3);
//		hs.add(5);
//		
//		System.out.println(hs);


		
		

	}

}
