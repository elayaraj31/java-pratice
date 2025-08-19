package string_methods;

public class ValidateIP {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		 String ip = "192.168.1.1";
	        String regex = "^((25[0-5]|2[0-4]\\d|1?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|1?\\d\\d?)$";
	        boolean isValid = ip.matches(regex);
	        System.out.println("Is valid IP? " + isValid);
	}

}
