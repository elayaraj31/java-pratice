package project;

public class Findpow {
	public static void main(String[] args) {
//		int pow = 3;
//		int base = 2;
		int i=power(3,3);
		System.out.println(i);
	}
	public static int power(int pow,int base) {
		int result=1;
		while(pow>0) {
			result=result*base;
			
			pow=pow-1;
		}
		return result;
	}

}
