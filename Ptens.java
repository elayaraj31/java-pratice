package Project;

public class Ptens {
	public static void main(String[] args) {
		for(int row=1;row<=5;row++) {
			for(int col=1;col<=6-row;col++) {
				System.out.print(col+row-1+" ");
			}
			System.out.println();
		}
	}

}
