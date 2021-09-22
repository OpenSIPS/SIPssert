
create database opensips;
use opensips

--
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `location` (
  `contact_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `username` char(64) NOT NULL DEFAULT '',
  `domain` char(64) DEFAULT NULL,
  `contact` char(255) NOT NULL DEFAULT '',
  `received` char(255) DEFAULT NULL,
  `path` char(255) DEFAULT NULL,
  `expires` int unsigned NOT NULL,
  `q` float(10,2) NOT NULL DEFAULT '1.00',
  `callid` char(255) NOT NULL DEFAULT 'Default-Call-ID',
  `cseq` int NOT NULL DEFAULT '13',
  `last_modified` datetime NOT NULL DEFAULT '1900-01-01 00:00:01',
  `flags` int NOT NULL DEFAULT '0',
  `cflags` char(255) DEFAULT NULL,
  `user_agent` char(255) NOT NULL DEFAULT '',
  `socket` char(64) DEFAULT NULL,
  `methods` int DEFAULT NULL,
  `sip_instance` char(255) DEFAULT NULL,
  `kv_store` text,
  `attr` char(255) DEFAULT NULL,
  PRIMARY KEY (`contact_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;



--
-- Table structure for table `subscriber`
--

DROP TABLE IF EXISTS `subscriber`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscriber` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `username` char(64) NOT NULL DEFAULT '',
  `domain` char(64) NOT NULL DEFAULT '',
  `password` char(25) NOT NULL DEFAULT '',
  `email_address` char(64) NOT NULL DEFAULT '',
  `ha1` char(64) NOT NULL DEFAULT '',
  `ha1b` char(64) NOT NULL DEFAULT '',
  `rpid` char(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_idx` (`username`,`domain`),
  KEY `username_idx` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscriber`
--

LOCK TABLES `subscriber` WRITE;
/*!40000 ALTER TABLE `subscriber` DISABLE KEYS */;
INSERT INTO `subscriber` VALUES (1,'test','opensips.org','superSecret','','','',NULL);
/*!40000 ALTER TABLE `subscriber` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `version`
--

DROP TABLE IF EXISTS `version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `version` (
  `table_name` char(32) NOT NULL,
  `table_version` int unsigned NOT NULL DEFAULT '0',
  UNIQUE KEY `t_name_idx` (`table_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `version`
--

LOCK TABLES `version` WRITE;
/*!40000 ALTER TABLE `version` DISABLE KEYS */;
INSERT INTO `version` VALUES ('location',1013),('subscriber',7);
/*!40000 ALTER TABLE `version` ENABLE KEYS */;
UNLOCK TABLES;

