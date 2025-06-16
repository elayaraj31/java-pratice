package com.example.demo.Controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.Student_entitiy.Student_entitiy;
import com.example.demo.stud_repository.StdRepo;

@RestController
@CrossOrigin(origins = "http://localhost:3000")
public class DbController {
	
	@Autowired
	StdRepo repo;

	@GetMapping("/api/stud")
	public List<Student_entitiy> listStudent() { 
		return repo.findAll();
	}
//	@PostMapping("/api/stud")
//    public String addUser(@RequestBody Student_entitiy user) {
//  repo.save(user);
//        System.out.println("User Received: " + user.getRoll_no()+" , "+ user.getName() + ", " + user.getLast_name());
//        return "User added successfully!";
//    }

}
