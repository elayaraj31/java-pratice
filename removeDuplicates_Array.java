package array_Program;

public class removeDuplicates_Array {

	public static void main(String[] args) {

		int arr[] = { 10, 20, 20, 70, 80, 30, 40, 40, 40, 70, 50, 80, 50 };
		int n = arr.length;

		int[] temp = new int[n];
		int j = 0; // index for temporary array (unique elements)

		for (int i = 0; i < n; i++) {
			boolean isDuplicate = false;

			// Check if arr[i] is already present in temp
			for (int k = 0; k < j; k++) {
				if (arr[i] == temp[k]) {
					isDuplicate = true;
					break;
				}
			}

			// If not duplicate, add to temp
			if (!isDuplicate) {
				temp[j] = arr[i];
				j++;
			}
		}

		// Now copy unique elements back to original array if needed
		for (int i = 0; i < j; i++) {
			arr[i] = temp[i];
		}

		// Print all unique elements
		for (int i = 0; i < j; i++) {
			System.out.print(arr[i] + " ");
		}
	}
}




// Using collection HasMap

//int []arr= {2,2,4,5,6,1};
//LinkedHashSet<Integer> set = new LinkedHashSet<>();
//for (int num : arr) {
//    set.add(num);
//}
//int[] result = new int[set.size()];
//int i = 0;
//for (int num : set) {
//    result[i++] = num;
//    System.err.print(num);
//}
