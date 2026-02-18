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
-- Table structure for table `listings`
--

DROP TABLE IF EXISTS `listings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `listings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `category_id` int DEFAULT NULL,
  `subcategory_id` int DEFAULT NULL,
  `title` varchar(150) NOT NULL,
  `description` longtext,
  `price` int DEFAULT NULL,
  `is_negotiable` tinyint(1) DEFAULT '0',
  `item_condition` varchar(50) DEFAULT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `year_of_purchase` int DEFAULT NULL,
  `warranty_available` tinyint(1) DEFAULT '0',
  `location` varchar(100) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `photos` varchar(1000) DEFAULT NULL,
  `approval_status` enum('pending','approved','rejected') DEFAULT 'pending',
  `rejection_reason` text,
  `status` enum('active','sold','archived') DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `category` varchar(100) DEFAULT NULL,
  `subcategory` varchar(100) DEFAULT NULL,
  `admin_notes` longtext,
  `approved_by` int DEFAULT NULL,
  `approved_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `category_id` (`category_id`),
  KEY `subcategory_id` (`subcategory_id`),
  CONSTRAINT `listings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `listings_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `listings_ibfk_3` FOREIGN KEY (`subcategory_id`) REFERENCES `subcategories` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `listings`
--

LOCK TABLES `listings` WRITE;
/*!40000 ALTER TABLE `listings` DISABLE KEYS */;
INSERT INTO `listings` VALUES (2,2,NULL,NULL,'Samsung Galaxy S25 Plus 5G for sale in excellent condition. 12GB RAM and 256GB ','Samsung Galaxy S25 Plus 5G for sale in excellent condition.\r\n12GB RAM and 256GB storage variant in premium Silver Shadow color.\r\n\r\n✔ Smooth performance\r\n✔ Super AMOLED display\r\n✔ Powerful camera\r\n✔ Battery backup is very good\r\n✔ No scratches or damage\r\n\r\nIncludes original box and charger.\r\nReason for selling: Upgraded to another device.',60000,0,'Brand New',NULL,NULL,NULL,0,'lucknow',NULL,NULL,'6307142274','mahimayadav2408@gmail.com','static/uploads/products/cdeb164e7d225f6723cffe03_Screenshot_2026-02-10_010620.png,static/uploads/products/984f586bbe5c39ac093c80d9_Screenshot_2026-02-10_010552.png','approved',NULL,'active','2026-02-09 20:14:01','2026-02-09 20:22:13','Mobile Phones','Android Phones','',3,'2026-02-09 20:22:13'),(3,2,NULL,NULL,'Samsung Galaxy S25 Plus 5G (12GB RAM + 256GB Storage) blue','Specifications:\r\n\r\n4GB RAM, 64GB Storage\r\n\r\nMediaTek Helio G99 processor (AnTuTu score: 624K)\r\n\r\n50MP main camera for sharp photos\r\n\r\nSlim 7.6mm design, IP54 dust & splash resistance\r\n\r\n5000mAh battery with 25W fast charging\r\n\r\n6 generations of OS upgrades for long-term use\r\n\r\nNote: Charger not included',60000,0,'Like New',NULL,NULL,NULL,0,'lucknow',NULL,NULL,'6307142274','mahimayadav2408@gmail.com','static/uploads/products/96254b14194e37f0fbe7a13b_Screenshot_2026-02-10_010552.png,static/uploads/products/c20db02291cde0db2ae3d9f5_Screenshot_2026-02-10_010620.png,static/uploads/products/f94588502210b80a1a8389a0_Screenshot_2026-02-10_010603.png','approved',NULL,'active','2026-02-10 05:57:32','2026-02-10 05:59:20','Mobile Phones','Android Phones','',3,'2026-02-10 05:59:20');
/*!40000 ALTER TABLE `listings` ENABLE KEYS */;
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
