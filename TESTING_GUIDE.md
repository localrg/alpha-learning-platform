# Alpha Learning Platform: Testing Guide

**Date:** October 17, 2025
**Author:** Manus AI

---

## 1. Introduction

This guide provides instructions for testing the Alpha Learning Platform. It includes access URLs, test credentials for all user roles, and a list of key features to test for each role. The backend and frontend servers are currently running and ready for testing.

## 2. Accessing the Application

The frontend application is accessible at the following URL:

- **Frontend URL:** [http://localhost:5175/](http://localhost:5175/)

The backend API is running at:

- **Backend URL:** [http://localhost:5000/](http://localhost:5000/)

## 3. Test Credentials

The following test accounts have been created for each user role. You can use these credentials to log in and test the platform's functionality.

| Role | Email | Password |
| :--- | :--- | :--- |
| Student | `student@test.com` | `password123` |
| Teacher | `teacher@test.com` | `password123` |
| Parent | `parent@test.com` | `password123` |
| Admin | `admin@test.com` | `password123` |

## 4. Testing Scenarios

### 4.1. Student Role

**Objective:** Test the core learning experience, gamification, and social features.

| Feature to Test | Steps to Perform |
| :--- | :--- |
| **Initial Assessment** | 1. Log in as the student. 2. Complete the initial assessment to get a personalized learning path. |
| **Learning Dashboard** | 1. View the dashboard to see recommended skills. 2. Start a practice session for a recommended skill. |
| **Skill Practice** | 1. Answer questions in a practice session. 2. Observe the XP gain and progress updates. |
| **Gamification** | 1. Check the leaderboard to see your ranking. 2. View your achievements on the achievements page. |
| **Social Features** | 1. Visit the activity feed to see what others are doing. 2. Add a friend and send a message. |

### 4.2. Teacher Role

**Objective:** Test class management, student monitoring, and assignment creation.

| Feature to Test | Steps to Perform |
| :--- | :--- |
| **Teacher Dashboard** | 1. Log in as the teacher. 2. View the dashboard to see an overview of your classes and students. |
| **Class Management** | 1. Create a new class. 2. Add the test student to your class. |
| **Student Progress** | 1. View the progress of the test student. 2. Check their assessment results and learning activity. |
| **Assignments** | 1. Create a new assignment for your class. 2. Assign a specific skill for students to practice. |

### 4.3. Parent Role

**Objective:** Test child monitoring, communication, and goal setting.

| Feature to Test | Steps to Perform |
| :--- | :--- |
| **Parent Dashboard** | 1. Log in as the parent. 2. View the dashboard for an overview of your child's activity. |
| **Child Linking** | 1. Link the test student to your parent account. |
| **Child Progress** | 1. View the test student's progress and performance reports. |
| **Goal Setting** | 1. Set a new learning goal for your child. 2. Track their progress towards the goal. |

### 4.4. Admin Role

**Objective:** Test platform management, user administration, and content control.

| Feature to Test | Steps to Perform |
| :--- | :--- |
| **Admin Dashboard** | 1. Log in as the admin. 2. View the platform-wide metrics and user statistics. |
| **User Management** | 1. View the list of all users. 2. Create a new test user and then delete it. |
| **Content Management** | 1. View the list of skills. 2. Create a new skill, edit it, and then delete it. |
| **System Settings** | 1. View the system settings. 2. Change a setting and save it. |
| **Audit Logs** | 1. View the audit logs to see a record of your recent actions. |

---

This guide covers the main features of the Alpha Learning Platform. Feel free to explore other features and functionalities as you test the application. If you encounter any issues or have any questions, please let me know.
