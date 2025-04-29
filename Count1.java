public class Count1 {
	public static void main(String[] args) {
		int n=-143;
		int count=0;
		
		if(n<0) {
			n=n*(-1);
		}
		
		
		if(n==0) {
			System.out.println(1);
		}
		else {
			while(0<n) {
				n=n/10;
				count=count+1;
			}
			System.out.println(count);

		}
		
	}

}

