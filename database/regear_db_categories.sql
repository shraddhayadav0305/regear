-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: regear_db
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `icon` varchar(20) DEFAULT NULL,
  `description` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Mobile Phones','?','Smartphones and mobile devices','2026-02-09 18:17:59'),(2,'Laptops & Computers','?','Laptops, desktops, and computers','2026-02-09 18:17:59'),(3,'Tablets','?','Tablet devices and e-readers','2026-02-09 18:17:59'),(4,'Computer Accessories','⌨️','Keyboards, mice, cables, and more','2026-02-09 18:17:59'),(5,'Printers & Scanners','?️','Printers, scanners, and related devices','2026-02-09 18:17:59'),(6,'Monitors & Displays','?️','Computer monitors and display devices','2026-02-09 18:17:59'),(7,'Gaming Consoles','?','PlayStation, Xbox, Nintendo devices','2026-02-09 18:17:59'),(8,'Smart Watches','⌚','Wearable smart devices','2026-02-09 18:17:59'),(9,'Cameras & DSLR','?','Digital cameras and DSLR equipment','2026-02-09 18:17:59'),(10,'Networking Devices','?','Routers, WiFi, networking equipment','2026-02-09 18:17:59'),(11,'Storage Devices','?','SSD, HDD, Pendrive, memory cards','2026-02-09 18:17:59'),(12,'Speakers & Headphones','?','Audio devices and headphones','2026-02-09 18:17:59'),(13,'Electronic Components','?','Circuit boards, chips, and components','2026-02-09 18:17:59'),(14,'TVs & Home Entertainment','?','Television sets and home theater','2026-02-09 18:17:59'),(15,'Smart Home Devices','?','Smart home automation devices','2026-02-09 18:17:59');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-18 22:57:18
