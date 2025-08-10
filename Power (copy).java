public class Power {
	public static void main(String[] args) {
		int result=power(5,3);
		System.out.println(result);
	}
	public static int power(int n,int base) {
		int result=1;
		int pow=1;
		while(pow>0) {
			result=result*base;
			
			pow=pow-1;
		}
		
		
		return result;
	}
}
		


