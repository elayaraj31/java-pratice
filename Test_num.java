package problem;

public class Test_num {
	public static void main(String[] args)
	{
	int c=153;
	int i=info(c);
	//System.out.println(i);
	}
	public static int info(int c) {
		int n=c;
		while(n>0) {
			int a=n%10;
			System.out.println(a);
			n=n/10;
		}
		return c;
	}
}

