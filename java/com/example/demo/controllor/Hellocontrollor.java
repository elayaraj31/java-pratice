package com.example.demo.controllor;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@CrossOrigin(origins = "http://localhost:3000/")
public class Hellocontrollor {
	
	@GetMapping("/api/payilagam")
	public String display() {
		System.out.println("==================");
		return "Hello World!";
		
	}

}
