public class Strong_num {

	public static void main(String[] args) {
		  int no=145;
		int sum=  strong_no(no);
		if (sum == no) {
	        System.out.println(no + " is a Strong Number");
	    } else {
	        System.out.println(no + " is not a Strong Number");
	    }
	}
	
	public static int strong_no(int no) {
	    int sum = 0;
	    while (no > 0) {
	        int rem = no % 10;
	        int fact = find_fact(rem);
	        sum += fact; 
	        no = no / 10;
	    }
	    return sum;
	

	}
	public static int find_fact(int no) 
	{
		int fact=1;
		while(no>0) 
		{
			fact=fact*no;
			no-=1;
			
		
	}
		return fact;

}
}


