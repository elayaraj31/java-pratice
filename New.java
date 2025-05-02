package project;

public class New {
	public static void main(String[] args) {
	int no = 55;
	int div = 2;
	boolean prime=true;
	while(div<=no) {
		if(no%div==0) {
			System.out.println("NOT PRIME");

			prime=false;
			break;
		}
		div=div+1;
		if(prime==true)
			System.out.println("PRIME");
		break;
	}
	
	}

}
