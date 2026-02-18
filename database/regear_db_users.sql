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
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role` varchar(20) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `warning_count` int DEFAULT '0',
  `last_warning_at` timestamp NULL DEFAULT NULL,
  `suspension_reason` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'buyer','shraddha','mahimayadav2408@gmail.com','05f282be80d42926e102d4b1e42bcd7c$5b138c6ab1d533c20c60f8e9daff089499d65a196dba99d1e107bd9a1b02fcc2','6307142274','2026-01-27 20:02:26',0,NULL,NULL),(2,'buyer','shraddha ','shraddhayadav0305@gmail.com','a66b75725395a211686018ecea66aa07$b209b461c7bec11dfc345fb7d23670366b6de9d8bd09d57e20409cf7b33bbbbd','6307142274','2026-01-29 06:09:58',0,NULL,NULL),(3,'admin','admin','admin@regear.com','79cededd529eee3b003a12ec8ad88a05$94e63efe9f55777d5de7dc585cf9cbf9e0c61d4ab82605fb9114b7a651e23dd3','9999999999','2026-01-30 03:52:54',0,NULL,NULL),(4,'buyer','testbuyer','buyer@test.com','8f43e048ff664bd2b3ce6b76e25b4277$13d821b3ed3ffa5a1d6d33738656bad01814b9e17bf56fdadc9c94d2e66dd5a5','8888888888','2026-01-30 03:52:54',0,NULL,NULL),(5,'seller','testseller','seller@test.com','f7d6186d6b12b7ccb1a4505c053a5719$72584f2d1f1145b9082265a4a85d1ae803bc8dc4bd006fb6a7788aa05be90273','7777777777','2026-01-30 03:52:54',0,NULL,NULL),(6,'buyer','blockeduser','blocked@test.com','ff7a1961a5569ab7387cd1518bde9e0c$240502991b72aaa6e008faef5aecded55f380f70d034c133ce7e7e1dba8c1d50','6666666666','2026-01-30 03:52:54',0,NULL,NULL),(7,'buyer','Aditi joshi','aditijoshi.141235@gmail.com','9984d1c839d6dcbf1726904d9695b077$0ceefd5ba207d961fd9c01c464d90021859760a7a00d415948d3088462af1d1a','9745363736','2026-02-09 17:35:54',0,NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
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
