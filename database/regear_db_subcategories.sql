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
-- Table structure for table `subcategories`
--

DROP TABLE IF EXISTS `subcategories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subcategories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `filters` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `subcategories_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subcategories`
--

LOCK TABLES `subcategories` WRITE;
/*!40000 ALTER TABLE `subcategories` DISABLE KEYS */;
INSERT INTO `subcategories` VALUES (1,1,'Android Phones',NULL,'2026-02-09 18:17:59'),(2,1,'iPhones',NULL,'2026-02-09 18:17:59'),(3,1,'Keypad Phones',NULL,'2026-02-09 18:17:59'),(4,2,'Gaming Laptop','{\"gpu\": [\"NVIDIA GTX\", \"NVIDIA RTX\", \"AMD Radeon\"], \"ram\": [\"8GB\", \"16GB\", \"32GB\"], \"storage\": [\"256GB SSD\", \"512GB SSD\", \"1TB SSD\"], \"processor\": [\"Intel i5\", \"Intel i7\", \"Intel i9\", \"AMD Ryzen 5\", \"AMD Ryzen 7\"]}','2026-02-09 18:17:59'),(5,2,'Business Laptop','{\"ram\": [\"8GB\", \"16GB\"], \"weight\": \"Light\", \"battery\": \"Good\", \"storage\": [\"256GB SSD\", \"512GB SSD\"], \"processor\": [\"Intel i5\", \"Intel i7\"]}','2026-02-09 18:17:59'),(6,2,'Student Laptop','{\"ram\": [\"8GB\", \"16GB\"], \"storage\": [\"256GB SSD\", \"512GB SSD\"], \"processor\": [\"Intel i5\", \"Intel i7\", \"AMD Ryzen 5\"]}','2026-02-09 18:17:59'),(7,2,'Chromebook','{\"ram\": [\"4GB\", \"8GB\"], \"storage\": [\"32GB\", \"64GB\", \"128GB\"], \"processor\": [\"Intel\", \"ARM\"]}','2026-02-09 18:17:59'),(8,2,'MacBook','{\"ram\": [\"8GB\", \"16GB\", \"32GB\"], \"model\": [\"MacBook Air\", \"MacBook Pro\", \"MacBook\"], \"processor\": [\"M1\", \"M2\", \"M3\", \"Intel\"]}','2026-02-09 18:17:59'),(9,3,'iPad','{\"model\": [\"iPad Air\", \"iPad Pro\", \"iPad Mini\"]}','2026-02-09 18:17:59'),(10,3,'Android Tablets','{\"brand\": [\"Samsung\", \"OnePlus\", \"Lenovo\"]}','2026-02-09 18:17:59'),(11,3,'Windows Tablets','{\"brand\": [\"Microsoft\", \"HP\", \"Lenovo\"]}','2026-02-09 18:17:59'),(12,4,'Keyboard','{\"type\": [\"Mechanical\", \"Membrane\", \"Wireless\"], \"connectivity\": [\"USB\", \"Bluetooth\"]}','2026-02-09 18:17:59'),(13,4,'Mouse','{\"dpi\": [\"Low\", \"Medium\", \"High\"], \"type\": [\"Wireless\", \"Wired\", \"Gaming\"]}','2026-02-09 18:17:59'),(14,4,'Monitor Stand','{\"adjustable\": \"Yes/No\"}','2026-02-09 18:17:59'),(15,4,'USB Cables','{\"type\": [\"USB-A\", \"USB-C\", \"Micro USB\"]}','2026-02-09 18:17:59'),(16,4,'HDMI Cables','{\"length\": [\"1m\", \"2m\", \"3m\"]}','2026-02-09 18:17:59'),(17,4,'Chargers','{\"type\": [\"Wall Charger\", \"Portable Charger\", \"Fast Charger\"]}','2026-02-09 18:17:59'),(18,5,'Inkjet Printer','{\"color\": \"Yes/No\"}','2026-02-09 18:17:59'),(19,5,'Laser Printer','{\"color\": \"Yes/No\"}','2026-02-09 18:17:59'),(20,5,'All-in-One Printer','{\"features\": [\"Print\", \"Scan\", \"Copy\"]}','2026-02-09 18:17:59'),(21,5,'Scanner','{\"type\": [\"Flatbed\", \"Sheet-fed\"]}','2026-02-09 18:17:59'),(22,6,'LED Monitor','{\"size\": [\"21\\\"\", \"23\\\"\", \"24\\\"\", \"27\\\"\", \"32\\\"\"]}','2026-02-09 18:17:59'),(23,6,'Gaming Monitor','{\"refresh_rate\": [\"60Hz\", \"120Hz\", \"144Hz\", \"165Hz\", \"240Hz\"]}','2026-02-09 18:17:59'),(24,6,'Curved Monitor','{\"curve_radius\": \"VA\"}','2026-02-09 18:17:59'),(25,6,'4K Monitor','{\"resolution\": \"4K\"}','2026-02-09 18:17:59'),(26,7,'PlayStation','{\"model\": [\"PS4\", \"PS5\"]}','2026-02-09 18:17:59'),(27,7,'Xbox','{\"model\": [\"Xbox One\", \"Xbox Series X\", \"Xbox Series S\"]}','2026-02-09 18:17:59'),(28,7,'Nintendo Switch','{\"type\": [\"Standard\", \"Lite\", \"OLED\"]}','2026-02-09 18:17:59'),(29,8,'Apple Watch','{\"series\": [\"Series 9\", \"SE\", \"Ultra\"]}','2026-02-09 18:17:59'),(30,8,'Samsung Watch','{\"model\": [\"Galaxy Watch\", \"Galaxy Fit\"]}','2026-02-09 18:17:59'),(31,8,'Fitbit','{\"type\": [\"Sense\", \"Inspire\", \"Charge\"]}','2026-02-09 18:17:59'),(32,8,'Other Smart Watches','{\"brand\": [\"Garmin\", \"Amazfit\", \"Others\"]}','2026-02-09 18:17:59'),(33,9,'DSLR Camera','{\"brand\": [\"Canon\", \"Nikon\", \"Sony\"], \"megapixels\": [\"12MP\", \"16MP\", \"20MP\", \"24MP+\"]}','2026-02-09 18:17:59'),(34,9,'Mirrorless Camera','{\"brand\": [\"Sony\", \"Canon\", \"Nikon\"]}','2026-02-09 18:17:59'),(35,9,'Point & Shoot Camera','{\"type\": [\"Compact\", \"Bridge\"]}','2026-02-09 18:17:59'),(36,9,'Camera Lenses','{\"type\": [\"Prime\", \"Zoom\"]}','2026-02-09 18:17:59'),(37,10,'WiFi Router','{\"standard\": [\"WiFi 5\", \"WiFi 6\", \"WiFi 6E\"]}','2026-02-09 18:17:59'),(38,10,'WiFi Extender','{\"standard\": [\"WiFi 5\", \"WiFi 6\"]}','2026-02-09 18:17:59'),(39,10,'Network Cable','{\"type\": [\"Cat5e\", \"Cat6\", \"Cat7\"]}','2026-02-09 18:17:59'),(40,10,'Modem','{\"type\": [\"ADSL\", \"Cable\", \"4G\"]}','2026-02-09 18:17:59'),(41,11,'SSD (Solid State Drive)','{\"capacity\": [\"240GB\", \"256GB\", \"512GB\", \"1TB\", \"2TB\"]}','2026-02-09 18:17:59'),(42,11,'HDD (Hard Disk Drive)','{\"capacity\": [\"500GB\", \"1TB\", \"2TB\", \"4TB\"]}','2026-02-09 18:17:59'),(43,11,'USB Pendrive','{\"capacity\": [\"8GB\", \"16GB\", \"32GB\", \"64GB\", \"128GB\"]}','2026-02-09 18:17:59'),(44,11,'Memory Card','{\"capacity\": [\"32GB\", \"64GB\", \"128GB\", \"256GB\"]}','2026-02-09 18:17:59'),(45,12,'Headphones','{\"type\": [\"Over-ear\", \"On-ear\", \"In-ear\"], \"connectivity\": [\"Wired\", \"Wireless\"]}','2026-02-09 18:17:59'),(46,12,'Earbuds','{\"type\": [\"True Wireless\", \"Wired\"], \"noise_cancellation\": \"Yes/No\"}','2026-02-09 18:17:59'),(47,12,'Speakers','{\"type\": [\"Bluetooth\", \"Wired\", \"Smart\"]}','2026-02-09 18:17:59'),(48,12,'Microphone','{\"type\": [\"Condenser\", \"Dynamic\", \"Lavalier\"]}','2026-02-09 18:17:59'),(49,13,'Motherboard','{\"socket\": [\"LGA 1700\", \"AM5\", \"TR4\"]}','2026-02-09 18:17:59'),(50,13,'Graphics Card','{\"type\": [\"NVIDIA\", \"AMD\"], \"vram\": [\"2GB\", \"4GB\", \"6GB\", \"8GB\", \"12GB\"]}','2026-02-09 18:17:59'),(51,13,'Power Supply','{\"wattage\": [\"500W\", \"650W\", \"750W\", \"1000W\"]}','2026-02-09 18:17:59'),(52,13,'RAM Memory','{\"type\": [\"DDR3\", \"DDR4\", \"DDR5\"], \"capacity\": [\"8GB\", \"16GB\", \"32GB\"]}','2026-02-09 18:17:59'),(53,14,'LED TV','{\"inches\": [\"32\", \"43\", \"50\", \"55\", \"65\"]}','2026-02-09 18:17:59'),(54,14,'QLED TV','{\"inches\": [\"55\", \"65\", \"75\", \"85\"]}','2026-02-09 18:17:59'),(55,14,'OLED TV','{\"inches\": [\"55\", \"65\", \"77\"]}','2026-02-09 18:17:59'),(56,14,'Smart TV','{\"os\": [\"Android\", \"WebOS\", \"Tizen\"]}','2026-02-09 18:17:59'),(57,15,'Smart Lights','{\"type\": [\"Bulb\", \"Strip\", \"Panel\"]}','2026-02-09 18:17:59'),(58,15,'Smart Speaker','{\"brand\": [\"Google\", \"Amazon\", \"Apple\"]}','2026-02-09 18:17:59'),(59,15,'Smart Thermostat','{\"model\": [\"Nest\", \"Ecobee\", \"Honeywell\"]}','2026-02-09 18:17:59'),(60,15,'Security Camera','{\"type\": [\"Indoor\", \"Outdoor\", \"Doorbell\"]}','2026-02-09 18:17:59');
/*!40000 ALTER TABLE `subcategories` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-18 22:57:19
