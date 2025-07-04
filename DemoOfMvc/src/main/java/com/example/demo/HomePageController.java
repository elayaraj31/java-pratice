package com.example.demo;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class HomePageController {
	@GetMapping("/page")
	public String display_Home_Page() {
		String meassge ="wlcome";
		System.out.println("Welcome to my Home Page");
		return "home";
	}

}
