-- MySQL dump 10.13  Distrib 9.5.0, for macos26.0 (arm64)
--
-- Host: localhost    Database: vital_track
-- ------------------------------------------------------
-- Server version	9.5.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `allergy`
--

DROP TABLE IF EXISTS `allergy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `allergy` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `allergy`
--

LOCK TABLES `allergy` WRITE;
/*!40000 ALTER TABLE `allergy` DISABLE KEYS */;
INSERT INTO `allergy` VALUES (1,'Penicillin','Antibiotic allergy - can cause rash, hives, or anaphylaxis'),(2,'Peanuts','Food allergy - can cause severe reactions, requires avoidance'),(3,'Shellfish','Food allergy - can cause mild to severe reactions'),(4,'Dust Mites','Environmental allergy - causes respiratory symptoms'),(5,'Pollen','Seasonal allergy - causes hay fever symptoms'),(6,'Latex','Contact allergy - causes skin and systemic reactions'),(7,'Sulfa Drugs','Medication allergy - can cause skin rashes and fever'),(8,'Aspirin','Medication allergy - causes respiratory or skin reactions'),(9,'Eggs','Food allergy - common in children, various symptoms'),(10,'Dairy/Milk','Food allergy - causes digestive and skin reactions'),(11,'Other','For allergies not listed above - specify in description'),(12,'Flour',''),(13,'Milk','');
/*!40000 ALTER TABLE `allergy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appointment`
--

DROP TABLE IF EXISTS `appointment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appointment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `doctor_id` int NOT NULL,
  `appointment_type` enum('CONSULTATION','FOLLOW_UP','EMERGENCY','CHECK_UP','SURGERY','PROCEDURE') DEFAULT NULL,
  `date` datetime NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `notes` text,
  `status` enum('SCHEDULED','COMPLETED','CANCELLED','NO_SHOW') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_appointment_doctor_date` (`doctor_id`,`date`),
  KEY `patient_id` (`patient_id`),
  KEY `ix_appointment_date` (`date`),
  CONSTRAINT `appointment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`),
  CONSTRAINT `appointment_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointment`
--

LOCK TABLES `appointment` WRITE;
/*!40000 ALTER TABLE `appointment` DISABLE KEYS */;
INSERT INTO `appointment` VALUES (2,3,1,'CHECK_UP','2025-12-24 16:30:00','2025-12-09 12:23:45','2025-12-09 16:17:50',NULL,'CANCELLED'),(3,5,1,'CHECK_UP','2025-12-12 17:40:00','2025-12-10 07:40:25','2025-12-10 07:40:25','regular checkup','SCHEDULED'),(5,7,1,'CHECK_UP','2025-12-30 12:30:00','2025-12-25 14:29:04','2025-12-25 14:29:04',NULL,'SCHEDULED');
/*!40000 ALTER TABLE `appointment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `demographic_info`
--

