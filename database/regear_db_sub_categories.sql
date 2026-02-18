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
-- Table structure for table `sub_categories`
--

DROP TABLE IF EXISTS `sub_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sub_categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `slug` varchar(100) NOT NULL,
  `description` text,
  `display_order` int DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_category_slug` (`category_id`,`slug`),
  KEY `idx_category` (`category_id`),
  KEY `idx_active` (`is_active`),
  KEY `idx_order` (`display_order`),
  CONSTRAINT `sub_categories_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sub_categories`
--

LOCK TABLES `sub_categories` WRITE;
/*!40000 ALTER TABLE `sub_categories` DISABLE KEYS */;
INSERT INTO `sub_categories` VALUES (1,1,'Apple iPhone','apple-iphone','iPhones of all models',1,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(2,1,'Samsung Galaxy','samsung-galaxy','Samsung Galaxy series',2,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(3,1,'OnePlus','oneplus','OnePlus devices',3,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(4,1,'Xiaomi & Poco','xiaomi-poco','Xiaomi and Poco phones',4,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(5,1,'Realme','realme','Realme devices',5,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(6,1,'Mobile Accessories','mobile-accessories','Phone cases, chargers, protectors',6,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(8,2,'Gaming Laptops','gaming-laptops','High-performance gaming laptops',1,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(9,2,'Business Laptops','business-laptops','Professional business laptops',2,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(10,2,'MacBooks','macbooks','Apple MacBook computers',3,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(11,2,'Desktop Computers','desktop-computers','Desktop PCs and workstations',4,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(12,2,'Ultrabooks','ultrabooks','Thin and light laptops',5,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(13,2,'Tablets','tablets','Tablets and iPad devices',6,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(15,3,'Graphics Cards (GPU)','graphics-cards','Video cards and GPUs',1,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(16,3,'Processors (CPU)','processors','CPUs and processors',2,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(17,3,'Motherboards','motherboards','Computer motherboards',3,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(18,3,'RAM Memory','ram-memory','RAM and memory modules',4,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(19,3,'Power Supplies','power-supplies','PSU and power units',5,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(20,3,'Cooling Solutions','cooling-solutions','CPU coolers and fans',6,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(22,4,'Hard Disk Drives (HDD)','hard-disk-drives','3.5\" and 2.5\" HDDs',1,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(23,4,'Solid State Drives (SSD)','solid-state-drives','2.5\" SATA SSDs',2,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(24,4,'NVMe SSDs','nvme-ssd','M.2 NVMe drives',3,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(25,4,'External Storage','external-storage','Portable and external drives',4,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(26,4,'Memory Cards','memory-cards','SD, microSD, and memory cards',5,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(27,4,'USB Flash Drives','usb-flash-drives','USB pen drives and sticks',6,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(29,5,'Cables & Connectors','cables-connectors','USB, HDMI, and other cables',1,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(30,5,'Adapters & Converters','adapters-converters','Power adapters and converters',2,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(31,5,'Chargers','chargers','Charging devices and chargers',3,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(32,5,'Power Banks','power-banks','Portable power banks',4,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(33,5,'Docking Stations','docking-stations','Docking and charging stations',5,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(36,6,'Gaming Consoles','gaming-consoles','PlayStation, Xbox, Nintendo',1,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(37,6,'Gaming Controllers','gaming-controllers','Game controllers and joysticks',2,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(38,6,'VR Headsets','vr-headsets','Virtual reality headsets',3,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(39,6,'Gaming Chairs','gaming-chairs','Gaming and racing chairs',4,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(40,6,'Gaming Accessories','gaming-accessories','Gaming mats, grips, and more',5,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(43,7,'24-27 inch Monitors','small-monitors','24-27 inch display monitors',1,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(44,7,'4K Monitors','4k-monitors','4K resolution monitors',2,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(45,7,'Gaming Monitors','gaming-monitors','High refresh rate gaming monitors',3,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(46,7,'Curved Monitors','curved-monitors','Curved display monitors',4,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(47,7,'Ultrawide Monitors','ultrawide-monitors','Ultrawide and super-wide monitors',5,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(48,7,'Projectors','projectors','Home and professional projectors',6,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(50,8,'Printers','printers','Inkjet and laser printers',1,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(51,8,'Scanners','scanners','Document and flatbed scanners',2,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(52,8,'Multifunction Devices','multifunction-devices','All-in-one printer/scanner devices',3,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(53,8,'Shredders','shredders','Paper shredders',4,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(54,8,'Laminating Machines','laminating-machines','Document laminating machines',5,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(57,9,'DSLR Cameras','dslr-cameras','Digital SLR cameras',1,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(58,9,'Mirrorless Cameras','mirrorless-cameras','Mirrorless digital cameras',2,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(59,9,'Camera Lenses','camera-lenses','Interchangeable lenses',3,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(60,9,'Action Cameras','action-cameras','GoPro and action cameras',4,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(61,9,'Photography Lighting','photography-lighting','Studio lights and reflectors',5,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(62,9,'Camera Tripods','camera-tripods','Tripods and monopods',6,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(64,10,'WiFi Routers','wifi-routers','WiFi and mesh routers',1,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(65,10,'Modems','modems','Network modems and gateways',2,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(66,10,'Network Switches','network-switches','Ethernet switches',3,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(67,10,'WiFi Extenders','wifi-extenders','WiFi range extenders',4,1,'2026-01-31 03:00:32','2026-01-31 03:00:32'),(68,10,'Network Cables','network-cables','Ethernet and network cables',5,1,'2026-01-31 03:00:32','2026-01-31 03:00:32');
/*!40000 ALTER TABLE `sub_categories` ENABLE KEYS */;
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
