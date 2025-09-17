package com.example.Course_Registration_System.Service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.PostMapping;

import com.example.Course_Registration_System.Model.Course;
import com.example.Course_Registration_System.Model.CourseRegistry;
import com.example.Course_Registration_System.Repo.CourseRepo;
import com.example.Course_Registration_System.Repo.CuurseRegistry;

@Service
public class CourseService {
	
	@Autowired
	CourseRepo courseRepo;
	
	@Autowired
	CuurseRegistry courseRegistry;

	public List<Course> availableCourses() {
		
		return courseRepo.findAll();
	}

	public List<CourseRegistry> enrolledStudents() {
		
		return courseRegistry.findAll();
	}

	public void enrollCourse(String name, String emailId, String courseName) {
		CourseRegistry courseRegistryStd = new CourseRegistry(name,emailId,courseName);
		courseRegistry.save(courseRegistryStd);
	}

	
	

}
