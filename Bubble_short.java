package array;

public class Bubble_short {

	public static void main(String[] args) {
		
		int [] ar= {50,40,30,20,10};
		for(int j=1;j<ar.length;j++) 
		{
			for(int i=0;i<ar.length-1;i++) 
			{
				if(ar[i]>ar[i+1]) 
				{
					int temp=ar[i];
					ar[i]=ar[i+1];
					ar[i+1]=temp;
//					System.out.print();
					
				}
			}
			
		}
		System.out.print("bubblesort:"+" ");
		for(int i=0;i<ar.length;i++)
			System.out.print(ar[i]+" ");
	}
	
}