DROP TABLE IF EXISTS `demographic_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `demographic_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `address` varchar(200) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `emergency_contact` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `patient_id` (`patient_id`),
  CONSTRAINT `demographic_info_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `demographic_info`
--

LOCK TABLES `demographic_info` WRITE;
/*!40000 ALTER TABLE `demographic_info` DISABLE KEYS */;
INSERT INTO `demographic_info` VALUES (1,2,'Somewhere in the middle of nowhere 14.','+49178145123','Sam Shuffel +49123145178'),(2,4,'Lower city 25','+49170005123',NULL),(3,5,'Passauer str. 25',NULL,'Frankestine, Lara +49876222785'),(4,3,'Hoshstrasse 26, passau','+49173332223',NULL);
/*!40000 ALTER TABLE `demographic_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doctor`
--

DROP TABLE IF EXISTS `doctor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) NOT NULL,
  `username` varchar(150) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `email` varchar(120) NOT NULL,
  `email_confirmed` tinyint(1) NOT NULL,
  `email_confirmed_at` datetime DEFAULT NULL,
  `password` varchar(200) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `ix_doctor_email` (`email`),
  KEY `ix_doctor_last_name` (`last_name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doctor`
--

LOCK TABLES `doctor` WRITE;
/*!40000 ALTER TABLE `doctor` DISABLE KEYS */;
INSERT INTO `doctor` VALUES (1,'Muhammad','Bashi','dr_bashi',NULL,'bashx0w@gmail.com',1,'2025-12-09 01:56:09','pbkdf2:sha256:600000$RYovEljkzYfWIpnL$1622bf9dc00b7641acc9cf29520cca8e8ad6b633ec3c70a0b8836845c7171951','2025-12-09 01:55:50','2025-12-09 02:05:47'),(2,'testy','klar','dr_testy',NULL,'pejap88962@dubokutv.com',1,'2026-01-06 11:30:58','pbkdf2:sha256:600000$Y5O8eL3XMFLguDxW$f2a58491924a310dc09027f71ecc0b2908e033ffd1674775dafff4ca4d245d31','2026-01-06 11:30:44','2026-01-06 11:30:58'),(3,'Smith','Tommaios','dr_smith',NULL,'nopigar342@gavrom.com',1,'2026-01-06 11:36:55','pbkdf2:sha256:600000$O2dxSg2d7JVhIYZE$4f2878889fa6fa7365e7ecbf6ca18d4e83115fe8bedb538dc9a749641117404b','2026-01-06 11:36:44','2026-01-06 11:36:55'),(4,'Nikalious','Screimburger','dr_nika',NULL,'pahiy46066@cameltok.com',0,NULL,'pbkdf2:sha256:600000$sGPLZrdOKAly23sg$847d9d798b09ef4b40b53a273350cd8e4066f764d65973a173f7f7c3114bb7dd','2026-01-07 16:39:55','2026-01-07 16:39:55'),(5,'George','Michael','dr_george',NULL,'bovixi2284@akixpres.com',0,NULL,'pbkdf2:sha256:600000$Tv5zwCPfoKcMSAhc$0f29a1950c3d0cbb73531d9acf1892a8855c31637cd00d2f29164f63ece62495','2026-01-10 20:03:09','2026-01-10 20:03:09');
/*!40000 ALTER TABLE `doctor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doctor_specialty`
--

DROP TABLE IF EXISTS `doctor_specialty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctor_specialty` (
  `doctor_id` int NOT NULL,
  `specialty_id` int NOT NULL,
  PRIMARY KEY (`doctor_id`,`specialty_id`),
  KEY `specialty_id` (`specialty_id`),
  CONSTRAINT `doctor_specialty_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`),
  CONSTRAINT `doctor_specialty_ibfk_2` FOREIGN KEY (`specialty_id`) REFERENCES `specialty` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doctor_specialty`
--

LOCK TABLES `doctor_specialty` WRITE;
/*!40000 ALTER TABLE `doctor_specialty` DISABLE KEYS */;
INSERT INTO `doctor_specialty` VALUES (1,1),(2,1),(3,2),(4,3);
/*!40000 ALTER TABLE `doctor_specialty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `laboratory_result`
--

DROP TABLE IF EXISTS `laboratory_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `laboratory_result` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `test_name` varchar(100) NOT NULL,
  `date` datetime NOT NULL,
  `result` varchar(200) NOT NULL,
  `unit` varchar(50) DEFAULT NULL,
  `reference_range` varchar(100) DEFAULT NULL,
  `status` enum('NORMAL','ABNORMAL','HIGH','LOW','CRITICAL','PENDING') DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `notes` text,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `ix_laboratory_result_date` (`date`),
  CONSTRAINT `laboratory_result_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `laboratory_result`
--

LOCK TABLES `laboratory_result` WRITE;
/*!40000 ALTER TABLE `laboratory_result` DISABLE KEYS */;
INSERT INTO `laboratory_result` VALUES (1,3,'Hemoglobin A1c (HbA1c)','2025-12-04 14:30:00','13.2 Normal',NULL,'10-17','NORMAL','2025-12-09 16:24:07','2026-01-10 21:04:12','Patient managed to raise her Hemoglobin'),(3,7,'Hemoglobin A1c (HbA1c)','2025-12-09 15:29:00','13.2',NULL,NULL,'NORMAL','2025-12-25 14:30:01','2025-12-25 14:30:01',NULL),(4,5,'Albumin','2025-12-24 08:19:00','Normal',NULL,NULL,NULL,'2026-01-06 13:24:02','2026-01-06 13:24:02',NULL);
/*!40000 ALTER TABLE `laboratory_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medical_history`
--

DROP TABLE IF EXISTS `medical_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medical_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `allergy_id` int NOT NULL,
  `description` text NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `allergy_id` (`allergy_id`),
  KEY `ix_medical_history_date` (`date`),
  CONSTRAINT `medical_history_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`),
  CONSTRAINT `medical_history_ibfk_2` FOREIGN KEY (`allergy_id`) REFERENCES `allergy` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medical_history`
--

LOCK TABLES `medical_history` WRITE;
/*!40000 ALTER TABLE `medical_history` DISABLE KEYS */;
INSERT INTO `medical_history` VALUES (1,3,9,'Rush after eating eggs','2025-12-02 00:00:00'),(3,4,8,'headache','2025-12-07 00:00:00'),(4,4,9,'stomachache','2025-12-01 00:00:00');
/*!40000 ALTER TABLE `medical_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient`
--

DROP TABLE IF EXISTS `patient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patient` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(120) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `gender` enum('MALE','FEMALE','OTHER') DEFAULT NULL,
  `date_of_birth` date NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `doctor_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `doctor_id` (`doctor_id`),
  KEY `ix_patient_email` (`email`),
  KEY `ix_patient_last_name` (`last_name`),
  KEY `ix_patient_first_name` (`first_name`),
  CONSTRAINT `patient_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient`
--

LOCK TABLES `patient` WRITE;
/*!40000 ALTER TABLE `patient` DISABLE KEYS */;
INSERT INTO `patient` VALUES (1,'Chris','Talerson','chris.tolerson@gmail.com',NULL,NULL,'MALE','1995-12-21','2025-12-09 02:13:34','2025-12-09 02:13:34',1),(2,'Clara','Shuffel','clara.shuffel@gmail.com',NULL,NULL,'FEMALE','1990-12-19','2025-12-09 10:45:13','2025-12-09 11:17:22',1),(3,'Lara','Confusy','lara_confusy@gmail.com',NULL,NULL,'OTHER','2000-12-28','2025-12-09 10:49:14','2026-01-07 08:04:24',1),(4,'Harry','Small','harry_small@gmail.com',NULL,NULL,'MALE','1988-12-26','2025-12-09 11:19:57','2025-12-09 12:20:51',1),(5,'Yeri','Nerde','yeri.nerde@gmail.com',NULL,NULL,'MALE','2004-12-11','2025-12-10 07:38:37','2026-01-06 11:27:29',1),(7,'Handy','Hannelore',NULL,NULL,NULL,'FEMALE','1990-12-20','2025-12-25 14:27:27','2026-01-06 11:26:15',1);
/*!40000 ALTER TABLE `patient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prescription`
--

DROP TABLE IF EXISTS `prescription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prescription` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `medication_name` varchar(100) NOT NULL,
  `dosage` varchar(100) NOT NULL,
  `frequency` varchar(100) NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `prescription_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prescription`
--

LOCK TABLES `prescription` WRITE;
/*!40000 ALTER TABLE `prescription` DISABLE KEYS */;
/*!40000 ALTER TABLE `prescription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `radiology_imaging`
--

DROP TABLE IF EXISTS `radiology_imaging`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `radiology_imaging` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `date` datetime NOT NULL,
  `image_filename` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `ix_radiology_imaging_date` (`date`),
  CONSTRAINT `radiology_imaging_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `radiology_imaging`
--

LOCK TABLES `radiology_imaging` WRITE;
/*!40000 ALTER TABLE `radiology_imaging` DISABLE KEYS */;
INSERT INTO `radiology_imaging` VALUES (3,1,'XRAY','2025-12-11 01:52:00','patient_1/d5ed01cd-c8c2-446b-8ab1-d29d9a43b225.png','2025-12-12 00:52:29','2025-12-12 00:52:29'),(5,7,'XRAY','2026-01-06 18:25:00','patient_7/4dcdccb7-8b91-470c-b99c-d324994cc258.png','2026-01-06 15:56:31','2026-01-11 06:50:59'),(8,3,'XRAY','2026-01-10 21:37:00','patient_3/b8836ffb-03bc-489f-a498-3352deecefe6.png','2026-01-10 20:37:37','2026-01-10 20:55:41');
/*!40000 ALTER TABLE `radiology_imaging` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `social_history`
--

DROP TABLE IF EXISTS `social_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `social_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `smoking_status` tinyint(1) NOT NULL,
  `alcohol_use` enum('LIGHT','MODERATE','HEAVY','NONE') DEFAULT NULL,
  `drug_use` enum('RECREATIONAL','MEDICAL','ADDICTIVE','NONE') DEFAULT NULL,
  `occupation` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `patient_id` (`patient_id`),
  CONSTRAINT `social_history_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `social_history`
--

LOCK TABLES `social_history` WRITE;
/*!40000 ALTER TABLE `social_history` DISABLE KEYS */;
INSERT INTO `social_history` VALUES (1,1,0,'LIGHT','RECREATIONAL',NULL),(2,2,0,'NONE','NONE','Teacher'),(3,3,0,'HEAVY','ADDICTIVE','Student'),(4,4,1,'MODERATE','RECREATIONAL','Doctor'),(5,5,0,'NONE','NONE','Software developer'),(7,7,0,'NONE','NONE','Best mom in the world');
/*!40000 ALTER TABLE `social_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `specialty`
--

DROP TABLE IF EXISTS `specialty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `specialty` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `specialty`
--

LOCK TABLES `specialty` WRITE;
/*!40000 ALTER TABLE `specialty` DISABLE KEYS */;
INSERT INTO `specialty` VALUES (3,'Dermatology'),(1,'General Practitioner'),(2,'Neurology');
/*!40000 ALTER TABLE `specialty` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-12 23:14:58
