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
-- Table structure for table `filter_types`
--

DROP TABLE IF EXISTS `filter_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `filter_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `slug` varchar(100) NOT NULL,
  `type` varchar(50) NOT NULL,
  `description` text,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`),
  KEY `idx_type` (`type`),
  KEY `idx_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filter_types`
--

LOCK TABLES `filter_types` WRITE;
/*!40000 ALTER TABLE `filter_types` DISABLE KEYS */;
INSERT INTO `filter_types` VALUES (1,'Price Range','price-range','range','Filter by price (min - max)',1,'2026-01-31 03:00:32'),(2,'Condition','condition','multi_select','New, Like New, Used, For Parts',1,'2026-01-31 03:00:32'),(3,'Brand','brand','multi_select','Product brand/manufacturer',1,'2026-01-31 03:00:32'),(4,'Location','location','select','City or state location',1,'2026-01-31 03:00:32'),(5,'Posted Date','posted-date','select','When listing was posted',1,'2026-01-31 03:00:32'),(6,'Processor (CPU)','processor','multi_select','CPU type for computers',1,'2026-01-31 03:00:32'),(7,'RAM','ram','multi_select','RAM capacity in GB',1,'2026-01-31 03:00:32'),(8,'Storage Type','storage-type','multi_select','HDD, SSD, NVMe',1,'2026-01-31 03:00:32'),(9,'Screen Size','screen-size','multi_select','Display size in inches',1,'2026-01-31 03:00:32'),(10,'Mobile Brand','mobile-brand','multi_select','Mobile phone brand',1,'2026-01-31 03:00:32'),(11,'Storage Capacity','storage-capacity','multi_select','Storage in GB/TB',1,'2026-01-31 03:00:32'),(12,'Warranty Status','warranty-status','multi_select','With/Without warranty',1,'2026-01-31 03:00:32'),(13,'Graphics Card','graphics-card','multi_select','GPU/Video card model',1,'2026-01-31 03:00:32'),(14,'Resolution','resolution','multi_select','Screen resolution (1080p, 4K, etc)',1,'2026-01-31 03:00:32'),(15,'Refresh Rate','refresh-rate','multi_select','Monitor refresh rate (Hz)',1,'2026-01-31 03:00:32');
/*!40000 ALTER TABLE `filter_types` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-18 22:57:20
