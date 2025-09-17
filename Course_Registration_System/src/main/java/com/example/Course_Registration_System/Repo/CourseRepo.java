package com.example.Course_Registration_System.Repo;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.example.Course_Registration_System.Model.Course;

@Repository
public interface CourseRepo extends JpaRepository<Course,String> {

}
