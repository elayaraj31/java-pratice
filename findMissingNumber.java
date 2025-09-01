package array_Program;

public class findMissingNumber {
    

    public static void main(String[] args) {
       
     
    }
    public static void moveZeros(int[] arr) {
    	int arr1[]= {1,0,6,0,7,0};
        int index = 0;
        for (int num : arr1) {
            if (num != 0) {
                arr1[index++] = num;
            }
        }
        while (index < arr1.length) {
            arr1[index++] = 0;
            
        }
        
    }

}
