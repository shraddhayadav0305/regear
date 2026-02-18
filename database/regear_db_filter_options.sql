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
-- Table structure for table `filter_options`
--

DROP TABLE IF EXISTS `filter_options`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `filter_options` (
  `id` int NOT NULL AUTO_INCREMENT,
  `filter_type_id` int NOT NULL,
  `option_value` varchar(100) NOT NULL,
  `option_label` varchar(100) NOT NULL,
  `display_order` int DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_filter_option` (`filter_type_id`,`option_value`),
  KEY `idx_filter_type` (`filter_type_id`),
  CONSTRAINT `filter_options_ibfk_1` FOREIGN KEY (`filter_type_id`) REFERENCES `filter_types` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filter_options`
--

LOCK TABLES `filter_options` WRITE;
/*!40000 ALTER TABLE `filter_options` DISABLE KEYS */;
INSERT INTO `filter_options` VALUES (1,2,'new','New',1,1,'2026-01-31 03:00:32'),(2,2,'like-new','Like New',2,1,'2026-01-31 03:00:32'),(3,2,'used','Used',3,1,'2026-01-31 03:00:32'),(4,2,'for-parts','For Parts',4,1,'2026-01-31 03:00:32'),(8,5,'last-24h','Last 24 Hours',1,1,'2026-01-31 03:00:32'),(9,5,'last-7d','Last 7 Days',2,1,'2026-01-31 03:00:32'),(10,5,'last-30d','Last 30 Days',3,1,'2026-01-31 03:00:32'),(11,5,'any-time','Any Time',4,1,'2026-01-31 03:00:32'),(15,7,'4gb','4 GB',1,1,'2026-01-31 03:00:32'),(16,7,'8gb','8 GB',2,1,'2026-01-31 03:00:32'),(17,7,'16gb','16 GB',3,1,'2026-01-31 03:00:32'),(18,7,'32gb','32 GB',4,1,'2026-01-31 03:00:32'),(19,7,'64gb','64 GB',5,1,'2026-01-31 03:00:32'),(22,11,'32gb','32 GB',1,1,'2026-01-31 03:00:32'),(23,11,'64gb','64 GB',2,1,'2026-01-31 03:00:32'),(24,11,'128gb','128 GB',3,1,'2026-01-31 03:00:32'),(25,11,'256gb','256 GB',4,1,'2026-01-31 03:00:32'),(26,11,'512gb','512 GB',5,1,'2026-01-31 03:00:32'),(27,11,'1tb','1 TB',6,1,'2026-01-31 03:00:32'),(29,8,'hdd','HDD',1,1,'2026-01-31 03:00:32'),(30,8,'ssd','SSD (SATA)',2,1,'2026-01-31 03:00:32'),(31,8,'nvme','NVMe SSD',3,1,'2026-01-31 03:00:32'),(32,8,'hybrid','Hybrid',4,1,'2026-01-31 03:00:32'),(36,9,'13inch','13\"',1,1,'2026-01-31 03:00:32'),(37,9,'14inch','14\"',2,1,'2026-01-31 03:00:32'),(38,9,'15inch','15\"',3,1,'2026-01-31 03:00:32'),(39,9,'16inch','16\"',4,1,'2026-01-31 03:00:32'),(40,9,'17inch','17\"',5,1,'2026-01-31 03:00:32'),(43,14,'1080p','Full HD (1080p)',1,1,'2026-01-31 03:00:32'),(44,14,'1440p','QHD (1440p)',2,1,'2026-01-31 03:00:32'),(45,14,'4k','4K (2160p)',3,1,'2026-01-31 03:00:32'),(46,14,'5k','5K',4,1,'2026-01-31 03:00:32'),(50,15,'60hz','60 Hz',1,1,'2026-01-31 03:00:32'),(51,15,'75hz','75 Hz',2,1,'2026-01-31 03:00:32'),(52,15,'120hz','120 Hz',3,1,'2026-01-31 03:00:32'),(53,15,'144hz','144 Hz',4,1,'2026-01-31 03:00:32'),(54,15,'165hz','165 Hz',5,1,'2026-01-31 03:00:32'),(55,15,'240hz','240 Hz',6,1,'2026-01-31 03:00:32');
/*!40000 ALTER TABLE `filter_options` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-18 22:57:17
